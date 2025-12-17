from celery import shared_task
from django.utils import timezone
from .models import RecurringExpense, Notification
from app.utils.telegram_utils import send_telegram_message

@shared_task
def check_recurring_expenses():
    today = timezone.now().date()

    expenses = RecurringExpense.objects.all()

    for exp in expenses:
        profile = getattr(exp.user, "userprofile", None)
        if not profile or not profile.chart_id:
            continue

        chat_id = profile.chart_id
        days_left = (exp.next_due_date - today).days

        # 🚫 Stop notifications after 3 days overdue
        if days_left < -3:
            continue

        # Only notify for: 3, 2, 1, 0
        if days_left not in [3, 2, 1, 0]:
            continue

        # Avoid duplicate notifications
        if exp.last_reminder_days == days_left:
            continue

        # Build message
        if days_left > 0:
            message = (
                f"⏰ Upcoming Recurring Expense\n"
                f"Expense: {exp.name}\n"
                f"Amount: {exp.amount}\n"
                f"Due in {days_left} day(s)\n"
                f"Due Date: {exp.next_due_date}"
            )
            title = f"Due in {days_left} days: {exp.name}"
        else:
            message = (
                f"🔔 Recurring Expense Due Today!\n"
                f"Expense: {exp.name}\n"
                f"Amount: {exp.amount}\n"
                f"Category: {exp.category.name if exp.category else 'None'}"
            )
            title = f"Due Today: {exp.name}"

        Notification.objects.create(
            user=exp.user,
            title=title,
            message=message,
            is_read=False
        )

        send_telegram_message(chat_id=chat_id, text=message)

        # Save reminder state
        exp.last_reminder_days = days_left
        exp.save()

        # 🔁 Move to next cycle when due date reached
        if days_left == 0:
            if exp.frequency == "daily":
                exp.next_due_date += timezone.timedelta(days=1)
            elif exp.frequency == "weekly":
                exp.next_due_date += timezone.timedelta(weeks=1)
            elif exp.frequency == "monthly":
                month = exp.next_due_date.month + 1
                year = exp.next_due_date.year + (month // 13)
                month = month % 12 or 12
                exp.next_due_date = exp.next_due_date.replace(
                    year=year, month=month
                )

            # reset reminder tracking
            exp.last_reminder_days = None
            exp.save()
