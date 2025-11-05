import openpyxl
from django.http import HttpResponse
import csv
from reportlab.pdfgen import canvas
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date
from ..models import Expense, Category
from django.utils import timezone

@login_required(login_url='login')
def reports(request):
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    category_filter = request.GET.get('category')

    expenses = Expense.objects.filter(user=request.user)

    # Apply filters
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    if category_filter:
        expenses = expenses.filter(category__name=category_filter)

    # Summary calculations
    total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    highest_expense = expenses.order_by('-amount').first()
    avg_per_day = 0

    if expenses.exists():
        first_date = expenses.order_by('date').first().date
        last_date = expenses.order_by('-date').first().date
        days = (last_date - first_date).days + 1
        avg_per_day = round(total_expenses / days, 2) if days > 0 else total_expenses

    top_category = (
        expenses.values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
        .first()
    )

    top_category_name = top_category['category__name'] if top_category else "N/A"

    # Data for Chart.js
    category_data = list(
        expenses.values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    category_labels = [c['category__name'] for c in category_data]
    category_totals = [float(c['total']) for c in category_data]

    # Monthly trend chart
    monthly_data = (
        expenses.extra(select={'month': "DATE_TRUNC('month', date)"})
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    months = [m['month'].strftime('%b %Y') for m in monthly_data]
    monthly_totals = [float(m['total']) for m in monthly_data]
    print(months, monthly_totals)
    return render(request, 'reports/reports.html', {
        'expenses': expenses,
        'total_expenses': total_expenses,
        'highest_expense': highest_expense,
        'avg_per_day': avg_per_day,
        'top_category': top_category_name,
        'category_labels': category_labels,
        'category_totals': category_totals,
        'months': months,
        'monthly_totals': monthly_totals,
        'categories': Category.objects.all(),
        'start_date': start_date or '',
        'end_date': end_date or '',
        'category_filter': category_filter or '',
    })


@login_required(login_url='login')
def export_expenses_excel(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = request.GET.get('category')

    expenses = Expense.objects.filter(user=request.user)

    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    if category and category != '':
        expenses = expenses.filter(category__name=category)

    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Expenses"

    # Header row
    ws.append(["Date", "Category", "Description", "Amount"])

    # Data rows
    for exp in expenses:
        ws.append([
            exp.date.strftime("%Y-%m-%d"),
            exp.category.name if exp.category else '',
            exp.description,
            float(exp.amount)
        ])

    # Response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"Expenses_Report_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response