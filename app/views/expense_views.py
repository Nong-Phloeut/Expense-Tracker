from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from ..models import Expense, Category
from app.utils.telegram_utils import check_alerts 

@login_required(login_url='login')
def expense_entry(request):
    if request.method == 'POST':
        expense_id = request.POST.get('expense_id')  # detect if editing
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('date') or timezone.now().date()

        category = get_object_or_404(Category, id=category_id) if category_id else None

        if expense_id:
            # 🔹 Update existing expense
            expense = get_object_or_404(Expense, id=expense_id, user=request.user)
            expense.category = category
            expense.amount = amount
            expense.description = description
            expense.date = date
            expense.save()
            messages.success(request, 'Expense updated successfully!')
        else:
            # 🔹 Create new expense
            Expense.objects.create(
                user=request.user,
                category=category,
                amount=amount,
                description=description,
                date=date
            )
                # 🔹 Check alerts for new expense
            triggered_alerts = check_alerts(request.user, amount ,category)
            if triggered_alerts:
                request.session['triggered_alerts'] = triggered_alerts
            # for alert_msg in triggered_alerts:
            #     messages.warning(request, alert_msg)  # show in web interface

            messages.success(request, 'Expense added successfully!')

        return redirect('expense_entry')

    # 🔹 Read (List + Pagination)
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page')
    expenses_page = paginator.get_page(page_number)
    categories = Category.objects.all()
    triggered_alerts = request.session.pop('triggered_alerts', [])

    return render(request, 'expense_entry/list.html', {
        'expenses': expenses_page,
        'categories': categories,
        'today': timezone.now().date(),
        'triggered_alerts': triggered_alerts

    })


@login_required(login_url='login')
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    messages.success(request, 'Expense deleted successfully!')
    return redirect('expense_entry')
