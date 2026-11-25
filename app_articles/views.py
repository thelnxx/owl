from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render
from .models import Article, Category


def article_list_view(request, category_slug=None):
    articles_qs = Article.objects.filter(is_published=True).select_related("category", "author")
    active_category = None

    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        articles_qs = articles_qs.filter(category=active_category)

    search_query = request.GET.get("q", "").strip()
    if search_query:
        articles_qs = articles_qs.filter(
            Q(title__icontains=search_query)
            | Q(summary__icontains=search_query)
            | Q(content__icontains=search_query)
        )

    paginator = Paginator(articles_qs, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "active_category": active_category,
        "search_query": search_query,
    }
    return render(request, "articles/article_list.html", context)


def article_detail_view(request, slug):
    article = get_object_or_404(
        Article.objects.select_related("category", "author"),
        slug=slug,
        is_published=True,
    )

    # Increment views once per session without modifying updated_at
    session_key = f"viewed_article_{article.pk}"
    if not request.session.get(session_key, False):
        Article.objects.filter(pk=article.pk).update(views_count=F("views_count") + 1)
        article.views_count += 1
        request.session[session_key] = True

    related_articles = []
    if article.category:
        related_articles = (
            Article.objects.filter(category=article.category, is_published=True)
            .exclude(pk=article.pk)[:3]
        )

    return render(
        request,
        "articles/article_detail.html",
        {
            "article": article,
            "related_articles": related_articles,
        },
    )