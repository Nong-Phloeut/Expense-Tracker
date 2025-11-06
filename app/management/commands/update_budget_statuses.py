from django.core.management.base import BaseCommand
from app.models import Budget

class Command(BaseCommand):
    help = "Auto-update all budget statuses based on date."

    def handle(self, *args, **kwargs):
        updated_count = 0
        for budget in Budget.objects.all():
            old_status = budget.status
            budget.update_status()
            if budget.status != old_status:
                updated_count += 1
        self.stdout.write(self.style.SUCCESS(f"✅ Updated {updated_count} budgets."))
