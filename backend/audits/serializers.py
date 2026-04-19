from rest_framework import serializers
from .models import (
    AuditEntity,
    AuditPlan,
    AuditPlanApproval,
    AuditEngagement,
    EntityProcessActivity,
    Checklist,
    ChecklistItem,
    ChecklistExecution,
    ChecklistItemResult,
)
from core.models import (
    ComplianceAssessment,
    RiskScenario,
    AppliedControl,
    Finding,
    Policy,
)


class EntityProcessActivitySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    depends_on = serializers.SerializerMethodField()
    depends_on_id = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = EntityProcessActivity
        fields = [
            "id",
            "audit_entity",
            "identifier",
            "name",
            "description",
            "depends_on",
            "depends_on_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_depends_on(self, obj):
        if obj.depends_on:
            return {
                "id": obj.depends_on.id,
                "identifier": obj.depends_on.identifier,
                "name": obj.depends_on.name,
                "entity_name": obj.depends_on.audit_entity.name,
            }
        return None

    def create(self, validated_data):
        depends_on_id = validated_data.pop("depends_on_id", None)
        if depends_on_id:
            try:
                validated_data["depends_on"] = EntityProcessActivity.objects.get(
                    id=depends_on_id
                )
            except EntityProcessActivity.DoesNotExist:
                pass
        return super().create(validated_data)

    def update(self, instance, validated_data):
        depends_on_id = validated_data.pop("depends_on_id", None)
        if depends_on_id is not None:
            if depends_on_id:
                try:
                    validated_data["depends_on"] = EntityProcessActivity.objects.get(
                        id=depends_on_id
                    )
                except EntityProcessActivity.DoesNotExist:
                    pass
            else:
                validated_data["depends_on"] = None
        return super().update(instance, validated_data)


class AuditEntitySerializer(serializers.ModelSerializer):
    # Read-only fields
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    # Optimized related field serialization (no recursion)
    parent_name = serializers.SerializerMethodField()
    owner_username = serializers.SerializerMethodField()
    owner_display = serializers.SerializerMethodField()
    team_member_username = serializers.SerializerMethodField()
    team_member_display = serializers.SerializerMethodField()
    key_contact_username = serializers.SerializerMethodField()
    key_contact_display = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    # Geographical location fields
    full_location = serializers.SerializerMethodField()
    coordinates = serializers.SerializerMethodField()
    org_structure_url = serializers.SerializerMethodField()

    # Processes / Activities
    processes = serializers.SerializerMethodField()

    class Meta:
        model = AuditEntity
        fields = [
            "id",
            "name",
            "entity_type",
            "description",
            "objectives",
            "parent",
            "parent_name",
            "owner",
            "owner_username",
            "owner_display",
            "team_member",
            "team_member_username",
            "team_member_display",
            "contact_type",
            "key_contact",
            "key_contact_username",
            "key_contact_display",
            "risk_score",
            "inherent_risk_score",
            "residual_risk_score",
            "control_maturity",
            "regulatory_relevance",
            "last_audited",
            "criticality",
            "priority",
            "audit_frequency",
            "next_audit_date",
            "location",
            "country",
            "region",
            "city",
            "address",
            "postal_code",
            "timezone",
            "coordinates",
            "full_location",
            "org_structure",
            "org_structure_url",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
            "children",
            "processes",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "parent_name",
            "owner_username",
            "owner_display",
            "team_member_username",
            "team_member_display",
            "key_contact_username",
            "key_contact_display",
            "children",
            "full_location",
            "coordinates",
            "org_structure_url",
            "processes",
        ]

    def get_parent_name(self, obj):
        """Get parent name safely without causing additional queries."""
        return obj.parent.name if obj.parent else None

    def get_owner_username(self, obj):
        """Get owner email safely without causing additional queries."""
        return obj.owner.email if obj.owner else None

    def get_owner_display(self, obj):
        """Get owner display name (username)."""
        return obj.owner.username if obj.owner else None

    def get_team_member_username(self, obj):
        """Get team member email safely without causing additional queries."""
        return obj.team_member.email if obj.team_member else None

    def get_team_member_display(self, obj):
        """Get team member display name (username)."""
        return obj.team_member.username if obj.team_member else None

    def get_key_contact_username(self, obj):
        """Get key contact email safely without causing additional queries."""
        return obj.key_contact.email if obj.key_contact else None

    def get_key_contact_display(self, obj):
        """Get key contact display name (username)."""
        return obj.key_contact.username if obj.key_contact else None

    def get_children(self, obj):
        """Get children entities for detail view."""
        # Only include children for detail view (when retrieving single entity)
        if hasattr(obj, "children") and obj.children.exists():
            return [
                {"id": child.id, "name": child.name, "entity_type": child.entity_type}
                for child in obj.children.all()
            ]
        return []

    def get_full_location(self, obj):
        """Get formatted full location string."""
        return obj.get_full_location()

    def get_coordinates(self, obj):
        """Get coordinates as a tuple (lat, lng) if available."""
        lat, lng = obj.get_coordinates()
        if lat is not None and lng is not None:
            return {"latitude": lat, "longitude": lng}
        return None

    def get_org_structure_url(self, obj):
        if getattr(obj, "org_structure", None):
            try:
                return obj.org_structure.url
            except Exception:
                return None
        return None

    def get_processes(self, obj):
        qs = getattr(obj, "process_activities", None)
        if qs is None:
            return []
        return EntityProcessActivitySerializer(
            qs.all().order_by("name"), many=True
        ).data

    def validate_risk_score(self, value):
        """Validate risk score is between 0 and 10"""
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError("Risk score must be between 0 and 10")
        return value

    def validate_inherent_risk_score(self, value):
        """Validate inherent risk score is between 0 and 10"""
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError(
                "Inherent risk score must be between 0 and 10"
            )
        return value

    def validate_residual_risk_score(self, value):
        """Validate residual risk score is between 0 and 10"""
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError(
                "Residual risk score must be between 0 and 10"
            )
        return value

    def validate_control_maturity(self, value):
        """Validate control maturity is between 0 and 5"""
        if value is not None and (value < 0 or value > 5):
            raise serializers.ValidationError(
                "Control maturity must be between 0 and 5"
            )
        return value

    def validate_name(self, value):
        """Validate name is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required and cannot be empty")
        return value.strip()

    def validate_entity_type(self, value):
        """Validate entity_type is valid choice"""
        valid_choices = [choice[0] for choice in self.Meta.model.ENTITY_TYPES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Entity type must be one of: {', '.join(valid_choices)}"
            )
        return value

    def validate_contact_type(self, value):
        """Validate contact_type is valid choice"""
        valid_choices = [choice[0] for choice in self.Meta.model.CONTACT_TYPE_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Contact type must be one of: {', '.join(valid_choices)}"
            )
        return value

    def validate_parent(self, value):
        """Validate parent is not self (prevent circular references)"""
        if (
            value
            and hasattr(self, "instance")
            and self.instance
            and value.id == self.instance.id
        ):
            raise serializers.ValidationError("An entity cannot be its own parent")
        return value

    def validate_coordinates(self, value):
        """Validate coordinates format"""
        if value is not None:
            if not isinstance(value, dict):
                raise serializers.ValidationError("Coordinates must be a dictionary")
            if "latitude" not in value or "longitude" not in value:
                raise serializers.ValidationError(
                    "Coordinates must contain 'latitude' and 'longitude' keys"
                )
            try:
                lat = float(value["latitude"])
                lng = float(value["longitude"])
                if not (-90 <= lat <= 90):
                    raise serializers.ValidationError(
                        "Latitude must be between -90 and 90"
                    )
                if not (-180 <= lng <= 180):
                    raise serializers.ValidationError(
                        "Longitude must be between -180 and 180"
                    )
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    "Latitude and longitude must be valid numbers"
                )
        return value

    def validate_timezone(self, value):
        """Validate timezone format"""
        if value:
            import pytz

            try:
                pytz.timezone(value)
            except pytz.exceptions.UnknownTimeZoneError:
                raise serializers.ValidationError("Invalid timezone format")
        return value

    def validate(self, data):
        """Validate for circular references in the hierarchy."""
        parent = data.get("parent")
        if parent and hasattr(self, "instance") and self.instance:
            # Check if this would create a circular reference
            if self._would_create_circular_reference(self.instance, parent):
                raise serializers.ValidationError(
                    "This would create a circular reference in the hierarchy"
                )
        return data

    def _would_create_circular_reference(self, instance, parent):
        """Check if setting parent would create a circular reference."""
        current = parent
        visited = set()

        while current:
            if current.id == instance.id:
                return True
            if current.id in visited:
                # Already checked this path, no circular reference found
                break
            visited.add(current.id)
            current = current.parent

        return False


# Lightweight serializers for related objects
class EngagementSummarySerializer(serializers.Serializer):
    """Placeholder for future AuditEngagement model"""

    id = serializers.IntegerField()
    title = serializers.CharField()
    status = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class ComplianceAuditSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for ComplianceAssessment"""

    framework = serializers.CharField(source="framework.name", read_only=True)

    class Meta:
        model = ComplianceAssessment
        fields = ["id", "name", "framework", "status"]


class RiskSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for RiskScenario"""

    severity = serializers.SerializerMethodField()

    class Meta:
        model = RiskScenario
        fields = ["id", "name", "severity"]

    def get_severity(self, obj):
        """Get severity as string"""
        return obj.current_level if hasattr(obj, "current_level") else "Unknown"


class ControlSummarySerializer(serializers.ModelSerializer):
    """Summary serializer for AppliedControl"""

    class Meta:
        model = AppliedControl
        fields = ["id", "name", "status"]


class RelatedObjectsSerializer(serializers.Serializer):
    """Serializer for the related objects endpoint"""

    engagements = EngagementSummarySerializer(many=True, read_only=True)
    compliance_audits = ComplianceAuditSummarySerializer(many=True, read_only=True)
    risks = RiskSummarySerializer(many=True, read_only=True)
    controls = ControlSummarySerializer(many=True, read_only=True)


class AuditPlanSerializer(serializers.ModelSerializer):
    """Serializer for AuditPlan model"""

    entity_name = serializers.CharField(source="entity.name", read_only=True)
    entity_type = serializers.CharField(source="entity.entity_type", read_only=True)
    auditable_entities = serializers.PrimaryKeyRelatedField(
        many=True, queryset=AuditEntity.objects.all(), required=False, allow_null=True
    )
    auditable_entities_display = serializers.SerializerMethodField()
    audit_team_display = serializers.SerializerMethodField()
    lead_auditor_display = serializers.SerializerMethodField()
    submitted_by_display = serializers.SerializerMethodField()
    approved_by_display = serializers.SerializerMethodField()
    rejected_by_display = serializers.SerializerMethodField()
    can_be_approved = serializers.SerializerMethodField()
    can_be_rejected = serializers.SerializerMethodField()

    class Meta:
        model = AuditPlan
        fields = [
            "id",
            "entity",
            "entity_name",
            "entity_type",
            "auditable_entities",
            "auditable_entities_display",
            "title",
            "description",
            "planned_start",
            "planned_end",
            "actual_start",
            "actual_end",
            "lead_auditor",
            "lead_auditor_display",
            "audit_team",
            "audit_team_display",
            "status",
            "objectives",
            "scope",
            "resources",
            "requires_approval",
            "submitted_for_approval_at",
            "submitted_by",
            "submitted_by_display",
            "approved_at",
            "approved_by",
            "approved_by_display",
            "rejection_reason",
            "rejection_date",
            "rejected_by",
            "rejected_by_display",
            "can_be_approved",
            "can_be_rejected",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "entity_name",
            "entity_type",
            "auditable_entities_display",
            "audit_team_display",
            "lead_auditor_display",
            "submitted_by_display",
            "approved_by_display",
            "rejected_by_display",
            "can_be_approved",
            "can_be_rejected",
            "submitted_for_approval_at",
            "submitted_by",
            "approved_at",
            "approved_by",
            "rejection_date",
            "rejected_by",
        ]

    def get_auditable_entities_display(self, obj):
        """Get list of auditable entity names"""
        try:
            if hasattr(obj, "auditable_entities"):
                return [
                    {
                        "id": entity.id,
                        "name": entity.name,
                        "entity_type": entity.entity_type,
                    }
                    for entity in obj.auditable_entities.all()
                ]
            return []
        except Exception:
            return []

    def get_audit_team_display(self, obj):
        """Get formatted audit team information"""
        try:
            if hasattr(obj, "audit_team") and obj.audit_team:
                return obj.audit_team
            return []
        except Exception:
            return []

    def get_lead_auditor_display(self, obj):
        """Get lead auditor display name"""
        try:
            return obj.lead_auditor.username if obj.lead_auditor else None
        except AttributeError:
            return None

    def get_submitted_by_display(self, obj):
        """Get submitted by display name"""
        try:
            return obj.submitted_by.username if obj.submitted_by else None
        except AttributeError:
            return None

    def get_approved_by_display(self, obj):
        """Get approved by display name"""
        try:
            return obj.approved_by.username if obj.approved_by else None
        except AttributeError:
            return None

    def get_rejected_by_display(self, obj):
        """Get rejected by display name"""
        try:
            return obj.rejected_by.username if obj.rejected_by else None
        except AttributeError:
            return None

    def get_can_be_approved(self, obj):
        """Check if audit plan can be approved"""
        return obj.can_be_approved()

    def get_can_be_rejected(self, obj):
        """Check if audit plan can be rejected"""
        return obj.can_be_rejected()

    def validate_planned_end(self, value):
        """Validate that planned_end is after planned_start"""
        planned_start = self.initial_data.get("planned_start")
        if planned_start and value:
            # Convert planned_start to date object for comparison
            from datetime import datetime

            if isinstance(planned_start, str):
                planned_start = datetime.strptime(planned_start, "%Y-%m-%d").date()
            if value < planned_start:
                raise serializers.ValidationError(
                    "Planned end date must be after planned start date"
                )
        return value

    def validate_title(self, value):
        """Validate title is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Title is required and cannot be empty")
        return value.strip()

    def validate_actual_start(self, value):
        """Validate actual start date"""
        if value:
            planned_start = self.initial_data.get("planned_start")
            if self.instance:
                planned_start = planned_start or self.instance.planned_start
            if planned_start:
                from datetime import datetime

                if isinstance(planned_start, str):
                    planned_start = datetime.strptime(planned_start, "%Y-%m-%d").date()
                if value < planned_start:
                    raise serializers.ValidationError(
                        "Actual start date cannot be before planned start date"
                    )
        return value

    def validate_actual_end(self, value):
        """Validate actual end date"""
        if value:
            actual_start = self.initial_data.get("actual_start")
            if self.instance:
                actual_start = actual_start or self.instance.actual_start
            if actual_start:
                from datetime import datetime

                if isinstance(actual_start, str):
                    actual_start = datetime.strptime(actual_start, "%Y-%m-%d").date()
                if value < actual_start:
                    raise serializers.ValidationError(
                        "Actual end date must be after actual start date"
                    )
        return value

    def validate_audit_team(self, value):
        """Validate audit team structure and roles"""
        if value:
            if not isinstance(value, list):
                raise serializers.ValidationError("Audit team must be a list")

            # Check if there's at least one Lead Auditor
            lead_auditor_count = sum(
                1 for member in value if member.get("role") == "lead_auditor"
            )
            if lead_auditor_count == 0:
                raise serializers.ValidationError(
                    "At least one Lead Auditor must be assigned to the audit team"
                )

            # Validate structure of each team member
            valid_roles = [
                "lead_auditor",
                "senior_auditor",
                "junior_auditor",
                "auditor",
            ]
            for member in value:
                if not isinstance(member, dict):
                    raise serializers.ValidationError(
                        "Each team member must be an object"
                    )
                if "user_id" not in member or "role" not in member:
                    raise serializers.ValidationError(
                        "Each team member must have 'user_id' and 'role'"
                    )
                if member["role"] not in valid_roles:
                    raise serializers.ValidationError(
                        f"Invalid role '{member['role']}'. Must be one of: {', '.join(valid_roles)}"
                    )
        return value

    def validate(self, data):
        """Validate the entire data set"""
        planned_start = data.get("planned_start")
        planned_end = data.get("planned_end")
        actual_start = data.get("actual_start")
        actual_end = data.get("actual_end")

        if planned_start and planned_end and planned_end < planned_start:
            raise serializers.ValidationError(
                "Planned end date must be after planned start date"
            )

        if actual_start and actual_end and actual_end < actual_start:
            raise serializers.ValidationError(
                "Actual end date must be after actual start date"
            )

        return data

    def create(self, validated_data):
        """Handle creation with ManyToMany field"""
        auditable_entities = validated_data.pop("auditable_entities", [])
        audit_plan = super().create(validated_data)
        try:
            if auditable_entities and hasattr(audit_plan, "auditable_entities"):
                audit_plan.auditable_entities.set(auditable_entities)
        except Exception as e:
            # Field doesn't exist yet, migration not applied
            pass
        return audit_plan

    def update(self, instance, validated_data):
        """Handle update with ManyToMany field"""
        auditable_entities = validated_data.pop("auditable_entities", None)
        audit_plan = super().update(instance, validated_data)
        try:
            if auditable_entities is not None and hasattr(
                audit_plan, "auditable_entities"
            ):
                audit_plan.auditable_entities.set(auditable_entities)
        except Exception as e:
            # Field doesn't exist yet, migration not applied
            pass
        return audit_plan


class AuditPlanApprovalSerializer(serializers.ModelSerializer):
    """Serializer for AuditPlanApproval model"""

    approver_display = serializers.SerializerMethodField()
    audit_plan_title = serializers.CharField(source="audit_plan.title", read_only=True)

    class Meta:
        model = AuditPlanApproval
        fields = [
            "id",
            "audit_plan",
            "audit_plan_title",
            "approver",
            "approver_display",
            "status",
            "comments",
            "approved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "audit_plan_title",
            "approver_display",
            "approved_at",
        ]

    def get_approver_display(self, obj):
        """Get approver display name"""
        return obj.approver.username if obj.approver else None

    def validate_status(self, value):
        """Validate status is valid choice"""
        valid_choices = [
            choice[0] for choice in self.Meta.model.APPROVAL_STATUS_CHOICES
        ]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(valid_choices)}"
            )
        return value


