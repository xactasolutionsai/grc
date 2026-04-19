"""
Management command to fix user relationships in existing workpapers.
Usage: poetry run python manage.py fix_workpaper_users
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from workpapers.models import Workpaper, WorkpaperApproval

User = get_user_model()


class Command(BaseCommand):
    help = 'Fix user relationships in existing workpapers that were created without proper user tracking'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-email',
            type=str,
            help='Email of the user to set as the default owner for workpapers without uploaded_by',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        user_email = options.get('user_email')
        
        # Find a default user
        default_user = None
        if user_email:
            try:
                default_user = User.objects.get(email=user_email)
                self.stdout.write(f"Using user: {default_user.email}")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User with email '{user_email}' not found"))
                return
        else:
            # Try to get the first superuser, then any user
            default_user = User.objects.filter(is_superuser=True).first()
            if not default_user:
                default_user = User.objects.first()
            
            if not default_user:
                self.stdout.write(self.style.ERROR("No users found in the system"))
                return
                
            self.stdout.write(f"Using default user: {default_user.email}")
        
        # Fix workpapers without uploaded_by
        workpapers_without_owner = Workpaper.objects.filter(uploaded_by__isnull=True)
        count = workpapers_without_owner.count()
        
        if count > 0:
            self.stdout.write(f"\nFound {count} workpaper(s) without uploaded_by")
            
            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
                for wp in workpapers_without_owner:
                    self.stdout.write(f"  - Would set uploaded_by for: {wp.title} (ID: {wp.id})")
            else:
                updated = workpapers_without_owner.update(uploaded_by=default_user)
                self.stdout.write(self.style.SUCCESS(f"✓ Updated {updated} workpaper(s) with uploaded_by"))
        else:
            self.stdout.write(self.style.SUCCESS("✓ All workpapers have uploaded_by set"))
        
        # Fix approval history without action_by
        approvals_without_user = WorkpaperApproval.objects.filter(action_by__isnull=True)
        count = approvals_without_user.count()
        
        if count > 0:
            self.stdout.write(f"\nFound {count} approval record(s) without action_by")
            
            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
                for approval in approvals_without_user:
                    self.stdout.write(f"  - Would set action_by for: {approval.workpaper.title} - {approval.action} (ID: {approval.id})")
            else:
                updated = approvals_without_user.update(action_by=default_user)
                self.stdout.write(self.style.SUCCESS(f"✓ Updated {updated} approval record(s) with action_by"))
        else:
            self.stdout.write(self.style.SUCCESS("✓ All approval records have action_by set"))
        
        # Fix workpapers with 'reviewed' status but no reviewer
        reviewed_without_reviewer = Workpaper.objects.filter(status='reviewed', reviewer__isnull=True)
        count = reviewed_without_reviewer.count()
        
        if count > 0:
            self.stdout.write(f"\nFound {count} reviewed workpaper(s) without reviewer")
            
            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
                for wp in reviewed_without_reviewer:
                    self.stdout.write(f"  - Would set reviewer for: {wp.title} (ID: {wp.id})")
            else:
                updated = reviewed_without_reviewer.update(reviewer=default_user)
                self.stdout.write(self.style.SUCCESS(f"✓ Updated {updated} workpaper(s) with reviewer"))
        else:
            self.stdout.write(self.style.SUCCESS("✓ All reviewed workpapers have reviewer set"))
        
        # Fix workpapers with 'approved' status but no approver
        approved_without_approver = Workpaper.objects.filter(status='approved', approver__isnull=True)
        count = approved_without_approver.count()
        
        if count > 0:
            self.stdout.write(f"\nFound {count} approved workpaper(s) without approver")
            
            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
                for wp in approved_without_approver:
                    self.stdout.write(f"  - Would set approver for: {wp.title} (ID: {wp.id})")
            else:
                updated = approved_without_approver.update(approver=default_user)
                self.stdout.write(self.style.SUCCESS(f"✓ Updated {updated} workpaper(s) with approver"))
        else:
            self.stdout.write(self.style.SUCCESS("✓ All approved workpapers have approver set"))
        
        self.stdout.write("\n" + self.style.SUCCESS("✓ Fix complete!"))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\nThis was a DRY RUN. Run without --dry-run to apply changes."))

