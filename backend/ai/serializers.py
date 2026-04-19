"""DRF input serializers for AI endpoints.

The AI endpoints return free-form structured JSON from the LLM, so we only
validate the *input* here. Output validation is done permissively by the
views (we surface a ``parse_error`` flag when Ollama returns non-JSON).
"""

from rest_framework import serializers


class AnalyzeRiskInputSerializer(serializers.Serializer):
    input = serializers.CharField(
        min_length=3,
        max_length=4000,
        trim_whitespace=True,
        help_text="Short risk title or description.",
    )


class ExpandTextInputSerializer(serializers.Serializer):
    text = serializers.CharField(min_length=1, max_length=4000, trim_whitespace=True)
    field_type = serializers.ChoiceField(
        choices=["risk", "control", "policy", "finding", "generic"],
        default="generic",
    )
    context = serializers.CharField(
        required=False, allow_blank=True, max_length=2000, default=""
    )


class GenerateControlsInputSerializer(serializers.Serializer):
    risk_description = serializers.CharField(
        min_length=3, max_length=4000, trim_whitespace=True
    )


class GenerateFindingInputSerializer(serializers.Serializer):
    observation = serializers.CharField(
        min_length=3, max_length=4000, trim_whitespace=True
    )


class DashboardInsightsInputSerializer(serializers.Serializer):
    """No input fields required; view reads scoped DB stats from request.user."""
