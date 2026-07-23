"""SiliconFlow 模块入口 — 复用 siliconflow_client，保持现有 import 路径。"""

from app.ai.siliconflow_client import (  # noqa: F401
    SiliconFlowClient,
    SiliconFlowEmptyResponseError,
    SiliconFlowNotConfiguredError,
    SiliconFlowRequestError,
    chat,
    get_model,
    is_configured,
)

__all__ = [
    "SiliconFlowClient",
    "SiliconFlowEmptyResponseError",
    "SiliconFlowNotConfiguredError",
    "SiliconFlowRequestError",
    "chat",
    "get_model",
    "is_configured",
]
