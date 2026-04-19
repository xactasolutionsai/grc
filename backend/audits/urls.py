from rest_framework.routers import DefaultRouter
from .views import (
    AuditEntityViewSet,
    AuditPlanViewSet,
    AuditPlanApprovalViewSet,
    AuditEngagementViewSet,
    ChecklistViewSet,
    ChecklistItemViewSet,
    ChecklistExecutionViewSet,
    ChecklistItemResultViewSet,
)

router = DefaultRouter()
router.register(r"entities", AuditEntityViewSet, basename="audit-entity")
router.register(r"plans", AuditPlanViewSet, basename="audit-plan")
router.register(r"approvals", AuditPlanApprovalViewSet, basename="audit-plan-approval")
router.register(r"engagements", AuditEngagementViewSet, basename="audit-engagement")
router.register(r"checklists", ChecklistViewSet, basename="checklist")
router.register(r"checklist-items", ChecklistItemViewSet, basename="checklist-item")
router.register(
    r"checklist-executions", ChecklistExecutionViewSet, basename="checklist-execution"
)
router.register(
    r"checklist-item-results",
    ChecklistItemResultViewSet,
    basename="checklist-item-result",
)

urlpatterns = router.urls
