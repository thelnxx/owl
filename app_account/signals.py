from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role


@receiver(post_migrate)
def seed_default_roles(sender, **kwargs):
    if sender.name != "app_account":
        return

    default_roles = [
        {"slug": "lnx", "name": "LnX", "bg_color": "#dc3545", "is_privileged": True, "is_default": False, "order": 1},
        {"slug": "admin", "name": "Admin", "bg_color": "#f59e0b", "is_privileged": True, "is_default": False, "order": 2},
        {"slug": "moderator", "name": "Moderator", "bg_color": "#0ea5e9", "is_privileged": True, "is_default": False, "order": 3},
        {"slug": "member", "name": "Member", "bg_color": "#6c757d", "is_privileged": False, "is_default": True, "order": 100},
    ]

    for item in default_roles:
        Role.objects.get_or_create(
            slug=item["slug"],
            defaults={
                "name": item["name"],
                "bg_color": item["bg_color"],
                "is_privileged": item["is_privileged"],
                "is_default": item["is_default"],
                "order": item["order"],
            },
        )