class AuditPlanApprovalActionSerializer(serializers.Serializer):
    """Serializer for approval/rejection actions"""

    action = serializers.ChoiceField(choices=["approve", "reject"])
    comments = serializers.CharField(required=False, allow_blank=True)

    def validate_action(self, value):
        """Validate action is valid"""
        if value not in ["approve", "reject"]:
            raise serializers.ValidationError("Action must be 'approve' or 'reject'")
        return value


class AuditEngagementSerializer(serializers.ModelSerializer):
    """Serializer for AuditEngagement model"""

    audit_plan_title = serializers.CharField(source="audit_plan.title", read_only=True)
    entity_name = serializers.CharField(source="entity.name", read_only=True)
    entity_type = serializers.CharField(source="entity.entity_type", read_only=True)
    assigned_auditor_display = serializers.SerializerMethodField()
    engagement_lead_display = serializers.SerializerMethodField()
    results_submitted_by_display = serializers.SerializerMethodField()
    closed_by_display = serializers.SerializerMethodField()
    created_by_display = serializers.SerializerMethodField()
    can_be_started = serializers.SerializerMethodField()
    can_submit_results = serializers.SerializerMethodField()
    can_be_closed = serializers.SerializerMethodField()
    duration_days = serializers.SerializerMethodField()
    actual_duration_days = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = AuditEngagement
        fields = [
            "id",
            "title",
            "description",
            "audit_plan",
            "audit_plan_title",
            "entity",
            "entity_name",
            "entity_type",
            "status",
            "priority",
            "audit_type",
            "assigned_auditor",
            "assigned_auditor_display",
            "engagement_lead",
            "engagement_lead_display",
            "planned_start_date",
            "planned_end_date",
            "actual_start_date",
            "actual_end_date",
            "scope",
            "objectives",
            "methodology",
            "progress_percentage",
            "fieldwork_notes",
            "findings_summary",
            "recommendations",
            "results_submitted_at",
            "results_submitted_by",
            "results_submitted_by_display",
            "closed_at",
            "closed_by",
            "closed_by_display",
            "closure_notes",
            "estimated_hours",
            "actual_hours",
            "budget_allocated",
            "actual_cost",
            "tags",
            "attachments",
            "is_active",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_display",
            "can_be_started",
            "can_submit_results",
            "can_be_closed",
            "duration_days",
            "actual_duration_days",
            "is_overdue",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "audit_plan_title",
            "entity_name",
            "entity_type",
            "assigned_auditor_display",
            "engagement_lead_display",
            "results_submitted_by_display",
            "closed_by_display",
            "created_by_display",
            "can_be_started",
            "can_submit_results",
            "can_be_closed",
            "duration_days",
            "actual_duration_days",
            "is_overdue",
            "results_submitted_at",
            "results_submitted_by",
            "closed_at",
            "closed_by",
        ]

    def get_assigned_auditor_display(self, obj):
        """Get assigned auditor display name"""
        try:
            return obj.assigned_auditor.username if obj.assigned_auditor else None
        except AttributeError:
            return None

    def get_engagement_lead_display(self, obj):
        """Get engagement lead display name"""
        try:
            return obj.engagement_lead.username if obj.engagement_lead else None
        except AttributeError:
            return None

    def get_results_submitted_by_display(self, obj):
        """Get results submitted by display name"""
        try:
            return (
                obj.results_submitted_by.username if obj.results_submitted_by else None
            )
        except AttributeError:
            return None

    def get_closed_by_display(self, obj):
        """Get closed by display name"""
        try:
            return obj.closed_by.username if obj.closed_by else None
        except AttributeError:
            return None

    def get_created_by_display(self, obj):
        """Get created by display name"""
        try:
            return obj.created_by.username if obj.created_by else None
        except AttributeError:
            return None

    def get_can_be_started(self, obj):
        """Check if engagement can be started"""
        return obj.can_be_started()

    def get_can_submit_results(self, obj):
        """Check if results can be submitted"""
        return obj.can_submit_results()

    def get_can_be_closed(self, obj):
        """Check if engagement can be closed"""
        return obj.can_be_closed()

    def get_duration_days(self, obj):
        """Get planned duration in days"""
        return obj.get_duration_days()

    def get_actual_duration_days(self, obj):
        """Get actual duration in days"""
        return obj.get_actual_duration_days()

    def get_is_overdue(self, obj):
        """Check if engagement is overdue"""
        return obj.is_overdue()

    def validate_planned_end_date(self, value):
        """Validate that planned_end_date is after planned_start_date"""
        planned_start_date = self.initial_data.get("planned_start_date")
        if planned_start_date and value:
            from datetime import datetime

            if isinstance(planned_start_date, str):
                planned_start_date = datetime.strptime(
                    planned_start_date, "%Y-%m-%d"
                ).date()
            if value < planned_start_date:
                raise serializers.ValidationError(
                    "Planned end date must be after planned start date"
                )
        return value

    def validate_progress_percentage(self, value):
        """Validate progress percentage is between 0 and 100"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Progress percentage must be between 0 and 100"
            )
        return value

    def validate_estimated_hours(self, value):
        """Validate estimated hours is positive"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Estimated hours must be positive")
        return value

    def validate_actual_hours(self, value):
        """Validate actual hours is positive"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Actual hours must be positive")
        return value

    def validate_budget_allocated(self, value):
        """Validate budget allocated is positive"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Budget allocated must be positive")
        return value

    def validate_actual_cost(self, value):
        """Validate actual cost is positive"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Actual cost must be positive")
        return value

    def validate_title(self, value):
        """Validate title is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Title is required and cannot be empty")
        return value.strip()

    def validate_status(self, value):
        """Validate status is valid choice"""
        valid_choices = [choice[0] for choice in self.Meta.model.STATUS_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(valid_choices)}"
            )
        return value

    def validate_priority(self, value):
        """Validate priority is valid choice"""
        valid_choices = [choice[0] for choice in self.Meta.model.PRIORITY_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Priority must be one of: {', '.join(valid_choices)}"
            )
        return value

    def validate_audit_type(self, value):
        """Validate audit_type is valid choice"""
        valid_choices = [choice[0] for choice in self.Meta.model.AUDIT_TYPE_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Audit type must be one of: {', '.join(valid_choices)}"
            )
        return value

    def validate_actual_start_date(self, value):
        """Validate actual start date"""
        if value:
            planned_start_date = self.initial_data.get("planned_start_date")
            if self.instance:
                planned_start_date = (
                    planned_start_date or self.instance.planned_start_date
                )
            # Optionally warn if actual is significantly different from planned
        return value

    def validate_actual_end_date(self, value):
        """Validate actual end date"""
        if value:
            actual_start_date = self.initial_data.get("actual_start_date")
            if self.instance:
                actual_start_date = actual_start_date or self.instance.actual_start_date
            if actual_start_date:
                from datetime import datetime

                if isinstance(actual_start_date, str):
                    actual_start_date = datetime.strptime(
                        actual_start_date, "%Y-%m-%d"
                    ).date()
                if value < actual_start_date:
                    raise serializers.ValidationError(
                        "Actual end date must be after actual start date"
                    )
        return value

    def validate(self, data):
        """Validate the entire data set"""
        planned_start_date = data.get("planned_start_date")
        planned_end_date = data.get("planned_end_date")
        actual_start_date = data.get("actual_start_date")
        actual_end_date = data.get("actual_end_date")

        if (
            planned_start_date
            and planned_end_date
            and planned_end_date < planned_start_date
        ):
            raise serializers.ValidationError(
                "Planned end date must be after planned start date"
            )

        if (
            actual_start_date
            and actual_end_date
            and actual_end_date < actual_start_date
        ):
            raise serializers.ValidationError(
                "Actual end date must be after actual start date"
            )

        return data


