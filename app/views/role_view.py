from django.shortcuts import render, redirect, get_object_or_404
from ..models import Role
from django.contrib.auth.models import Group, Permission
from django.contrib import messages

def role_list(request):
    groups = Group.objects.prefetch_related('permissions').all()
    return render(request, 'roles/role_list.html', {'groups': groups})

def role_create(request):
    permissions = Permission.objects.all()
    error = None  # initialize error
    name_value = "" 
    selected_permissions = []  # to preserve checked permissions
    if request.method == 'POST':
        name_value = request.POST.get('name', '').strip()
        selected_permissions = request.POST.getlist('permissions')  # list of strings

        name = request.POST.get('name')
        selected_permissions = request.POST.getlist('permissions')

        if Group.objects.filter(name__iexact=name).exists():
            error = f"A role with the name '{name}' already exists."
        else:
            group = Group.objects.create(name=name)
            group.permissions.set(selected_permissions)
            group.save()

            messages.success(request, f"Role '{name}' created successfully.")
            return redirect('role_list')

    return render(request, 'roles/role_form.html', {
        'permissions': permissions,
        'group': None,
        'error': error,
        'name_value': name_value,
        'selected_permissions': selected_permissions,
    })

def role_edit(request, role_id):
    group = get_object_or_404(Group, id=role_id)
    permissions = Permission.objects.all()
    error = None
    name_value = group.name  # default to current name
    selected_permissions = [str(p.id) for p in group.permissions.all()]  # preserve as string

    if request.method == 'POST':
        name_value = request.POST.get('name', '').strip()
        selected_permissions = request.POST.getlist('permissions')

        # Check for duplicate name excluding the current group
        if Group.objects.filter(name__iexact=name_value).exclude(id=group.id).exists():
            error = f"A role with the name '{name_value}' already exists."
        else:
            group.name = name_value
            group.save()
            group.permissions.set(selected_permissions)
            return redirect('role_list')

    return render(request, 'roles/role_form.html', {
        'permissions': permissions,
        'group': group,
        'error': error,
        'name_value': name_value,
        'selected_permissions': selected_permissions,
    })

def role_delete(request, role_id):
    group = get_object_or_404(Group, id=role_id)
    group.delete()
    messages.success(request, "Role deleted successfully.")
    return redirect('role_list')
