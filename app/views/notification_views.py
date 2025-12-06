from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Notification
from django.http import JsonResponse

@login_required
def notifications_view(request):
    filter_option = request.GET.get('filter')

    notifications = Notification.objects.filter(user=request.user)

    if filter_option == "unread":
        notifications = notifications.filter(is_read=False)

    unread_count = notifications.filter(is_read=False).count()

    return render(request, 'notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
        'filter_option': filter_option,
    })

@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'ok'})

    # return redirect('notifications')

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications')

@login_required
def delete_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.delete()
    return redirect('notifications')


def create_notification(user, title, message):
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        is_read=False
    )