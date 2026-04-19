from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from audits.models import AuditEngagement
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Create fake timeline data for existing audit engagements"

    def add_arguments(self, parser):
        parser.add_argument(
            "--engagement-id",
            type=int,
            help="Specific engagement ID to update (optional)",
        )

    def handle(self, *args, **options):
        engagement_id = options.get("engagement_id")

        if engagement_id:
            engagements = AuditEngagement.objects.filter(id=engagement_id)
        else:
            engagements = AuditEngagement.objects.all()

        if not engagements.exists():
            self.stdout.write(self.style.ERROR("No engagements found."))
            return

        updated_count = 0

        for engagement in engagements:
            self.stdout.write(f"Updating timeline for: {engagement.title}")

            # Update engagement with realistic timeline data based on status
            self.update_engagement_timeline(engagement)
            updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated timeline for {updated_count} engagements!"
            )
        )

    def update_engagement_timeline(self, engagement):
        """Update engagement with realistic timeline data"""
        now = timezone.now()
        created_date = engagement.created_at

        # Set actual start date if engagement is in progress or beyond
        if engagement.status in [
            "in_progress",
            "fieldwork",
            "review",
            "submitted",
            "closed",
        ]:
            if not engagement.actual_start_date:
                # Start 1-5 days after creation
                days_after_creation = random.randint(1, 5)
                engagement.actual_start_date = created_date.date() + timedelta(
                    days=days_after_creation
                )

        # Set results submitted date if engagement is submitted or closed
        if engagement.status in ["submitted", "closed"]:
            if not engagement.results_submitted_at:
                # Submit results 10-30 days after start
                if engagement.actual_start_date:
                    days_after_start = random.randint(10, 30)
                    submit_date = engagement.actual_start_date + timedelta(
                        days=days_after_start
                    )
                    engagement.results_submitted_at = timezone.make_aware(
                        submit_date.replace(hour=14, minute=0, second=0, microsecond=0)
                    )
                    # Set submitted by user
                    if not engagement.results_submitted_by:
                        engagement.results_submitted_by = (
                            engagement.assigned_auditor or engagement.created_by
                        )

        # Set closed date if engagement is closed
        if engagement.status == "closed":
            if not engagement.closed_at:
                # Close 1-7 days after submission
                if engagement.results_submitted_at:
                    days_after_submit = random.randint(1, 7)
                    close_date = engagement.results_submitted_at.date() + timedelta(
                        days=days_after_submit
                    )
                    engagement.closed_at = timezone.make_aware(
                        close_date.replace(hour=16, minute=0, second=0, microsecond=0)
                    )
                    # Set closed by user
                    if not engagement.closed_by:
                        engagement.closed_by = (
                            engagement.engagement_lead
                            or engagement.assigned_auditor
                            or engagement.created_by
                        )

        # Update progress percentage based on status
        if engagement.status == "draft":
            engagement.progress_percentage = 0
        elif engagement.status == "in_progress":
            engagement.progress_percentage = random.randint(10, 30)
        elif engagement.status == "fieldwork":
            engagement.progress_percentage = random.randint(40, 70)
        elif engagement.status == "review":
            engagement.progress_percentage = random.randint(70, 90)
        elif engagement.status == "submitted":
            engagement.progress_percentage = 95
        elif engagement.status == "closed":
            engagement.progress_percentage = 100

        # Add some realistic fieldwork notes for fieldwork status
        if engagement.status == "fieldwork" and not engagement.fieldwork_notes:
            fieldwork_notes_templates = [
                "Initial fieldwork has begun. Documenting current processes and controls.",
                "Conducting interviews with key personnel. Gathering evidence and documentation.",
                "Testing controls and procedures. Identifying potential gaps and areas for improvement.",
                "Fieldwork in progress. Reviewing documentation and conducting walkthroughs.",
                "Performing detailed testing of identified controls and processes.",
            ]
            engagement.fieldwork_notes = random.choice(fieldwork_notes_templates)

        # Add findings summary for submitted/closed engagements
        if (
            engagement.status in ["submitted", "closed"]
            and not engagement.findings_summary
        ):
            findings_templates = [
                "Minor control deficiencies identified. Recommendations provided for improvement.",
                "Several areas of non-compliance found. Management has been notified of required actions.",
                "Overall control environment is adequate with some areas requiring attention.",
                "Significant findings identified requiring immediate management attention.",
                "Control testing completed with satisfactory results overall.",
            ]
            engagement.findings_summary = random.choice(findings_templates)

        # Add recommendations for submitted/closed engagements
        if (
            engagement.status in ["submitted", "closed"]
            and not engagement.recommendations
        ):
            recommendations_templates = [
                "Implement additional monitoring controls to strengthen the control environment.",
                "Update policies and procedures to address identified gaps.",
                "Provide additional training to staff on control requirements.",
                "Establish regular review processes to ensure ongoing compliance.",
                "Consider implementing automated controls to reduce manual error risk.",
            ]
            engagement.recommendations = random.choice(recommendations_templates)

        # Add closure notes for closed engagements
        if engagement.status == "closed" and not engagement.closure_notes:
            closure_templates = [
                "Engagement completed successfully. All findings have been addressed by management.",
                "Audit closed with satisfactory results. Follow-up actions scheduled.",
                "Engagement concluded. Management has implemented all recommended improvements.",
                "Audit completed on schedule. No significant issues remaining.",
                "Engagement closed successfully. All audit objectives achieved.",
            ]
            engagement.closure_notes = random.choice(closure_templates)

        # Update actual hours based on status
        if engagement.status in [
            "in_progress",
            "fieldwork",
            "review",
            "submitted",
            "closed",
        ]:
            if not engagement.actual_hours or engagement.actual_hours == 0:
                # Calculate actual hours based on status and estimated hours
                base_hours = engagement.estimated_hours or 40
                if engagement.status == "in_progress":
                    engagement.actual_hours = int(base_hours * random.uniform(0.1, 0.3))
                elif engagement.status == "fieldwork":
                    engagement.actual_hours = int(base_hours * random.uniform(0.4, 0.7))
                elif engagement.status == "review":
                    engagement.actual_hours = int(base_hours * random.uniform(0.7, 0.9))
                elif engagement.status in ["submitted", "closed"]:
                    engagement.actual_hours = int(base_hours * random.uniform(0.9, 1.2))

        # Update actual cost based on actual hours
        if engagement.actual_hours and not engagement.actual_cost:
            hourly_rate = random.uniform(75, 150)  # $75-$150 per hour
            engagement.actual_cost = round(engagement.actual_hours * hourly_rate, 2)

        # Save the updated engagement
        engagement.save()

        self.stdout.write(f"  - Status: {engagement.status}")
        self.stdout.write(f"  - Progress: {engagement.progress_percentage}%")
        self.stdout.write(f"  - Actual Hours: {engagement.actual_hours}")
        self.stdout.write(f"  - Actual Cost: ${engagement.actual_cost}")
        if engagement.actual_start_date:
            self.stdout.write(f"  - Started: {engagement.actual_start_date}")
        if engagement.results_submitted_at:
            self.stdout.write(f"  - Submitted: {engagement.results_submitted_at}")
        if engagement.closed_at:
            self.stdout.write(f"  - Closed: {engagement.closed_at}")
