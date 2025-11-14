from ..models import ActivityLog

def log_activity(request, action, model_name=None, object_id=None, description=None):
    ip = request.META.get("HTTP_X_FORWARDED_FOR")
    ip = ip.split(",")[0] if ip else request.META.get("REMOTE_ADDR")

    ActivityLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        model_name=model_name,
        object_id=object_id,
        description=description,
        ip_address=ip,
    )