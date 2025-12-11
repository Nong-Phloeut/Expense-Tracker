from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import timedelta, date
from decimal import Decimal
import calendar

from ..models import Expense, Alert, RecurringExpense, Budget


# --------------------- HELPER FUNCTIONS ---------------------

def get_total_expenses(user):
    return Expense.objects.filter(user=user).aggregate(
        Sum("amount")
    )["amount__sum"] or Decimal("0")


def get_monthly_budget(user):
    return Budget.objects.filter(user=user).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")


def get_recurring_expenses(user):
    recurring = RecurringExpense.objects.filter(user=user)
    total = Decimal("0")

    for r in recurring:
        if r.frequency == "daily":
            total += r.amount * 30
        elif r.frequency == "weekly":
            total += r.amount * 4
        elif r.frequency == "monthly":
            total += r.amount
        elif r.frequency == "yearly":
            total += r.amount / 12

    return total


def get_category_expenses(user):
    data = (
        Expense.objects.filter(user=user)
        .values("category__name")
        .annotate(total=Sum("amount"))
    )
    labels = [d["category__name"] or "Uncategorized" for d in data]
    totals = [float(d["total"]) for d in data]
    return labels, totals


def get_weekly_expenses(user):
    today = date.today()
    last_week_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    labels = [d.strftime("%b %d") for d in last_week_days]

    totals = [
        float(
            Expense.objects.filter(user=user, date=day)
            .aggregate(Sum("amount"))["amount__sum"] or 0
        )
        for day in last_week_days
    ]

    return labels, totals


def get_monthly_expenses(user):
    today = date.today()
    start_month = today.replace(day=1)

    months = []
    totals = []

    for i in range(5, -1, -1):
        # Handle month/year rollover
        month_num = start_month.month - i
        year_num = start_month.year
        if month_num <= 0:
            month_num += 12
            year_num -= 1

        month_start = date(year_num, month_num, 1)
        next_month = month_start.replace(day=28) + timedelta(days=4)
        month_end = next_month - timedelta(days=next_month.day)

        amount = (
            Expense.objects.filter(user=user, date__gte=month_start, date__lte=month_end)
            .aggregate(Sum("amount"))["amount__sum"]
            or 0
        )

        months.append(month_start.strftime("%b %Y"))
        totals.append(float(amount))

    return months, totals


def get_budget_chart_data(user):
    monthly_budget = get_monthly_budget(user)

    category_budgets = (
        Budget.objects.filter(user=user)
        .values("category__name")
        .annotate(total=Sum("amount"))
    )

    labels = []
    totals = []

    remaining = monthly_budget

    for b in category_budgets:
        name = b["category__name"] or "Other"
        amount = b["total"]

        labels.append(name)
        totals.append(float(amount))

        remaining -= amount

    # Add "Other" bucket if some budget is not assigned to categories
    if remaining > 0:
        labels.append("Other")
        totals.append(float(remaining))

    return labels, totals


def get_monthly_budget_planning(user):
    today = date.today()
    start_month = today.replace(day=1)

    months = []
    totals = []

    for i in range(5, -1, -1):
        month_num = start_month.month - i
        year_num = start_month.year

        if month_num <= 0:
            month_num += 12
            year_num -= 1

        # First and last day of the month
        month_start = date(year_num, month_num, 1)
        month_end = date(year_num, month_num, calendar.monthrange(year_num, month_num)[1])

        # Filter budgets that overlap with the month
        amount = (
            Budget.objects.filter(
                user=user,
                start_date__lte=month_end,
                end_date__gte=month_start
            )
            .aggregate(total=Sum("amount"))
            .get("total")
            or 0
        )

        month_label = month_start.strftime("%b %Y")
        months.append(month_label)
        totals.append(float(amount))

    return months, totals


# --------------------- MAIN DASHBOARD VIEW ---------------------

@login_required(login_url="login")
def dashboard(request):

    user = request.user

    # Fetch data from separated functions
    total_expenses = get_total_expenses(user)
    monthly_budget = get_monthly_budget(user)
    recurring_total = get_recurring_expenses(user)
    category_labels, category_totals = get_category_expenses(user)
    weekly_labels, weekly_totals = get_weekly_expenses(user)
    month_labels, monthly_totals = get_monthly_expenses(user)
    budget_labels, budget_totals = get_budget_chart_data(user)

    budget_remaining = monthly_budget - total_expenses
    alert_count = Alert.objects.count()

    # NEW DATA
    monthly_budget_labels, monthly_budget_values = get_monthly_budget_planning(user)

    context = {
        "total_expenses": f"${total_expenses:,.2f}",
        "budget_remaining": f"${budget_remaining:,.2f}",
        "recurring_total": f"${recurring_total:,.2f}",
        "alert_count": alert_count,

        # Charts
        "category_labels": category_labels,
        "category_totals": category_totals,
        "date_labels": weekly_labels,
        "month_labels": month_labels,
        "monthly_totals": monthly_totals,

        # Budget planning chart
        "budget_labels": budget_labels,
        "budget_totals": budget_totals,

        # NEW charts
        "monthly_budget_labels": monthly_budget_labels,
        "monthly_budget_values": monthly_budget_values,
    }

    return render(request, "dashboard.html", context)
