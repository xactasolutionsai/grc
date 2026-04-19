from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from audits.models import AuditEntity, AuditPlan, AuditEngagement
from datetime import date, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Create demo audit engagements with realistic data and workflow states"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing audit engagements before creating demo data",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing audit engagements...")
            AuditEngagement.objects.all().delete()

        # Get existing data
        users = self.get_or_create_demo_users()
        audit_plans = self.get_audit_plans()
        audit_entities = self.get_audit_entities()

        if not audit_plans:
            self.stdout.write(
                self.style.ERROR(
                    "No audit plans found. Please create audit plans first."
                )
            )
            return

        if not audit_entities:
            self.stdout.write(
                self.style.ERROR(
                    "No audit entities found. Please create audit entities first."
                )
            )
            return

        # Create demo audit engagements
        self.create_demo_engagements(users, audit_plans, audit_entities)

        self.stdout.write(
            self.style.SUCCESS("Successfully created demo audit engagements!")
        )

    def get_or_create_demo_users(self):
        """Get or create demo users for audit engagements"""
        users = []

        # Create some demo users if they don't exist
        demo_users = [
            {
                "email": "auditor1@company.com",
                "first_name": "Alice",
                "last_name": "Auditor",
            },
            {
                "email": "auditor2@company.com",
                "first_name": "Bob",
                "last_name": "Smith",
            },
            {
                "email": "auditor3@company.com",
                "first_name": "Carol",
                "last_name": "Johnson",
            },
            {
                "email": "audit.manager@company.com",
                "first_name": "David",
                "last_name": "Manager",
            },
            {
                "email": "senior.auditor@company.com",
                "first_name": "Eva",
                "last_name": "Wilson",
            },
        ]

        for user_data in demo_users:
            user, created = User.objects.get_or_create(
                email=user_data["email"], defaults=user_data
            )
            users.append(user)
            if created:
                self.stdout.write(f"Created user: {user.email}")

        return users

    def get_audit_plans(self):
        """Get existing audit plans"""
        return list(AuditPlan.objects.all()[:5])  # Get up to 5 plans

    def get_audit_entities(self):
        """Get existing audit entities"""
        return list(
            AuditEntity.objects.filter(is_active=True)[:10]
        )  # Get up to 10 active entities

    def create_demo_engagements(self, users, audit_plans, audit_entities):
        """Create demo audit engagements with various statuses and scenarios"""

        # Define engagement templates with realistic scenarios
        engagement_templates = [
            {
                "title": "Q1 2024 Financial Controls Audit",
                "description": "Comprehensive audit of financial reporting controls and SOX compliance for Q1 2024",
                "status": "in_progress",
                "priority": "high",
                "scope": "Financial reporting processes, internal controls, and SOX compliance requirements",
                "objectives": "Assess effectiveness of financial controls, identify control gaps, ensure SOX compliance",
                "methodology": "Risk-based audit approach with walkthroughs, testing, and documentation review",
                "progress_percentage": 65,
                "fieldwork_notes": "Completed walkthroughs of revenue recognition and expense processing. Currently testing journal entry controls.",
                "estimated_hours": 120,
                "actual_hours": 78,
                "budget_allocated": 15000,
                "actual_cost": 9750,
                "tags": ["SOX", "Financial", "Q1-2024", "Controls"],
            },
            {
                "title": "IT Security Infrastructure Assessment",
                "description": "Annual security assessment of IT infrastructure, systems, and security controls",
                "status": "fieldwork",
                "priority": "critical",
                "scope": "Network security, endpoint protection, access controls, and security monitoring",
                "objectives": "Evaluate security posture, identify vulnerabilities, assess compliance with security policies",
                "methodology": "Penetration testing, vulnerability assessment, and security control testing",
                "progress_percentage": 85,
                "fieldwork_notes": "Completed network scanning and vulnerability assessment. Currently conducting penetration testing of critical systems.",
                "estimated_hours": 200,
                "actual_hours": 170,
                "budget_allocated": 25000,
                "actual_cost": 21250,
                "tags": ["Security", "IT", "Infrastructure", "Penetration-Testing"],
            },
            {
                "title": "HR Data Privacy Compliance Review",
                "description": "Review of HR data processing activities and GDPR compliance",
                "status": "submitted",
                "priority": "medium",
                "scope": "Employee data collection, processing, storage, and retention practices",
                "objectives": "Ensure GDPR compliance, assess data protection measures, review consent management",
                "methodology": "Documentation review, interviews, and data flow analysis",
                "progress_percentage": 100,
                "fieldwork_notes": "Completed all fieldwork activities. Identified minor gaps in consent management process.",
                "findings_summary": "Overall good compliance posture with minor improvements needed in consent tracking",
                "recommendations": "Implement automated consent tracking system and update privacy notices",
                "estimated_hours": 80,
                "actual_hours": 85,
                "budget_allocated": 10000,
                "actual_cost": 10625,
                "tags": ["GDPR", "Privacy", "HR", "Data-Protection"],
            },
            {
                "title": "Vendor Risk Assessment - Critical Suppliers",
                "description": "Risk assessment of critical third-party vendors and suppliers",
                "status": "draft",
                "priority": "high",
                "scope": "Critical vendor security controls, data handling practices, and business continuity",
                "objectives": "Assess vendor security posture, evaluate data protection measures, review business continuity plans",
                "methodology": "Vendor questionnaires, on-site assessments, and documentation review",
                "progress_percentage": 0,
                "estimated_hours": 150,
                "budget_allocated": 18000,
                "tags": ["Vendor", "Risk", "Third-Party", "Security"],
            },
            {
                "title": "Operational Process Efficiency Review",
                "description": "Review of operational processes for efficiency and compliance with ISO 9001",
                "status": "review",
                "priority": "medium",
                "scope": "Core operational processes, quality management, and continuous improvement",
                "objectives": "Assess process efficiency, identify improvement opportunities, ensure ISO 9001 compliance",
                "methodology": "Process mapping, interviews, and performance data analysis",
                "progress_percentage": 90,
                "fieldwork_notes": "Completed process mapping and data collection. Currently analyzing performance metrics.",
                "estimated_hours": 100,
                "actual_hours": 90,
                "budget_allocated": 12000,
                "actual_cost": 10800,
                "tags": ["Operations", "ISO9001", "Efficiency", "Process"],
            },
            {
                "title": "Cybersecurity Incident Response Audit",
                "description": "Post-incident audit of cybersecurity incident response procedures and effectiveness",
                "status": "closed",
                "priority": "critical",
                "scope": "Incident response procedures, communication protocols, and recovery processes",
                "objectives": "Evaluate incident response effectiveness, identify lessons learned, improve procedures",
                "methodology": "Incident analysis, procedure review, and stakeholder interviews",
                "progress_percentage": 100,
                "fieldwork_notes": "Completed comprehensive review of recent security incident response.",
                "findings_summary": "Response was effective but communication could be improved",
                "recommendations": "Update communication protocols and conduct additional training",
                "estimated_hours": 60,
                "actual_hours": 65,
                "budget_allocated": 8000,
                "actual_cost": 8667,
                "tags": [
                    "Security",
                    "Incident-Response",
                    "Cybersecurity",
                    "Post-Incident",
                ],
            },
            {
                "title": "Regulatory Compliance Assessment",
                "description": "Comprehensive assessment of regulatory compliance across multiple frameworks",
                "status": "in_progress",
                "priority": "high",
                "scope": "SOX, GDPR, ISO 27001, and industry-specific regulations",
                "objectives": "Ensure comprehensive regulatory compliance, identify gaps, prioritize remediation",
                "methodology": "Framework mapping, control testing, and gap analysis",
                "progress_percentage": 40,
                "fieldwork_notes": "Completed framework mapping. Currently testing SOX controls.",
                "estimated_hours": 300,
                "actual_hours": 120,
                "budget_allocated": 35000,
                "actual_cost": 14000,
                "tags": ["Compliance", "SOX", "GDPR", "ISO27001", "Regulatory"],
            },
            {
                "title": "Business Continuity Plan Validation",
                "description": "Testing and validation of business continuity and disaster recovery plans",
                "status": "draft",
                "priority": "medium",
                "scope": "BCP procedures, DR testing, and recovery time objectives",
                "objectives": "Validate BCP effectiveness, test recovery procedures, ensure RTO/RPO compliance",
                "methodology": "Tabletop exercises, DR testing, and procedure validation",
                "progress_percentage": 0,
                "estimated_hours": 120,
                "budget_allocated": 15000,
                "tags": ["BCP", "DR", "Business-Continuity", "Testing"],
            },
        ]

        # Create engagements
        created_engagements = []
        for i, template in enumerate(engagement_templates):
            # Select random plan and entity
            audit_plan = random.choice(audit_plans) if audit_plans else None
            entity = random.choice(audit_entities) if audit_entities else None

            # Select users for different roles
            assigned_auditor = random.choice(users)
            engagement_lead = random.choice([u for u in users if u != assigned_auditor])
            created_by = random.choice(users)

            # Calculate dates based on status
            planned_start = date.today() - timedelta(days=random.randint(30, 90))
            planned_end = planned_start + timedelta(days=random.randint(14, 60))

            actual_start = None
            actual_end = None
            results_submitted_at = None
            closed_at = None

            if template["status"] in [
                "in_progress",
                "fieldwork",
                "review",
                "submitted",
                "closed",
            ]:
                actual_start = planned_start + timedelta(days=random.randint(0, 5))

            if template["status"] in ["submitted", "closed"]:
                results_submitted_at = (
                    timezone.make_aware(
                        (actual_start + timedelta(days=random.randint(10, 30))).replace(
                            hour=14, minute=0, second=0, microsecond=0
                        )
                    )
                    if actual_start
                    else None
                )
                results_submitted_by = random.choice(users)
            else:
                results_submitted_by = None

            if template["status"] == "closed":
                closed_at = (
                    timezone.make_aware(
                        (
                            results_submitted_at.date()
                            + timedelta(days=random.randint(1, 7))
                        ).replace(hour=16, minute=0, second=0, microsecond=0)
                    )
                    if results_submitted_at
                    else None
                )
                closed_by = random.choice(users)
            else:
                closed_by = None

            engagement_data = {
                "title": template["title"],
                "description": template["description"],
                "audit_plan": audit_plan,
                "entity": entity,
                "status": template["status"],
                "priority": template["priority"],
                "assigned_auditor": assigned_auditor,
                "engagement_lead": engagement_lead,
                "created_by": created_by,
                "planned_start_date": planned_start,
                "planned_end_date": planned_end,
                "actual_start_date": actual_start,
                "actual_end_date": actual_end,
                "scope": template["scope"],
                "objectives": template["objectives"],
                "methodology": template["methodology"],
                "progress_percentage": template["progress_percentage"],
                "fieldwork_notes": template.get("fieldwork_notes", ""),
                "findings_summary": template.get("findings_summary", ""),
                "recommendations": template.get("recommendations", ""),
                "results_submitted_at": results_submitted_at,
                "results_submitted_by": results_submitted_by,
                "closed_at": closed_at,
                "closed_by": closed_by,
                "estimated_hours": template["estimated_hours"],
                "actual_hours": template.get("actual_hours", 0),
                "budget_allocated": template["budget_allocated"],
                "actual_cost": template.get("actual_cost", 0),
                "tags": template["tags"],
                "is_active": True,
            }

            engagement = AuditEngagement.objects.create(**engagement_data)
            created_engagements.append(engagement)

            self.stdout.write(
                f"Created engagement: {engagement.title} (Status: {engagement.status})"
            )

        # Create some overdue engagements
        overdue_engagements = [
            {
                "title": "Overdue Security Assessment",
                "description": "Security assessment that is behind schedule",
                "status": "in_progress",
                "priority": "high",
                "scope": "Network security and access controls",
                "objectives": "Assess security controls and identify vulnerabilities",
                "methodology": "Security testing and control review",
                "progress_percentage": 45,
                "fieldwork_notes": "Delayed due to resource constraints and system availability issues.",
                "estimated_hours": 100,
                "actual_hours": 45,
                "budget_allocated": 12000,
                "actual_cost": 5400,
                "tags": ["Security", "Overdue", "High-Priority"],
            },
            {
                "title": "Delayed Compliance Review",
                "description": "Compliance review that has exceeded planned timeline",
                "status": "fieldwork",
                "priority": "medium",
                "scope": "Regulatory compliance and policy adherence",
                "objectives": "Ensure compliance with applicable regulations",
                "methodology": "Documentation review and control testing",
                "progress_percentage": 70,
                "fieldwork_notes": "Extended timeline due to additional regulatory requirements discovered.",
                "estimated_hours": 80,
                "actual_hours": 56,
                "budget_allocated": 10000,
                "actual_cost": 7000,
                "tags": ["Compliance", "Overdue", "Regulatory"],
            },
        ]

        for template in overdue_engagements:
            audit_plan = random.choice(audit_plans) if audit_plans else None
            entity = random.choice(audit_entities) if audit_entities else None
            assigned_auditor = random.choice(users)
            engagement_lead = random.choice([u for u in users if u != assigned_auditor])
            created_by = random.choice(users)

            # Make these overdue by setting planned dates in the past
            planned_start = date.today() - timedelta(days=random.randint(60, 120))
            planned_end = planned_start + timedelta(days=random.randint(20, 40))
            actual_start = planned_start + timedelta(days=random.randint(0, 10))

            engagement_data = {
                "title": template["title"],
                "description": template["description"],
                "audit_plan": audit_plan,
                "entity": entity,
                "status": template["status"],
                "priority": template["priority"],
                "assigned_auditor": assigned_auditor,
                "engagement_lead": engagement_lead,
                "created_by": created_by,
                "planned_start_date": planned_start,
                "planned_end_date": planned_end,
                "actual_start_date": actual_start,
                "scope": template["scope"],
                "objectives": template["objectives"],
                "methodology": template["methodology"],
                "progress_percentage": template["progress_percentage"],
                "fieldwork_notes": template["fieldwork_notes"],
                "estimated_hours": template["estimated_hours"],
                "actual_hours": template["actual_hours"],
                "budget_allocated": template["budget_allocated"],
                "actual_cost": template["actual_cost"],
                "tags": template["tags"],
                "is_active": True,
            }

            engagement = AuditEngagement.objects.create(**engagement_data)
            created_engagements.append(engagement)

            self.stdout.write(
                f"Created overdue engagement: {engagement.title} (Status: {engagement.status})"
            )

        # Summary
        total_engagements = AuditEngagement.objects.count()
        self.stdout.write(f"\nDemo engagement creation complete!")
        self.stdout.write(f"Total engagements created: {total_engagements}")
        self.stdout.write(
            f"Draft: {AuditEngagement.objects.filter(status='draft').count()}"
        )
        self.stdout.write(
            f"In Progress: {AuditEngagement.objects.filter(status='in_progress').count()}"
        )
        self.stdout.write(
            f"Fieldwork: {AuditEngagement.objects.filter(status='fieldwork').count()}"
        )
        self.stdout.write(
            f"Review: {AuditEngagement.objects.filter(status='review').count()}"
        )
        self.stdout.write(
            f"Submitted: {AuditEngagement.objects.filter(status='submitted').count()}"
        )
        self.stdout.write(
            f"Closed: {AuditEngagement.objects.filter(status='closed').count()}"
        )
        self.stdout.write(
            f"Overdue engagements: {AuditEngagement.objects.filter(planned_end_date__lt=date.today(), status__in=['draft', 'in_progress', 'fieldwork', 'review']).count()}"
        )
