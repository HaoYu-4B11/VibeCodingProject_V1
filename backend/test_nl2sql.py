"""
NL2SQL 全链路测试脚本
基于 Qwen3.6-plus + SQLDatabaseToolkit + create_agent
测试内容：
  1. SQLDatabase 连接与工具生成
  2. Agent 单轮查询 - 观察每一步的 tool_calls 和 tool 返回
  3. Agent 流式输出 - 观察 stream 的 step 结构
  4. 多轮对话 - 观察上下文保持
"""

import os
import json
import sqlite3

os.environ["DASHSCOPE_API_KEY"] = "sk-b0be5f2df663445da7ce420f309b7c73"

SEPARATOR = "\n" + "=" * 70 + "\n"
MODEL_NAME = "qwen3.6-plus"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
TEST_DB_PATH = "test_sales.db"


# ─── Step 0: 创建测试用 SQLite 数据库 ────────────────────────────────
def create_test_database():
    """创建销售数据示例库"""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL
    );

    CREATE TABLE sales (
        id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        sale_date TEXT NOT NULL,
        region TEXT NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    INSERT INTO products (id, name, category, price) VALUES
        (1, '笔记本电脑', '电子产品', 5999.00),
        (2, '机械键盘', '电子产品', 399.00),
        (3, '运动鞋', '服装', 599.00),
        (4, 'T恤', '服装', 99.00),
        (5, '咖啡豆', '食品', 89.00),
        (6, '牛奶', '食品', 15.00),
        (7, '显示器', '电子产品', 2499.00),
        (8, '书包', '日用品', 199.00);

    INSERT INTO sales (id, product_id, quantity, sale_date, region) VALUES
        (1, 1, 5, '2024-01-15', '华东'),
        (2, 2, 20, '2024-01-16', '华东'),
        (3, 3, 15, '2024-01-17', '华南'),
        (4, 4, 50, '2024-01-18', '华南'),
        (5, 5, 30, '2024-01-19', '华北'),
        (6, 6, 100, '2024-01-20', '华北'),
        (7, 1, 3, '2024-02-01', '华南'),
        (8, 7, 8, '2024-02-02', '华东'),
        (9, 2, 25, '2024-02-03', '华北'),
        (10, 3, 10, '2024-02-04', '华东'),
        (11, 4, 40, '2024-02-05', '华南'),
        (12, 5, 20, '2024-02-06', '华北'),
        (13, 8, 35, '2024-02-07', '华东'),
        (14, 1, 7, '2024-03-01', '华北'),
        (15, 6, 80, '2024-03-02', '华南'),
        (16, 7, 12, '2024-03-03', '华东'),
        (17, 2, 18, '2024-03-04', '华南'),
        (18, 5, 25, '2024-03-05', '华东'),
        (19, 4, 60, '2024-03-06', '华北'),
        (20, 3, 22, '2024-03-07', '华南');
    """)

    conn.commit()
    conn.close()
    print(f"[OK] 测试数据库已创建: {TEST_DB_PATH}")
    print(f"     products 表: 8 条记录")
    print(f"     sales 表: 20 条记录")


# ─── Step 1: 测试 SQLDatabase 包装器 + SQLDatabaseToolkit ────────────
def test_database_and_toolkit():
    """测试 SQLDatabase 连接和 Toolkit 工具生成"""
    print(SEPARATOR)
    print(">>> 测试 1: SQLDatabase + SQLDatabaseToolkit")
    print(SEPARATOR)

    from langchain_community.utilities import SQLDatabase
    from langchain_community.agent_toolkits import SQLDatabaseToolkit
    from langchain_openai import ChatOpenAI

    db = SQLDatabase.from_uri(f"sqlite:///{TEST_DB_PATH}")
    print(f"[SQLDatabase]")
    print(f"  dialect:    {db.dialect}")
    print(f"  tables:     {db.get_usable_table_names()}")
    print(f"  table_info: {db.get_table_info()[:500]}...")

    llm = ChatOpenAI(
        model=MODEL_NAME,
        base_url=BASE_URL,
        api_key=os.environ["DASHSCOPE_API_KEY"],
    )

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    print(f"\n[SQLDatabaseToolkit] 生成的工具列表:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description[:100]}...")

    print(f"\n[手动测试工具调用]")
    list_tool = next(t for t in tools if t.name == "sql_db_list_tables")
    result = list_tool.invoke("")
    print(f"  sql_db_list_tables('')  =>  {repr(result)}")

    schema_tool = next(t for t in tools if t.name == "sql_db_schema")
    result = schema_tool.invoke("products")
    print(f"  sql_db_schema('products')  =>\n{result}")

    query_tool = next(t for t in tools if t.name == "sql_db_query")
    result = query_tool.invoke("SELECT category, COUNT(*) as cnt FROM products GROUP BY category")
    print(f"  sql_db_query(...)  =>  {repr(result)}")

    return db, llm, tools


# ─── Step 2: 测试 create_agent 完整链路 ──────────────────────────────
def test_agent_invoke(db, llm, tools):
    """测试 Agent 完整调用链路，逐步打印每一步的输入输出"""
    print(SEPARATOR)
    print(">>> 测试 2: create_agent 完整链路 (stream)")
    print(SEPARATOR)

    from langchain.agents import create_agent

    system_prompt = """你是一个数据分析专家，专门帮助用户查询和分析 SQL 数据库中的数据。

规则：
1. 先列出可用的表
2. 查看相关表的 schema
3. 生成正确的 SQL 查询
4. 用 query_checker 检查 SQL
5. 执行查询并基于结果用中文回答用户问题
6. 只执行 SELECT 查询，不修改数据
7. 回答要简洁明了"""

    agent = create_agent(llm, tools, system_prompt=system_prompt)

    question = "各个商品类别的总销售额分别是多少？按销售额从高到低排列。"
    print(f"[用户问题] {question}\n")

    step_count = 0
    for step in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="updates",
    ):
        step_count += 1
        print(f"--- Step {step_count} ---")
        print(f"  [keys] {list(step.keys())}")

        for node_name, node_output in step.items():
            print(f"  [node] {node_name}")

            if "messages" in node_output:
                for msg in node_output["messages"]:
                    msg_type = type(msg).__name__
                    print(f"    [{msg_type}]")
                    print(f"      content:          {repr(msg.content[:200]) if msg.content else repr(msg.content)}")

                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        print(f"      tool_calls:")
                        for tc in msg.tool_calls:
                            print(f"        - name: {tc['name']}")
                            print(f"          args: {json.dumps(tc['args'], ensure_ascii=False)}")
                            print(f"          id:   {tc['id']}")

                    if hasattr(msg, "name") and msg.name:
                        print(f"      tool_name:        {msg.name}")

                    if hasattr(msg, "tool_call_id") and msg.tool_call_id:
                        print(f"      tool_call_id:     {msg.tool_call_id}")

                    if msg.response_metadata:
                        finish = msg.response_metadata.get("finish_reason")
                        if finish:
                            print(f"      finish_reason:    {finish}")

                    if hasattr(msg, "usage_metadata") and msg.usage_metadata:
                        print(f"      usage_metadata:   {msg.usage_metadata}")
        print()

    print(f"[完成] 共 {step_count} 步")


# ─── Step 3: 测试 Agent stream 的 values 模式 ────────────────────────
def test_agent_stream_values(db, llm, tools):
    """测试 Agent stream_mode='values' 观察完整 state 结构"""
    print(SEPARATOR)
    print(">>> 测试 3: Agent stream_mode='values' 观察 state")
    print(SEPARATOR)

    from langchain.agents import create_agent

    system_prompt = "你是一个数据分析专家。用中文回答问题。只执行SELECT查询。"
    agent = create_agent(llm, tools, system_prompt=system_prompt)

    question = "哪个地区的销售总量最多？"
    print(f"[用户问题] {question}\n")

    last_state = None
    for state in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        stream_mode="values",
    ):
        last_state = state
        msg = state["messages"][-1]
        msg_type = type(msg).__name__
        content_preview = repr(msg.content[:150]) if msg.content else repr(msg.content)
        tc = msg.tool_calls if hasattr(msg, "tool_calls") and msg.tool_calls else None
        print(f"  [{msg_type}] content={content_preview}")
        if tc:
            for t in tc:
                print(f"             tool_call: {t['name']}({json.dumps(t['args'], ensure_ascii=False)})")

    if last_state:
        print(f"\n[最终 state]")
        print(f"  messages 总数: {len(last_state['messages'])}")
        print(f"  消息类型序列: {[type(m).__name__ for m in last_state['messages']]}")

        final_msg = last_state["messages"][-1]
        print(f"\n[最终回答]")
        print(f"  type:    {type(final_msg).__name__}")
        print(f"  content: {final_msg.content}")
        if final_msg.response_metadata:
            print(f"  response_metadata: {json.dumps(final_msg.response_metadata, ensure_ascii=False, indent=2)}")
        if hasattr(final_msg, "usage_metadata") and final_msg.usage_metadata:
            print(f"  usage_metadata: {final_msg.usage_metadata}")


if __name__ == "__main__":
    print("=" * 70)
    print("  NL2SQL 全链路测试")
    print(f"  模型: {MODEL_NAME} (DashScope OpenAI Compatible)")
    print("=" * 70)

    create_test_database()
    db, llm, tools = test_database_and_toolkit()
    test_agent_invoke(db, llm, tools)
    test_agent_stream_values(db, llm, tools)

    # 清理
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
        print(f"\n[清理] 已删除测试数据库 {TEST_DB_PATH}")

    print(SEPARATOR)
    print("全部测试完成!")
