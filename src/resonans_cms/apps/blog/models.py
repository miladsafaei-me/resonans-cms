import math
import re
import uuid

from django.conf import settings
from django.db import models
from django.utils.html import strip_tags


class ContentScope(models.TextChoices):
    """Whether a Category or Tag applies to blog posts or news articles."""

    BLOG = "blog", "Blog"
    NEWS = "news", "News"


class Author(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cms_author",
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=150, unique=True)
    role = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resonans_cms_blog_author"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    content_scope = models.CharField(
        max_length=10,
        choices=ContentScope.choices,
        default=ContentScope.BLOG,
        db_index=True,
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resonans_cms_blog_category"
        verbose_name = "Topic"
        verbose_name_plural = "Topics"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["slug", "content_scope"],
                name="resonans_cms_category_slug_scope_uniq",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """Shared taxonomy across blog posts and news articles."""

    id = models.BigAutoField(primary_key=True)
    slug = models.SlugField(max_length=120, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resonans_cms_blog_tag"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(blank=True)
    key_takeaways = models.TextField(
        blank=True,
        help_text="Sanitized HTML for public display; generated from Markdown on save.",
    )
    key_takeaways_markdown_source = models.TextField(
        blank=True,
        default="",
        help_text="Markdown source for key takeaways (round-trip).",
    )
    content_raw = models.TextField(
        blank=True,
        default="",
        help_text="Sanitized HTML produced from the Markdown editor (before auto-linking).",
    )
    content_markdown_source = models.TextField(
        blank=True,
        default="",
        help_text="Last Markdown source from the editor (round-trip; not shown publicly).",
    )
    content_rendered = models.TextField(
        blank=True,
        null=True,
        help_text="Final HTML with injected internal links. Populated by the auto-linker task.",
    )
    featured_image_url = models.URLField(max_length=500, blank=True)
    read_time_minutes = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    author = models.ForeignKey(Author, on_delete=models.RESTRICT, related_name="posts")
    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="Topic",
    )
    tags = models.ManyToManyField(Tag, through="PostTag", related_name="posts", blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resonans_cms_blog_post"
        ordering = ["-published_at", "-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_read_time_minutes(self) -> int:
        if self.read_time_minutes and self.read_time_minutes > 0:
            return self.read_time_minutes
        content = self.content_rendered or self.content_raw or ""
        text = strip_tags(content)
        words = len(re.findall(r"\S+", text))
        return max(1, math.ceil(words / 200))

    @property
    def content(self) -> str:
        return self.content_rendered or self.content_raw or ""


class PostTag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_tags")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="post_tags")

    class Meta:
        db_table = "resonans_cms_blog_post_tags"
        unique_together = [["post", "tag"]]


class Comment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        SPAM = "spam", "Spam"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blog_comments",
    )
    author_name = models.CharField(max_length=150, blank=True)
    author_email = models.EmailField(blank=True)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    depth = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resonans_cms_blog_comment"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.author_name or self.user} on {self.post}"
