from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import render
from .models import AppMaintenance, NavbarLink, SiteSettings


def can_bypass_maintenance(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    return bool(getattr(user, "is_privileged", False))


class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_prefix = f"/{settings.ADMIN_URL.strip('/')}/"

    def __call__(self, request):
        path = request.path

        # Allow static and media files
        if path.startswith(settings.STATIC_URL) or path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        # Restrict /admin/ strictly to LnX, Admin, and Moderator roles
        if path.startswith(self.admin_prefix):
            if request.user.is_authenticated and not can_bypass_maintenance(request.user):
                return HttpResponseForbidden("403 Forbidden - Insufficient privileges.")
            return self.get_response(request)

        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path

        if (
            path.startswith(settings.STATIC_URL)
            or path.startswith(settings.MEDIA_URL)
            or path.startswith(self.admin_prefix)
            or path in {"/offline/", "/sw.js"}
        ):
            return None

        # Privileged roles bypass all maintenance restrictions
        if can_bypass_maintenance(request.user):
            return None

        resolver_match = getattr(request, "resolver_match", None)
        view_name = resolver_match.view_name if resolver_match else ""
        app_name = resolver_match.app_name if resolver_match else ""

        # Keep auth & password reset endpoints accessible during site-wide maintenance
        auth_exempt_views = {
            "app_account:login",
            "app_account:logout",
            "app_account:password_reset",
            "app_account:password_reset_done",
            "app_account:password_reset_confirm",
            "app_account:password_reset_complete",
            "login",
            "logout",
        }
        if view_name in auth_exempt_views:
            return None

        # 1. Check Site-Wide Maintenance Mode
        site_settings = SiteSettings.load()
        if site_settings.is_maintenance_mode:
            return render(
                request,
                "maintenance.html",
                {
                    "maintenance_title": site_settings.maintenance_title,
                    "maintenance_message": site_settings.maintenance_message,
                    "maintenance_until": site_settings.maintenance_until,
                    "updated_at": site_settings.updated_at,
                    "is_site_wide": True,
                },
                status=503,
            )

        # 2. Check App-Level Maintenance Mode
        if app_name:
            app_maint = AppMaintenance.objects.filter(
                app_name=app_name, is_under_maintenance=True
            ).first()
            if app_maint:
                return render(
                    request,
                    "maintenance.html",
                    {
                        "maintenance_title": app_maint.maintenance_title,
                        "maintenance_message": app_maint.maintenance_message,
                        "maintenance_until": app_maint.maintenance_until,
                        "updated_at": app_maint.updated_at,
                        "is_site_wide": False,
                    },
                    status=503,
                )

        # 3. Check Single NavbarLink / Page Maintenance Mode
        if view_name:
            disabled_link = NavbarLink.objects.filter(
                url_name=view_name, is_active=False
            ).first()
            if disabled_link:
                return render(
                    request,
                    "maintenance.html",
                    {
                        "maintenance_title": f"{disabled_link.title} - Under Maintenance",
                        "maintenance_message": disabled_link.maintenance_message or site_settings.maintenance_message,
                        "maintenance_until": disabled_link.maintenance_until or site_settings.maintenance_until,
                        "updated_at": disabled_link.updated_at,
                        "is_site_wide": False,
                    },
                    status=503,
                )

        return None