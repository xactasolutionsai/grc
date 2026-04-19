# Generated manually for audit plan enhancements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audits', '0025_add_priority_field'),
    ]

    operations = [
        # Add audit_domain to ENTITY_TYPES
        migrations.AlterField(
            model_name='auditentity',
            name='entity_type',
            field=models.CharField(
                max_length=50,
                choices=[
                    ('business_unit', 'Business Unit'),
                    ('division', 'Division'),
                    ('function', 'Function'),
                    ('section', 'Section'),
                    ('unit', 'Unit'),
                    ('process', 'Process'),
                    ('system', 'System'),
                    ('vendor', 'Vendor'),
                    ('compliance_domain', 'Compliance Domain'),
                    ('audit_domain', 'Audit Domain'),
                ]
            ),
        ),
        # Add auditable_entities ManyToManyField
        migrations.AddField(
            model_name='auditplan',
            name='auditable_entities',
            field=models.ManyToManyField(
                blank=True,
                help_text='Additional auditable entities associated with this plan',
                related_name='related_audit_plans',
                to='audits.auditentity'
            ),
        ),
        # Add audit_team JSONField
        migrations.AddField(
            model_name='auditplan',
            name='audit_team',
            field=models.JSONField(
                blank=True,
                null=True,
                help_text="Audit team members with their roles: [{'user_id': int, 'role': str, 'username': str, 'email': str}]"
            ),
        ),
        # Add actual_start DateField
        migrations.AddField(
            model_name='auditplan',
            name='actual_start',
            field=models.DateField(
                blank=True,
                null=True,
                help_text='Actual start date of the audit'
            ),
        ),
        # Add actual_end DateField
        migrations.AddField(
            model_name='auditplan',
            name='actual_end',
            field=models.DateField(
                blank=True,
                null=True,
                help_text='Actual end date of the audit'
            ),
        ),
    ]

