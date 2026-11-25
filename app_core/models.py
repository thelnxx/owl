from datetime import timedelta
from django.db import models
from django.utils import timezone


def default_maintenance_end():
    """Returns a timestamp 7 days from the moment of record creation."""
    return timezone.now() + timedelta(days=7)


class SiteSettings(models.Model):
    site_title = models.CharField(
        max_length=120,
        default="LnX Platform",
        verbose_name="Site Title",
    )
    site_description = models.TextField(
        default="A modern platform for all your needs.",
        verbose_name="Site Description",
    )
    is_maintenance_mode = models.BooleanField(
        default=False,
        verbose_name="Site-Wide Maintenance Mode",
        help_text="If enabled, non-admin users will see the maintenance page across the entire site.",
    )
    maintenance_title = models.CharField(
        max_length=200,
        default="Scheduled Site Maintenance",
        verbose_name="Maintenance Title",
    )
    maintenance_message = models.TextField(
        default="We are currently performing scheduled upgrades and improvements. Please check back shortly.",
        verbose_name="Maintenance Message",
    )
    maintenance_until = models.DateTimeField(
        default=default_maintenance_end,
        null=True,
        blank=True,
        verbose_name="Estimated Completion Time",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated",
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        status = "MAINTENANCE ON" if self.is_maintenance_mode else "LIVE"
        return f"{self.site_title} [{status}]"

    def save(self, *args, **kwargs):
        self.pk = 1  # Enforce single configuration row
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AppMaintenance(models.Model):
    app_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Django App Name",
        help_text="Automatically discovered from INSTALLED_APPS (e.g., app_articles).",
    )
    display_name = models.CharField(
        max_length=120,
        verbose_name="Display Name",
    )
    is_under_maintenance = models.BooleanField(
        default=False,
        verbose_name="Under Maintenance",
    )
    maintenance_title = models.CharField(
        max_length=200,
        default="Module Under Maintenance",
        verbose_name="Maintenance Title",
    )
    maintenance_message = models.TextField(
        default="This section is temporarily unavailable while we perform updates. Please try again later.",
        verbose_name="Maintenance Message",
    )
    maintenance_until = models.DateTimeField(
        default=default_maintenance_end,
        null=True,
        blank=True,
        verbose_name="Estimated Completion Time",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Updated",
    )

    class Meta:
        ordering = ["app_name"]
        verbose_name = "App Maintenance"
        verbose_name_plural = "App Maintenances"

    def __str__(self):
        state = "Maintenance" if self.is_under_maintenance else "Active"
        return f"{self.display_name} ({self.app_name}) - {state}"


class NavbarLink(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name="Menu Title",
    )
    url_name = models.CharField(
        max_length=150,
        verbose_name="Django URL Name",
        help_text="Format: app_name:url_name (e.g., app_main:index or app_articles:list).",
    )
    app = models.ForeignKey(
        AppMaintenance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="navbar_links",
        verbose_name="Linked App",
        help_text="If the linked app is put under maintenance, this link is disabled automatically.",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active",
        help_text="Uncheck to put only this specific page into maintenance mode.",
    )
    maintenance_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Page Maintenance Message",
        help_text="Optional. Leave blank to use the default site maintenance message.",
    )
    maintenance_until = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Estimated Completion",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last Status Update",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Display Order",
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Navbar Link"
        verbose_name_plural = "Navbar Links"

    def __str__(self):
        return f"{self.title} ({self.url_name})"

    @property
    def is_disabled(self):
        app_blocked = self.app.is_under_maintenance if self.app else False
        return (not self.is_active) or app_blocked