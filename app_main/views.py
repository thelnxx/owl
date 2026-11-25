from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from .forms import ContactForm

User = get_user_model()


def index_view(request):
    context = {
        "total_members": User.objects.filter(is_active=True).count(),
    }
    return render(request, "main/index.html", context)


def about_view(request):
    return render(request, "main/about.html")


def contact_view(request):
    initial_data = {}
    if request.user.is_authenticated:
        full_name = f"{request.user.name} {request.user.surname}".strip()
        initial_data = {
            "name": full_name or request.user.username,
            "email": request.user.email,
        }

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save(commit=False)
            if request.user.is_authenticated:
                contact_msg.user = request.user
            contact_msg.save()
            messages.success(
                request,
                "Your message has been received. We will review it shortly.",
            )
            return redirect("app_main:contact")
    else:
        form = ContactForm(initial=initial_data)

    return render(request, "main/contact.html", {"form": form})