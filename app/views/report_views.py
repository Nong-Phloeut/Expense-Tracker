
# @login_required(login_url='login')
# def reports(request):
#     return render(request, 'reports/reports.html')

from django.http import HttpResponse
import csv
from reportlab.pdfgen import canvas
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date
from ..models import Expense, Category

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



@login_required
def export_report(request, format):
    expenses = Expense.objects.filter(user=request.user)
    if format == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
        writer = csv.writer(response)
        writer.writerow(['Date', 'Category', 'Description', 'Amount'])
        for e in expenses:
            writer.writerow([e.date, e.category.name, e.description, e.amount])
        return response
    elif format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="expenses.pdf"'
        p = canvas.Canvas(response)
        y = 800
        for e in expenses:
            p.drawString(50, y, f"{e.date} - {e.category.name} - {e.amount}")
            y -= 20
        p.showPage()
        p.save()
        return response
