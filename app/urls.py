from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # ← This imports auth_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('logout', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('users', views.user_management, name='user_management'),
    path('expenses', views.expense_entry, name='expense_entry'),
    path('expenses/delete/<int:id>/', views.delete_expense, name='delete_expense'),
    path('budget', views.budget_list, name='budget_planning'),
    path('budget/delete/<int:id>/', views.budget_delete, name='budget_delete'),
    path('reports', views.reports, name='reports'),
    path('categories', views.category_management, name='category_management'),
    path('categories/delete/<int:id>/', views.delete_category, name='delete_category'),
    path('recurring', views.recurring_expenses, name='recurring_expenses'),
    path('recurring/delete/<int:pk>/', views.delete_recurring, name='delete_recurring_expense'),
    path('alerts', views.alerts, name='alerts'),
]
    