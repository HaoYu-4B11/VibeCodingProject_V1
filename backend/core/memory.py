from db.session_store import get_messages
from config import settings


def load_history(session_id: str) -> list[dict]:
    """
    从数据库加载会话历史，截取最近 N 轮对话作为上下文。
    返回格式: [{"role": "user"/"assistant", "content": "..."}]
    """
    all_messages = get_messages(session_id)
    window = settings.memory_window_size * 2  # N 轮 = N条user + N条assistant
    recent = all_messages[-window:] if len(all_messages) > window else all_messages

    history = []
    for m in recent:
        history.append({
            "role": m["role"],
            "content": m["content"],
        })
    return history
