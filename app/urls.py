from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # ← This imports auth_views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('logout', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('users', views.user_management, name='user_management'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('expenses', views.expense_entry, name='expense_entry'),
    path('expenses/delete/<int:id>/', views.delete_expense, name='delete_expense'),
    path('budget', views.budget_management, name='budget_management'),
    path('budget/delete/<int:id>/', views.budget_delete, name='budget_delete'),
    path('reports', views.reports, name='reports'),
    path('categories', views.category_management, name='category_management'),
    path('categories/delete/<int:id>/', views.delete_category, name='delete_category'),
    path('recurring', views.recurring_expenses, name='recurring_expenses'),
    path('recurring/delete/<int:pk>/', views.delete_recurring, name='delete_recurring_expense'),
    path('alerts', views.alert_list, name='alerts'),
    path('alerts/delete/<int:pk>/', views.delete_alert, name='delete_alert'),
    path("account/profile/", views.account_profile, name="account_profile"),
    path("account/password/", views.account_password, name="account_password"),
    path('reports/export/', views.export_expenses_excel, name='export_expenses_excel'),
    path('activity_log', views.activity_log_list, name='activity_log'),
    path('activity_log/delete_log/<int:pk>/', views.delete_log, name='delete_log'),
    path('activity_log/export/', views.export_auditlog_excel, name='export_auditlog_excel'),
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<int:role_id>/edit/', views.role_edit, name='role_edit'),   # <-- fix here
    path('roles/<int:role_id>/delete/', views.role_delete, name='role_delete'),
]
    