from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from app.utils.activity_log import log_activity 

def login_view(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            log_activity(
                request,
                action="LOGIN",
                model_name="User",
                object_id=username,
                description=f"User login Successfully"
            )
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            log_activity(
                request,
                action="LOGIN",
                model_name="User",
                object_id=username,
                description=f"Invalid username or password."
            )
            context['username'] = username  # keep the username value
            context['password'] = password  # keep the username value
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'account_profile.html', {
        'user': request.user
    })


@login_required
def account_profile(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.username = request.POST.get("username")
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("account_profile")
    return render(request, "account_profile.html")

@login_required
def account_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # keep user logged in
            messages.success(request, "Password changed successfully.")
            return redirect("account_password")
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, "account_password.html", {"form": form})
