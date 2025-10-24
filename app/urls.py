from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('users', views.user_management, name='user_management'),
    path('expenses', views.expense_entry, name='expense_entry'),
    path('budget', views.budget_planning, name='budget_planning'),
    path('visualization', views.visualization, name='visualization'),
    path('reports', views.reports, name='reports'),
    path('categories', views.category_management, name='category_management'),
    path('recurring', views.recurring_expenses, name='recurring_expenses'),
    path('alerts', views.alerts, name='alerts'),
]
