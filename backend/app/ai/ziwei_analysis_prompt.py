"""紫微分析 Prompt — 兼容旧导入路径。"""

from app.ai.prompt import ZIWEI_SYSTEM_PROMPT, build_user_message

ZIWEI_ANALYSIS_SYSTEM_PROMPT = ZIWEI_SYSTEM_PROMPT

__all__ = [
    "ZIWEI_ANALYSIS_SYSTEM_PROMPT",
    "ZIWEI_SYSTEM_PROMPT",
    "build_user_message",
]
