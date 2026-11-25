from django.contrib import admin
from .models import AppMaintenance, NavbarLink, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_title", "is_maintenance_mode", "maintenance_until", "updated_at")
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AppMaintenance)
class AppMaintenanceAdmin(admin.ModelAdmin):
    list_display = ("display_name", "app_name", "is_under_maintenance", "maintenance_until", "updated_at")
    list_editable = ("is_under_maintenance", "maintenance_until")
    readonly_fields = ("app_name", "updated_at")
    search_fields = ("app_name", "display_name")


@admin.register(NavbarLink)
class NavbarLinkAdmin(admin.ModelAdmin):
    list_display = ("title", "url_name", "app", "order", "is_active", "updated_at")
    list_filter = ("is_active", "app")
    list_editable = ("order", "is_active")
    search_fields = ("title", "url_name")
    readonly_fields = ("updated_at",)
    ordering = ("order", "id")