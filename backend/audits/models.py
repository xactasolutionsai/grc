from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils import timezone
from iam.models import FolderMixin, PublishInRootFolderMixin
from core.base_models import NameDescriptionMixin

User = settings.AUTH_USER_MODEL


class AuditEntity(models.Model):
    """Represents an item in the Audit Universe: business unit, process, system, vendor, or compliance domain."""

    ENTITY_TYPES = [
        ("business_unit", "Business Unit"),
        ("division", "Division"),
        ("function", "Function"),
        ("section", "Section"),
        ("unit", "Unit"),
        ("process", "Process"),
        ("system", "System"),
        ("vendor", "Vendor"),
        ("compliance_domain", "Compliance Domain"),
        ("audit_domain", "Audit Domain"),
    ]

    CRITICALITY_CHOICES = [
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    AUDIT_FREQUENCY_CHOICES = [
        ("annual", "Annual"),
        ("semiannual", "Semi-annual"),
        ("quarterly", "Quarterly"),
        ("monthly", "Monthly"),
        ("ad-hoc", "Ad-hoc"),
    ]

    name = models.CharField(max_length=255, null=False, blank=False)
    entity_type = models.CharField(
        max_length=50, choices=ENTITY_TYPES, null=False, blank=False
    )
    description = models.TextField(blank=True)
    objectives = models.TextField(
        null=True, blank=True, help_text="Key responsibilities and goals of this entity"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_audit_entities",
        help_text="Entity owner/lead",
    )
    team_member = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="team_member_audit_entities",
        help_text="Entity team member/assigned person",
    )

    # Contact information
    CONTACT_TYPE_CHOICES = [
        ("owner", "Owner"),
        ("key_contact", "Key Contact"),
    ]
    contact_type = models.CharField(
        max_length=20,
        choices=CONTACT_TYPE_CHOICES,
        default="owner",
        help_text="Type of contact person",
    )
    key_contact = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="key_contact_audit_entities",
        help_text="Key contact person for this entity",
    )
    risk_score = models.FloatField(default=0.0, null=True, blank=True)
    inherent_risk_score = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    residual_risk_score = models.FloatField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    control_maturity = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    regulatory_relevance = models.JSONField(blank=True, null=True)
    last_audited = models.DateField(null=True, blank=True)
    criticality = models.CharField(
        max_length=10, choices=CRITICALITY_CHOICES, default="Medium"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="medium",
        help_text="Priority level for this entity",
    )
    audit_frequency = models.CharField(
        max_length=20, choices=AUDIT_FREQUENCY_CHOICES, default="annual"
    )
    next_audit_date = models.DateField(null=True, blank=True)
    # Geographical location fields for corporate enterprises
    location = models.CharField(
        max_length=255, blank=True
    )  # Keep for backward compatibility
    country = models.CharField(
        max_length=100, blank=True, help_text="Country where the entity is located"
    )
    region = models.CharField(
        max_length=100, blank=True, help_text="Region/State/Province"
    )
    city = models.CharField(
        max_length=100, blank=True, help_text="City where the entity is located"
    )
    address = models.TextField(blank=True, help_text="Physical address of the entity")
    postal_code = models.CharField(
        max_length=20, blank=True, help_text="Postal/ZIP code"
    )
    timezone = models.CharField(
        max_length=50, blank=True, help_text="Timezone (e.g., America/New_York)"
    )
    coordinates = models.JSONField(
        blank=True, null=True, help_text="Latitude and longitude coordinates"
    )

    # Optional organizational structure document (image/PDF)
    org_structure = models.FileField(
        upload_to="org_structures/",
        blank=True,
        null=True,
        help_text="Organizational structure file (PDF or image)",
    )

    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Audit Entity"
        verbose_name_plural = "Audit Entities"
        indexes = [
            models.Index(fields=["parent"]),
            models.Index(fields=["owner"]),
            models.Index(fields=["team_member"]),
            models.Index(fields=["key_contact"]),
            models.Index(fields=["contact_type"]),
            models.Index(fields=["entity_type"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["name"]),
            models.Index(fields=["last_audited"]),
            models.Index(fields=["next_audit_date"]),
            models.Index(fields=["criticality"]),
            models.Index(fields=["audit_frequency"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["country"]),
            models.Index(fields=["region"]),
            models.Index(fields=["city"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.entity_type})"

    def get_full_location(self):
        """Get formatted full location string"""
        location_parts = []
        if self.city:
            location_parts.append(self.city)
        if self.region:
            location_parts.append(self.region)
        if self.country:
            location_parts.append(self.country)
        return ", ".join(location_parts) if location_parts else self.location

    def get_coordinates(self):
        """Get coordinates as a tuple (lat, lng) if available"""
        if self.coordinates and isinstance(self.coordinates, dict):
            return (self.coordinates.get("latitude"), self.coordinates.get("longitude"))
        return (None, None)

    def set_coordinates(self, latitude, longitude):
        """Set coordinates from latitude and longitude values"""
        if latitude is not None and longitude is not None:
            self.coordinates = {
                "latitude": float(latitude),
                "longitude": float(longitude),
            }
        else:
            self.coordinates = None


class AuditPlan(models.Model):
    """Represents a planned audit engagement derived from the audit universe."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending_approval", "Pending Approval"),
        ("approved", "Approved"),
        ("in_review", "In Review"),
        ("rejected", "Rejected"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    AUDIT_TEAM_ROLES = [
        ("lead_auditor", "Lead Auditor"),
        ("senior_auditor", "Senior Auditor"),
        ("junior_auditor", "Junior Auditor"),
        ("auditor", "Auditor"),
    ]

    entity = models.ForeignKey(
        "AuditEntity", on_delete=models.CASCADE, related_name="audit_plans"
    )
    auditable_entities = models.ManyToManyField(
        "AuditEntity",
        blank=True,
        related_name="related_audit_plans",
        help_text="Additional auditable entities associated with this plan",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    planned_start = models.DateField()
    planned_end = models.DateField()
    actual_start = models.DateField(
        null=True, blank=True, help_text="Actual start date of the audit"
    )
    actual_end = models.DateField(
        null=True, blank=True, help_text="Actual end date of the audit"
    )
    lead_auditor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_audit_plans",
    )
    audit_team = models.JSONField(
        blank=True,
        null=True,
        help_text="Audit team members with their roles: [{'user_id': int, 'role': str, 'username': str, 'email': str}]",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    objectives = models.TextField(blank=True)
    scope = models.TextField(blank=True)
    resources = models.JSONField(blank=True, null=True)

    # Approval workflow fields
    requires_approval = models.BooleanField(default=True)
    submitted_for_approval_at = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_audit_plans",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_audit_plans",
    )
    rejection_reason = models.TextField(blank=True)
    rejection_date = models.DateTimeField(null=True, blank=True)
    rejected_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rejected_audit_plans",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["planned_start"]
        verbose_name = "Audit Plan"
        verbose_name_plural = "Audit Plans"
        indexes = [
            models.Index(fields=["entity"]),
            models.Index(fields=["lead_auditor"]),
            models.Index(fields=["status"]),
            models.Index(fields=["planned_start"]),
            models.Index(fields=["planned_end"]),
            models.Index(fields=["submitted_for_approval_at"]),
            models.Index(fields=["approved_at"]),
        ]

    def __str__(self):
        return f"Audit Plan: {self.title} ({self.entity.name})"

    def submit_for_approval(self, user):
        """Submit the audit plan for approval"""
        if self.status == "draft":
            self.status = "pending_approval"
            self.submitted_for_approval_at = timezone.now()
            self.submitted_by = user
            self.save()

    def approve(self, user):
        """Approve the audit plan"""
        if self.status == "pending_approval":
            self.status = "approved"
            self.approved_at = timezone.now()
            self.approved_by = user
            self.save()

    def reject(self, user, reason=""):
        """Reject the audit plan"""
        if self.status == "pending_approval":
            self.status = "rejected"
            self.rejection_date = timezone.now()
            self.rejected_by = user
            self.rejection_reason = reason
            self.save()

    def can_be_approved(self):
        """Check if the audit plan can be approved"""
        return self.status == "pending_approval"

    def can_be_rejected(self):
        """Check if the audit plan can be rejected"""
        return self.status == "pending_approval"


class AuditPlanApproval(models.Model):
    """Represents approval workflow for audit plans"""

    APPROVAL_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    audit_plan = models.ForeignKey(
        "AuditPlan", on_delete=models.CASCADE, related_name="approvals"
    )
    approver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="audit_plan_approvals"
    )
    status = models.CharField(
        max_length=20, choices=APPROVAL_STATUS_CHOICES, default="pending"
    )
    comments = models.TextField(blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["audit_plan", "approver"]
        ordering = ["created_at"]
        verbose_name = "Audit Plan Approval"
        verbose_name_plural = "Audit Plan Approvals"
        indexes = [
            models.Index(fields=["audit_plan"]),
            models.Index(fields=["approver"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Approval for {self.audit_plan.title} by {self.approver.email}"

    def approve(self, comments=""):
        """Approve the audit plan"""
        self.status = "approved"
        self.comments = comments
        self.approved_at = timezone.now()
        self.save()

    def reject(self, comments=""):
        """Reject the audit plan"""
        self.status = "rejected"
        self.comments = comments
        self.save()


class AuditEngagement(models.Model):
    """Represents an audit engagement derived from an audit plan"""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("in_progress", "In Progress"),
        ("fieldwork", "Fieldwork"),
        ("review", "Review"),
        ("submitted", "Submitted"),
        ("closed", "Closed"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    AUDIT_TYPE_CHOICES = [
        ("internal", "Internal Audit"),
        ("external", "External Audit"),
        ("it_audit", "IT Audit"),
        ("compliance", "Compliance Audit"),
        ("financial", "Financial Audit"),
        ("operational", "Operational Audit"),
        ("risk_assessment", "Risk Assessment"),
    ]

    # Basic information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    audit_plan = models.ForeignKey(
        "AuditPlan", on_delete=models.CASCADE, related_name="engagements"
    )
    entity = models.ForeignKey(
        "AuditEntity", on_delete=models.CASCADE, related_name="engagements"
    )

    # Engagement details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )
    audit_type = models.CharField(
        max_length=30,
        choices=AUDIT_TYPE_CHOICES,
        default="internal",
        null=True,
        blank=True,
    )
    assigned_auditor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_engagements",
    )
    engagement_lead = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_engagements",
    )

    # Dates
    planned_start_date = models.DateField()
    planned_end_date = models.DateField()
    actual_start_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)

    # Engagement scope and objectives
    scope = models.TextField(blank=True)
    objectives = models.TextField(blank=True)
    methodology = models.TextField(blank=True)

    # Progress tracking
    progress_percentage = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    fieldwork_notes = models.TextField(blank=True)
    findings_summary = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)

    # Results and closure
    results_submitted_at = models.DateTimeField(null=True, blank=True)
    results_submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_engagements",
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="closed_engagements",
    )
    closure_notes = models.TextField(blank=True)

    # Resources and budget
    estimated_hours = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    actual_hours = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    budget_allocated = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    actual_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Additional fields
    tags = models.JSONField(blank=True, null=True)
    attachments = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_engagements",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Audit Engagement"
        verbose_name_plural = "Audit Engagements"
        indexes = [
            models.Index(fields=["audit_plan"]),
            models.Index(fields=["entity"]),
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["audit_type"]),
            models.Index(fields=["assigned_auditor"]),
            models.Index(fields=["engagement_lead"]),
            models.Index(fields=["planned_start_date"]),
            models.Index(fields=["planned_end_date"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Engagement: {self.title} ({self.entity.name})"

    def start_engagement(self, user):
        """Start the engagement"""
        if self.status == "draft":
            self.status = "in_progress"
            self.actual_start_date = timezone.now().date()
            self.save()

    def submit_results(self, user, findings_summary="", recommendations=""):
        """Submit engagement results"""
        if self.status in ["in_progress", "fieldwork", "review"]:
            self.status = "submitted"
            self.results_submitted_at = timezone.now()
            self.results_submitted_by = user
            if findings_summary:
                self.findings_summary = findings_summary
            if recommendations:
                self.recommendations = recommendations
            self.save()

    def close_engagement(self, user, closure_notes=""):
        """Close the engagement"""
        if self.status == "submitted":
            self.status = "closed"
            self.closed_at = timezone.now()
            self.closed_by = user
            self.actual_end_date = timezone.now().date()
            if closure_notes:
                self.closure_notes = closure_notes
            self.save()

    def can_be_started(self):
        """Check if engagement can be started"""
        return self.status == "draft"

    def can_submit_results(self):
        """Check if results can be submitted"""
        return self.status in ["in_progress", "fieldwork", "review"]

    def can_be_closed(self):
        """Check if engagement can be closed"""
        return self.status == "submitted"

    def get_duration_days(self):
        """Get planned duration in days"""
        if self.planned_start_date and self.planned_end_date:
            return (self.planned_end_date - self.planned_start_date).days + 1
        return 0

    def get_actual_duration_days(self):
        """Get actual duration in days"""
        if self.actual_start_date and self.actual_end_date:
            return (self.actual_end_date - self.actual_start_date).days + 1
        return 0

    def is_overdue(self):
        """Check if engagement is overdue"""
        if self.status in ["draft", "in_progress", "fieldwork", "review"]:
            return timezone.now().date() > self.planned_end_date
        return False


class EngagementTimelineEvent(models.Model):
    """Represents a historical event in an engagement's timeline"""

    EVENT_TYPES = [
        ("created", "Created"),
        ("started", "Started"),
        ("fieldwork", "Fieldwork Phase"),
        ("review", "Review Phase"),
        ("submitted", "Results Submitted"),
        ("closed", "Closed"),
        ("progress_updated", "Progress Updated"),
        ("overdue", "Overdue"),
    ]

    engagement = models.ForeignKey(
        "AuditEngagement", on_delete=models.CASCADE, related_name="timeline_events"
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Store the state at the time of the event
    progress_percentage = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    status = models.CharField(max_length=20, null=True, blank=True)

    # Event metadata
    icon = models.CharField(max_length=50, default="circle")
    color = models.CharField(max_length=20, default="blue")

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Engagement Timeline Event"
        verbose_name_plural = "Engagement Timeline Events"
        indexes = [
            models.Index(fields=["engagement", "created_at"]),
            models.Index(fields=["event_type"]),
        ]

    def __str__(self):
        return f"{self.engagement.title} - {self.title} ({self.created_at})"


class EntityProcessActivity(models.Model):
    """Structured process/activity under an AuditEntity."""

    audit_entity = models.ForeignKey(
        "AuditEntity", on_delete=models.CASCADE, related_name="process_activities"
    )
    identifier = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    depends_on = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="dependents",
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Entity Process/Activity"
        verbose_name_plural = "Entity Processes/Activities"
        indexes = [
            models.Index(fields=["audit_entity", "name"]),
            models.Index(fields=["audit_entity", "identifier"]),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["audit_entity", "identifier"],
                name="uniq_entity_process_identifier",
            )
        ]

    def __str__(self):
        return f"{self.identifier or self.name} ({self.audit_entity.name})"

    def _generate_entity_code(self) -> str:
        name = (self.audit_entity.name or "").strip()
        if not name:
            return "EN"
        # Build code from first letters of up to first 3 words; fallback to first 3 letters
        parts = [p for p in name.split() if p]
        code_chars = "".join(p[0] for p in parts[:3]).upper()
        if len(code_chars) < 2:
            code_chars = name[:3].upper()
        return (code_chars[:3] or "EN").upper()

    def _next_sequence_for_entity(self, code: str) -> int:
        # Find existing identifiers like CODE-XXX and compute next NNN
        existing = self.audit_entity.process_activities.filter(
            identifier__startswith=f"{code}-"
        ).values_list("identifier", flat=True)
        max_n = 0
        for ident in existing:
            try:
                suffix = ident.split("-", 1)[1]
                n = int(suffix)
                if n > max_n:
                    max_n = n
            except Exception:
                continue
        return max_n + 1

    def save(self, *args, **kwargs):
        # Auto-generate identifier if not provided
        if not self.identifier or not self.identifier.strip():
            code = self._generate_entity_code()
            seq = self._next_sequence_for_entity(code)
            self.identifier = f"{code}-{seq:03d}"
        else:
            self.identifier = self.identifier.strip()
        super().save(*args, **kwargs)


class Checklist(NameDescriptionMixin, FolderMixin, PublishInRootFolderMixin):
    """Represents a reusable audit checklist (audit program) with multiple test items."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("archived", "Archived"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        help_text="Status of the checklist",
    )
    is_published = models.BooleanField(
        default=True, help_text="Whether the checklist is published"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_checklists",
        help_text="User who created this checklist",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Checklist"
        verbose_name_plural = "Checklists"
        indexes = [
            models.Index(fields=["folder"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["is_published"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class ChecklistItem(models.Model):
    """Represents a single test/question within an audit checklist."""

    checklist = models.ForeignKey(
        Checklist,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="Parent checklist",
    )
    title = models.CharField(
        max_length=500, help_text="Title of the audit test/question"
    )
    description = models.TextField(
        blank=True, help_text="Detailed objective or procedure for this test"
    )
    order = models.PositiveIntegerField(
        default=0, help_text="Display order within the checklist"
    )

    # Optional links to existing system objects
    control = models.ForeignKey(
        "core.AppliedControl",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checklist_items_as_control",
        help_text="Linked control being tested",
    )
    risk = models.ForeignKey(
        "core.RiskScenario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checklist_items",
        help_text="Linked risk scenario",
    )
    policy = models.ForeignKey(
        "core.Policy",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="checklist_items_as_policy",
        help_text="Linked policy",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["checklist", "order"]
        verbose_name = "Checklist Item"
        verbose_name_plural = "Checklist Items"
        indexes = [
            models.Index(fields=["checklist", "order"]),
            models.Index(fields=["control"]),
            models.Index(fields=["risk"]),
            models.Index(fields=["policy"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["checklist", "order"], name="unique_checklist_item_order"
            )
        ]

    def __str__(self):
        return f"{self.checklist.name} - {self.title}"


class ChecklistExecution(models.Model):
    """Represents an execution/instance of a checklist within an audit engagement"""

    checklist = models.ForeignKey(
        Checklist,
        on_delete=models.PROTECT,
        related_name="executions",
        help_text="Template checklist being executed",
    )
    audit_engagement = models.ForeignKey(
        "AuditEngagement",
        on_delete=models.CASCADE,
        related_name="checklist_executions",
        help_text="Audit engagement this execution belongs to",
    )

    # Status tracking
    STATUS_CHOICES = [
        ("not_started", "Not Started"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="not_started"
    )

    # Audit trail
    started_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="started_executions"
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="completed_executions"
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    # Progress tracking
    total_items = models.PositiveIntegerField(default=0)
    completed_items = models.PositiveIntegerField(default=0)

    notes = models.TextField(blank=True, help_text="Overall notes for this execution")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["checklist", "audit_engagement"]]
        verbose_name = "Checklist Execution"
        verbose_name_plural = "Checklist Executions"
        indexes = [
            models.Index(fields=["audit_engagement"]),
            models.Index(fields=["status"]),
            models.Index(fields=["started_at"]),
        ]

    def __str__(self):
        return f"{self.checklist.name} - {self.audit_engagement.title}"


class ChecklistItemResult(models.Model):
    """Stores execution results for individual checklist items"""

    execution = models.ForeignKey(
        ChecklistExecution,
        on_delete=models.CASCADE,
        related_name="item_results",
        help_text="Parent execution",
    )
    checklist_item = models.ForeignKey(
        ChecklistItem,
        on_delete=models.PROTECT,
        related_name="results",
        help_text="Template item being tested",
    )

    # Test result
    RESULT_CHOICES = [
        ("not_tested", "Not Tested"),
        ("pass", "Pass"),
        ("fail", "Fail"),
        ("needs_followup", "Needs Follow-up"),
        ("not_applicable", "Not Applicable"),
    ]
    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        default="not_tested",
        help_text="Test result status",
    )

    # Findings and comments
    comments = models.TextField(blank=True, help_text="Auditor comments and findings")
    finding_summary = models.TextField(blank=True, help_text="Summary of issues found")

    # Audit trail
    tested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tested_items",
    )
    tested_at = models.DateTimeField(null=True, blank=True)

    # Evidence (optional future enhancement)
    evidence_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["checklist_item__order"]
        unique_together = [["execution", "checklist_item"]]
        verbose_name = "Checklist Item Result"
        verbose_name_plural = "Checklist Item Results"
        indexes = [
            models.Index(fields=["execution"]),
            models.Index(fields=["result"]),
            models.Index(fields=["tested_at"]),
        ]

    def __str__(self):
        return f"{self.execution} - {self.checklist_item.title} ({self.result})"
