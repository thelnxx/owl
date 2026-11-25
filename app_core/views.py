from django.shortcuts import render
from .models import NavbarLink


def custom_404_view(request, exception=None):
    available_links = [
        link for link in NavbarLink.objects.select_related("app").all()
        if not link.is_disabled
    ]
    return render(
        request,
        "404.html",
        {"requested_path": request.path, "available_links": available_links},
        status=404,
    )
    

def offline_view(request):
    return render(request, "offline.html")