from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    dashscope_api_key: str = ""
    model_name: str = "qwen3.6-plus"
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    business_db_path: str = "./data/business.db"
    session_db_path: str = "./data/sessions.db"

    memory_window_size: int = 10
    enable_thinking: bool = False
    # 调高可使回答更丰富、少模板化；范围通常 0~2，推荐 0.7~1.0
    temperature: float = 0.85

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
