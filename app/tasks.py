from celery import shared_task
from django.utils import timezone
from .models import RecurringExpense, Notification

from app.utils.telegram_utils import send_telegram_message

@shared_task
def check_recurring_expenses():
    
    today = timezone.now().date()

    expenses = RecurringExpense.objects.filter(next_due_date__lt=today)

    for exp in expenses:
        message = (
            f"🔔 Recurring Expense Due Today {today}\n"
            f"User: {exp.user.username}\n"
            f"Expense: {exp.name}\n"
            f"Amount: {exp.amount}\n"
            f"Category: {exp.category.name if exp.category else 'None'}"
        )

        Notification.objects.create(
            user=exp.user,
            title=f"Recurring Expense: {exp.name}",
            message=message,
            is_read=False
        )
        send_telegram_message(message)

        # update next due date
        if exp.frequency == "daily":
            exp.next_due_date += timezone.timedelta(days=1)
        elif exp.frequency == "weekly":
            exp.next_due_date += timezone.timedelta(weeks=1)
        elif exp.frequency == "monthly":
            exp.next_due_date = exp.next_due_date.replace(month=exp.next_due_date.month + 1)

        exp.save()
