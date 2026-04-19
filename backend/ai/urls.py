from django.urls import path

from .views import (
    AnalyzeRiskView,
    DashboardInsightsView,
    ExpandTextView,
    GenerateControlsView,
    GenerateFindingView,
)

urlpatterns = [
    path("analyze-risk/", AnalyzeRiskView.as_view(), name="ai-analyze-risk"),
    path("expand-text/", ExpandTextView.as_view(), name="ai-expand-text"),
    path(
        "generate-controls/",
        GenerateControlsView.as_view(),
        name="ai-generate-controls",
    ),
    path(
        "generate-finding/",
        GenerateFindingView.as_view(),
        name="ai-generate-finding",
    ),
    path(
        "dashboard-insights/",
        DashboardInsightsView.as_view(),
        name="ai-dashboard-insights",
    ),
]
