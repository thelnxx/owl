import os
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST
from .forms import LoginForm, ProfileUpdateForm, RegisterForm
from .models import CustomUser


@require_GET
def check_username_view(request):
    username = request.GET.get("username", "").strip()
    if not username:
        return JsonResponse({
            "available": True,
            "is_empty": True,
            "message": "Leave blank to auto-generate from your first and last name.",
        })

    qs = CustomUser.objects.filter(username__iexact=username)
    if request.user.is_authenticated:
        qs = qs.exclude(pk=request.user.pk)

    if qs.exists():
        return JsonResponse({
            "available": False,
            "is_empty": False,
            "message": f"'{username}' is already taken.",
        })
    return JsonResponse({
        "available": True,
        "is_empty": False,
        "message": f"'{username}' is available.",
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect("app_account:profile")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome, {user.name}! Your account has been created with username '{user.username}'.",
            )
            return redirect("app_account:profile")
    else:
        form = RegisterForm()

    return render(request, "account/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("app_account:profile")

    if request.method == "POST":
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get("next") or "app_account:profile"
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, "account/login.html", {"form": form})


@require_POST
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": "logged_out"})

    messages.info(request, "You have been logged out securely.")
    return redirect("app_account:login")


@login_required
def profile_view(request):
    return render(request, "account/profile.html", {"profile_user": request.user})


@login_required
def profile_edit_view(request):
    old_avatar_path = (
        request.user.avatar.path
        if request.user.avatar and os.path.isfile(request.user.avatar.path)
        else None
    )

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            updated_user = form.save()
            if (
                "avatar" in request.FILES
                and old_avatar_path
                and updated_user.avatar
                and old_avatar_path != updated_user.avatar.path
                and os.path.isfile(old_avatar_path)
            ):
                os.remove(old_avatar_path)

            messages.success(request, "Your profile has been updated.")
            return redirect("app_account:profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "account/profile_edit.html", {"form": form})