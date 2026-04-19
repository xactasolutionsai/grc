"""
Thin Ollama HTTP client used by the AI feature endpoints.

The LLM runs locally (default: http://ollama:11434). No external calls are made.
The client prefers Ollama's ``format=json`` mode and attempts to parse the
response as JSON. If parsing fails, callers receive ``(None, raw_text)`` and
are expected to surface a ``parse_error`` to the client.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

import requests
import structlog

logger = structlog.get_logger(__name__)


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434").rstrip("/")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
DEFAULT_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))
AI_ENABLED = _bool_env("AI_ENABLED", default=True)


class AIServiceError(Exception):
    """Base exception for AI service failures."""


class AIServiceUnavailable(AIServiceError):
    """Raised when the Ollama service is unreachable or returns an error."""


class AIDisabledError(AIServiceError):
    """Raised when AI features are disabled via env flag."""


def call_ollama(
    prompt: str,
    *,
    model: str | None = None,
    format: str | None = "json",
    timeout: int | None = None,
    options: dict[str, Any] | None = None,
) -> str:
    """Call the Ollama ``/api/generate`` endpoint and return the raw string response.

    Raises :class:`AIServiceUnavailable` on connection/HTTP/timeout errors so
    views can map to a 503 consistently.
    """

    if not AI_ENABLED:
        raise AIDisabledError("AI features are disabled (set AI_ENABLED=True).")

    payload: dict[str, Any] = {
        "model": model or DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    if format:
        payload["format"] = format
    if options:
        payload["options"] = options

    url = f"{OLLAMA_URL}/api/generate"
    started = time.monotonic()
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=timeout or DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError as exc:
        logger.warning(
            "ollama_unreachable", url=url, model=payload["model"], error=str(exc)
        )
        raise AIServiceUnavailable("Unable to reach the AI service.") from exc
    except requests.exceptions.Timeout as exc:
        logger.warning("ollama_timeout", url=url, model=payload["model"])
        raise AIServiceUnavailable("The AI service timed out.") from exc
    except requests.exceptions.HTTPError as exc:
        logger.warning(
            "ollama_http_error",
            url=url,
            model=payload["model"],
            status=response.status_code if response is not None else None,
            body=response.text[:500] if response is not None else None,
        )
        raise AIServiceUnavailable(
            f"The AI service returned an error (HTTP {response.status_code})."
        ) from exc
    except requests.RequestException as exc:
        logger.warning("ollama_request_error", url=url, error=str(exc))
        raise AIServiceUnavailable("AI request failed.") from exc

    elapsed_ms = int((time.monotonic() - started) * 1000)
    logger.info(
        "ollama_call_ok",
        url=url,
        model=payload["model"],
        prompt_len=len(prompt),
        elapsed_ms=elapsed_ms,
    )

    try:
        return response.json()["response"]
    except (ValueError, KeyError) as exc:
        raise AIServiceUnavailable("Malformed response from AI service.") from exc


def call_ollama_json(
    prompt: str,
    **kwargs: Any,
) -> tuple[Any | None, str]:
    """Like :func:`call_ollama` but also attempts to ``json.loads`` the response.

    Returns ``(parsed, raw)``; ``parsed`` is ``None`` on JSON parse failure so
    callers can surface a ``parse_error`` flag.
    """

    raw = call_ollama(prompt, **kwargs)
    try:
        return json.loads(raw), raw
    except json.JSONDecodeError:
        logger.info("ollama_json_parse_failed", raw_len=len(raw))
        return None, raw
