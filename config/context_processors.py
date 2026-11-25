from django.conf import settings


def session_settings(request):
    return {
        "SESSION_COOKIE_AGE": getattr(settings, "SESSION_COOKIE_AGE", 14400),
        "ADMIN_URL": getattr(settings, "ADMIN_URL", "admin/"),
    }