from __future__ import annotations

from typing import Any

import httpx

from config.settings import settings


def _trace_url() -> str:
    return f"{settings.TRACER_BASE_URL.rstrip('/')}/{settings.TRACER_API_KEY}"


async def trace_action(action: str, *, step_data: dict[str, Any] | None = None, title: str | None = None) -> None:
    payload: dict[str, Any] = {"action": action}

    if step_data is not None:
        payload["stepData"] = step_data
    if title is not None:
        payload["title"] = title

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.post(_trace_url(), json=payload)
            response.raise_for_status()
    except Exception:
        # Tracing must never break the agent pipeline.
        return
