from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Alert ,Category

@login_required(login_url='login')
def alert_list(request):
    alerts = Alert.objects.filter(user=request.user).order_by('-created_at')
    categories = Category.objects.all()
    if request.method == 'POST':
        alert_id = request.POST.get('alert_id')
        name = request.POST.get('alertName')
        condition = request.POST.get('condition')
        amount = request.POST.get('amount')
        status = request.POST.get('status')
        category_id = request.POST.get('category')

        category = get_object_or_404(Category, id=category_id) if category_id else None

        if alert_id:
            # Update existing alert
            alert = get_object_or_404(Alert, id=alert_id, user=request.user)
            alert.name = name
            alert.condition = condition
            alert.amount = amount
            alert.status = status
            alert.category = category
            alert.save()
            messages.success(request, "Alert updated successfully.")
        else:
            # Create new alert
            Alert.objects.create(
                user=request.user,
                name=name,
                condition=condition,
                amount=amount,
                status=status,
                category=category
            )
            messages.success(request, "Alert created successfully.")

        return redirect('alerts')  # redirect to alerts page

    return render(request, 'alerts/alerts.html', {
        'alerts': alerts,
        'categories': categories,
    })


@login_required(login_url='login')
def delete_alert(request, pk):
    alert = get_object_or_404(Alert, pk=pk, user=request.user)
    alert.delete()
    messages.success(request, "Alert deleted successfully.")
    return redirect('alerts')
