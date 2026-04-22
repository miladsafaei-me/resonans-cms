from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import NewsComment, NewsPost, NewsPostTag


class NewsPostTagInline(admin.TabularInline):
    model = NewsPostTag
    extra = 1


@admin.register(NewsPost)
class NewsPostAdmin(ModelAdmin):
    list_display = ("title", "author", "category", "status", "published_at")
    list_filter = ("status", "category")
    search_fields = ("title", "slug", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("author", "category")
    inlines = [NewsPostTagInline]


@admin.register(NewsComment)
class NewsCommentAdmin(ModelAdmin):
    list_display = ("author_name", "news_post", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("author_name", "author_email", "body", "news_post__title")
