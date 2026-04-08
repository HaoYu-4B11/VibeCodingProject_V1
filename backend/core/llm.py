from langchain_openai import ChatOpenAI
from config import settings


def get_llm(streaming: bool = False, **kwargs) -> ChatOpenAI:
    """创建 Qwen3 LLM 实例 (DashScope OpenAI 兼容接口)"""
    extra_kwargs = {}
    if not settings.enable_thinking:
        extra_kwargs["extra_body"] = {"enable_thinking": False}

    return ChatOpenAI(
        model=settings.model_name,
        base_url=settings.dashscope_base_url,
        api_key=settings.dashscope_api_key,
        temperature=settings.temperature,
        streaming=streaming,
        **extra_kwargs,
        **kwargs,
    )
