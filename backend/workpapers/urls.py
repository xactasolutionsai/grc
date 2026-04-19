from rest_framework.routers import DefaultRouter
from .views import WorkpaperViewSet, WorkpaperApprovalViewSet

router = DefaultRouter()
router.register(r'workpapers', WorkpaperViewSet, basename='workpaper')
router.register(r'approvals', WorkpaperApprovalViewSet, basename='workpaper-approval')

urlpatterns = router.urls

