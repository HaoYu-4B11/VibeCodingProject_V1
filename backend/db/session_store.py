import sqlite3
import json
import uuid
from datetime import datetime, timezone
from typing import Optional
from config import DATA_DIR

DB_PATH = DATA_DIR / "sessions.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_session_db():
    """初始化会话数据库表"""
    conn = _get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL DEFAULT '新对话',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
        content TEXT NOT NULL DEFAULT '',
        sql_text TEXT,
        chart_config TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
    """)
    conn.commit()
    conn.close()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Session CRUD ─────────────────────────────────────────────

def create_session(title: str = "新对话") -> dict:
    conn = _get_conn()
    sid = str(uuid.uuid4())
    now = _now()
    conn.execute(
        "INSERT INTO sessions (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (sid, title, now, now),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
    conn.close()
    return dict(row)


def list_sessions() -> list[dict]:
    conn = _get_conn()
    rows = conn.execute("SELECT * FROM sessions ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_session(session_id: str) -> Optional[dict]:
    conn = _get_conn()
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_session(session_id: str, title: str) -> Optional[dict]:
    conn = _get_conn()
    conn.execute(
        "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
        (title, _now(), session_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_session(session_id: str) -> bool:
    conn = _get_conn()
    cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


def touch_session(session_id: str):
    """更新会话的 updated_at 时间戳"""
    conn = _get_conn()
    conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (_now(), session_id))
    conn.commit()
    conn.close()


# ─── Message CRUD ─────────────────────────────────────────────

def add_message(
    session_id: str,
    role: str,
    content: str,
    sql_text: Optional[str] = None,
    chart_config: Optional[dict] = None,
) -> dict:
    conn = _get_conn()
    mid = str(uuid.uuid4())
    now = _now()
    chart_json = json.dumps(chart_config, ensure_ascii=False) if chart_config else None
    conn.execute(
        "INSERT INTO messages (id, session_id, role, content, sql_text, chart_config, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (mid, session_id, role, content, sql_text, chart_json, now),
    )
    conn.execute("UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id))
    conn.commit()
    row = conn.execute("SELECT * FROM messages WHERE id = ?", (mid,)).fetchone()
    conn.close()
    return _row_to_message(row)


def get_messages(session_id: str, limit: int = 100) -> list[dict]:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC LIMIT ?",
        (session_id, limit),
    ).fetchall()
    conn.close()
    return [_row_to_message(r) for r in rows]


def _row_to_message(row: sqlite3.Row) -> dict:
    d = dict(row)
    if d.get("chart_config"):
        try:
            d["chart_config"] = json.loads(d["chart_config"])
        except json.JSONDecodeError:
            d["chart_config"] = None
    d["sql"] = d.pop("sql_text", None)
    return d
