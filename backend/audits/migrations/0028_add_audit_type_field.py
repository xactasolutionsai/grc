# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audits', '0027_add_in_review_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditengagement',
            name='audit_type',
            field=models.CharField(
                choices=[
                    ('internal', 'Internal Audit'),
                    ('external', 'External Audit'),
                    ('it_audit', 'IT Audit'),
                    ('compliance', 'Compliance Audit'),
                    ('financial', 'Financial Audit'),
                    ('operational', 'Operational Audit'),
                    ('risk_assessment', 'Risk Assessment')
                ],
                default='internal',
                max_length=30,
                null=True,
                blank=True
            ),
        ),
        migrations.AddIndex(
            model_name='auditengagement',
            index=models.Index(fields=['audit_type'], name='audits_audi_audit_t_idx'),
        ),
    ]

