from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import timedelta, date
from ..models import Expense, Alert ,RecurringExpense ,Budget
from decimal import Decimal

@login_required(login_url='login')
def dashboard(request):
    user = request.user

    # Total expenses
    total_expenses = Expense.objects.filter(user=user).aggregate(Sum('amount'))['amount__sum'] or 0

      # Get user's monthly budget from Budget table
    monthly_budget = Budget.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    budget_remaining = monthly_budget - total_expenses

    # Alerts (simple example — when budget exceeds 90%)
    alert_count = alert_count = Alert.objects.filter().count()
    # if total_expenses > monthly_budget * 0.9 else 0
    # Recurring Expenses for current month
    recurring_monthly = RecurringExpense.objects.filter(user=request.user)
    recurring_total = 0
    for r in recurring_monthly:
        if r.frequency == 'daily':
            recurring_total += r.amount * 30
        elif r.frequency == 'weekly':
            recurring_total += r.amount * 4
        elif r.frequency == 'monthly':
            recurring_total += r.amount
        elif r.frequency == 'yearly':
            recurring_total += r.amount / 12
            
    # One-time Expenses = total_expenses - recurring_total
    one_time_total = total_expenses - recurring_total

    # Expenses by Category
    category_data = (
        Expense.objects.filter(user=user)
        .values('category__name')
        .annotate(total=Sum('amount'))
    )

    category_labels = [c['category__name'] or 'Uncategorized' for c in category_data]
    category_totals = [float(c['total']) for c in category_data]

    # Expenses over last 7 days
    today = date.today()
    last_week = [today - timedelta(days=i) for i in range(6, -1, -1)]
    expenses_by_day = []
    for d in last_week:
        total = (
            Expense.objects.filter(user=user, date=d)
            .aggregate(Sum('amount'))['amount__sum'] or 0
        )
        expenses_by_day.append(float(total))

    labels = [d.strftime('%b %d') for d in last_week]
   
    # Get expenses for the last 6 months
    start_month = today.replace(day=1)  # first day of this month
    months = []
    monthly_totals = []

    for i in range(5, -1, -1):  # last 6 months
        month_start = start_month.replace(month=start_month.month - i if start_month.month - i > 0 else 12 + (start_month.month - i))
        month_end = month_start.replace(day=28) + timedelta(days=4)  # ensures we get last day of month
        month_end = month_end - timedelta(days=month_end.day)  # last day of month

        total = Expense.objects.filter(user=user, date__gte=month_start, date__lte=month_end).aggregate(Sum('amount'))['amount__sum'] or 0
        months.append(month_start.strftime('%b %Y'))
        monthly_totals.append(float(total))
    print('monthly_totals',monthly_totals)
    print('months',months)

    context = {
        'total_expenses': total_expenses,
        'budget_remaining': budget_remaining,
        'recurring_total': round(recurring_total, 2),
        'alert_count': alert_count,
        'category_labels': category_labels,
        'category_totals': category_totals,
        'date_labels': labels,
        'expenses_by_day': expenses_by_day,
        'one_time_total': one_time_total,
        'month_labels': months,
        'monthly_totals': monthly_totals,

    }
    return render(request, 'dashboard.html', context)