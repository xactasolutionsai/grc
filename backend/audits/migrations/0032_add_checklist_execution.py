# Generated manually for checklist execution feature

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("audits", "0031_add_checklist_models"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ChecklistExecution",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("not_started", "Not Started"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                        ],
                        default="not_started",
                        max_length=20,
                    ),
                ),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("total_items", models.PositiveIntegerField(default=0)),
                ("completed_items", models.PositiveIntegerField(default=0)),
                (
                    "notes",
                    models.TextField(
                        blank=True, help_text="Overall notes for this execution"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "audit_engagement",
                    models.ForeignKey(
                        help_text="Audit engagement this execution belongs to",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="checklist_executions",
                        to="audits.auditengagement",
                    ),
                ),
                (
                    "checklist",
                    models.ForeignKey(
                        help_text="Template checklist being executed",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="executions",
                        to="audits.checklist",
                    ),
                ),
                (
                    "completed_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="completed_executions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "started_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="started_executions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Checklist Execution",
                "verbose_name_plural": "Checklist Executions",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ChecklistItemResult",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "result",
                    models.CharField(
                        choices=[
                            ("not_tested", "Not Tested"),
                            ("pass", "Pass"),
                            ("fail", "Fail"),
                            ("needs_followup", "Needs Follow-up"),
                            ("not_applicable", "Not Applicable"),
                        ],
                        default="not_tested",
                        help_text="Test result status",
                        max_length=20,
                    ),
                ),
                (
                    "comments",
                    models.TextField(
                        blank=True, help_text="Auditor comments and findings"
                    ),
                ),
                (
                    "finding_summary",
                    models.TextField(blank=True, help_text="Summary of issues found"),
                ),
                ("tested_at", models.DateTimeField(blank=True, null=True)),
                ("evidence_notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "checklist_item",
                    models.ForeignKey(
                        help_text="Template item being tested",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="results",
                        to="audits.checklistitem",
                    ),
                ),
                (
                    "execution",
                    models.ForeignKey(
                        help_text="Parent execution",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="item_results",
                        to="audits.checklistexecution",
                    ),
                ),
                (
                    "tested_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tested_items",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Checklist Item Result",
                "verbose_name_plural": "Checklist Item Results",
                "ordering": ["checklist_item__order"],
            },
        ),
        migrations.AddIndex(
            model_name="checklistexecution",
            index=models.Index(
                fields=["audit_engagement"], name="audits_chec_audit_e_idx123"
            ),
        ),
        migrations.AddIndex(
            model_name="checklistexecution",
            index=models.Index(fields=["status"], name="audits_chec_status_idx456"),
        ),
        migrations.AddIndex(
            model_name="checklistexecution",
            index=models.Index(
                fields=["started_at"], name="audits_chec_started_idx789"
            ),
        ),
        migrations.AddIndex(
            model_name="checklistitemresult",
            index=models.Index(fields=["execution"], name="audits_chec_executi_idx012"),
        ),
        migrations.AddIndex(
            model_name="checklistitemresult",
            index=models.Index(fields=["result"], name="audits_chec_result_idx345"),
        ),
        migrations.AddIndex(
            model_name="checklistitemresult",
            index=models.Index(fields=["tested_at"], name="audits_chec_tested__idx678"),
        ),
        migrations.AlterUniqueTogether(
            name="checklistexecution",
            unique_together={("checklist", "audit_engagement")},
        ),
        migrations.AlterUniqueTogether(
            name="checklistitemresult",
            unique_together={("execution", "checklist_item")},
        ),
    ]
