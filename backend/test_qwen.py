"""
Qwen3 模型接入测试脚本
通过 DashScope OpenAI 兼容接口调用
测试内容：基础调用、流式输出、函数调用（Tool Calling）
重点观察各场景下的返回字段结构
"""

import os
import json

os.environ["DASHSCOPE_API_KEY"] = "sk-b0be5f2df663445da7ce420f309b7c73"

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

MODEL_NAME = "qwen3.6-plus"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

SEPARATOR = "\n" + "=" * 70 + "\n"


def get_llm(**kwargs):
    return ChatOpenAI(
        model=MODEL_NAME,
        base_url=BASE_URL,
        api_key=os.environ["DASHSCOPE_API_KEY"],
        **kwargs,
    )


def test_basic_invoke():
    """测试 1：基础调用，观察完整返回结构"""
    print(SEPARATOR)
    print(">>> 测试 1：基础调用 (invoke)")
    print(SEPARATOR)

    llm = get_llm()
    messages = [
        SystemMessage(content="你是一个简洁的助手，回答控制在50字以内。"),
        HumanMessage(content="用一句话介绍 Python 语言"),
    ]

    response = llm.invoke(messages)

    print(f"[type]              {type(response).__name__}")
    print(f"[content]           {response.content}")
    print(f"[id]                {response.id}")
    print(f"[response_metadata] {json.dumps(response.response_metadata, ensure_ascii=False, indent=2)}")
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        print(f"[usage_metadata]    {response.usage_metadata}")
    print(f"[additional_kwargs] {json.dumps(response.additional_kwargs, ensure_ascii=False, indent=2)}")


def test_streaming():
    """测试 2：流式输出，逐 chunk 打印字段"""
    print(SEPARATOR)
    print(">>> 测试 2：流式输出 (stream)")
    print(SEPARATOR)

    llm = get_llm(streaming=True)
    messages = [
        SystemMessage(content="你是一个简洁的助手，回答控制在50字以内。"),
        HumanMessage(content="什么是 LangChain？"),
    ]

    print("--- 逐 chunk 详情 ---")
    chunks = []
    for i, chunk in enumerate(llm.stream(messages)):
        chunks.append(chunk)
        meta = chunk.response_metadata if chunk.response_metadata else {}
        print(
            f"  chunk[{i:02d}] "
            f"content={repr(chunk.content):30s} "
            f"id={chunk.id}  "
            f"metadata={json.dumps(meta, ensure_ascii=False)}"
        )

    print(f"\n--- 汇总 ---")
    print(f"  总 chunk 数: {len(chunks)}")
    if chunks:
        last = chunks[-1]
        print(f"  最后一个 chunk response_metadata: {json.dumps(last.response_metadata, ensure_ascii=False, indent=2)}")
        if hasattr(last, "usage_metadata") and last.usage_metadata:
            print(f"  最后一个 chunk usage_metadata: {last.usage_metadata}")
        full_text = "".join(c.content for c in chunks)
        print(f"  拼接完整文本: {full_text}")


def test_tool_calling():
    """测试 3：函数调用 / Tool Calling，观察返回的 tool_calls 字段结构"""
    print(SEPARATOR)
    print(">>> 测试 3：函数调用 (Tool Calling)")
    print(SEPARATOR)

    from langchain_core.tools import tool

    @tool
    def get_weather(city: str) -> str:
        """查询指定城市的天气信息"""
        return f"{city}今天晴，气温25°C"

    @tool
    def calculate(expression: str) -> str:
        """计算数学表达式"""
        return str(eval(expression))

    llm = get_llm()
    llm_with_tools = llm.bind_tools([get_weather, calculate])

    print("--- 3a: 触发天气工具 ---")
    msg = llm_with_tools.invoke("北京今天天气怎么样？")
    print(f"  [type]              {type(msg).__name__}")
    print(f"  [content]           {repr(msg.content)}")
    print(f"  [tool_calls]        {json.dumps(msg.tool_calls, ensure_ascii=False, indent=4) if msg.tool_calls else 'None'}")
    print(f"  [additional_kwargs] {json.dumps(msg.additional_kwargs, ensure_ascii=False, indent=4)}")
    print(f"  [response_metadata] {json.dumps(msg.response_metadata, ensure_ascii=False, indent=4)}")

    print("\n--- 3b: 触发计算工具 ---")
    msg2 = llm_with_tools.invoke("帮我算一下 123 * 456 等于多少")
    print(f"  [type]              {type(msg2).__name__}")
    print(f"  [content]           {repr(msg2.content)}")
    print(f"  [tool_calls]        {json.dumps(msg2.tool_calls, ensure_ascii=False, indent=4) if msg2.tool_calls else 'None'}")
    print(f"  [additional_kwargs] {json.dumps(msg2.additional_kwargs, ensure_ascii=False, indent=4)}")


def test_streaming_with_tools():
    """测试 4：流式 + 工具调用，观察 stream 中 tool_calls 的分片情况"""
    print(SEPARATOR)
    print(">>> 测试 4：流式 + 工具调用")
    print(SEPARATOR)

    from langchain_core.tools import tool

    @tool
    def get_weather(city: str) -> str:
        """查询指定城市的天气信息"""
        return f"{city}今天晴，气温25°C"

    llm = get_llm(streaming=True)
    llm_with_tools = llm.bind_tools([get_weather])

    print("--- 流式 chunk 详情 ---")
    chunks = []
    for i, chunk in enumerate(llm_with_tools.stream("上海天气如何？")):
        chunks.append(chunk)
        tc = chunk.tool_call_chunks if hasattr(chunk, "tool_call_chunks") else None
        print(
            f"  chunk[{i:02d}] "
            f"content={repr(chunk.content):20s} "
            f"tool_call_chunks={tc}  "
            f"additional_kwargs={chunk.additional_kwargs}"
        )

    print(f"\n  总 chunk 数: {len(chunks)}")
    if chunks:
        last = chunks[-1]
        if hasattr(last, "usage_metadata") and last.usage_metadata:
            print(f"  最后一个 chunk usage_metadata: {last.usage_metadata}")


if __name__ == "__main__":
    print("=" * 70)
    print("  Qwen3 模型接入测试 (DashScope OpenAI Compatible)")
    print(f"  模型: {MODEL_NAME}")
    print(f"  Base URL: {BASE_URL}")
    print(f"  API Key: {os.environ['DASHSCOPE_API_KEY'][:10]}...")
    print("=" * 70)

    test_basic_invoke()
    test_streaming()
    test_tool_calling()
    test_streaming_with_tools()

    print(SEPARATOR)
    print("全部测试完成!")
