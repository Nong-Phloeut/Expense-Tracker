from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Budget, Category
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime

@login_required(login_url='login')
def budget_management(request):
    """
    Handles:
    - GET: list budgets with filters
    - POST: create or update a budget
    """
    categories = Category.objects.all()

    # --- Handle POST (Create/Update) ---
    if request.method == 'POST':
        budget_id = request.POST.get('budget_id')
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        category = get_object_or_404(Category, id=category_id) if category_id else None
        # convert to date objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        if budget_id:
            # Update existing
            budget = get_object_or_404(Budget, id=budget_id, user=request.user)
            budget.category = category
            budget.amount = amount
            budget.start_date = start_date
            budget.end_date = end_date
            budget.update_status()
            budget.save()
            messages.success(request, "Budget updated successfully.")
        else:
            # Create new
            budget = Budget.objects.create(
                user=request.user,
                category=category,
                amount=amount,
                start_date=start_date,
                end_date=end_date
            )
            budget.update_status()
            messages.success(request, "Budget created successfully.")

        return redirect('budget_management')  # redirect to same page after POST

    # --- Handle GET (Filters + List) ---
    budgets = Budget.objects.filter(user=request.user).order_by('-start_date')

    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    category = request.GET.get('categoryFilter')
    status = request.GET.get('status')
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')

    if start_date and end_date:
        budgets = budgets.filter(start_date__range=[start_date, end_date])
    elif start_date:
        budgets = budgets.filter(start_date__gte=start_date)
    elif end_date:
        budgets = budgets.filter(start_date__lte=end_date)

    if category:
        budgets = budgets.filter(category_id=category)
    if status:
        budgets = budgets.filter(status=status)
    if min_amount:
        budgets = budgets.filter(amount__gte=min_amount)
    if max_amount:
        budgets = budgets.filter(amount__lte=max_amount)

    # Pagination
    paginator = Paginator(budgets, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'budget_planning/budget_management.html', {
        'budgets': page_obj,
        'categories': categories,
        'request': request,
    })


@login_required(login_url='login')
def budget_delete(request, id):
    budget = get_object_or_404(Budget, id=id, user=request.user)
    budget.delete()
    messages.success(request, "Budget deleted successfully.")
    return redirect('budget_management')
