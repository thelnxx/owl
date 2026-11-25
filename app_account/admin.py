from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Role
from .widgets import RoleColorPickerWidget


class RoleAdminForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = "__all__"
        widgets = {
            "bg_color": RoleColorPickerWidget(),
        }


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    form = RoleAdminForm
    list_display = ("name", "slug", "badge_preview", "is_privileged", "is_default", "order")
    list_editable = ("is_privileged", "is_default", "order")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")

    @admin.display(description="Color Badge")
    def badge_preview(self, obj):
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 3px 10px; '
            'border-radius: 6px; font-weight: 600; font-size: 12px;">{}</span>',
            obj.bg_color,
            obj.text_color,
            obj.name,
        )


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "name", "surname", "role_badge", "is_email_verified", "is_active")
    list_filter = ("role", "is_email_verified", "is_active")
    search_fields = ("username", "email", "name", "surname")
    ordering = ("-create_date",)

    fieldsets = (
        ("Credentials", {"fields": ("username", "email", "password")}),
        ("Personal Info", {"fields": ("name", "surname", "avatar")}),
        ("Role & Permissions", {"fields": ("role", "is_email_verified", "is_active", "is_staff", "is_superuser")}),
        ("Dates", {"fields": ("last_login", "create_date")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "surname", "username", "role", "password1", "password2"),
        }),
    )

    @admin.display(description="Role")
    def role_badge(self, obj):
        if not obj.role:
            return "-"
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 2px 8px; '
            'border-radius: 5px; font-weight: 600; font-size: 11px;">{}</span>',
            obj.role.bg_color,
            obj.role.text_color,
            obj.role.name,
        )