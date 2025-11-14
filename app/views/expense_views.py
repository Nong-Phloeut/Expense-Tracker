from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from ..models import Expense, Category
from app.utils.telegram_utils import check_alerts 
from app.utils.activity_log import log_activity 

@login_required(login_url='login')
def expense_entry(request):
    """Create or update an expense and list expenses with filters and pagination."""
    
    # --- Handle POST (Create / Update) ---
    if request.method == 'POST':
        expense_id = request.POST.get('expense_id')
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        date = request.POST.get('date') or timezone.now().date()

        category = get_object_or_404(Category, id=category_id) if category_id else None

        if expense_id:
            # Update existing expense
            expense = get_object_or_404(Expense, id=expense_id, user=request.user)
            expense.category = category
            expense.amount = amount
            expense.description = description
            expense.date = date
            expense.save()
            log_activity(
                request,
                action="UPDATE",
                model_name="Expense",
                object_id=expense.id,
                description=f"Update expense amount'{expense.amount}'"
            )
            messages.success(request, 'Expense updated successfully!')
        else:
            # Create new expense
            expense = Expense.objects.create(
                user=request.user,
                category=category,
                amount=amount,
                description=description,
                date=date
            )
            log_activity(
                request,
                action="CREATE",
                model_name="Expense",
                object_id=expense.id,
                description=f"Create expense amount'{expense.amount}'"
            )
            # Check alerts for new expense
            triggered_alerts = check_alerts(request.user, amount, category)
            if triggered_alerts:
                request.session['triggered_alerts'] = triggered_alerts
            messages.success(request, 'Expense added successfully!')

        return redirect('expense_entry')

    # --- GET: List & Filter Expenses ---
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    categories = Category.objects.all()

    # --- Filters ---
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    category_id = request.GET.get('categoryFilter')
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')

    if start_date and end_date:
        expenses = expenses.filter(date__range=[start_date, end_date])
    elif start_date:
        expenses = expenses.filter(date__gte=start_date)
    elif end_date:
        expenses = expenses.filter(date__lte=end_date)

    if category_id:
        expenses = expenses.filter(category__id=category_id)
    if min_amount:
        expenses = expenses.filter(amount__gte=min_amount)
    if max_amount:
        expenses = expenses.filter(amount__lte=max_amount)

    # --- Pagination ---
    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page')
    expenses_page = paginator.get_page(page_number)

    # --- Show filter collapse if any filter active ---
    show_filter = any([start_date, end_date, category_id, min_amount, max_amount])

    # --- Triggered alerts ---
    triggered_alerts = request.session.pop('triggered_alerts', [])

    return render(request, 'expense_entry/list.html', {
        'expenses': expenses_page,
        'categories': categories,
        'today': timezone.now().date(),
        'triggered_alerts': triggered_alerts,
        'show_filter': show_filter,
        'request': request
    })


@login_required(login_url='login')
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    log_activity(
        request,
        action="DELETE",
        model_name="Expense",
        object_id=expense.id,
        description=f"Delete expense amount'{expense.amount}'"
    )
    expense.delete()
    messages.success(request, 'Expense deleted successfully!')
    return redirect('expense_entry')
