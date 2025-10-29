from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Alert

@login_required(login_url='login')
def alerts(request):
    alert_list = Alert.objects.filter(user=request.user)
    return render(request, 'alerts/alerts.html', {
        'alerts': alert_list
    })