class AuditEngagementActionSerializer(serializers.Serializer):
    """Serializer for engagement actions"""

    action = serializers.ChoiceField(choices=["start", "submit_results", "close"])
    findings_summary = serializers.CharField(required=False, allow_blank=True)
    recommendations = serializers.CharField(required=False, allow_blank=True)
    closure_notes = serializers.CharField(required=False, allow_blank=True)

    def validate_action(self, value):
        """Validate action is valid"""
        if value not in ["start", "submit_results", "close"]:
            raise serializers.ValidationError(
                "Action must be 'start', 'submit_results', or 'close'"
            )
        return value


class ChecklistItemSerializer(serializers.ModelSerializer):
    """Serializer for ChecklistItem model"""

    control_name = serializers.SerializerMethodField()
    control_display = serializers.SerializerMethodField()
    risk_name = serializers.SerializerMethodField()
    risk_display = serializers.SerializerMethodField()
    policy_name = serializers.SerializerMethodField()
    policy_display = serializers.SerializerMethodField()

    class Meta:
        model = ChecklistItem
        fields = [
            "id",
            "checklist",
            "title",
            "description",
            "order",
            "control",
            "control_name",
            "control_display",
            "risk",
            "risk_name",
            "risk_display",
            "policy",
            "policy_name",
            "policy_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "control_name",
            "control_display",
            "risk_name",
            "risk_display",
            "policy_name",
            "policy_display",
        ]

    def get_control_name(self, obj):
        """Get control name"""
        return obj.control.name if obj.control else None

    def get_control_display(self, obj):
        """Get control display info"""
        if obj.control:
            return {
                "id": obj.control.id,
                "name": obj.control.name,
                "status": getattr(obj.control, "status", None),
            }
        return None

    def get_risk_name(self, obj):
        """Get risk scenario name"""
        return obj.risk.name if obj.risk else None

    def get_risk_display(self, obj):
        """Get risk display info"""
        if obj.risk:
            return {
                "id": obj.risk.id,
                "name": obj.risk.name,
                "current_level": getattr(obj.risk, "current_level", None),
            }
        return None

    def get_policy_name(self, obj):
        """Get policy name"""
        return obj.policy.name if obj.policy else None

    def get_policy_display(self, obj):
        """Get policy display info"""
        if obj.policy:
            return {
                "id": obj.policy.id,
                "name": obj.policy.name,
                "status": getattr(obj.policy, "status", None),
            }
        return None

    def validate_title(self, value):
        """Validate title is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Title is required and cannot be empty")
        return value.strip()

    def validate_order(self, value):
        """Validate order is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Order must be non-negative")
        return value


