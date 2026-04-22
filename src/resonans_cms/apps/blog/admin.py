from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Author, Category, Comment, Post, PostTag, Tag


@admin.register(Author)
class AuthorAdmin(ModelAdmin):
    list_display = ("name", "slug", "role", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "email")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "content_scope")
    list_filter = ("content_scope",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class PostTagInline(admin.TabularInline):
    model = PostTag
    extra = 1


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ("title", "author", "category", "status", "published_at")
    list_filter = ("status", "category", "author")
    search_fields = ("title", "slug", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("author", "category")
    inlines = [PostTagInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "status", "published_at")}),
        ("Content", {"fields": ("excerpt", "key_takeaways_markdown_source", "content_markdown_source")}),
        ("Meta", {"fields": ("author", "category", "featured_image_url", "read_time_minutes")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ("author_name", "post", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("author_name", "author_email", "body", "post__title")
    readonly_fields = ("created_at", "updated_at")
