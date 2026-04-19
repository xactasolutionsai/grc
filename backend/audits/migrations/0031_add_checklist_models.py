# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("audits", "0030_auditentity_team_member_alter_auditentity_owner_and_more"),
        ("iam", "0001_initial"),
        ("core", "0006_remove_securitymeasure_security_function_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Checklist",
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
                ("name", models.CharField(max_length=200, verbose_name="name")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("active", "Active"),
                            ("archived", "Archived"),
                        ],
                        default="draft",
                        help_text="Status of the checklist",
                        max_length=20,
                    ),
                ),
                (
                    "is_published",
                    models.BooleanField(
                        default=True, help_text="Whether the checklist is published"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        help_text="User who created this checklist",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_checklists",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "folder",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_folder",
                        to="iam.folder",
                        verbose_name="domain",
                    ),
                ),
            ],
            options={
                "verbose_name": "Checklist",
                "verbose_name_plural": "Checklists",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="ChecklistItem",
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
                    "title",
                    models.CharField(
                        help_text="Title of the audit test/question", max_length=500
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Detailed objective or procedure for this test",
                    ),
                ),
                (
                    "order",
                    models.PositiveIntegerField(
                        default=0, help_text="Display order within the checklist"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "checklist",
                    models.ForeignKey(
                        help_text="Parent checklist",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="audits.checklist",
                    ),
                ),
                (
                    "control",
                    models.ForeignKey(
                        blank=True,
                        help_text="Linked control being tested",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="checklist_items_as_control",
                        to="core.appliedcontrol",
                    ),
                ),
                (
                    "risk",
                    models.ForeignKey(
                        blank=True,
                        help_text="Linked risk scenario",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="checklist_items",
                        to="core.riskscenario",
                    ),
                ),
                (
                    "policy",
                    models.ForeignKey(
                        blank=True,
                        help_text="Linked policy",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="checklist_items_as_policy",
                        to="core.policy",
                    ),
                ),
            ],
            options={
                "verbose_name": "Checklist Item",
                "verbose_name_plural": "Checklist Items",
                "ordering": ["checklist", "order"],
            },
        ),
        migrations.AddIndex(
            model_name="checklist",
            index=models.Index(
                fields=["folder"], name="audits_chec_folder__f5c21e_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="checklist",
            index=models.Index(fields=["status"], name="audits_chec_status_6a8e12_idx"),
        ),
        migrations.AddIndex(
            model_name="checklist",
            index=models.Index(
                fields=["created_at"], name="audits_chec_created_3b9f45_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="checklist",
            index=models.Index(
                fields=["created_by"], name="audits_chec_created_b8c534_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="checklist",
            index=models.Index(
                fields=["is_published"], name="audits_chec_is_publ_7d2a91_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="checklistitem",
            index=models.Index(
                fields=["checklist", "order"], name="audits_chec_checkli_4f8e2a_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="checklistitem",
            index=models.Index(
                fields=["control"], name="audits_chec_control_9e3b1c_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="checklistitem",
            index=models.Index(fields=["risk"], name="audits_chec_risk_id_5c7d9f_idx"),
        ),
        migrations.AddIndex(
            model_name="checklistitem",
            index=models.Index(
                fields=["policy"], name="audits_chec_policy__2a4e6b_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="checklistitem",
            constraint=models.UniqueConstraint(
                fields=("checklist", "order"), name="unique_checklist_item_order"
            ),
        ),
    ]
