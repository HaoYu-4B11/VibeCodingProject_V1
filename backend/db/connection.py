from langchain_community.utilities import SQLDatabase
from config import settings, DATA_DIR


_business_db: SQLDatabase | None = None


def get_business_db() -> SQLDatabase:
    """获取业务数据库的 LangChain SQLDatabase 包装"""
    global _business_db
    if _business_db is None:
        db_path = DATA_DIR / "business.db"
        _business_db = SQLDatabase.from_uri(
            f"sqlite:///{db_path}",
            sample_rows_in_table_info=3,
        )
    return _business_db


def reset_business_db():
    """重置业务数据库连接（上传新数据后需要刷新）"""
    global _business_db
    _business_db = None
