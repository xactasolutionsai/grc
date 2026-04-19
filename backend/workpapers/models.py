from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import os

User = settings.AUTH_USER_MODEL


class Workpaper(models.Model):
    """
    Represents a workpaper or evidence document with file attachment support
    and approval workflow.
    
    Workflow states: collected → reviewed → approved
    
    Future integration points:
    - Can be linked to AuditEngagement (when ready)
    - Can be linked to Test/Finding records (when created)
    """
    
    WORKPAPER_TYPE_CHOICES = [
        ('excel', 'Excel Spreadsheet'),
        ('word', 'Word Document'),
        ('pdf', 'PDF Document'),
        ('image', 'Image'),
        ('link', 'External Link'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('collected', 'Collected'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=255, help_text="Title of the workpaper")
    description = models.TextField(blank=True, help_text="Detailed description of the workpaper")
    workpaper_type = models.CharField(
        max_length=20,
        choices=WORKPAPER_TYPE_CHOICES,
        default='other',
        help_text="Type of workpaper"
    )
    
    # File or Link
    file = models.FileField(
        upload_to='workpapers/%Y/%m/%d/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(
            allowed_extensions=['xlsx', 'xls', 'doc', 'docx', 'pdf', 'jpg', 'jpeg', 'png', 'gif', 'txt', 'csv']
        )],
        help_text="Upload file (Excel, Word, PDF, images, etc.)"
    )
    file_size = models.BigIntegerField(null=True, blank=True, help_text="File size in bytes")
    external_link = models.URLField(
        blank=True,
        max_length=500,
        help_text="External link as alternative to file upload"
    )
    
    # Metadata
    tags = models.JSONField(
        blank=True,
        null=True,
        help_text="Tags for categorization (JSON array)"
    )
    metadata = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional metadata about the file"
    )
    
    # Workflow Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='collected',
        help_text="Current workflow status"
    )
    
    # Workflow Users
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_workpapers',
        help_text="User who uploaded this workpaper"
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_workpapers',
        help_text="User who reviewed this workpaper"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp of review")
    
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_workpapers',
        help_text="User who approved this workpaper"
    )
    approved_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp of approval")
    
    # Rejection Info
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection (if applicable)"
    )
    
    # Version Control
    version = models.IntegerField(default=1, help_text="Version number of this workpaper")
    
    # Status
    is_active = models.BooleanField(default=True, help_text="Whether this workpaper is active")
    
    # Audit Trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Workpaper'
        verbose_name_plural = 'Workpapers'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['workpaper_type']),
            models.Index(fields=['uploaded_by']),
            models.Index(fields=['reviewer']),
            models.Index(fields=['approver']),
            models.Index(fields=['created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Override save to calculate file size"""
        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
            except Exception:
                pass
        super().save(*args, **kwargs)
    
    def submit_for_review(self, user):
        """
        Mark workpaper as ready for review.
        Status: collected → reviewed
        """
        if self.status == 'collected':
            self.status = 'reviewed'
            self.reviewer = user
            self.reviewed_at = timezone.now()
            self.save()
            
            # Create approval history record
            WorkpaperApproval.objects.create(
                workpaper=self,
                action='reviewed',
                action_by=user,
                previous_status='collected',
                new_status='reviewed'
            )
            return True
        return False
    
    def approve(self, user, comments=""):
        """
        Approve the workpaper.
        Status: reviewed → approved
        """
        if self.status == 'reviewed':
            previous_status = self.status
            self.status = 'approved'
            self.approver = user
            self.approved_at = timezone.now()
            self.rejection_reason = ""  # Clear any previous rejection reason
            self.save()
            
            # Create approval history record
            WorkpaperApproval.objects.create(
                workpaper=self,
                action='approved',
                action_by=user,
                comments=comments,
                previous_status=previous_status,
                new_status='approved'
            )
            return True
        return False
    
    def reject(self, user, reason=""):
        """
        Reject the workpaper.
        Status remains unchanged, but adds rejection reason.
        """
        previous_status = self.status
        self.rejection_reason = reason
        self.save()
        
        # Create approval history record
        WorkpaperApproval.objects.create(
            workpaper=self,
            action='rejected',
            action_by=user,
            comments=reason,
            previous_status=previous_status,
            new_status=previous_status
        )
        return True
    
    def can_be_reviewed(self):
        """Check if workpaper can be reviewed"""
        return self.status == 'collected'
    
    def can_be_approved(self):
        """Check if workpaper can be approved"""
        return self.status == 'reviewed'
    
    def get_file_extension(self):
        """Get file extension if file exists"""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return None
    
    def get_file_name(self):
        """Get file name without path"""
        if self.file:
            return os.path.basename(self.file.name)
        return None


class WorkpaperApproval(models.Model):
    """
    Records the approval workflow history for workpapers.
    Tracks all status changes and actions performed on a workpaper.
    """
    
    ACTION_CHOICES = [
        ('submit_for_review', 'Submitted for Review'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    workpaper = models.ForeignKey(
        'Workpaper',
        on_delete=models.CASCADE,
        related_name='approval_history',
        help_text="Associated workpaper"
    )
    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        help_text="Action performed"
    )
    action_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text="User who performed the action"
    )
    comments = models.TextField(
        blank=True,
        help_text="Comments or notes about the action"
    )
    previous_status = models.CharField(
        max_length=20,
        help_text="Status before the action"
    )
    new_status = models.CharField(
        max_length=20,
        help_text="Status after the action"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Workpaper Approval History'
        verbose_name_plural = 'Workpaper Approval History'
        indexes = [
            models.Index(fields=['workpaper', 'created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['action_by']),
        ]
    
    def __str__(self):
        return f"{self.workpaper.title} - {self.get_action_display()} by {self.action_by}"

