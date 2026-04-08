import json
import traceback

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse
from langchain_core.messages import AIMessage, ToolMessage

from models.schemas import ChatRequest
from db import session_store
from core.agent import run_agent_stream
from core.memory import load_history
from core.chart_parser import (
    extract_chart_config,
    extract_sql_from_args,
    normalize_message_content,
    strip_chart_block,
)

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat_endpoint(body: ChatRequest):
    """聊天接口 - SSE 流式响应"""
    session = session_store.get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session_store.add_message(body.session_id, "user", body.message)

    return EventSourceResponse(
        _stream_response(body.session_id, body.message),
        media_type="text/event-stream",
    )


async def _stream_response(session_id: str, question: str):
    """生成 SSE 事件流"""
    collected_sql = None
    final_content = ""
    query_result = None

    try:
        history = load_history(session_id)
        history = history[:-1]  # 排除刚添加的 user 消息（agent 自己会带上）

        for node_name, msg in run_agent_stream(question, history):
            if isinstance(msg, AIMessage):
                if msg.tool_calls:
                    sql = extract_sql_from_args(msg.tool_calls)
                    if sql:
                        collected_sql = sql
                        yield _sse("sql", sql)
                elif msg.content:
                    final_content = normalize_message_content(msg.content)
                    text_only = strip_chart_block(final_content)
                    yield _sse("text", text_only)

            elif isinstance(msg, ToolMessage):
                if msg.name == "sql_db_query" and msg.content:
                    query_result = msg.content
                    yield _sse("data", msg.content)

        chart_config = extract_chart_config(final_content) if final_content else None
        if chart_config:
            yield _sse("chart", json.dumps(chart_config, ensure_ascii=False))

        session_store.add_message(
            session_id,
            "assistant",
            strip_chart_block(final_content) if final_content else "",
            sql_text=collected_sql,
            chart_config=chart_config,
        )

        if session_store.get_session(session_id)["title"] == "新对话":
            title = question[:20] + ("..." if len(question) > 20 else "")
            session_store.update_session(session_id, title)

        yield _sse("done", "")

    except Exception as e:
        traceback.print_exc()
        yield _sse("error", str(e))


def _sse(event: str, data: str) -> dict:
    return {"event": event, "data": data}
