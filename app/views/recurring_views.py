from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import RecurringExpense, Category
from django.utils import timezone


@login_required(login_url='login')
def recurring_expenses(request):
    """List, filter, create, and update recurring expenses"""
    # Get filters from request
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    category_filter = request.GET.get('categoryFilter')
    frequency_filter = request.GET.get('frequency')
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')

    # Base queryset
    recurring_list = RecurringExpense.objects.filter(user=request.user).select_related('category')

    # Apply filters
    if start_date:
        recurring_list = recurring_list.filter(start_date__gte=start_date)
    if end_date:
        recurring_list = recurring_list.filter(start_date__lte=end_date)
    if category_filter:
        recurring_list = recurring_list.filter(category__id=category_filter)
    if frequency_filter:
        recurring_list = recurring_list.filter(frequency=frequency_filter)
    if min_amount:
        recurring_list = recurring_list.filter(amount__gte=min_amount)
    if max_amount:
        recurring_list = recurring_list.filter(amount__lte=max_amount)

    recurring_list = recurring_list.order_by('-next_due_date')

    # Pagination
    paginator = Paginator(recurring_list, 10)
    page_number = request.GET.get('page')
    recurring_page = paginator.get_page(page_number)

    categories = Category.objects.all()

    # Handle POST (Create / Update)
    if request.method == "POST":
        recurring_id = request.POST.get('recurring_id')
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        name = request.POST.get('name')
        frequency = request.POST.get('frequency')
        start_date = request.POST.get('start_date')
        next_due_date = request.POST.get('next_due_date')

        category = get_object_or_404(Category, id=category_id) if category_id else None

        if recurring_id:
            expense = get_object_or_404(RecurringExpense, id=recurring_id, user=request.user)
            expense.category = category
            expense.amount = amount
            expense.name = name
            expense.frequency = frequency
            expense.start_date = start_date
            expense.next_due_date = next_due_date
            expense.save()
            messages.success(request, "Recurring expense updated successfully!")
        else:
            RecurringExpense.objects.create(
                user=request.user,
                category=category,
                amount=amount,
                name=name,
                frequency=frequency,
                start_date=start_date,
                next_due_date=next_due_date,
            )
            messages.success(request, "Recurring expense added successfully!")

        return redirect('recurring_expenses')

    return render(request, 'recurring_expenses/recurring.html', {
        'recurring_list': recurring_page,
        'categories': categories,
        'today': timezone.now(),
    })

@login_required(login_url='login')
def delete_recurring(request, pk):
    """Delete a recurring expense"""
    expense = get_object_or_404(RecurringExpense, pk=pk, user=request.user)
    expense.delete()
    messages.success(request, "Recurring expense deleted successfully!")
    return redirect('recurring_expenses')
