from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def user_management(request):
    return render(request, 'user_management/list.html')

def expense_entry(request):
    return render(request, 'expense_entry/list.html')

def budget_planning(request):
    return render(request, 'budget_planning/form.html')

def visualization(request):
    return render(request, 'visualization/charts.html')

def reports(request):
    return render(request, 'reports/reports.html')

def category_management(request):
    # Handle edit mode
    category_id = request.GET.get('id')  # e.g. /categories/?id=3
    category_to_edit = None
    if category_id:
        category_to_edit = get_object_or_404(Category, id=category_id)

    # Handle form submission (create or update)
    if request.method == 'POST':
        name = request.POST.get('name')

        if category_to_edit:  # Update existing
            category_to_edit.name = name
            category_to_edit.save()
            messages.success(request, f"Category '{name}' updated successfully!")
            return redirect('category_management')
        else:  # Create new
            Category.objects.create(name=name)
            messages.success(request, f"Category '{name}' added successfully!")
            return redirect('category_management')

    # Display all categories
    categories = Category.objects.all().order_by('id')

    return render(request, 'category_management/categories.html', {
        'categories': categories,
        'edit_category': category_to_edit
    })

@login_required(login_url='login')
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    messages.success(request, f'Category "{category.name}" deleted successfully.')
    return redirect('category_management')

def recurring_expenses(request):
    return render(request, 'recurring_expenses/recurring.html')

def alerts(request):
    return render(request, 'alerts/alerts.html')
