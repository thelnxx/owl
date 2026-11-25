from django.db.models import Count, Q
from .models import Article, Category


def articles_sidebar_context(request):
    try:
        categories = (
            Category.objects.filter(is_active=True)
            .annotate(
                published_count=Count(
                    "articles",
                    filter=Q(articles__is_published=True),
                )
            )
            .order_by("order", "name")
        )

        random_articles = (
            Article.objects.filter(is_published=True)
            .select_related("category", "author")
            .order_by("?")[:3]
        )

        random_quotes = [
            {
                "title": art.title,
                "slug": art.slug,
                "category": art.category,
                "author": art.author,
                "snippet": art.get_random_snippet(),
            }
            for art in random_articles
        ]
    except Exception:
        categories = []
        random_quotes = []

    return {
        "sidebar_categories": categories,
        "random_article_quotes": random_quotes,
    }