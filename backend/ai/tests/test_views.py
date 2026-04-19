"""Tests for the AI endpoints.

The tests mock :func:`ai.ai_service.call_ollama` so no real Ollama instance
is required. They cover: happy path, non-JSON response (parse_error),
Ollama unreachable (503), invalid input (400), and auth required (401).
"""

import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from ai.ai_service import AIServiceUnavailable

User = get_user_model()

ENDPOINTS = {
    "analyze-risk": ("/api/ai/analyze-risk/", {"input": "ransomware on HR server"}),
    "expand-text": (
        "/api/ai/expand-text/",
        {"text": "weak passwords", "field_type": "risk"},
    ),
    "generate-controls": (
        "/api/ai/generate-controls/",
        {"risk_description": "ransomware on HR server"},
    ),
    "generate-finding": (
        "/api/ai/generate-finding/",
        {"observation": "MFA is not enforced on admin accounts"},
    ),
    "dashboard-insights": ("/api/ai/dashboard-insights/", {}),
}


class AIEndpointsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="ai-tester@example.com", password="pw-ai-tester-1!"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # -- auth ---------------------------------------------------------------

    def test_auth_required(self):
        anon = APIClient()
        for _name, (url, body) in ENDPOINTS.items():
            r = anon.post(url, body, format="json")
            self.assertIn(
                r.status_code,
                (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
                f"{url} should require auth, got {r.status_code}",
            )

    # -- happy path ---------------------------------------------------------

    @patch("ai.views.call_ollama_json")
    def test_happy_paths_return_structured_data(self, mock_call):
        sample_payloads = {
            "analyze-risk": {
                "description": "d",
                "threat_scenario": "t",
                "impact": "i",
                "likelihood": {"level": "Low", "justification": "x"},
                "risk_level": "Low",
                "recommended_mitigations": ["m1"],
                "security_domains": ["Identity"],
            },
            "expand-text": {"expanded": "rewritten"},
            "generate-controls": {
                "controls": [
                    {
                        "name": "MFA",
                        "description": "d",
                        "implementation_guidance": "g",
                        "control_type": "preventive",
                    }
                ]
            },
            "generate-finding": {
                "title": "t",
                "description": "d",
                "impact": "i",
                "recommendation": "r",
                "severity": "medium",
            },
            "dashboard-insights": {
                "top_risks": [],
                "compliance_gaps": [],
                "recommended_actions": [],
                "summary": "all good",
            },
        }

        for name, (url, body) in ENDPOINTS.items():
            mock_call.return_value = (
                sample_payloads[name],
                json.dumps(sample_payloads[name]),
            )
            r = self.client.post(url, body, format="json")
            self.assertEqual(r.status_code, status.HTTP_200_OK, f"{url}: {r.content}")
            self.assertFalse(r.data["parse_error"], f"{url} parse_error was True")
            self.assertEqual(r.data["data"], sample_payloads[name])

    # -- parse error --------------------------------------------------------

    @patch("ai.views.call_ollama_json")
    def test_parse_error_is_surfaced(self, mock_call):
        mock_call.return_value = (None, "not json at all")
        url, body = ENDPOINTS["analyze-risk"]
        r = self.client.post(url, body, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(r.data["parse_error"])
        self.assertEqual(r.data["raw"], "not json at all")
        self.assertIsNone(r.data["data"])

    # -- Ollama unreachable -------------------------------------------------

    @patch("ai.views.call_ollama_json")
    def test_service_unavailable_returns_503(self, mock_call):
        mock_call.side_effect = AIServiceUnavailable("down")
        url, body = ENDPOINTS["analyze-risk"]
        r = self.client.post(url, body, format="json")
        self.assertEqual(r.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("detail", r.data)

    # -- input validation ---------------------------------------------------

    def test_analyze_risk_missing_input(self):
        r = self.client.post("/api/ai/analyze-risk/", {}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expand_text_too_short_input(self):
        r = self.client.post("/api/ai/expand-text/", {"text": ""}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_finding_invalid_field_type(self):
        r = self.client.post(
            "/api/ai/expand-text/",
            {"text": "abc", "field_type": "not-a-choice"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
