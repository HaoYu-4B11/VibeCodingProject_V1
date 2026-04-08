from langchain.agents import create_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from core.llm import get_llm
from core.prompts import SQL_AGENT_SYSTEM_PROMPT
from db.connection import get_business_db


def build_sql_agent():
    """构建 SQL Agent (每次调用返回新实例)"""
    llm = get_llm()
    db = get_business_db()
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    tools = toolkit.get_tools()

    system_prompt = SQL_AGENT_SYSTEM_PROMPT.format(dialect=db.dialect)

    agent = create_agent(llm, tools, system_prompt=system_prompt)
    return agent


def run_agent_stream(question: str, history_messages: list[dict] | None = None):
    """
    运行 SQL Agent 并以 stream_mode="updates" 逐步产出结果。

    Yields: (node_name, message) 元组
        - node_name: "model" 或 "tools"
        - message: AIMessage 或 ToolMessage
    """
    agent = build_sql_agent()

    messages = []
    if history_messages:
        for m in history_messages:
            messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": question})

    for step in agent.stream(
        {"messages": messages},
        stream_mode="updates",
    ):
        for node_name, node_output in step.items():
            if "messages" in node_output:
                for msg in node_output["messages"]:
                    yield node_name, msg
