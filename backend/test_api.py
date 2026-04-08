"""Phase 3 API 集成测试脚本"""

import requests
import json

BASE = "http://localhost:8000/api"


def test_health():
    print("=== 1. Health ===")
    r = requests.get(f"{BASE}/health")
    print(f"  [{r.status_code}] {r.json()}")
    assert r.status_code == 200


def test_database_tables():
    print("\n=== 2. Database Tables ===")
    r = requests.get(f"{BASE}/database/tables")
    tables = r.json()
    print(f"  [{r.status_code}] {len(tables)} 张表:")
    for t in tables:
        print(f"    - {t['name']}: {t['row_count']} 行, {len(t['columns'])} 列")
    assert r.status_code == 200
    assert len(tables) >= 3


def test_database_preview():
    print("\n=== 3. Database Preview ===")
    r = requests.get(f"{BASE}/database/preview/products?limit=3")
    data = r.json()
    print(f"  [{r.status_code}] 表 {data['table']}: {data['total']} 行")
    for row in data["rows"]:
        print(f"    {row}")
    assert r.status_code == 200


def test_session_crud():
    print("\n=== 4. Session CRUD ===")

    r = requests.post(f"{BASE}/sessions", json={"title": "API测试会话"})
    session = r.json()
    sid = session["id"]
    print(f"  创建: [{r.status_code}] id={sid}, title={session['title']}")
    assert r.status_code == 201

    r = requests.get(f"{BASE}/sessions")
    sessions = r.json()
    print(f"  列表: [{r.status_code}] {len(sessions)} 个会话")
    assert r.status_code == 200

    r = requests.get(f"{BASE}/sessions/{sid}")
    detail = r.json()
    print(f"  详情: [{r.status_code}] messages={len(detail['messages'])}")
    assert r.status_code == 200

    r = requests.put(f"{BASE}/sessions/{sid}", json={"title": "已更名会话"})
    print(f"  更新: [{r.status_code}] new_title={r.json()['title']}")
    assert r.status_code == 200

    return sid


def test_chat_sse(session_id: str):
    print("\n=== 5. Chat SSE (NL2SQL 全链路) ===")
    r = requests.post(
        f"{BASE}/chat",
        json={"session_id": session_id, "message": "各个商品类别的总销售额是多少？按金额从高到低排列"},
        stream=True,
        timeout=120,
    )
    print(f"  [{r.status_code}] SSE stream:")

    events = []
    for line in r.iter_lines(decode_unicode=True):
        if not line:
            continue
        if line.startswith("event:"):
            event_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            data = line.split(":", 1)[1].strip()
            events.append({"event": event_type, "data": data})
            preview = data[:100] + "..." if len(data) > 100 else data
            print(f"    [{event_type:6s}] {preview}")

    print(f"\n  共 {len(events)} 个 SSE 事件")
    event_types = [e["event"] for e in events]
    print(f"  事件类型: {event_types}")

    assert "sql" in event_types, "应包含 sql 事件"
    assert "text" in event_types, "应包含 text 事件"
    assert "done" in event_types, "应包含 done 事件"

    print("\n  验证消息持久化:")
    r = requests.get(f"{BASE}/sessions/{session_id}")
    msgs = r.json()["messages"]
    print(f"  会话中共 {len(msgs)} 条消息:")
    for m in msgs:
        preview = m["content"][:80] + "..." if len(m["content"]) > 80 else m["content"]
        sql_tag = " [有SQL]" if m.get("sql") else ""
        chart_tag = " [有图表]" if m.get("chart_config") else ""
        print(f"    [{m['role']:9s}] {preview}{sql_tag}{chart_tag}")

    return session_id


def test_delete_session(session_id: str):
    print(f"\n=== 6. Delete Session ===")
    r = requests.delete(f"{BASE}/sessions/{session_id}")
    print(f"  [{r.status_code}] {r.json()}")
    assert r.status_code == 200


if __name__ == "__main__":
    print("=" * 60)
    print("  Phase 3 API 集成测试")
    print("=" * 60)

    test_health()
    test_database_tables()
    test_database_preview()
    sid = test_session_crud()
    test_chat_sse(sid)
    test_delete_session(sid)

    print("\n" + "=" * 60)
    print("  全部测试通过!")
    print("=" * 60)
