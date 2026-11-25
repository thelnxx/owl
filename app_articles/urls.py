from django.urls import path
from . import views

app_name = "app_articles"

urlpatterns = [
    path("", views.article_list_view, name="list"),
    path("category/<slug:category_slug>/", views.article_list_view, name="category"),
    path("<slug:slug>/", views.article_detail_view, name="detail"),
]