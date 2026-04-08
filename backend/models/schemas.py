from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SessionCreate(BaseModel):
    title: Optional[str] = "新对话"


class SessionUpdate(BaseModel):
    title: str


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class MessageOut(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    sql: Optional[str] = None
    chart_config: Optional[dict] = None
    created_at: str


class SessionDetail(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: list[MessageOut] = []


class ChatRequest(BaseModel):
    session_id: str
    message: str


class TableInfo(BaseModel):
    name: str
    columns: list[dict]
    row_count: int


class UploadResponse(BaseModel):
    table_name: str
    row_count: int
    columns: list[str]
