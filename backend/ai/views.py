"""AI feature API views.

Each view is a small DRF ``APIView`` that:
  1. Validates input via a dedicated serializer.
  2. Renders a prompt template from :mod:`ai.prompts`.
  3. Calls the local Ollama runtime via :mod:`ai.ai_service`.
  4. Returns ``{data, raw, parse_error}`` so the frontend can gracefully fall
     back when the model returns non-JSON.

All endpoints require authentication (default project auth). They are
throttled under the ``ai`` scope (see ``REST_FRAMEWORK`` settings).
"""

from __future__ import annotations

import json
from typing import Any

import structlog
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from core.models import (
    AppliedControl,
    ComplianceAssessment,
    Finding,
    Folder,
    RequirementAssessment,
    RiskScenario,
)
from iam.models import RoleAssignment

from .ai_service import (
    AIDisabledError,
    AIServiceUnavailable,
    call_ollama_json,
)
from .prompts import (
    render_dashboard_insights_prompt,
    render_expand_text_prompt,
    render_generate_controls_prompt,
    render_generate_finding_prompt,
    render_risk_scenario_prompt,
)
from .serializers import (
    AnalyzeRiskInputSerializer,
    DashboardInsightsInputSerializer,
    ExpandTextInputSerializer,
    GenerateControlsInputSerializer,
    GenerateFindingInputSerializer,
)

logger = structlog.get_logger(__name__)


class BaseAIView(APIView):
    """Shared base: auth, throttling, consistent error handling."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "ai"

    #: Subclasses set these.
    input_serializer_class: type | None = None

    def build_prompt(self, validated: dict, request) -> str:
        raise NotImplementedError

    def post(self, request, *args, **kwargs):
        serializer = self.input_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            prompt = self.build_prompt(serializer.validated_data, request)
            parsed, raw = call_ollama_json(prompt)
        except AIDisabledError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIServiceUnavailable as exc:
            return Response(
                {"detail": str(exc) or "AI service unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception:
            logger.exception("ai_view_unexpected_error", view=self.__class__.__name__)
            return Response(
                {"detail": "AI request failed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "data": parsed,
                "raw": raw if parsed is None else None,
                "parse_error": parsed is None,
            },
            status=status.HTTP_200_OK,
        )


class AnalyzeRiskView(BaseAIView):
    input_serializer_class = AnalyzeRiskInputSerializer

    def build_prompt(self, validated: dict, request) -> str:
        return render_risk_scenario_prompt(validated["input"])


class ExpandTextView(BaseAIView):
    input_serializer_class = ExpandTextInputSerializer

    def build_prompt(self, validated: dict, request) -> str:
        return render_expand_text_prompt(
            text=validated["text"],
            field_type=validated.get("field_type") or "generic",
            context=validated.get("context") or None,
        )


class GenerateControlsView(BaseAIView):
    input_serializer_class = GenerateControlsInputSerializer

    def build_prompt(self, validated: dict, request) -> str:
        return render_generate_controls_prompt(validated["risk_description"])


class GenerateFindingView(BaseAIView):
    input_serializer_class = GenerateFindingInputSerializer

    def build_prompt(self, validated: dict, request) -> str:
        return render_generate_finding_prompt(validated["observation"])


class DashboardInsightsView(BaseAIView):
    """Aggregates (scoped) stats from the user's accessible folders and asks
    the LLM to produce executive insights.
    """

    input_serializer_class = DashboardInsightsInputSerializer

    def _accessible_ids(self, user, model) -> list[Any]:
        viewable, _, _ = RoleAssignment.get_accessible_object_ids(
            Folder.get_root_folder(), user, model
        )
        return viewable

    def _gather_stats(self, user) -> dict[str, Any]:
        try:
            scenario_ids = self._accessible_ids(user, RiskScenario)
            control_ids = self._accessible_ids(user, AppliedControl)
            compliance_ids = self._accessible_ids(user, ComplianceAssessment)
            finding_ids = self._accessible_ids(user, Finding)
            req_assess_ids = self._accessible_ids(user, RequirementAssessment)
        except Exception:
            logger.exception("ai_dashboard_scope_error")
            scenario_ids = control_ids = compliance_ids = finding_ids = (
                req_assess_ids
            ) = []

        scenarios = RiskScenario.objects.filter(id__in=scenario_ids)
        controls = AppliedControl.objects.filter(id__in=control_ids)
        compliance = ComplianceAssessment.objects.filter(id__in=compliance_ids)
        findings = Finding.objects.filter(id__in=finding_ids)
        req_assessments = RequirementAssessment.objects.filter(id__in=req_assess_ids)

        risks_by_treatment: dict[str, int] = {}
        for value, _label in RiskScenario.TREATMENT_OPTIONS:
            risks_by_treatment[value] = scenarios.filter(treatment=value).count()

        top_risks = [
            {
                "name": s.name[:120],
                "impact": s.current_impact,
                "proba": s.current_proba,
                "treatment": s.treatment,
            }
            for s in scenarios.order_by("-current_impact", "-current_proba")[:5]
        ]

        controls_by_status: dict[str, int] = {}
        for choice in AppliedControl.Status.values:
            controls_by_status[choice] = controls.filter(status=choice).count()

        compliance_list = [
            {"name": c.name[:120], "status": getattr(c, "status", None)}
            for c in compliance[:5]
        ]

        return {
            "risks": {
                "total": scenarios.count(),
                "by_treatment": risks_by_treatment,
                "top": top_risks,
            },
            "controls": {
                "total": controls.count(),
                "by_status": controls_by_status,
            },
            "compliance": {
                "total": compliance.count(),
                "assessments_sample": compliance_list,
                "requirement_assessments_total": req_assessments.count(),
            },
            "findings": {
                "total": findings.count(),
            },
        }

    def build_prompt(self, validated: dict, request) -> str:
        stats = self._gather_stats(request.user)
        return render_dashboard_insights_prompt(json.dumps(stats, default=str))
