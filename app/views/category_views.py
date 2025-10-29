from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Category
from django.core.paginator import Paginator

@login_required(login_url='login')
def category_management(request):
    category_id = request.GET.get('id')
    category_to_edit = None
    if category_id:
        category_to_edit = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        if category_to_edit:
            category_to_edit.name = name
            category_to_edit.save()
            messages.success(request, f"Category '{name}' updated successfully!")
        else:
            Category.objects.create(name=name)
            messages.success(request, f"Category '{name}' added successfully!")
        return redirect('category_management')

    all_categories = Category.objects.all().order_by('id')
    paginator = Paginator(all_categories, 10)
    page_number = request.GET.get('page')
    categories = paginator.get_page(page_number)

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
