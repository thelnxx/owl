from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

app_name = "app_account"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit_view, name="profile_edit"),
    path("check-username/", views.check_username_view, name="check_username"),

    # Forgot Password Flow
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="account/password_reset.html",
            form_class=CustomPasswordResetForm,
            email_template_name="account/password_reset_email.html",
            subject_template_name="account/password_reset_subject.txt",
            success_url=reverse_lazy("app_account:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="account/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="account/password_reset_confirm.html",
            form_class=CustomSetPasswordForm,
            success_url=reverse_lazy("app_account:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="account/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
]