class ChecklistSerializer(serializers.ModelSerializer):
    """Serializer for Checklist model"""

    items = serializers.SerializerMethodField()
    folder_name = serializers.SerializerMethodField()
    created_by_display = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Checklist
        fields = [
            "id",
            "name",
            "description",
            "folder",
            "folder_name",
            "status",
            "is_published",
            "created_by",
            "created_by_display",
            "created_at",
            "updated_at",
            "items",
            "item_count",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "folder_name",
            "created_by_display",
            "items",
            "item_count",
        ]

    def get_items(self, obj):
        """Get nested checklist items"""
        if hasattr(obj, "items"):
            items = obj.items.all().order_by("order")
            return ChecklistItemSerializer(items, many=True).data
        return []

    def get_folder_name(self, obj):
        """Get folder name"""
        return obj.folder.name if obj.folder else None

    def get_created_by_display(self, obj):
        """Get created by display name"""
        try:
            return obj.created_by.username if obj.created_by else None
        except AttributeError:
            return None

    def get_item_count(self, obj):
        """Get count of items in this checklist"""
        if hasattr(obj, "items"):
            return obj.items.count()
        return 0

    def validate_name(self, value):
        """Validate name is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required and cannot be empty")
        return value.strip()

    def validate_status(self, value):
        """Validate status is valid choice"""
        valid_choices = [choice[0] for choice in Checklist.STATUS_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(valid_choices)}"
            )
        return value

    def create(self, validated_data):
        """Handle creation with nested items if provided"""
        # Items will be created separately via the items endpoint
        # This serializer focuses on the checklist itself
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Handle update with nested items if provided"""
        # Items will be updated separately via the items endpoint
        # This serializer focuses on the checklist itself
        return super().update(instance, validated_data)


