import json
import re
from typing import Any, Optional, Tuple


def normalize_message_content(content: Any) -> str:
    """
    将 LangChain / 多模型返回的 message.content 统一为纯字符串。
    OpenAI 兼容接口下可能出现 str，也可能出现 [{'type':'text','text':'...'}, ...]。
    """
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                t = block.get("text") or block.get("content")
                if isinstance(t, str):
                    parts.append(t)
                elif t is not None:
                    parts.append(str(t))
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts)
    return str(content)


def _first_echarts_block_span(text: str) -> Optional[Tuple[int, int, int, int]]:
    """
    定位第一个 ```echarts ... ``` 围栏块。
    返回 (block_start, block_end_excl, json_start, json_end_excl)，按行识别闭合围栏，
    避免在 JSON 内部误匹配非贪婪 `` *?\n``` `` 导致的过早截断。
    """
    marker = "```echarts"
    i = text.find(marker)
    if i < 0:
        return None
    j = i + len(marker)
    while j < len(text) and text[j] in " \t":
        j += 1
    if j >= len(text):
        return None
    if text[j] == "\n":
        j += 1
    elif text[j] == "\r" and j + 1 < len(text) and text[j + 1] == "\n":
        j += 2
    json_start = j
    pos = json_start
    while True:
        nl = text.find("\n", pos)
        if nl < 0:
            line = text[pos:]
            stripped = line.strip()
            if stripped == "```" or (
                stripped.startswith("```")
                and not stripped.lower().startswith("```echarts")
            ):
                json_end = pos
                block_end = len(text)
                return (i, block_end, json_start, json_end)
            return None
        line = text[pos:nl]
        stripped = line.strip()
        if stripped == "```" or (
            stripped.startswith("```")
            and not stripped.lower().startswith("```echarts")
        ):
            json_end = pos
            block_end = nl + 1
            return (i, block_end, json_start, json_end)
        pos = nl + 1


def strip_chart_block(text: str) -> str:
    """移除所有 echarts 围栏代码块，保留其余说明文字。"""
    if not text:
        return ""
    out = text
    while True:
        span = _first_echarts_block_span(out)
        if not span:
            break
        block_start, block_end_excl, _, _ = span
        out = (out[:block_start] + out[block_end_excl:]).strip()
    return out.strip()


def extract_chart_config(text: str) -> Optional[dict]:
    """从 LLM 输出文本中提取 ECharts 图表配置 JSON"""
    span = _first_echarts_block_span(text)
    if span:
        _, _, js, je = span
        json_str = text[js:je].strip()
        try:
            config = json.loads(json_str)
            if isinstance(config, dict) and ("series" in config or "xAxis" in config):
                return config
        except json.JSONDecodeError:
            fixed = _try_fix_json(json_str)
            if fixed:
                return fixed
    # 兜底：旧版正则（兼容性）
    pattern = r"```echarts\s*\n([\s\S]*?)\n```"
    match = re.search(pattern, text)
    if not match:
        return None
    json_str = match.group(1).strip()
    try:
        config = json.loads(json_str)
        if isinstance(config, dict) and ("series" in config or "xAxis" in config):
            return config
    except json.JSONDecodeError:
        pass
    return _try_fix_json(json_str)


def extract_sql_from_args(tool_calls: list[dict]) -> Optional[str]:
    """从 Agent tool_calls 中提取 SQL 语句"""
    for tc in tool_calls:
        if tc.get("name") in ("sql_db_query", "sql_db_query_checker"):
            args = tc.get("args", {})
            return args.get("query")
    return None


def extract_query_result(content: str) -> Optional[list]:
    """将 ToolMessage 中的查询结果字符串解析为 Python 对象"""
    content = content.strip()
    if not content.startswith("["):
        return None
    try:
        return eval(content)  # noqa: S307 - 工具返回的结构化结果
    except Exception:
        return None


def _try_fix_json(json_str: str) -> Optional[dict]:
    """尝试修复常见的 JSON 格式问题"""
    json_str = re.sub(r",\s*([}\]])", r"\1", json_str)
    json_str = re.sub(r"'", '"', json_str)
    try:
        config = json.loads(json_str)
        if isinstance(config, dict):
            return config
    except json.JSONDecodeError:
        pass
    return None
