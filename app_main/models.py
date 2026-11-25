from django.conf import settings
from django.db import models


class ContactMessage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_messages",
        verbose_name="Registered User",
    )
    name = models.CharField(max_length=120, verbose_name="Full Name")
    email = models.EmailField(verbose_name="Email Address")
    subject = models.CharField(max_length=200, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Read Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sent At")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        status = "Read" if self.is_read else "Unread"
        return f"[{status}] {self.subject} - {self.email}"