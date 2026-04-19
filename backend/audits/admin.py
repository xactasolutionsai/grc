from django.contrib import admin
from .models import AuditEntity, AuditPlan, AuditPlanApproval, AuditEngagement, Checklist, ChecklistItem, ChecklistExecution, ChecklistItemResult

@admin.register(AuditEntity)
class AuditEntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity_type', 'owner', 'risk_score', 'last_audited', 'is_active')
    list_filter = ('entity_type', 'is_active')
    search_fields = ('name', 'description')

@admin.register(AuditPlan)
class AuditPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'entity', 'status', 'planned_start', 'planned_end', 'lead_auditor', 'requires_approval')
    list_filter = ('status', 'requires_approval', 'planned_start', 'entity__entity_type')
    search_fields = ('title', 'description', 'entity__name')
    readonly_fields = ('submitted_for_approval_at', 'submitted_by', 'approved_at', 'approved_by', 'rejection_date', 'rejected_by')

@admin.register(AuditPlanApproval)
class AuditPlanApprovalAdmin(admin.ModelAdmin):
    list_display = ('audit_plan', 'approver', 'status', 'created_at', 'approved_at')
    list_filter = ('status', 'created_at')
    search_fields = ('audit_plan__title', 'approver__username', 'comments')
    readonly_fields = ('created_at', 'updated_at', 'approved_at')

@admin.register(AuditEngagement)
class AuditEngagementAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'audit_plan', 'entity', 'status', 'priority', 
        'assigned_auditor', 'planned_start_date', 'planned_end_date', 'progress_percentage'
    )
    list_filter = ('status', 'priority', 'planned_start_date', 'is_active')
    search_fields = ('title', 'description', 'audit_plan__title', 'entity__name')
    readonly_fields = (
        'created_at', 'updated_at', 'actual_start_date', 'actual_end_date',
        'results_submitted_at', 'results_submitted_by', 'closed_at', 'closed_by'
    )
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'audit_plan', 'entity', 'status', 'priority')
        }),
        ('Assignment', {
            'fields': ('assigned_auditor', 'engagement_lead', 'created_by')
        }),
        ('Dates', {
            'fields': ('planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_end_date')
        }),
        ('Scope & Objectives', {
            'fields': ('scope', 'objectives', 'methodology')
        }),
        ('Progress', {
            'fields': ('progress_percentage', 'fieldwork_notes', 'findings_summary', 'recommendations')
        }),
        ('Resources', {
            'fields': ('estimated_hours', 'actual_hours', 'budget_allocated', 'actual_cost')
        }),
        ('Closure', {
            'fields': ('results_submitted_at', 'results_submitted_by', 'closed_at', 'closed_by', 'closure_notes')
        }),
        ('Additional', {
            'fields': ('tags', 'attachments', 'is_active')
        })
    )

class ChecklistItemInline(admin.TabularInline):
    model = ChecklistItem
    extra = 1
    fields = ('order', 'title', 'description', 'control', 'risk', 'policy')
    ordering = ('order',)

@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ('name', 'folder', 'status', 'is_published', 'created_by', 'created_at')
    list_filter = ('status', 'is_published', 'folder', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ChecklistItemInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'folder')
        }),
        ('Status', {
            'fields': ('status', 'is_published')
        }),
        ('Audit Trail', {
            'fields': ('created_by', 'created_at', 'updated_at')
        })
    )

@admin.register(ChecklistItem)
class ChecklistItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'checklist', 'order', 'control', 'risk', 'policy')
    list_filter = ('checklist__status', 'checklist')
    search_fields = ('title', 'description', 'checklist__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('checklist', 'order', 'title', 'description')
        }),
        ('Links', {
            'fields': ('control', 'risk', 'policy')
        }),
        ('Audit Trail', {
            'fields': ('created_at', 'updated_at')
        })
    )


class ChecklistItemResultInline(admin.TabularInline):
    model = ChecklistItemResult
    extra = 0
    fields = ('checklist_item', 'result', 'comments', 'tested_by', 'tested_at')
    readonly_fields = ('tested_at',)
    ordering = ('checklist_item__order',)


@admin.register(ChecklistExecution)
class ChecklistExecutionAdmin(admin.ModelAdmin):
    list_display = ('checklist', 'audit_engagement', 'status', 'progress_display', 'started_at', 'completed_at')
    list_filter = ('status', 'started_at', 'completed_at')
    search_fields = ('checklist__name', 'audit_engagement__title')
    readonly_fields = ('created_at', 'updated_at', 'total_items', 'completed_items')
    inlines = [ChecklistItemResultInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('checklist', 'audit_engagement', 'status')
        }),
        ('Progress', {
            'fields': ('total_items', 'completed_items', 'notes')
        }),
        ('Audit Trail', {
            'fields': ('started_by', 'started_at', 'completed_by', 'completed_at', 'created_at', 'updated_at')
        })
    )
    
    def progress_display(self, obj):
        if obj.total_items == 0:
            return "0%"
        percentage = round((obj.completed_items / obj.total_items) * 100, 1)
        return f"{obj.completed_items}/{obj.total_items} ({percentage}%)"
    progress_display.short_description = 'Progress'


@admin.register(ChecklistItemResult)
class ChecklistItemResultAdmin(admin.ModelAdmin):
    list_display = ('execution', 'checklist_item', 'result', 'tested_by', 'tested_at')
    list_filter = ('result', 'tested_at')
    search_fields = ('execution__checklist__name', 'checklist_item__title', 'comments')
    readonly_fields = ('created_at', 'updated_at', 'tested_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('execution', 'checklist_item', 'result')
        }),
        ('Comments & Findings', {
            'fields': ('comments', 'finding_summary', 'evidence_notes')
        }),
        ('Audit Trail', {
            'fields': ('tested_by', 'tested_at', 'created_at', 'updated_at')
        })
    )