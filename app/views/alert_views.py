from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Alert ,Category
from django.core.paginator import Paginator

@login_required(login_url='login')
def alert_list(request):
    categories = Category.objects.all()

    # Base queryset
    alerts = Alert.objects.filter(user=request.user).order_by('-created_at')

    # Get filters from GET parameters
    alert_name = request.GET.get('alertName')
    category_filter = request.GET.get('categoryFilter')
    status_filter = request.GET.get('status')

    # Apply filters
    if alert_name:
        alerts = alerts.filter(name__icontains=alert_name)
    if category_filter:
        alerts = alerts.filter(category__id=category_filter)
    if status_filter:
        alerts = alerts.filter(status=status_filter)

    # Pagination (optional)
    paginator = Paginator(alerts, 10)
    page_number = request.GET.get('page')
    alerts_page = paginator.get_page(page_number)

    # Handle POST (Create / Update)
    if request.method == 'POST':
        alert_id = request.POST.get('alert_id')
        name = request.POST.get('alertName')
        condition = request.POST.get('condition')
        amount = request.POST.get('amount')
        status = request.POST.get('status')
        category_id = request.POST.get('category')

        category = get_object_or_404(Category, id=category_id) if category_id else None

        if alert_id:
            alert = get_object_or_404(Alert, id=alert_id, user=request.user)
            alert.name = name
            alert.condition = condition
            alert.amount = amount
            alert.status = status
            alert.category = category
            alert.save()
            messages.success(request, "Alert updated successfully.")
        else:
            Alert.objects.create(
                user=request.user,
                name=name,
                condition=condition,
                amount=amount,
                status=status,
                category=category
            )
            messages.success(request, "Alert created successfully.")

        return redirect('alerts')

    return render(request, 'alerts/alerts.html', {
        'alerts': alerts_page,
        'categories': categories,
    })

@login_required(login_url='login')
def delete_alert(request, pk):
    alert = get_object_or_404(Alert, pk=pk, user=request.user)
    alert.delete()
    messages.success(request, "Alert deleted successfully.")
    return redirect('alerts')
