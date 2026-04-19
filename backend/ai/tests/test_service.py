"""Unit tests for the Ollama service wrapper."""

from unittest.mock import patch, MagicMock

import pytest
import requests

from ai import ai_service
from ai.ai_service import (
    AIServiceUnavailable,
    call_ollama,
    call_ollama_json,
)


def _fake_response(payload: str, status_code: int = 200) -> MagicMock:
    r = MagicMock()
    r.status_code = status_code
    r.json.return_value = {"response": payload}
    r.text = payload
    r.raise_for_status = MagicMock()
    if status_code >= 400:
        err = requests.exceptions.HTTPError(response=r)
        r.raise_for_status.side_effect = err
    return r


@patch.object(ai_service, "AI_ENABLED", True)
@patch("ai.ai_service.requests.post")
def test_call_ollama_returns_response(mock_post):
    mock_post.return_value = _fake_response('{"ok": true}')
    assert call_ollama("hi") == '{"ok": true}'
    mock_post.assert_called_once()


@patch.object(ai_service, "AI_ENABLED", True)
@patch("ai.ai_service.requests.post")
def test_call_ollama_connection_error_maps_to_service_unavailable(mock_post):
    mock_post.side_effect = requests.exceptions.ConnectionError("nope")
    with pytest.raises(AIServiceUnavailable):
        call_ollama("hi")


@patch.object(ai_service, "AI_ENABLED", True)
@patch("ai.ai_service.requests.post")
def test_call_ollama_timeout_maps_to_service_unavailable(mock_post):
    mock_post.side_effect = requests.exceptions.Timeout()
    with pytest.raises(AIServiceUnavailable):
        call_ollama("hi")


@patch.object(ai_service, "AI_ENABLED", True)
@patch("ai.ai_service.requests.post")
def test_call_ollama_json_parses_when_possible(mock_post):
    mock_post.return_value = _fake_response('{"a": 1}')
    parsed, raw = call_ollama_json("hi")
    assert parsed == {"a": 1}
    assert raw == '{"a": 1}'


@patch.object(ai_service, "AI_ENABLED", True)
@patch("ai.ai_service.requests.post")
def test_call_ollama_json_returns_none_on_bad_json(mock_post):
    mock_post.return_value = _fake_response("not json")
    parsed, raw = call_ollama_json("hi")
    assert parsed is None
    assert raw == "not json"
