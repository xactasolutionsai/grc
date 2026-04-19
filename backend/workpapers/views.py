from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Workpaper, WorkpaperApproval
from .serializers import (
    WorkpaperSerializer,
    WorkpaperApprovalSerializer,
    WorkpaperActionSerializer
)


class IsWorkpaperTeamOrReadOnly(permissions.BasePermission):
    """Simple placeholder permission: authenticated users can interact. Replace with project's RBAC."""
    def has_permission(self, request, view):
        # Temporarily allow unauthenticated access for testing
        return True


class WorkpaperViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Workpaper model with CRUD operations and workflow actions.
    
    Custom actions:
    - upload_file: Upload a file to existing workpaper
    - submit_for_review: Submit workpaper for review
    - review: Mark workpaper as reviewed
    - approve: Approve workpaper
    - reject: Reject workpaper with reason
    - delete_file: Remove attached file
    """
    
    queryset = Workpaper.objects.select_related('uploaded_by', 'reviewer', 'approver').all()
    serializer_class = WorkpaperSerializer
    permission_classes = [IsWorkpaperTeamOrReadOnly]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'workpaper_type', 'uploaded_by', 'reviewer', 'approver', 'is_active']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'title', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter queryset based on query parameters with optimized queries.
        """
        queryset = Workpaper.objects.select_related('uploaded_by', 'reviewer', 'approver').all()
        
        # Filter by current user's uploads
        my_uploads = self.request.query_params.get('my_uploads', None)
        if my_uploads and my_uploads.lower() == 'true':
            queryset = queryset.filter(uploaded_by=self.request.user)
        
        # Filter by pending review (status=collected or reviewed but not approved)
        pending_review = self.request.query_params.get('pending_review', None)
        if pending_review and pending_review.lower() == 'true':
            queryset = queryset.filter(status__in=['collected', 'reviewed'])
        
        # Filter by tags (JSON field search)
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tags__contains=[tag])
        
        return queryset
    
    def get_serializer_context(self):
        """Pass request to serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def perform_create(self, serializer):
        """Set uploaded_by to current user on creation"""
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_file(self, request, pk=None):
        """
        Upload or replace file for a workpaper.
        Expects 'file' in multipart form data.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        workpaper = self.get_object()
        logger.info(f"Upload file request for workpaper {pk}")
        
        if 'file' not in request.FILES:
            logger.error("No file provided in request")
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        logger.info(f"Received file: {uploaded_file.name}, size: {uploaded_file.size}, content_type: {uploaded_file.content_type}")
        
        # Delete old file if exists
        if workpaper.file:
            workpaper.file.delete(save=False)
        
        # Save new file
        try:
            workpaper.file = uploaded_file
            workpaper.file_size = uploaded_file.size
            workpaper.save()
            logger.info(f"File saved successfully for workpaper {pk}")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return Response(
                {'error': f'Failed to save file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = self.get_serializer(workpaper)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'])
    def delete_file(self, request, pk=None):
        """
        Remove the attached file from a workpaper.
        """
        workpaper = self.get_object()
        
        if not workpaper.file:
            return Response(
                {'error': 'No file attached to this workpaper'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete the file
        workpaper.file.delete(save=False)
        workpaper.file = None
        workpaper.file_size = None
        workpaper.save()
        
        return Response(
            {'message': 'File deleted successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        """
        Submit workpaper for review.
        Changes status from 'collected' to 'reviewed'.
        """
        workpaper = self.get_object()
        
        if not workpaper.can_be_reviewed():
            return Response(
                {'error': f'Workpaper cannot be reviewed. Current status: {workpaper.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = workpaper.submit_for_review(request.user)
        
        if success:
            serializer = self.get_serializer(workpaper)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Failed to submit for review'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """
        Mark workpaper as reviewed (same as submit_for_review).
        For backward compatibility and clarity.
        """
        return self.submit_for_review(request, pk)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a workpaper.
        Changes status from 'reviewed' to 'approved'.
        """
        workpaper = self.get_object()
        action_serializer = WorkpaperActionSerializer(data=request.data)
        
        if not action_serializer.is_valid():
            return Response(action_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if not workpaper.can_be_approved():
            return Response(
                {'error': f'Workpaper cannot be approved. Current status: {workpaper.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comments = action_serializer.validated_data.get('comments', '')
        success = workpaper.approve(request.user, comments)
        
        if success:
            serializer = self.get_serializer(workpaper)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Failed to approve workpaper'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a workpaper with a reason.
        Status remains unchanged but rejection_reason is recorded.
        """
        workpaper = self.get_object()
        action_serializer = WorkpaperActionSerializer(data=request.data)
        
        if not action_serializer.is_valid():
            return Response(action_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        reason = action_serializer.validated_data.get('reason', '')
        success = workpaper.reject(request.user, reason)
        
        if success:
            serializer = self.get_serializer(workpaper)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Failed to reject workpaper'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def approval_history(self, request, pk=None):
        """
        Get approval history for a specific workpaper.
        """
        workpaper = self.get_object()
        history = workpaper.approval_history.select_related('action_by').all()
        serializer = WorkpaperApprovalSerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkpaperApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for WorkpaperApproval (approval history).
    """
    
    queryset = WorkpaperApproval.objects.select_related('workpaper', 'action_by').all()
    serializer_class = WorkpaperApprovalSerializer
    permission_classes = [IsWorkpaperTeamOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['workpaper', 'action', 'action_by']
    ordering_fields = ['created_at']
    ordering = ['created_at']

