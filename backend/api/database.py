import sqlite3
import io

from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd

from config import DATA_DIR
from db.connection import get_business_db, reset_business_db
from models.schemas import TableInfo, UploadResponse

router = APIRouter(tags=["database"])

DB_PATH = DATA_DIR / "business.db"


@router.get("/database/tables", response_model=list[TableInfo])
async def list_tables():
    """获取所有表及其结构"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()

    result = []
    for t in tables:
        name = t["name"]
        cols = conn.execute(f"PRAGMA table_info({name})").fetchall()
        count = conn.execute(f"SELECT COUNT(*) FROM [{name}]").fetchone()[0]
        result.append({
            "name": name,
            "columns": [{"name": c["name"], "type": c["type"], "notnull": bool(c["notnull"]), "pk": bool(c["pk"])} for c in cols],
            "row_count": count,
        })

    conn.close()
    return result


@router.get("/database/preview/{table_name}")
async def preview_table(table_name: str, limit: int = 50):
    """预览表数据"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    check = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
    ).fetchone()
    if not check:
        conn.close()
        raise HTTPException(status_code=404, detail=f"表 '{table_name}' 不存在")

    rows = conn.execute(f"SELECT * FROM [{table_name}] LIMIT ?", (limit,)).fetchall()
    columns = [desc[0] for desc in conn.execute(f"SELECT * FROM [{table_name}] LIMIT 1").description] if rows else []
    conn.close()

    return {
        "table": table_name,
        "columns": columns,
        "rows": [dict(r) for r in rows],
        "total": len(rows),
    }


@router.post("/database/upload", response_model=UploadResponse)
async def upload_data(file: UploadFile = File(...), table_name: str | None = None):
    """上传 CSV/Excel 文件并导入到数据库"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("csv", "xlsx", "xls"):
        raise HTTPException(status_code=400, detail="仅支持 CSV 和 Excel 文件")

    content = await file.read()

    try:
        if ext == "csv":
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件解析失败: {e}")

    if not table_name:
        table_name = file.filename.rsplit(".", 1)[0]
        table_name = "".join(c if c.isalnum() or c == "_" else "_" for c in table_name)

    conn = sqlite3.connect(str(DB_PATH))
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

    reset_business_db()

    return {
        "table_name": table_name,
        "row_count": len(df),
        "columns": list(df.columns),
    }
