from django.core.management.base import BaseCommand
from audits.models import AuditEntity
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Add test next_audit_date to some audit entities'

    def handle(self, *args, **options):
        # Get some entities and add next_audit_date
        entities = AuditEntity.objects.all()[:10]
        
        for entity in entities:
            # Add a random date in the next 3 months
            days_ahead = random.randint(1, 90)
            entity.next_audit_date = date.today() + timedelta(days=days_ahead)
            entity.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated {entity.name} with next_audit_date: {entity.next_audit_date}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {len(entities)} entities with test audit dates')
        )
