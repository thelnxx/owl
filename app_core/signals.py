from django.apps import apps
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.urls import URLPattern, URLResolver, get_resolver
from .models import AppMaintenance, NavbarLink, SiteSettings

EXCLUDED_APPS = {"app_core", "app_account"}


def _discover_static_routes(url_patterns, local_apps_map, current_namespace=None):
    """
    Recursively inspects Django's URLConf and yields parameter-free routes
    belonging to local content applications.
    """
    discovered = []

    for entry in url_patterns:
        if isinstance(entry, URLResolver):
            ns = entry.namespace or current_namespace
            discovered.extend(
                _discover_static_routes(entry.url_patterns, local_apps_map, ns)
            )
        elif isinstance(entry, URLPattern):
            if not current_namespace or current_namespace not in local_apps_map:
                continue
            if not entry.name:
                continue
            # Skip dynamic routes requiring URL parameters (e.g. <slug:slug>, <int:pk>)
            if getattr(entry.pattern, "converters", None):
                continue

            full_url_name = f"{current_namespace}:{entry.name}"

            # Generate a clean human-readable title automatically
            if current_namespace == "app_main" and entry.name in {"index", "home"}:
                title = "Home"
                default_order = 1
            elif entry.name in {"index", "list"}:
                title = current_namespace.replace("app_", "").replace("_", " ").title()
                default_order = 10
            else:
                title = entry.name.replace("_", " ").title()
                default_order = 20

            discovered.append(
                {
                    "app_name": current_namespace,
                    "url_name": full_url_name,
                    "title": title,
                    "order": default_order,
                }
            )

    return discovered


@receiver(post_migrate)
def setup_core_defaults(sender, **kwargs):
    if sender.name != "app_core":
        return

    # 1. Tekil SiteSettings kaydını garanti altına al
    SiteSettings.load()

    # 2. Proje dizinindeki yerel uygulamaları keşfet ve AppMaintenance tablosuna kaydet
    local_apps_map = {}
    model_fields = {f.name for f in AppMaintenance._meta.get_fields()}

    for app_config in apps.get_app_configs():
        app_label = app_config.label
        if app_config.name.startswith("django.") or app_label in EXCLUDED_APPS:
            continue

        if str(settings.BASE_DIR) not in str(app_config.path):
            continue

        defaults = {}
        pretty_name = app_label.replace("app_", "").replace("_", " ").title()
        if "display_name" in model_fields:
            defaults["display_name"] = pretty_name
        elif "title" in model_fields:
            defaults["title"] = pretty_name

        app_obj, _ = AppMaintenance.objects.get_or_create(
            app_name=app_label,
            defaults=defaults,
        )
        local_apps_map[app_label] = app_obj

    # 3. urls.py dosyalarındaki parametresiz tüm rotaları otomatik olarak NavbarLink tablosuna ekle
    resolver = get_resolver()
    routes = _discover_static_routes(resolver.url_patterns, local_apps_map)

    for index, route in enumerate(routes, start=1):
        NavbarLink.objects.get_or_create(
            url_name=route["url_name"],
            defaults={
                "title": route["title"],
                "app": local_apps_map.get(route["app_name"]),
                "order": route["order"] + index,
                "is_active": True,
            },
        )