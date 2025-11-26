from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User ,Group
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from app.utils.activity_log import log_activity 
from app.models import UserProfile
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from smtplib import SMTPException

@login_required(login_url='login')
def user_management(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        role_id = request.POST.get('role')  # this is the group ID
        chart_id = request.POST.get('chartId')

        # ===== Define group first =====
        group = None
        if role_id:
            group = get_object_or_404(Group, id=role_id)

        if user_id:
            # Update existing user
            user = get_object_or_404(User, id=user_id)
            user.username = username
            user.email = email
            user.is_superuser = True if group and group.name == 'Admin' else False

            user.groups.clear()
            if group:
                user.groups.add(group)
            user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.chart_id = chart_id
            profile.save()

            log_activity(
                request,
                action="UPDATE",
                model_name="User",
                object_id=user.id,
                description=f"Update username'{user.username}'"
            )
            messages.success(request, 'User updated successfully!')
        else:
            # Create new user
            random_password = get_random_string(12)
            is_superuser = True if group and group.name == 'Admin' else False

            user = User.objects.create_user(
                username=username,
                email=email,
                password=random_password,
                is_superuser=is_superuser
            )

            if group:
                user.groups.add(group)

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.chart_id = chart_id
            profile.save()

            log_activity(
                request,
                action="CREATE",
                model_name="User",
                object_id=user.id,
                description=f"Create username '{user.username}'"
            )

            # Send password email
            try:
                validate_email(email)
                login_url = request.build_absolute_uri(reverse('login'))
                subject = "Welcome to Expense Tracker System"
                message = f"""
                    Hello {username},

                    Your account has been created on Expense Tracker System.

                    🔹 Username: {username}
                    🔹 Password: {random_password}

                    Please click the link below to access the system and change your password immediately:
                    {login_url}

                    Best regards,
                    Expense Tracker System Team
                """
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
                messages.success(request, f'User created successfully! Password sent to {username}')
            except (ValidationError, SMTPException):
                messages.success(request, f'User created successfully (email not sent)')

        return redirect('user_management')

    # ===== Filtering & Pagination =====
    role_filter = request.GET.get('roleFilter')
    search = request.GET.get('search')

    users = User.objects.all().order_by('id')
    for user in users:
        UserProfile.objects.get_or_create(user=user)

    if role_filter:
        users = users.filter(is_superuser=True if role_filter == 'Admin' else False)
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search))

    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    roles = Group.objects.all()

    return render(request, 'user_management/user_management.html', {'users': users, 'roles': roles})
 

@login_required(login_url='login')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user != request.user:
        log_activity(
            request,
            action="DELETE",
            model_name="User",
            object_id=user.id,
            description=f"Delete user username'{user.username}'"
        )
        user.delete()
        messages.success(request, 'User deleted successfully!')
    else:
        messages.warning(request, 'You cannot delete yourself!')
    return redirect('user_management')