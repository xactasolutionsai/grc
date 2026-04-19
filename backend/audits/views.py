from rest_framework import viewsets, permissions, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
import csv
import io
from .models import AuditEntity, AuditPlan, AuditPlanApproval, AuditEngagement, EntityProcessActivity, Checklist, ChecklistItem, ChecklistExecution, ChecklistItemResult
from .serializers import (
    AuditEntitySerializer, AuditPlanSerializer, RelatedObjectsSerializer,
    AuditPlanApprovalSerializer, AuditPlanApprovalActionSerializer,
    AuditEngagementSerializer, AuditEngagementActionSerializer,
    EntityProcessActivitySerializer, ChecklistSerializer, ChecklistItemSerializer,
    ChecklistExecutionSerializer, ChecklistItemResultSerializer,
)
from core.models import ComplianceAssessment, RiskScenario, AppliedControl, Finding

class IsAuditTeamOrReadOnly(permissions.BasePermission):
    """Simple placeholder permission: authenticated users can interact. Replace with project's RBAC."""
    def has_permission(self, request, view):
        # Temporarily allow unauthenticated access for testing
        return True

class AuditEntityPagination(PageNumberPagination):
    """Pagination for AuditEntity list view."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class AuditEntityViewSet(viewsets.ModelViewSet):
    """CRUD for AuditEntity."""
    queryset = AuditEntity.objects.select_related('parent', 'owner', 'team_member').all()
    serializer_class = AuditEntitySerializer
    permission_classes = [IsAuditTeamOrReadOnly]
    pagination_class = AuditEntityPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['entity_type', 'is_active', 'priority', 'criticality', 'country', 'region', 'city']
    search_fields = ['name', 'description', 'entity_type', 'owner__email', 'country', 'region', 'city', 'address']
    ordering_fields = ['name', 'risk_score', 'last_audited', 'created_at', 'criticality', 'priority', 'audit_frequency', 'country', 'region', 'city']
    ordering = ['name']
    
    def get_queryset(self):
        """Optimized queryset with select_related to avoid N+1 queries."""
        queryset = AuditEntity.objects.select_related('parent', 'owner', 'team_member').all()
        
        # Only apply user-specific filters if user is authenticated
        if self.request.user and self.request.user.is_authenticated:
            # Filter by my entities (current user is owner OR team_member)
            my_entities = self.request.query_params.get('my_entities')
            if my_entities and my_entities.lower() == 'true':
                queryset = queryset.filter(
                    Q(owner=self.request.user) | Q(team_member=self.request.user)
                )
            
            # Filter by my team's entities (current user is owner/lead)
            my_team = self.request.query_params.get('my_team')
            if my_team and my_team.lower() == 'true':
                queryset = queryset.filter(owner=self.request.user)
        
        return queryset
    
    def get_object(self):
        """Optimized single object retrieval with prefetch_related for children."""
        queryset = self.get_queryset()
        # For detail view, prefetch children and processes
        if hasattr(self, 'action') and self.action == 'retrieve':
            queryset = queryset.prefetch_related('children', 'process_activities')
        return super().get_object()

    # --- Processes / Activities ---
    @action(detail=True, methods=["get", "post"], url_path="processes")
    def processes(self, request, pk=None):
        entity = self.get_object()
        if request.method.lower() == 'get':
            qs = entity.process_activities.all().order_by('name')
            serializer = EntityProcessActivitySerializer(qs, many=True)
            return Response(serializer.data)
        # POST create new
        serializer = EntityProcessActivitySerializer(data=request.data)
        if serializer.is_valid():
            # Check identifier uniqueness per entity
            identifier = serializer.validated_data.get('identifier', '').strip()
            if identifier and entity.process_activities.filter(identifier=identifier).exists():
                return Response({"detail": "identifier must be unique per entity"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(audit_entity=entity)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["put", "patch", "delete"], url_path=r"processes/(?P<process_id>[^/.]+)")
    def process_detail(self, request, pk=None, process_id=None):
        entity = self.get_object()
        try:
            process = entity.process_activities.get(pk=process_id)
        except EntityProcessActivity.DoesNotExist:
            return Response({"detail": "Process not found"}, status=status.HTTP_404_NOT_FOUND)
        if request.method.lower() == 'delete':
            process.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # update
        serializer = EntityProcessActivitySerializer(process, data=request.data, partial=True)
        if serializer.is_valid():
            # Check identifier uniqueness per entity
            identifier = serializer.validated_data.get('identifier', '').strip()
            if identifier and entity.process_activities.exclude(pk=process.pk).filter(identifier=identifier).exists():
                return Response({"detail": "identifier must be unique per entity"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="processes/upload-csv")
    def processes_upload_csv(self, request, pk=None):
        entity = self.get_object()
        file = request.FILES.get('file')
        if not file:
            return Response({"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        if not file.name.endswith('.csv'):
            return Response({"detail": "File must be a CSV"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))
            created_count = 0
            updated_count = 0
            errors = []
            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    name = (row.get('name') or '').strip()
                    description = (row.get('description') or '').strip()
                    if not name:
                        errors.append(f"Row {row_num}: name is required")
                        continue
                    process, created = EntityProcessActivity.objects.get_or_create(
                        audit_entity=entity,
                        name=name,
                        defaults={'description': description}
                    )
                    if created:
                        created_count += 1
                    else:
                        process.description = description
                        process.save()
                        updated_count += 1
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            return Response({
                "message": f"CSV processed. Created: {created_count}, Updated: {updated_count}",
                "created_count": created_count,
                "updated_count": updated_count,
                "errors": errors
            })
        except Exception as e:
            return Response({"detail": f"Error processing CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="related")
    def related(self, request, pk=None):
        """
        Get all related objects for the given AuditEntity.
        Returns engagements, compliance_audits, risks, and controls.
        """
        entity = self.get_object()
        
        # For now, return empty arrays since direct relationships don't exist yet
        # This endpoint is ready for when relationships are established
        
        # Placeholder for future AuditEngagement model
        engagements = []
        
        # Compliance assessments - currently no direct relationship
        # When relationship is established, use: ComplianceAssessment.objects.filter(entities__id=entity.id)
        compliance_audits = []
        
        # Risk scenarios - currently no direct relationship
        # When relationship is established, use: RiskScenario.objects.filter(entities__id=entity.id)
        risks = []
        
        # Applied controls - currently no direct relationship
        # When relationship is established, use: AppliedControl.objects.filter(entities__id=entity.id)
        controls = []
        
        # For demonstration, let's return some sample data if any exist
        # This can be removed when proper relationships are established
        try:
            # Get some sample compliance assessments (not filtered by entity)
            compliance_audits = ComplianceAssessment.objects.select_related('framework').all()[:5]
            # Get some sample risk scenarios
            risks = RiskScenario.objects.all()[:5]
            # Get some sample applied controls
            controls = AppliedControl.objects.all()[:5]
        except Exception:
            # If models don't exist or have issues, return empty arrays
            compliance_audits = []
            risks = []
            controls = []
        
        # Prepare the response data
        data = {
            'engagements': engagements,
            'compliance_audits': compliance_audits,
            'risks': risks,
            'controls': controls
        }
        
        # Serialize the data
        serializer = RelatedObjectsSerializer(data)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="upload-org-structure")
    def upload_org_structure(self, request, pk=None):
        entity = self.get_object()
        file = request.FILES.get('file')
        if not file:
            return Response({"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        # Optionally validate extension/size
        allowed = {"pdf", "png", "jpg", "jpeg", "svg"}
        ext = (file.name.rsplit('.', 1)[-1] or '').lower()
        if ext not in allowed:
            return Response({"detail": "Unsupported file type"}, status=status.HTTP_400_BAD_REQUEST)
        entity.org_structure = file
        entity.save()
        return Response({"org_structure_url": entity.org_structure.url}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="hierarchy")
    def get_hierarchy(self, request):
        """Return hierarchical structure of all entities"""
        from django.db.models import Q
        
        # Start with base queryset
        entities = AuditEntity.objects.select_related('parent', 'owner', 'team_member').prefetch_related('children').all()
        
        # Apply filtering based on query parameters (same as get_queryset)
        if request.user and request.user.is_authenticated:
            my_entities = request.query_params.get('my_entities')
            if my_entities and my_entities.lower() == 'true':
                entities = entities.filter(Q(owner=request.user) | Q(team_member=request.user))
            
            my_team = request.query_params.get('my_team')
            if my_team and my_team.lower() == 'true':
                entities = entities.filter(owner=request.user)
        
        entity_list = list(entities)
        hierarchy = self._build_hierarchy(entity_list)
        return Response(hierarchy)

    @action(detail=False, methods=["post"], url_path="upload-hierarchy-csv")
    def upload_hierarchy_csv(self, request):
        """Upload CSV to create/update hierarchy"""
        file = request.FILES.get('file')
        if not file:
            return Response({"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not file.name.endswith('.csv'):
            return Response({"detail": "File must be a CSV"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Read CSV
            content = file.read().decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content))
            
            created_count = 0
            updated_count = 0
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
                try:
                    entity_name = row.get('entity_name', '').strip()
                    parent_name = row.get('parent_name', '').strip()
                    entity_type = row.get('type', '').strip()
                    
                    if not entity_name:
                        errors.append(f"Row {row_num}: entity_name is required")
                        continue
                    
                    if not entity_type:
                        errors.append(f"Row {row_num}: type is required")
                        continue
                    
                    # Validate entity type
                    valid_types = [choice[0] for choice in AuditEntity.ENTITY_TYPES]
                    if entity_type not in valid_types:
                        errors.append(f"Row {row_num}: Invalid type '{entity_type}'. Must be one of: {', '.join(valid_types)}")
                        continue
                    
                    # Find or create parent
                    parent = None
                    if parent_name:
                        try:
                            parent = AuditEntity.objects.get(name=parent_name)
                        except AuditEntity.DoesNotExist:
                            errors.append(f"Row {row_num}: Parent '{parent_name}' not found")
                            continue
                    
                    # Create or update entity
                    entity, created = AuditEntity.objects.get_or_create(
                        name=entity_name,
                        defaults={
                            'entity_type': entity_type,
                            'parent': parent,
                            'description': f"Created from CSV upload",
                            'is_active': True
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        # Update existing entity
                        entity.entity_type = entity_type
                        entity.parent = parent
                        entity.save()
                        updated_count += 1
                        
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            return Response({
                "message": f"CSV processed successfully. Created: {created_count}, Updated: {updated_count}",
                "created_count": created_count,
                "updated_count": updated_count,
                "errors": errors
            })
            
        except Exception as e:
            return Response({"detail": f"Error processing CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

    def _build_hierarchy(self, entities):
        """Build hierarchical structure from flat entity list"""
        # Create lookup dictionary
        entity_dict = {entity.id: {
            'id': entity.id,
            'name': entity.name,
            'entity_type': entity.entity_type,
            'description': entity.description,
            'risk_score': entity.risk_score,
            'is_active': entity.is_active,
            'children': []
        } for entity in entities}
        
        # Build hierarchy
        roots = []
        for entity in entities:
            entity_data = entity_dict[entity.id]
            if entity.parent_id:
                # If parent exists in filtered results, attach as child
                if entity.parent_id in entity_dict:
                    entity_dict[entity.parent_id]['children'].append(entity_data)
                else:
                    # Parent not in filtered results, show as root
                    # This allows filtered entities to be visible even when parent is excluded
                    roots.append(entity_data)
            else:
                # No parent - show as root
                roots.append(entity_data)
        
        return roots

    @action(detail=False, methods=["get"], url_path="processes/lookup")
    def processes_lookup(self, request):
        """Get all processes across entities for dropdown selection."""
        processes = EntityProcessActivity.objects.select_related('audit_entity').all().order_by('audit_entity__name', 'name')
        data = []
        for process in processes:
            data.append({
                'id': process.id,
                'identifier': process.identifier,
                'name': process.name,
                'entity_name': process.audit_entity.name,
                'display_name': f"{process.identifier} – {process.name} ({process.audit_entity.name})" if process.identifier else f"{process.name} ({process.audit_entity.name})"
            })
        return Response(data)


class AuditPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for managing audit plans"""
    queryset = AuditPlan.objects.all().select_related(
        "entity", "lead_auditor", "submitted_by", "approved_by", "rejected_by"
    ).prefetch_related("auditable_entities")
    serializer_class = AuditPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'entity', 'lead_auditor']
    search_fields = ["title", "entity__name", "lead_auditor__email", "description"]
    ordering_fields = ["planned_start", "planned_end", "status", "created_at"]
    ordering = ["planned_start"]
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by entity if provided
        entity_id = self.request.query_params.get('entity')
        if entity_id:
            queryset = queryset.filter(entity_id=entity_id)
        
        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by lead auditor if provided
        lead_auditor = self.request.query_params.get('lead_auditor')
        if lead_auditor:
            queryset = queryset.filter(lead_auditor_id=lead_auditor)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('planned_start__gte')
        if start_date:
            queryset = queryset.filter(planned_start__gte=start_date)
        
        end_date = self.request.query_params.get('planned_end__lte')
        if end_date:
            queryset = queryset.filter(planned_end__lte=end_date)
        
        return queryset
    
    @action(detail=True, methods=['post'], url_path='submit-for-approval')
    def submit_for_approval(self, request, pk=None):
        """Submit audit plan for approval"""
        audit_plan = self.get_object()
        
        if audit_plan.status != 'draft':
            return Response(
                {'error': 'Only draft audit plans can be submitted for approval'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audit_plan.submit_for_approval(request.user)
        serializer = self.get_serializer(audit_plan)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """Approve audit plan"""
        audit_plan = self.get_object()
        
        if not audit_plan.can_be_approved():
            return Response(
                {'error': 'Audit plan cannot be approved in its current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        audit_plan.approve(request.user)
        serializer = self.get_serializer(audit_plan)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """Reject audit plan"""
        audit_plan = self.get_object()
        
        if not audit_plan.can_be_rejected():
            return Response(
                {'error': 'Audit plan cannot be rejected in its current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        audit_plan.reject(request.user, reason)
        serializer = self.get_serializer(audit_plan)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='approvals')
    def approvals(self, request, pk=None):
        """Get all approvals for this audit plan"""
        audit_plan = self.get_object()
        approvals = audit_plan.approvals.all().select_related('approver')
        serializer = AuditPlanApprovalSerializer(approvals, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='add-approver')
    def add_approver(self, request, pk=None):
        """Add an approver to the audit plan"""
        audit_plan = self.get_object()
        approver_id = request.data.get('approver_id')
        
        if not approver_id:
            return Response(
                {'error': 'approver_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            approver = User.objects.get(id=approver_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Approver not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approval, created = AuditPlanApproval.objects.get_or_create(
            audit_plan=audit_plan,
            approver=approver,
            defaults={'status': 'pending'}
        )
        
        if not created:
            return Response(
                {'error': 'Approver already exists for this audit plan'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = AuditPlanApprovalSerializer(approval)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AuditPlanApprovalViewSet(viewsets.ModelViewSet):
    """ViewSet for managing audit plan approvals"""
    queryset = AuditPlanApproval.objects.all().select_related("audit_plan", "approver")
    serializer_class = AuditPlanApprovalSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["audit_plan__title", "approver__username", "comments"]
    ordering_fields = ["status", "created_at", "approved_at"]
    ordering = ["-created_at"]
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by audit plan if provided
        audit_plan_id = self.request.query_params.get('audit_plan')
        if audit_plan_id:
            queryset = queryset.filter(audit_plan_id=audit_plan_id)
        
        # Filter by approver if provided
        approver_id = self.request.query_params.get('approver')
        if approver_id:
            queryset = queryset.filter(approver_id=approver_id)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """Approve the audit plan"""
        approval = self.get_object()
        comments = request.data.get('comments', '')
        
        if approval.status != 'pending':
            return Response(
                {'error': 'Only pending approvals can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approval.approve(comments)
        serializer = self.get_serializer(approval)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """Reject the audit plan"""
        approval = self.get_object()
        comments = request.data.get('comments', '')
        
        if approval.status != 'pending':
            return Response(
                {'error': 'Only pending approvals can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        approval.reject(comments)
        serializer = self.get_serializer(approval)
        return Response(serializer.data)


class AuditEngagementViewSet(viewsets.ModelViewSet):
    """ViewSet for managing audit engagements"""
    queryset = AuditEngagement.objects.all().select_related(
        "audit_plan", "entity", "assigned_auditor", "engagement_lead",
        "results_submitted_by", "closed_by", "created_by"
    )
    serializer_class = AuditEngagementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'audit_type', 'audit_plan', 'entity', 'assigned_auditor', 'engagement_lead']
    search_fields = [
        "title", "description", "audit_plan__title", "entity__name",
        "assigned_auditor__email", "engagement_lead__email"
    ]
    ordering_fields = [
        "title", "status", "priority", "planned_start_date", "planned_end_date",
        "created_at", "progress_percentage"
    ]
    ordering = ["-created_at"]
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by audit plan if provided
        audit_plan_id = self.request.query_params.get('audit_plan')
        if audit_plan_id:
            queryset = queryset.filter(audit_plan_id=audit_plan_id)
        
        # Filter by entity if provided
        entity_id = self.request.query_params.get('entity')
        if entity_id:
            queryset = queryset.filter(entity_id=entity_id)
        
        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by priority if provided
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by assigned auditor if provided
        assigned_auditor = self.request.query_params.get('assigned_auditor')
        if assigned_auditor:
            queryset = queryset.filter(assigned_auditor_id=assigned_auditor)
        
        # Filter by engagement lead if provided
        engagement_lead = self.request.query_params.get('engagement_lead')
        if engagement_lead:
            queryset = queryset.filter(engagement_lead_id=engagement_lead)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('planned_start_date__gte')
        if start_date:
            queryset = queryset.filter(planned_start_date__gte=start_date)
        
        end_date = self.request.query_params.get('planned_end_date__lte')
        if end_date:
            queryset = queryset.filter(planned_end_date__lte=end_date)
        
        # Filter by overdue status
        overdue = self.request.query_params.get('overdue')
        if overdue and overdue.lower() == 'true':
            queryset = queryset.filter(
                planned_end_date__lt=timezone.now().date(),
                status__in=['draft', 'in_progress', 'fieldwork', 'review']
            )
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by my engagements (current user is assigned_auditor OR engagement_lead)
        my_engagements = self.request.query_params.get('my_engagements')
        if my_engagements and my_engagements.lower() == 'true':
            queryset = queryset.filter(
                Q(assigned_auditor=self.request.user) | Q(engagement_lead=self.request.user)
            )
        
        # Filter by my team's engagements (current user is engagement_lead)
        my_team = self.request.query_params.get('my_team')
        if my_team and my_team.lower() == 'true':
            queryset = queryset.filter(engagement_lead=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by when creating engagement"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'], url_path='start')
    def start_engagement(self, request, pk=None):
        """Start the engagement"""
        from .models import EngagementTimelineEvent
        
        engagement = self.get_object()
        
        if not engagement.can_be_started():
            return Response(
                {'error': 'Engagement cannot be started in its current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        engagement.start_engagement(request.user)
        
        # Create timeline event
        EngagementTimelineEvent.objects.create(
            engagement=engagement,
            event_type='started',
            title='Engagement Started',
            description=f'Fieldwork began on {engagement.actual_start_date.strftime("%B %d, %Y")}',
            user=request.user,
            status=engagement.status,
            progress_percentage=engagement.progress_percentage,
            icon='play-circle',
            color='green'
        )
        
        serializer = self.get_serializer(engagement)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='submit-results')
    def submit_results(self, request, pk=None):
        """Submit engagement results"""
        from .models import EngagementTimelineEvent
        
        engagement = self.get_object()
        
        if not engagement.can_submit_results():
            return Response(
                {'error': 'Results cannot be submitted in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        findings_summary = request.data.get('findings_summary', '')
        recommendations = request.data.get('recommendations', '')
        
        engagement.submit_results(request.user, findings_summary, recommendations)
        
        # Create timeline event
        EngagementTimelineEvent.objects.create(
            engagement=engagement,
            event_type='submitted',
            title='Results Submitted',
            description='Final results submitted for review',
            user=request.user,
            status=engagement.status,
            progress_percentage=engagement.progress_percentage,
            icon='check-circle',
            color='green'
        )
        
        serializer = self.get_serializer(engagement)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='close')
    def close_engagement(self, request, pk=None):
        """Close the engagement"""
        from .models import EngagementTimelineEvent
        
        engagement = self.get_object()
        
        if not engagement.can_be_closed():
            return Response(
                {'error': 'Engagement cannot be closed in current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        closure_notes = request.data.get('closure_notes', '')
        engagement.close_engagement(request.user, closure_notes)
        
        # Create timeline event
        EngagementTimelineEvent.objects.create(
            engagement=engagement,
            event_type='closed',
            title='Engagement Closed',
            description='Engagement completed and closed',
            user=request.user,
            status=engagement.status,
            progress_percentage=engagement.progress_percentage,
            icon='lock-closed',
            color='gray'
        )
        
        serializer = self.get_serializer(engagement)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='update-progress')
    def update_progress(self, request, pk=None):
        """Update engagement progress"""
        from .models import EngagementTimelineEvent
        
        engagement = self.get_object()
        
        progress_percentage = request.data.get('progress_percentage')
        fieldwork_notes = request.data.get('fieldwork_notes', '')
        
        if progress_percentage is not None:
            if not 0 <= progress_percentage <= 100:
                return Response(
                    {'error': 'Progress percentage must be between 0 and 100'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            engagement.progress_percentage = progress_percentage
        
        if fieldwork_notes:
            engagement.fieldwork_notes = fieldwork_notes
        
        engagement.save()
        
        # Create timeline event for progress update
        if progress_percentage is not None:
            # Determine phase based on progress and status
            if progress_percentage < 30:
                phase = "Planning Phase"
                icon = "plus-circle"
                color = "blue"
            elif progress_percentage < 70:
                phase = "Fieldwork Phase"
                icon = "search"
                color = "yellow"
            else:
                phase = "Review Phase"
                icon = "eye"
                color = "purple"
            
            EngagementTimelineEvent.objects.create(
                engagement=engagement,
                event_type='progress_updated',
                title=phase,
                description=f'{phase} - {progress_percentage}% complete',
                user=request.user,
                status=engagement.status,
                progress_percentage=progress_percentage,
                icon=icon,
                color=color
            )
        
        serializer = self.get_serializer(engagement)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='timeline')
    def timeline(self, request, pk=None):
        """Get engagement timeline/activities from stored events"""
        from .models import EngagementTimelineEvent
        
        engagement = self.get_object()
        
        # Get stored timeline events
        stored_events = engagement.timeline_events.all()
        
        # Convert to frontend format
        timeline_events = []
        for event in stored_events:
            timeline_events.append({
                'id': event.event_type,
                'date': event.created_at,
                'user': event.user.username if event.user else None,
                'action': event.title,
                'description': event.description,
                'status': 'completed' if event.event_type in ['submitted', 'closed'] else 'in_progress',
                'icon': event.icon,
                'color': event.color
            })
        
        # If no stored events exist, create the initial "created" event
        if not stored_events.exists():
            EngagementTimelineEvent.objects.create(
                engagement=engagement,
                event_type='created',
                title='Engagement Created',
                description=f'Engagement "{engagement.title}" was created',
                user=engagement.created_by,
                status=engagement.status,
                progress_percentage=engagement.progress_percentage,
                icon='plus-circle',
                color='blue'
            )
            # Re-fetch events
            stored_events = engagement.timeline_events.all()
            timeline_events = []
            for event in stored_events:
                timeline_events.append({
                    'id': event.event_type,
                    'date': event.created_at,
                    'user': event.user.username if event.user else None,
                    'action': event.title,
                    'description': event.description,
                    'status': 'completed' if event.event_type in ['submitted', 'closed'] else 'in_progress',
                    'icon': event.icon,
                    'color': event.color
                })
        
        return Response({
            'events': timeline_events,
            'engagement_id': engagement.id,
            'engagement_title': engagement.title,
            'current_status': engagement.status,
            'progress_percentage': engagement.progress_percentage,
            'is_overdue': engagement.is_overdue()
        })
    
    @action(detail=False, methods=['get'], url_path='calendar')
    def calendar(self, request):
        """Get engagements for calendar view"""
        year = request.query_params.get('year')
        month = request.query_params.get('month')
        
        queryset = self.get_queryset()
        
        if year and month:
            from datetime import date
            try:
                start_date = date(int(year), int(month), 1)
                if int(month) == 12:
                    end_date = date(int(year) + 1, 1, 1)
                else:
                    end_date = date(int(year), int(month) + 1, 1)
                
                queryset = queryset.filter(
                    planned_start_date__lt=end_date,
                    planned_end_date__gte=start_date
                )
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid year or month format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """Get engagement summary statistics for dashboard"""
        queryset = self.get_queryset()
        today = timezone.now().date()
        thirty_days_from_now = today + timedelta(days=30)
        
        # Total engagements
        total = queryset.count()
        
        # Upcoming engagements (starting in next 30 days, status=draft)
        upcoming = queryset.filter(
            planned_start_date__gte=today,
            planned_start_date__lte=thirty_days_from_now,
            status='draft'
        ).count()
        
        # Overdue engagements (past end date, not closed/cancelled)
        overdue = queryset.filter(
            planned_end_date__lt=today,
            status__in=['draft', 'in_progress', 'fieldwork', 'review']
        ).count()
        
        # Due in 30 days (ending in next 30 days, not closed/cancelled)
        due_soon = queryset.filter(
            planned_end_date__gte=today,
            planned_end_date__lte=thirty_days_from_now,
            status__in=['draft', 'in_progress', 'fieldwork', 'review']
        ).count()
        
        # In progress count
        in_progress = queryset.filter(
            status__in=['in_progress', 'fieldwork', 'review']
        ).count()
        
        # Completed this month
        completed_this_month = queryset.filter(
            status='closed',
            closed_at__year=today.year,
            closed_at__month=today.month
        ).count()
        
        return Response({
            'total': total,
            'upcoming': upcoming,
            'overdue': overdue,
            'due_soon': due_soon,
            'in_progress': in_progress,
            'completed_this_month': completed_this_month
        })
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Get engagement statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'by_status': {},
            'by_priority': {},
            'overdue': queryset.filter(
                planned_end_date__lt=timezone.now().date(),
                status__in=['draft', 'in_progress', 'fieldwork', 'review']
            ).count(),
            'completed_this_month': queryset.filter(
                status='closed',
                closed_at__year=timezone.now().year,
                closed_at__month=timezone.now().month
            ).count()
        }
        
        # Count by status
        for status_choice in AuditEngagement.STATUS_CHOICES:
            stats['by_status'][status_choice[0]] = queryset.filter(status=status_choice[0]).count()
        
        # Count by priority
        for priority_choice in AuditEngagement.PRIORITY_CHOICES:
            stats['by_priority'][priority_choice[0]] = queryset.filter(priority=priority_choice[0]).count()
        
        return Response(stats)
    
    @action(detail=False, methods=['get'], url_path='dashboard-metrics')
    def dashboard_metrics(self, request):
        """
        Comprehensive dashboard metrics including:
        - Core metrics (total, overdue, completed)
        - Status/priority/type distributions
        - Entity coverage analysis
        - Budget/hours tracking
        - Checklist results
        """
        from django.db.models import Count, Sum, Avg, Q, F
        from datetime import datetime, timedelta
        
        queryset = self.get_queryset()
        today = timezone.now().date()
        
        # Core metrics
        total_engagements = queryset.count()
        overdue_engagements = queryset.filter(
            planned_end_date__lt=today,
            status__in=['draft', 'in_progress', 'fieldwork', 'review']
        ).count()
        in_progress_engagements = queryset.filter(
            status__in=['in_progress', 'fieldwork', 'review']
        ).count()
        completed_this_month = queryset.filter(
            status='closed',
            closed_at__year=today.year,
            closed_at__month=today.month
        ).count()
        
        # Status distribution
        status_distribution = {}
        for status_choice in AuditEngagement.STATUS_CHOICES:
            count = queryset.filter(status=status_choice[0]).count()
            status_distribution[status_choice[0]] = {
                'count': count,
                'label': status_choice[1]
            }
        
        # Priority distribution
        priority_distribution = {}
        for priority_choice in AuditEngagement.PRIORITY_CHOICES:
            count = queryset.filter(priority=priority_choice[0]).count()
            priority_distribution[priority_choice[0]] = {
                'count': count,
                'label': priority_choice[1]
            }
        
        # Audit type distribution
        audit_type_distribution = {}
        for type_choice in AuditEngagement.AUDIT_TYPE_CHOICES:
            count = queryset.filter(audit_type=type_choice[0]).count()
            audit_type_distribution[type_choice[0]] = {
                'count': count,
                'label': type_choice[1]
            }
        
        # Budget and hours tracking
        budget_stats = queryset.aggregate(
            total_estimated_hours=Sum('estimated_hours'),
            total_actual_hours=Sum('actual_hours'),
            total_budget_allocated=Sum('budget_allocated'),
            total_actual_cost=Sum('actual_cost'),
            avg_estimated_hours=Avg('estimated_hours'),
            avg_actual_hours=Avg('actual_hours')
        )
        
        # Timeline - upcoming engagements (next 90 days)
        upcoming_end_date = today + timedelta(days=90)
        upcoming_engagements = list(queryset.filter(
            planned_start_date__lte=upcoming_end_date,
            planned_end_date__gte=today,
            status__in=['draft', 'in_progress', 'fieldwork', 'review']
        ).values(
            'id', 'title', 'status', 'priority',
            'planned_start_date', 'planned_end_date',
            'entity__name'
        ).order_by('planned_start_date')[:20])
        
        # Entity coverage analysis
        entities = AuditEntity.objects.all()
        entity_coverage = {
            'total_entities': entities.count(),
            'entities_by_criticality': {},
            'entities_by_type': {},
            'coverage_matrix': []
        }
        
        # Count entities by criticality
        for criticality_choice in AuditEntity.CRITICALITY_CHOICES:
            entity_coverage['entities_by_criticality'][criticality_choice[0]] = entities.filter(
                criticality=criticality_choice[0]
            ).count()
        
        # Count entities by type
        for type_choice in AuditEntity.ENTITY_TYPES:
            entity_coverage['entities_by_type'][type_choice[0]] = entities.filter(
                entity_type=type_choice[0]
            ).count()
        
        # Coverage matrix: entity_type x criticality with audit status
        for entity_type in AuditEntity.ENTITY_TYPES:
            for criticality in AuditEntity.CRITICALITY_CHOICES:
                entities_in_cell = entities.filter(
                    entity_type=entity_type[0],
                    criticality=criticality[0]
                )
                
                if entities_in_cell.exists():
                    # Calculate audit status
                    current = 0
                    due_soon = 0
                    overdue = 0
                    never_audited = 0
                    
                    for entity in entities_in_cell:
                        if not entity.last_audited:
                            never_audited += 1
                        else:
                            # Calculate days since last audit
                            days_since = (today - entity.last_audited).days
                            
                            # Determine if overdue based on audit frequency
                            frequency_days = {
                                'monthly': 30,
                                'quarterly': 90,
                                'semiannual': 180,
                                'annual': 365,
                                'ad-hoc': 730  # 2 years for ad-hoc
                            }
                            threshold = frequency_days.get(entity.audit_frequency, 365)
                            
                            if days_since > threshold:
                                overdue += 1
                            elif days_since > threshold * 0.8:  # 80% of threshold
                                due_soon += 1
                            else:
                                current += 1
                    
                    entity_coverage['coverage_matrix'].append({
                        'entity_type': entity_type[0],
                        'entity_type_label': entity_type[1],
                        'criticality': criticality[0],
                        'criticality_label': criticality[1],
                        'total': entities_in_cell.count(),
                        'current': current,
                        'due_soon': due_soon,
                        'overdue': overdue,
                        'never_audited': never_audited
                    })
        
        # Entity risk distribution for treemap
        entity_risk_data = []
        for entity in entities.filter(risk_score__gt=0).order_by('-risk_score')[:50]:
            entity_risk_data.append({
                'id': entity.id,
                'name': entity.name,
                'entity_type': entity.entity_type,
                'risk_score': float(entity.risk_score) if entity.risk_score else 0,
                'criticality': entity.criticality
            })
        
        # Checklist execution statistics
        from .models import ChecklistExecution, ChecklistItemResult
        
        executions = ChecklistExecution.objects.all()
        checklist_stats = {
            'total_executions': executions.count(),
            'by_status': {}
        }
        
        for status_choice in ChecklistExecution.STATUS_CHOICES:
            checklist_stats['by_status'][status_choice[0]] = {
                'count': executions.filter(status=status_choice[0]).count(),
                'label': status_choice[1]
            }
        
        # Checklist item results
        item_results = ChecklistItemResult.objects.all()
        checklist_results = {
            'total_results': item_results.count(),
            'by_result': {}
        }
        
        for result_choice in ChecklistItemResult.RESULT_CHOICES:
            checklist_results['by_result'][result_choice[0]] = {
                'count': item_results.filter(result=result_choice[0]).count(),
                'label': result_choice[1]
            }
        
        # Performance metrics
        completed_engagements = queryset.filter(status='closed', actual_end_date__isnull=False)
        
        performance_metrics = {
            'total_completed': completed_engagements.count(),
            'avg_duration_days': 0,
            'on_time_completion_rate': 0,
            'budget_variance_percent': 0
        }
        
        if completed_engagements.exists():
            # Calculate average duration
            durations = []
            on_time_count = 0
            
            for engagement in completed_engagements:
                if engagement.actual_start_date and engagement.actual_end_date:
                    duration = (engagement.actual_end_date - engagement.actual_start_date).days
                    durations.append(duration)
                    
                    if engagement.actual_end_date <= engagement.planned_end_date:
                        on_time_count += 1
            
            if durations:
                performance_metrics['avg_duration_days'] = sum(durations) / len(durations)
                performance_metrics['on_time_completion_rate'] = (on_time_count / len(durations)) * 100
            
            # Budget variance
            if budget_stats['total_budget_allocated'] and budget_stats['total_actual_cost']:
                variance = (
                    (budget_stats['total_actual_cost'] - budget_stats['total_budget_allocated']) 
                    / budget_stats['total_budget_allocated'] * 100
                )
                performance_metrics['budget_variance_percent'] = float(variance)
        
        # Alerts for dashboard
        alerts = {
            'overdue_engagements': [],
            'never_audited_entities': [],
            'budget_overruns': [],
            'upcoming_deadlines': []
        }
        
        # 1. Overdue engagements
        overdue = queryset.filter(
            planned_end_date__lt=today,
            status__in=['draft', 'in_progress', 'fieldwork', 'review']
        ).select_related('entity').order_by('planned_end_date')[:10]
        
        for eng in overdue:
            days_overdue = (today - eng.planned_end_date).days
            alerts['overdue_engagements'].append({
                'id': eng.id,
                'title': eng.title,
                'entity': eng.entity.name if eng.entity else 'N/A',
                'planned_end_date': eng.planned_end_date,
                'days_overdue': days_overdue,
                'priority': eng.priority,
                'status': eng.status
            })
        
        # 2. Never audited entities (high priority)
        never_audited = AuditEntity.objects.filter(
            last_audited__isnull=True,
            criticality__in=['High', 'Medium'],
            is_active=True
        ).order_by('-criticality', 'name')[:10]
        
        for entity in never_audited:
            alerts['never_audited_entities'].append({
                'id': entity.id,
                'name': entity.name,
                'entity_type': entity.entity_type,
                'criticality': entity.criticality,
                'risk_score': float(entity.risk_score) if entity.risk_score else 0
            })
        
        # 3. Budget overruns (>10% over budget)
        budget_issues = queryset.filter(
            budget_allocated__gt=0,
            actual_cost__gt=F('budget_allocated') * 1.1,
            status__in=['in_progress', 'fieldwork', 'review']
        ).order_by('-actual_cost')[:10]
        
        for eng in budget_issues:
            variance = ((eng.actual_cost - eng.budget_allocated) / eng.budget_allocated * 100)
            alerts['budget_overruns'].append({
                'id': eng.id,
                'title': eng.title,
                'budget_allocated': float(eng.budget_allocated),
                'actual_cost': float(eng.actual_cost),
                'variance_percent': float(variance),
                'status': eng.status
            })
        
        # 4. Upcoming deadlines (next 30 days)
        upcoming_deadline_date = today + timedelta(days=30)
        upcoming_deadlines = queryset.filter(
            planned_end_date__gte=today,
            planned_end_date__lte=upcoming_deadline_date,
            status__in=['draft', 'in_progress', 'fieldwork', 'review']
        ).select_related('entity').order_by('planned_end_date')[:10]
        
        for eng in upcoming_deadlines:
            days_remaining = (eng.planned_end_date - today).days
            alerts['upcoming_deadlines'].append({
                'id': eng.id,
                'title': eng.title,
                'entity': eng.entity.name if eng.entity else 'N/A',
                'planned_end_date': eng.planned_end_date,
                'days_remaining': days_remaining,
                'priority': eng.priority,
                'status': eng.status
            })
        
        # Completion trend - last 12 months
        from dateutil.relativedelta import relativedelta
        
        completion_trend = []
        for i in range(11, -1, -1):  # Last 12 months
            month_date = today - relativedelta(months=i)
            month_start = month_date.replace(day=1)
            if i == 0:
                month_end = today
            else:
                month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
            
            completed = queryset.filter(
                status='closed',
                closed_at__gte=month_start,
                closed_at__lte=month_end
            ).count()
            
            planned = queryset.filter(
                planned_end_date__gte=month_start,
                planned_end_date__lte=month_end
            ).count()
            
            completion_trend.append({
                'month': month_start.strftime('%b %Y'),
                'completed': completed,
                'planned': planned,
                'completion_rate': (completed / planned * 100) if planned > 0 else 0
            })
        
        # Compile all metrics
        dashboard_data = {
            'core_metrics': {
                'total': total_engagements,
                'overdue': overdue_engagements,
                'in_progress': in_progress_engagements,
                'completed_this_month': completed_this_month
            },
            'status_distribution': status_distribution,
            'priority_distribution': priority_distribution,
            'audit_type_distribution': audit_type_distribution,
            'budget_stats': budget_stats,
            'upcoming_engagements': upcoming_engagements,
            'entity_coverage': entity_coverage,
            'entity_risk_data': entity_risk_data,
            'checklist_stats': checklist_stats,
            'checklist_results': checklist_results,
            'performance_metrics': performance_metrics,
            'alerts': alerts,
            'completion_trend': completion_trend
        }
        
        return Response(dashboard_data)


class ChecklistViewSet(viewsets.ModelViewSet):
    """ViewSet for managing audit checklists"""
    queryset = Checklist.objects.all().select_related('folder', 'created_by').prefetch_related('items')
    serializer_class = ChecklistSerializer
    permission_classes = [IsAuditTeamOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'folder', 'is_published']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'status', 'created_at', 'updated_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by folder if provided
        folder_id = self.request.query_params.get('folder')
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        
        # Filter by published status if provided
        is_published = self.request.query_params.get('is_published')
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published.lower() == 'true')
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by when creating checklist"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'], url_path='duplicate')
    def duplicate(self, request, pk=None):
        """Duplicate a checklist with all its items"""
        original_checklist = self.get_object()
        
        # Create a copy of the checklist
        new_checklist = Checklist.objects.create(
            name=f"{original_checklist.name} (Copy)",
            description=original_checklist.description,
            folder=original_checklist.folder,
            status='draft',  # Reset to draft
            is_published=original_checklist.is_published,
            created_by=request.user
        )
        
        # Copy all items
        original_items = original_checklist.items.all()
        for item in original_items:
            ChecklistItem.objects.create(
                checklist=new_checklist,
                title=item.title,
                description=item.description,
                order=item.order,
                control=item.control,
                risk=item.risk,
                policy=item.policy
            )
        
        serializer = self.get_serializer(new_checklist)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChecklistItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing checklist items"""
    queryset = ChecklistItem.objects.all().select_related('checklist', 'control', 'risk', 'policy')
    serializer_class = ChecklistItemSerializer
    permission_classes = [IsAuditTeamOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['checklist']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()
        
        # Filter by checklist if provided
        checklist_id = self.request.query_params.get('checklist')
        if checklist_id:
            queryset = queryset.filter(checklist_id=checklist_id)
        
        return queryset
    
    @action(detail=True, methods=['post'], url_path='reorder')
    def reorder(self, request, pk=None):
        """Update the order of a checklist item"""
        item = self.get_object()
        new_order = request.data.get('order')
        
        if new_order is None:
            return Response(
                {'error': 'order is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            new_order = int(new_order)
            if new_order < 0:
                return Response(
                    {'error': 'order must be non-negative'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'order must be a valid integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the new order would violate uniqueness constraint
        checklist = item.checklist
        existing_item = ChecklistItem.objects.filter(
            checklist=checklist,
            order=new_order
        ).exclude(id=item.id).first()
        
        if existing_item:
            # Swap orders
            old_order = item.order
            existing_item.order = old_order
            existing_item.save()
        
        item.order = new_order
        item.save()
        
        serializer = self.get_serializer(item)
        return Response(serializer.data)


class ChecklistExecutionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing checklist executions"""
    queryset = ChecklistExecution.objects.select_related(
        'checklist', 'audit_engagement', 'started_by', 'completed_by'
    ).prefetch_related('item_results__checklist_item')
    serializer_class = ChecklistExecutionSerializer
    permission_classes = [IsAuditTeamOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'audit_engagement', 'checklist']
    ordering_fields = ['created_at', 'started_at', 'completed_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Initialize execution with items from template"""
        execution = serializer.save(
            started_by=self.request.user,
            started_at=timezone.now()
        )
        
        # Create result records for each item in the template
        checklist_items = execution.checklist.items.all()
        execution.total_items = checklist_items.count()
        execution.save()
        
        ChecklistItemResult.objects.bulk_create([
            ChecklistItemResult(
                execution=execution,
                checklist_item=item,
                result='not_tested'
            )
            for item in checklist_items
        ])
    
    @action(detail=True, methods=['post'])
    def start_execution(self, request, pk=None):
        """Mark execution as started"""
        execution = self.get_object()
        execution.status = 'in_progress'
        execution.started_by = request.user
        execution.started_at = timezone.now()
        execution.save()
        return Response(self.get_serializer(execution).data)
    
    @action(detail=True, methods=['post'])
    def complete_execution(self, request, pk=None):
        """Mark execution as completed"""
        execution = self.get_object()
        execution.status = 'completed'
        execution.completed_by = request.user
        execution.completed_at = timezone.now()
        execution.save()
        return Response(self.get_serializer(execution).data)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get execution summary statistics"""
        execution = self.get_object()
        results = execution.item_results.all()
        
        summary = {
            'total': results.count(),
            'not_tested': results.filter(result='not_tested').count(),
            'pass': results.filter(result='pass').count(),
            'fail': results.filter(result='fail').count(),
            'needs_followup': results.filter(result='needs_followup').count(),
            'not_applicable': results.filter(result='not_applicable').count(),
        }
        return Response(summary)


class ChecklistItemResultViewSet(viewsets.ModelViewSet):
    """ViewSet for managing individual item results"""
    queryset = ChecklistItemResult.objects.select_related(
        'execution', 'checklist_item', 'tested_by'
    )
    serializer_class = ChecklistItemResultSerializer
    permission_classes = [IsAuditTeamOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['execution', 'result']
    ordering = ['checklist_item__order']
    
    def perform_update(self, serializer):
        """Update result and track tester/time"""
        result = serializer.save(
            tested_by=self.request.user,
            tested_at=timezone.now()
        )
        
        # Update execution progress
        execution = result.execution
        completed = execution.item_results.exclude(result='not_tested').count()
        execution.completed_items = completed
        
        # Auto-complete execution if all items are tested
        if completed == execution.total_items and execution.status != 'completed':
            execution.status = 'completed'
            execution.completed_by = self.request.user
            execution.completed_at = timezone.now()
        
        execution.save()
    
    @action(detail=True, methods=['post'])
    def mark_pass(self, request, pk=None):
        """Quick action to mark as pass"""
        result = self.get_object()
        result.result = 'pass'
        result.tested_by = request.user
        result.tested_at = timezone.now()
        result.save()
        self._update_execution_progress(result.execution)
        return Response(self.get_serializer(result).data)
    
    @action(detail=True, methods=['post'])
    def mark_fail(self, request, pk=None):
        """Quick action to mark as fail"""
        result = self.get_object()
        result.result = 'fail'
        result.comments = request.data.get('comments', result.comments)
        result.tested_by = request.user
        result.tested_at = timezone.now()
        result.save()
        self._update_execution_progress(result.execution)
        return Response(self.get_serializer(result).data)
    
    def _update_execution_progress(self, execution):
        """Helper to update execution progress"""
        completed = execution.item_results.exclude(result='not_tested').count()
        execution.completed_items = completed
        if completed == execution.total_items:
            execution.status = 'completed'
            execution.completed_by = self.request.user
            execution.completed_at = timezone.now()
        execution.save()