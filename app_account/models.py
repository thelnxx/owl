import os
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


def turkish_to_ascii(text: str) -> str:
    mapping = str.maketrans({
        "ç": "c", "Ç": "c",
        "ğ": "g", "Ğ": "g",
        "ı": "i", "İ": "i",
        "ö": "o", "Ö": "o",
        "ş": "s", "Ş": "s",
        "ü": "u", "Ü": "u",
    })
    return text.translate(mapping)


def avatar_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    random_key = uuid.uuid4().hex[:12]
    safe_username = turkish_to_ascii(instance.username or "user").lower()
    return f"avatars/{safe_username}_{random_key}{ext}"


hex_color_validator = RegexValidator(
    regex=r"^#[0-9A-Fa-f]{6}$",
    message="Enter a valid 6-digit HEX color code (e.g. #dc3545).",
)


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Role Name")
    slug = models.SlugField(max_length=60, unique=True, verbose_name="System Key")
    bg_color = models.CharField(
        max_length=7,
        default="#6c757d",
        validators=[hex_color_validator],
        verbose_name="Badge Background Color",
    )
    is_privileged = models.BooleanField(
        default=False,
        verbose_name="Staff / Maintenance Bypass",
        help_text="Grants access to /admin/ and allows bypassing maintenance pages.",
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name="Default for New Users",
        help_text="Automatically assigned to newly registered accounts.",
    )
    order = models.PositiveIntegerField(default=10, verbose_name="Display Order")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def save(self, *args, **kwargs):
        self.bg_color = self.bg_color.upper()
        if self.is_default:
            Role.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def text_color(self) -> str:
        """Automatically picks dark or light text based on background brightness."""
        hex_val = self.bg_color.lstrip("#")
        if len(hex_val) != 6:
            return "#ffffff"
        r, g, b = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return "#121417" if luminance > 0.6 else "#ffffff"

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, username=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required.")
        email = self.normalize_email(email)

        if not username:
            username = self.generate_unique_username(name, surname)

        if "role" not in extra_fields or extra_fields["role"] is None:
            extra_fields["role"] = Role.objects.filter(is_default=True).first()

        user = self.model(
            email=email,
            username=username,
            name=name.strip(),
            surname=surname.strip(),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, username=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)

        if "role" not in extra_fields or extra_fields["role"] is None:
            lnx_role, _ = Role.objects.get_or_create(
                slug="lnx",
                defaults={
                    "name": "LnX",
                    "bg_color": "#dc3545",
                    "is_privileged": True,
                    "order": 1,
                },
            )
            extra_fields["role"] = lnx_role

        return self.create_user(email, name, surname, password, username, **extra_fields)

    def generate_unique_username(self, name: str, surname: str) -> str:
        raw = turkish_to_ascii(f"{name}{surname}").lower()
        base = "".join(ch for ch in raw if ch.isalnum()) or "user"
        candidate = base
        counter = 1
        while self.model.objects.filter(username__iexact=candidate).exists():
            candidate = f"{base}{counter}"
            counter += 1
        return candidate


class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=60, verbose_name="First Name")
    surname = models.CharField(max_length=60, verbose_name="Last Name")
    username = models.CharField(max_length=60, unique=True, verbose_name="Username")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="Role",
    )

    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    create_date = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "name", "surname"]

    class Meta:
        ordering = ["-create_date"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    @property
    def is_privileged(self) -> bool:
        return bool(self.is_superuser or (self.role and self.role.is_privileged))

    @property
    def avatar_url(self) -> str:
        if self.avatar and hasattr(self.avatar, "url"):
            return self.avatar.url
        return "/static/img/default-avatar.png"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = CustomUser.objects.generate_unique_username(self.name, self.surname)
        if not self.role_id:
            default_role = Role.objects.filter(is_default=True).first()
            if default_role:
                self.role = default_role
        self.is_staff = self.is_privileged
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role.name if self.role else 'No Role'})"