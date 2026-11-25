import os
import random
import uuid
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def turkish_slugify(text: str) -> str:
    tr_map = str.maketrans({
        "ç": "c", "Ç": "c",
        "ğ": "g", "Ğ": "g",
        "ı": "i", "İ": "i",
        "ö": "o", "Ö": "o",
        "ş": "s", "Ş": "s",
        "ü": "u", "Ü": "u",
    })
    return slugify(text.translate(tr_map))


def article_cover_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    base = instance.slug or turkish_slugify(instance.title) or "cover"
    return f"articles/covers/{base}_{uuid.uuid4().hex[:8]}{ext}"


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Category Name")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.CharField(max_length=255, blank=True, verbose_name="Short Description")
    icon = models.CharField(
        max_length=60,
        default="fa-solid fa-folder",
        help_text="Font Awesome icon class (e.g. fa-solid fa-code, fa-brands fa-linux)",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Display Order")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = turkish_slugify(self.name) or "category"
            slug = base_slug
            counter = 2
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("app_articles:category", kwargs={"category_slug": self.slug})

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=220, verbose_name="Article Title")
    slug = models.SlugField(max_length=440, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name="Category",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name="Author",
    )
    summary = models.TextField(
        max_length=400,
        blank=True,
        verbose_name="Short Summary",
        help_text="Optional. Auto-generated from content if left empty.",
    )
    content = models.TextField(
        verbose_name="Article Content",
        max_length=2048,
        )
    cover_image = models.ImageField(
        upload_to=article_cover_upload_path,
        blank=True,
        null=True,
        verbose_name="Cover Image",
    )
    views_count = models.PositiveIntegerField(default=0, verbose_name="Views")
    is_published = models.BooleanField(default=True, verbose_name="Published")
    is_featured = models.BooleanField(default=False, verbose_name="Featured")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Published At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = turkish_slugify(self.title) or "article"
            slug = base_slug
            counter = 2
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if not self.summary and self.content:
            clean_text = " ".join(self.content.split())
            self.summary = clean_text[:220] + ("..." if len(clean_text) > 220 else "")

        super().save(*args, **kwargs)

    @property
    def is_edited(self) -> bool:
        """Returns True only if the article was edited after initial creation."""
        if not self.created_at or not self.updated_at:
            return False
        return (self.updated_at - self.created_at).total_seconds() > 2

    @property
    def reading_time(self) -> int:
        words = len(self.content.split())
        return max(1, round(words / 200))

    def get_random_snippet(self) -> str:
        """Extracts a random paragraph/sentence snippet for the right sidebar."""
        paragraphs = [p.strip() for p in self.content.splitlines() if len(p.strip()) >= 35]
        if paragraphs:
            chosen = random.choice(paragraphs)
            return chosen[:140] + ("..." if len(chosen) > 140 else "")
        if self.summary:
            return self.summary[:140] + ("..." if len(self.summary) > 140 else "")
        return self.title

    def get_absolute_url(self):
        return reverse("app_articles:detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title