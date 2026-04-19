from django.contrib import admin
from .models import Workpaper, WorkpaperApproval


@admin.register(Workpaper)
class WorkpaperAdmin(admin.ModelAdmin):
    """Admin interface for Workpaper model"""

    list_display = [
        "title",
        "workpaper_type",
        "status",
        "uploaded_by",
        "reviewer",
        "approver",
        "created_at",
        "is_active",
    ]
    list_filter = [
        "status",
        "workpaper_type",
        "is_active",
        "created_at",
        "reviewed_at",
        "approved_at",
    ]
    search_fields = ["title", "description", "tags"]
    readonly_fields = [
        "file_size",
        "created_at",
        "updated_at",
        "reviewed_at",
        "approved_at",
    ]
    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "description", "workpaper_type", "version")},
        ),
        ("File/Link", {"fields": ("file", "file_size", "external_link")}),
        ("Metadata", {"fields": ("tags", "metadata"), "classes": ("collapse",)}),
        (
            "Workflow Status",
            {
                "fields": (
                    "status",
                    "uploaded_by",
                    "reviewer",
                    "reviewed_at",
                    "approver",
                    "approved_at",
                    "rejection_reason",
                )
            },
        ),
        ("Status", {"fields": ("is_active",)}),
        (
            "Audit Trail",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        """Make workflow fields readonly in admin"""
        readonly = list(self.readonly_fields)
        if obj:  # Editing existing object
            readonly.extend(
                ["uploaded_by", "reviewer", "approver", "reviewed_at", "approved_at"]
            )
        return readonly


@admin.register(WorkpaperApproval)
class WorkpaperApprovalAdmin(admin.ModelAdmin):
    """Admin interface for WorkpaperApproval model"""

    list_display = [
        "workpaper",
        "action",
        "action_by",
        "previous_status",
        "new_status",
        "created_at",
    ]
    list_filter = ["action", "created_at"]
    search_fields = ["workpaper__title", "comments"]
    readonly_fields = [
        "workpaper",
        "action",
        "action_by",
        "comments",
        "previous_status",
        "new_status",
        "created_at",
    ]

    def has_add_permission(self, request):
        """Disable manual creation of approval records"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deletion of approval records"""
        return False
