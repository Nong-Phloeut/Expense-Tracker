# logs/views.py
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from ..models import ActivityLog
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from app.utils.activity_log import log_activity 

@login_required(login_url='login')
# @permission_re quired('logs.view_activitylog', raise_exception=True)
def activity_log_list(request):
    logs = ActivityLog.objects.select_related('user').all()

    # Optional filtering (e.g. by user or action)
    search_user = request.GET.get('user')
    if search_user:
        logs = logs.filter(user__username__icontains=search_user)

    paginator = Paginator(logs, 10)  # Show 10 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'logs/activity_log_list.html', context)


@login_required
def delete_log(request, pk):
    log = get_object_or_404(ActivityLog, pk=pk)
    log.delete()

    # Meta-log: record deletion
    log_activity(
        request,
        action="DELETE",
        model_name="ActivityLog",
        object_id=pk,
        description=f"Deleted audit log entry #{pk}"
    )

    messages.success(request, "Audit log entry deleted successfully.")
    return redirect('activity_log')
