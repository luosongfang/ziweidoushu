"""LLM 客户端 — OpenAI 兼容 API（可选）。"""

from __future__ import annotations

import httpx

from app.config import settings


class LlmClient:
    """通过 httpx 调用 OpenAI Chat Completions，无 openai SDK 依赖。"""

    @classmethod
    def is_available(cls) -> bool:
        return bool(settings.openai_api_key)

    @classmethod
    async def chat(cls, messages: list[dict[str, str]]) -> tuple[str, int]:
        if not cls.is_available():
            raise RuntimeError("未配置 OPENAI_API_KEY")

        url = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.openai_model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        return content, tokens
