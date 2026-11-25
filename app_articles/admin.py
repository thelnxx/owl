from django.contrib import admin
from .models import Article, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "is_published", "is_featured", "views_count", "created_at", "updated_at")
    list_filter = ("is_published", "is_featured", "category", "created_at")
    list_editable = ("is_published", "is_featured")
    search_fields = ("title", "summary", "content", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("views_count", "created_at", "updated_at")
    autocomplete_fields = ("author",)
    ordering = ("-created_at",)

    fieldsets = (
        ("Article Details", {
            "fields": ("title", "slug", "category", "author", "cover_image"),
        }),
        ("Content", {
            "fields": ("summary", "content"),
        }),
        ("Publishing & Metrics", {
            "fields": ("is_published", "is_featured", "views_count", "created_at", "updated_at"),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)