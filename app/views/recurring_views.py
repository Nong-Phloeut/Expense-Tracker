from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import RecurringExpense, Category
from django.utils import timezone


@login_required(login_url='login')
def recurring_expenses(request):
    """List, Create, and Update recurring expenses"""
    recurring_list = RecurringExpense.objects.filter(user=request.user).select_related('category').order_by('-next_due_date')
    categories = Category.objects.all()

    paginator = Paginator(recurring_list, 10)
    page_number = request.GET.get('page')
    recurring_page = paginator.get_page(page_number)

    if request.method == "POST":
        recurring_id = request.POST.get('recurring_id')
        category_id = request.POST.get('category')
        amount = request.POST.get('amount')
        name = request.POST.get('name')
        frequency = request.POST.get('frequency')
        start_date = request.POST.get('start_date')
        next_due_date = request.POST.get('next_due_date')

        # category validation
        category = get_object_or_404(Category, id=category_id) if category_id else None

        if recurring_id:
            # Update existing recurring expense
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
            # Create new recurring expense
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
        'today': timezone.now()
    })


@login_required(login_url='login')
def delete_recurring(request, pk):
    """Delete a recurring expense"""
    expense = get_object_or_404(RecurringExpense, pk=pk, user=request.user)
    expense.delete()
    messages.success(request, "Recurring expense deleted successfully!")
    return redirect('recurring_expenses')
