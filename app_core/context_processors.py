from .models import NavbarLink, SiteSettings


def core_context(request):
    return {
        "site_settings": SiteSettings.load(),
        "navbar_links": NavbarLink.objects.select_related("app").all(),
    }