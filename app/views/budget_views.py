from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Budget, Category
from django.core.paginator import Paginator
from django.utils import timezone

@login_required(login_url='login')
def budget_list(request):
    budgets = Budget.objects.select_related('category').filter(user=request.user).order_by('-start_date')
    categories = Category.objects.all()

    paginator = Paginator(budgets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        budget_id = request.POST.get('budget_id')
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        category = get_object_or_404(Category, id=category_id) if category_id else None

        if budget_id:
            # Update existing
            budget = get_object_or_404(Budget, id=budget_id, user=request.user)
            budget.category = category
            budget.amount = amount
            budget.start_date = start_date
            budget.end_date = end_date
            budget.save()
            messages.success(request, "Budget updated successfully.")
        else:
            # Create new
            Budget.objects.create(
                user=request.user,
                category=category,
                amount=amount,
                start_date=start_date,
                end_date=end_date
            )
            messages.success(request, "Budget created successfully.")

        return redirect('budget_planning')

    return render(request, 'budget_planning/budget_management.html', {
        'budgets': page_obj,
        'categories': categories,
        'today': timezone.now()
    })


@login_required(login_url='login')
def budget_delete(request, id):
    budget = get_object_or_404(Budget, id=id, user=request.user)
    budget.delete()
    messages.success(request, "Budget deleted successfully.")
    return redirect('budget_planning')
