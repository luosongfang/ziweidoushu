"""SiliconFlow 客户端 — OpenAI 兼容调用（仅服务端使用）。"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

from app.config import settings

_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"
_DEFAULT_BASE = "https://api.siliconflow.cn/v1"
_DEFAULT_MODEL = "deepseek-ai/DeepSeek-V3"


class SiliconFlowNotConfiguredError(Exception):
    """未配置 SILICONFLOW_API_KEY。"""


class SiliconFlowRequestError(Exception):
    """SiliconFlow 调用失败。"""


class SiliconFlowEmptyResponseError(Exception):
    """模型返回为空。"""


def _refresh_env() -> None:
    """每次调用前刷新 .env，避免改 Key 后必须整进程重启。"""
    load_dotenv(_ENV_FILE, override=True)


def _api_key() -> str:
    _refresh_env()
    return (
        os.getenv("SILICONFLOW_API_KEY")
        or settings.siliconflow_api_key
        or ""
    ).strip()


def _base_url() -> str:
    _refresh_env()
    return (
        os.getenv("SILICONFLOW_BASE_URL")
        or settings.siliconflow_base_url
        or _DEFAULT_BASE
    ).rstrip("/")


def is_configured() -> bool:
    return bool(_api_key())


def get_model() -> str:
    """模型名独立配置：AI_MODEL，默认 DeepSeek-V3。"""
    _refresh_env()
    return (os.getenv("AI_MODEL") or settings.ai_model or _DEFAULT_MODEL).strip()


def _client() -> AsyncOpenAI:
    key = _api_key()
    if not key:
        raise SiliconFlowNotConfiguredError("SILICONFLOW_API_KEY 未配置")
    # OpenAI 兼容客户端 → SiliconFlow
    return AsyncOpenAI(api_key=key, base_url=_base_url())


async def chat(messages: list[dict[str, str]]) -> str:
    """调用 SiliconFlow Chat Completions，返回助手文本。"""
    client = _client()
    try:
        response = await client.chat.completions.create(
            model=get_model(),
            messages=messages,
            temperature=0.7,
            max_tokens=3000,
        )
    except SiliconFlowNotConfiguredError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise SiliconFlowRequestError(str(exc)) from exc

    try:
        content = response.choices[0].message.content
    except (IndexError, AttributeError, TypeError) as exc:
        raise SiliconFlowRequestError("响应格式异常") from exc

    if content is None or not str(content).strip():
        raise SiliconFlowEmptyResponseError("AI返回为空")

    return str(content).strip()


class SiliconFlowClient:
    """面向接口层的客户端封装。"""

    is_configured = staticmethod(is_configured)
    get_model = staticmethod(get_model)

    @classmethod
    async def chat(cls, messages: list[dict[str, str]]) -> str:
        return await chat(messages)
