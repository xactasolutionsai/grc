"""
Management command to create demo checklists with sample audit programs
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from audits.models import (
    Checklist,
    ChecklistItem,
    AuditEngagement,
    ChecklistExecution,
    ChecklistItemResult,
)
from core.models import AppliedControl, RiskScenario
from iam.models import Folder


User = get_user_model()


class Command(BaseCommand):
    help = "Create demo checklists and executions for testing the audit module"

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-execution",
            action="store_true",
            help="Also create sample executions if engagements exist",
        )

    def handle(self, *args, **options):
        self.stdout.write("Creating demo checklists...")

        # Get or create first user
        admin = User.objects.first()
        if not admin:
            self.stdout.write(
                self.style.ERROR("No users found. Please create a user first.")
            )
            return

        # Get or create demo folder
        folder, created = Folder.objects.get_or_create(
            name="Demo Checklists",
            defaults={
                "content_type": Folder.ContentType.DOMAIN,
                "description": "Sample audit checklists for testing",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created folder: {folder.name}"))

        # Create SOC 2 Type II Checklist
        soc2, created = Checklist.objects.get_or_create(
            name="SOC 2 Type II - Access Controls",
            defaults={
                "description": "Standard test procedures for SOC 2 Trust Services Criteria - Access Controls",
                "folder": folder,
                "status": "active",
                "is_published": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created checklist: {soc2.name}"))

            # Add SOC 2 checklist items
            items = [
                {
                    "title": "Verify MFA is enforced for all administrative accounts",
                    "description": "Review system configuration to confirm multi-factor authentication is required for all users with administrative privileges. Test login process to verify MFA cannot be bypassed.",
                    "order": 1,
                },
                {
                    "title": "Review user access provisioning procedures",
                    "description": "Examine documented procedures for granting user access. Select a sample of new user accounts and verify proper authorization was obtained before access was granted.",
                    "order": 2,
                },
                {
                    "title": "Test user access de-provisioning process",
                    "description": "Select a sample of terminated users and verify their access was revoked within required timeframe (typically same day or within 24 hours). Check all systems including VPN, applications, and physical access.",
                    "order": 3,
                },
                {
                    "title": "Validate periodic access reviews are performed",
                    "description": "Obtain evidence of quarterly/annual access reviews. Verify management reviews and approves user access lists. Confirm inappropriate access was identified and removed.",
                    "order": 4,
                },
                {
                    "title": "Test password policy enforcement",
                    "description": "Review password policy configuration (complexity, length, expiration). Attempt to create passwords that violate policy to confirm controls are enforced technically.",
                    "order": 5,
                },
            ]

            for item_data in items:
                ChecklistItem.objects.create(checklist=soc2, **item_data)

            self.stdout.write(
                self.style.SUCCESS(f"  Added {len(items)} items to SOC 2 checklist")
            )

        # Create ISO 27001 Checklist
        iso27001, created = Checklist.objects.get_or_create(
            name="ISO 27001 - Information Security Controls",
            defaults={
                "description": "Key audit tests based on ISO/IEC 27001:2013 Annex A controls",
                "folder": folder,
                "status": "active",
                "is_published": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created checklist: {iso27001.name}"))

            # Add ISO 27001 checklist items
            items = [
                {
                    "title": "A.9.2.1 - User registration and de-registration",
                    "description": "Verify formal user registration and de-registration process exists and is documented. Test sample of users to confirm process is followed.",
                    "order": 1,
                },
                {
                    "title": "A.9.4.3 - Password management system",
                    "description": "Review password management system. Verify passwords are enforced to be strong, changed regularly, and stored using secure hashing.",
                    "order": 2,
                },
                {
                    "title": "A.12.3.1 - Information backup",
                    "description": "Examine backup procedures and schedules. Test backup restoration process. Verify backups are stored securely and tested regularly.",
                    "order": 3,
                },
                {
                    "title": "A.12.4.1 - Event logging",
                    "description": "Review system logging configuration. Verify security events, access attempts, and changes are logged. Test log retention meets requirements.",
                    "order": 4,
                },
                {
                    "title": "A.14.2.5 - Secure system engineering principles",
                    "description": "Review development standards and procedures. Verify secure coding practices are documented and followed. Test security is considered in system design.",
                    "order": 5,
                },
            ]

            for item_data in items:
                ChecklistItem.objects.create(checklist=iso27001, **item_data)

            self.stdout.write(
                self.style.SUCCESS(f"  Added {len(items)} items to ISO 27001 checklist")
            )

        # Create GDPR Compliance Checklist
        gdpr, created = Checklist.objects.get_or_create(
            name="GDPR Compliance Testing",
            defaults={
                "description": "Audit procedures for General Data Protection Regulation compliance",
                "folder": folder,
                "status": "active",
                "is_published": True,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created checklist: {gdpr.name}"))

            # Add GDPR checklist items
            items = [
                {
                    "title": "Verify data processing inventory is maintained",
                    "description": "Review Records of Processing Activities (ROPA). Verify all personal data processing is documented including purpose, data types, retention periods.",
                    "order": 1,
                },
                {
                    "title": "Test data subject rights procedures",
                    "description": "Review procedures for handling data subject access requests (DSAR). Test response times meet regulatory requirements (typically 30 days). Verify identity verification process.",
                    "order": 2,
                },
                {
                    "title": "Validate consent management",
                    "description": "Review consent collection mechanisms. Verify consent is freely given, specific, informed, and unambiguous. Test withdrawal of consent functionality.",
                    "order": 3,
                },
                {
                    "title": "Review data breach notification procedures",
                    "description": "Examine incident response plan specific to data breaches. Verify notification procedures to supervisory authority and data subjects are documented and tested.",
                    "order": 4,
                },
            ]

            for item_data in items:
                ChecklistItem.objects.create(checklist=gdpr, **item_data)

            self.stdout.write(
                self.style.SUCCESS(f"  Added {len(items)} items to GDPR checklist")
            )

        # Create sample executions if requested
        if options["with_execution"]:
            engagement = AuditEngagement.objects.first()
            if engagement:
                self.stdout.write("Creating sample execution...")

                execution, created = ChecklistExecution.objects.get_or_create(
                    checklist=soc2,
                    audit_engagement=engagement,
                    defaults={
                        "status": "in_progress",
                        "started_by": admin,
                        "started_at": timezone.now(),
                        "notes": "Sample execution created by management command",
                    },
                )

                if created:
                    # Create result records for each item
                    checklist_items = soc2.items.all()
                    execution.total_items = checklist_items.count()
                    execution.save()

                    results = []
                    for idx, item in enumerate(checklist_items):
                        # Mark first 2 items as pass, 1 as fail, rest not tested
                        if idx == 0:
                            result = ChecklistItemResult(
                                execution=execution,
                                checklist_item=item,
                                result="pass",
                                comments="MFA verified across all admin accounts. Tested with sample logins.",
                                tested_by=admin,
                                tested_at=timezone.now(),
                            )
                        elif idx == 1:
                            result = ChecklistItemResult(
                                execution=execution,
                                checklist_item=item,
                                result="pass",
                                comments="Provisioning procedures are documented and followed. Sampled 5 new users, all had proper authorization.",
                                tested_by=admin,
                                tested_at=timezone.now(),
                            )
                        elif idx == 2:
                            result = ChecklistItemResult(
                                execution=execution,
                                checklist_item=item,
                                result="fail",
                                comments="Found 2 terminated users with access not revoked within 24 hours. Delays ranged from 48-72 hours.",
                                finding_summary="De-provisioning not timely for 2/10 sampled users",
                                tested_by=admin,
                                tested_at=timezone.now(),
                            )
                        else:
                            result = ChecklistItemResult(
                                execution=execution,
                                checklist_item=item,
                                result="not_tested",
                            )
                        results.append(result)

                    ChecklistItemResult.objects.bulk_create(results)

                    # Update completion count
                    execution.completed_items = execution.item_results.exclude(
                        result="not_tested"
                    ).count()
                    execution.save()

                    self.stdout.write(
                        self.style.SUCCESS(f"Created sample execution: {execution}")
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "No audit engagements found. Skipping execution creation."
                    )
                )

        # Summary
        total_checklists = Checklist.objects.filter(folder=folder).count()
        total_items = ChecklistItem.objects.filter(checklist__folder=folder).count()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("✅ Demo data creation complete!"))
        self.stdout.write(f"  📋 Total checklists: {total_checklists}")
        self.stdout.write(f"  📝 Total checklist items: {total_items}")

        if options["with_execution"]:
            total_executions = ChecklistExecution.objects.count()
            self.stdout.write(f"  🔄 Total executions: {total_executions}")