class ChecklistItemResultSerializer(serializers.ModelSerializer):
    """Serializer for ChecklistItemResult model"""

    checklist_item_title = serializers.CharField(
        source="checklist_item.title", read_only=True
    )
    checklist_item_description = serializers.CharField(
        source="checklist_item.description", read_only=True
    )
    checklist_item_order = serializers.IntegerField(
        source="checklist_item.order", read_only=True
    )
    tested_by_display = serializers.SerializerMethodField()

    # Include linked objects from template item
    control_name = serializers.SerializerMethodField()
    risk_name = serializers.SerializerMethodField()
    policy_name = serializers.SerializerMethodField()

    class Meta:
        model = ChecklistItemResult
        fields = [
            "id",
            "execution",
            "checklist_item",
            "checklist_item_title",
            "checklist_item_description",
            "checklist_item_order",
            "result",
            "comments",
            "finding_summary",
            "tested_by",
            "tested_by_display",
            "tested_at",
            "control_name",
            "risk_name",
            "policy_name",
            "evidence_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_tested_by_display(self, obj):
        """Get tested by display name"""
        if obj.tested_by:
            return (
                f"{obj.tested_by.first_name} {obj.tested_by.last_name}".strip()
                or obj.tested_by.username
            )
        return None

    def get_control_name(self, obj):
        """Get control name from checklist item"""
        return obj.checklist_item.control.name if obj.checklist_item.control else None

    def get_risk_name(self, obj):
        """Get risk name from checklist item"""
        return obj.checklist_item.risk.name if obj.checklist_item.risk else None

    def get_policy_name(self, obj):
        """Get policy name from checklist item"""
        return obj.checklist_item.policy.name if obj.checklist_item.policy else None


class ChecklistExecutionSerializer(serializers.ModelSerializer):
    """Serializer for ChecklistExecution model"""

    checklist_name = serializers.CharField(source="checklist.name", read_only=True)
    engagement_title = serializers.CharField(
        source="audit_engagement.title", read_only=True
    )
    started_by_display = serializers.SerializerMethodField()
    completed_by_display = serializers.SerializerMethodField()

    item_results = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = ChecklistExecution
        fields = [
            "id",
            "checklist",
            "checklist_name",
            "audit_engagement",
            "engagement_title",
            "status",
            "started_by",
            "started_by_display",
            "started_at",
            "completed_by",
            "completed_by_display",
            "completed_at",
            "total_items",
            "completed_items",
            "progress_percentage",
            "notes",
            "item_results",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "total_items",
            "completed_items",
            "created_at",
            "updated_at",
        ]

    def get_started_by_display(self, obj):
        """Get started by display name"""
        if obj.started_by:
            return (
                f"{obj.started_by.first_name} {obj.started_by.last_name}".strip()
                or obj.started_by.username
            )
        return None

    def get_completed_by_display(self, obj):
        """Get completed by display name"""
        if obj.completed_by:
            return (
                f"{obj.completed_by.first_name} {obj.completed_by.last_name}".strip()
                or obj.completed_by.username
            )
        return None

    def get_item_results(self, obj):
        """Get nested item results"""
        results = obj.item_results.select_related(
            "checklist_item", "tested_by"
        ).order_by("checklist_item__order")
        return ChecklistItemResultSerializer(results, many=True).data

    def get_progress_percentage(self, obj):
        """Calculate progress percentage"""
        if obj.total_items == 0:
            return 0
        return round((obj.completed_items / obj.total_items) * 100, 1)
