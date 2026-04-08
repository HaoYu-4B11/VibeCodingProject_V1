from fastapi import APIRouter, HTTPException

from models.schemas import SessionCreate, SessionUpdate, SessionOut, SessionDetail, MessageOut
from db import session_store

router = APIRouter(tags=["sessions"])


@router.get("/sessions", response_model=list[SessionOut])
async def list_sessions():
    """获取所有会话列表"""
    return session_store.list_sessions()


@router.post("/sessions", response_model=SessionOut, status_code=201)
async def create_session(body: SessionCreate):
    """创建新会话"""
    return session_store.create_session(title=body.title)


@router.get("/sessions/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str):
    """获取会话详情（含历史消息）"""
    s = session_store.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="会话不存在")
    messages = session_store.get_messages(session_id)
    return {**s, "messages": messages}


@router.put("/sessions/{session_id}", response_model=SessionOut)
async def update_session(session_id: str, body: SessionUpdate):
    """更新会话标题"""
    s = session_store.update_session(session_id, body.title)
    if not s:
        raise HTTPException(status_code=404, detail="会话不存在")
    return s


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话及其所有消息"""
    ok = session_store.delete_session(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"message": "已删除"}
