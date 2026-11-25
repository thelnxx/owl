from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "user", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    list_editable = ("is_read",)
    search_fields = ("subject", "name", "email", "message")
    readonly_fields = ("user", "name", "email", "subject", "message", "created_at")
    ordering = ("-created_at",)