from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Category
from django.core.paginator import Paginator
from app.utils.activity_log import log_activity 

@login_required(login_url='login')
def category_management(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        name = request.POST.get('name')
        description = request.POST.get('description') or ''

        if category_id:
            # Update existing category
            category = get_object_or_404(Category, id=category_id)
            category.name = name
            category.description = description
            category.save()
            log_activity(
                request,
                action="UPDATE",
                model_name="Category",
                object_id=category.id,
                description=f"Update category name'{category.name}'"
            )
            messages.success(request, f"Category '{name}' updated successfully!")
        else:
            # Create new category
            category = Category.objects.create(
                name=name,
                description=description
            )
            log_activity(
                request,
                action="CREATE",
                model_name="Category",
                object_id=category.id,
                description=f"Create category name'{category.name}'"
            )
            messages.success(request, f"Category '{name}' added successfully!")


    all_categories = Category.objects.all().order_by('id')
    paginator = Paginator(all_categories, 10)
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number)

    return render(request, 'category_management/categories.html', {
        'categories': categories
    })

@login_required(login_url='login')
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    log_activity(
        request,
        action="DELETE",
        model_name="Category",
        object_id=category.id,
        description=f"Delete ca category '{category.name}'"
    )
    category.delete()
    messages.success(request, f'Category "{category.name}" deleted successfully.')
    return redirect('category_management')
