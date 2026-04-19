from rest_framework import serializers
from .models import Workpaper, WorkpaperApproval
from django.contrib.auth import get_user_model

User = get_user_model()


class WorkpaperSerializer(serializers.ModelSerializer):
    """
    Serializer for Workpaper model with full validation and display fields.
    """
    
    # Read-only fields
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    file_size = serializers.IntegerField(read_only=True)
    
    # Display fields for related users
    uploaded_by_display = serializers.SerializerMethodField()
    reviewer_display = serializers.SerializerMethodField()
    approver_display = serializers.SerializerMethodField()
    
    # File information
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_extension = serializers.SerializerMethodField()
    
    # Workflow status checks
    can_be_reviewed = serializers.SerializerMethodField()
    can_be_approved = serializers.SerializerMethodField()
    
    class Meta:
        model = Workpaper
        fields = [
            'id',
            'title',
            'description',
            'workpaper_type',
            'file',
            'file_size',
            'file_url',
            'file_name',
            'file_extension',
            'external_link',
            'tags',
            'metadata',
            'status',
            'uploaded_by',
            'uploaded_by_display',
            'reviewer',
            'reviewer_display',
            'reviewed_at',
            'approver',
            'approver_display',
            'approved_at',
            'rejection_reason',
            'version',
            'is_active',
            'can_be_reviewed',
            'can_be_approved',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'file_size',
            'uploaded_by',
            'uploaded_by_display',
            'reviewer',
            'reviewer_display',
            'reviewed_at',
            'approver',
            'approver_display',
            'approved_at',
            'file_url',
            'file_name',
            'file_extension',
            'can_be_reviewed',
            'can_be_approved',
            'created_at',
            'updated_at',
        ]
    
    def get_uploaded_by_display(self, obj):
        """Get uploaded by user display name"""
        if obj.uploaded_by:
            full_name = obj.uploaded_by.get_full_name()
            display_name = full_name if full_name and full_name.strip() else obj.uploaded_by.email
            return {
                'id': obj.uploaded_by.id,
                'email': obj.uploaded_by.email,
                'name': display_name
            }
        return None
    
    def get_reviewer_display(self, obj):
        """Get reviewer user display name"""
        if obj.reviewer:
            full_name = obj.reviewer.get_full_name()
            display_name = full_name if full_name and full_name.strip() else obj.reviewer.email
            return {
                'id': obj.reviewer.id,
                'email': obj.reviewer.email,
                'name': display_name
            }
        return None
    
    def get_approver_display(self, obj):
        """Get approver user display name"""
        if obj.approver:
            full_name = obj.approver.get_full_name()
            display_name = full_name if full_name and full_name.strip() else obj.approver.email
            return {
                'id': obj.approver.id,
                'email': obj.approver.email,
                'name': display_name
            }
        return None
    
    def get_file_url(self, obj):
        """Get file URL if file exists"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None
    
    def get_file_name(self, obj):
        """Get file name"""
        return obj.get_file_name()
    
    def get_file_extension(self, obj):
        """Get file extension"""
        return obj.get_file_extension()
    
    def get_can_be_reviewed(self, obj):
        """Check if workpaper can be reviewed"""
        return obj.can_be_reviewed()
    
    def get_can_be_approved(self, obj):
        """Check if workpaper can be approved"""
        return obj.can_be_approved()
    
    def validate_title(self, value):
        """Validate title is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Title is required and cannot be empty")
        return value.strip()
    
    def validate_workpaper_type(self, value):
        """Validate workpaper_type is valid choice"""
        valid_choices = [choice[0] for choice in Workpaper.WORKPAPER_TYPE_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Workpaper type must be one of: {', '.join(valid_choices)}"
            )
        return value
    
    def validate_status(self, value):
        """Validate status is valid choice"""
        valid_choices = [choice[0] for choice in Workpaper.STATUS_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(valid_choices)}"
            )
        return value
    
    def validate(self, data):
        """Validate the entire data set"""
        # Ensure either file or external_link is provided (but not required for update)
        file = data.get('file')
        external_link = data.get('external_link', '')
        workpaper_type = data.get('workpaper_type', self.instance.workpaper_type if self.instance else None)
        
        # For link type, external_link should be provided
        if workpaper_type == 'link' and not external_link:
            if not self.instance or not self.instance.external_link:
                raise serializers.ValidationError(
                    "External link is required for workpaper type 'link'"
                )
        
        return data
    
    def create(self, validated_data):
        """Create workpaper with uploaded_by set to current user"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['uploaded_by'] = request.user
        return super().create(validated_data)


class WorkpaperApprovalSerializer(serializers.ModelSerializer):
    """
    Serializer for WorkpaperApproval model (approval history).
    """
    
    action_by_display = serializers.SerializerMethodField()
    workpaper_title = serializers.CharField(source='workpaper.title', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = WorkpaperApproval
        fields = [
            'id',
            'workpaper',
            'workpaper_title',
            'action',
            'action_display',
            'action_by',
            'action_by_display',
            'comments',
            'previous_status',
            'new_status',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'workpaper',
            'workpaper_title',
            'action',
            'action_display',
            'action_by',
            'action_by_display',
            'comments',
            'previous_status',
            'new_status',
            'created_at',
        ]
    
    def get_action_by_display(self, obj):
        """Get action_by user display name"""
        if obj.action_by:
            full_name = obj.action_by.get_full_name()
            display_name = full_name if full_name and full_name.strip() else obj.action_by.email
            return {
                'id': obj.action_by.id,
                'email': obj.action_by.email,
                'name': display_name
            }
        return None


class WorkpaperActionSerializer(serializers.Serializer):
    """
    Serializer for workpaper workflow actions.
    """
    
    action = serializers.ChoiceField(
        choices=['submit_for_review', 'review', 'approve', 'reject'],
        help_text="Action to perform on the workpaper"
    )
    comments = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Comments or notes about the action"
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Reason for rejection (required for reject action)"
    )
    
    def validate_action(self, value):
        """Validate action is valid"""
        valid_actions = ['submit_for_review', 'review', 'approve', 'reject']
        if value not in valid_actions:
            raise serializers.ValidationError(
                f"Action must be one of: {', '.join(valid_actions)}"
            )
        return value
    
    def validate(self, data):
        """Validate the entire data set"""
        action = data.get('action')
        reason = data.get('reason', '').strip()
        
        # For reject action, reason is required
        if action == 'reject' and not reason:
            raise serializers.ValidationError({
                'reason': 'Reason is required for reject action'
            })
        
        return data

