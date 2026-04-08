from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import chat, session, database
from db.init_db import init_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_all()
    yield


app = FastAPI(
    title="智能数据分析系统",
    description="基于 LangChain + Qwen3 的自然语言数据库查询与可视化系统",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")
app.include_router(session.router, prefix="/api")
app.include_router(database.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "智能数据分析系统", "version": "0.2.0"}
