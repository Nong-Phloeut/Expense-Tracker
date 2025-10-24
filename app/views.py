from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages

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
    return render(request, 'category_management/categories.html')

def recurring_expenses(request):
    return render(request, 'recurring_expenses/recurring.html')

def alerts(request):
    return render(request, 'alerts/alerts.html')
