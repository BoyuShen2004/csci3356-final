def perch_context(request):
    from django.conf import settings
    profile = None
    unread_count = 0
    display_first_name = ""
    display_last_name = ""
    perch_admin_email = (getattr(settings, "PERCH_ADMIN_EMAIL", None) or "").strip()
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            if profile and profile.role == "admin":
                display_first_name = "Admin"
                display_last_name = "User"
            else:
                display_first_name = request.user.first_name
                display_last_name = request.user.last_name
        except Exception:
            display_first_name = request.user.first_name
            display_last_name = request.user.last_name
        from .models import Message
        unread_count = Message.objects.filter(receiver=request.user, read=False).count()
    return {
        "profile": profile,
        "unread_count": unread_count,
        "display_first_name": display_first_name,
        "display_last_name": display_last_name,
        "perch_admin_email": perch_admin_email,
    }
