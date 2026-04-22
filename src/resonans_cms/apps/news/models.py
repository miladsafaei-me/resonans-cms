import math
import re
import uuid

from django.conf import settings
from django.db import models
from django.utils.html import strip_tags

from resonans_cms.apps.blog.models import Author, Category, ContentScope, Tag


class NewsPost(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(blank=True)
    key_takeaways = models.TextField(blank=True)
    key_takeaways_markdown_source = models.TextField(blank=True, default="")
    content_raw = models.TextField(blank=True, default="")
    content_markdown_source = models.TextField(blank=True, default="")
    content_rendered = models.TextField(blank=True, null=True)
    featured_image_url = models.URLField(max_length=500, blank=True)
    read_time_minutes = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    author = models.ForeignKey(Author, on_delete=models.RESTRICT, related_name="news_posts")
    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="news_posts",
        limit_choices_to={"content_scope": ContentScope.NEWS},
        verbose_name="Topic",
    )
    tags = models.ManyToManyField(Tag, through="NewsPostTag", related_name="news_posts", blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resonans_cms_news_post"
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


class NewsPostTag(models.Model):
    news_post = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name="news_post_tags")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="news_post_tags")

    class Meta:
        db_table = "resonans_cms_news_post_tags"
        unique_together = [["news_post", "tag"]]


class NewsComment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        SPAM = "spam", "Spam"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    news_post = models.ForeignKey(NewsPost, on_delete=models.CASCADE, related_name="comments")
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
        related_name="news_comments",
    )
    author_name = models.CharField(max_length=150, blank=True)
    author_email = models.EmailField(blank=True)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    depth = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resonans_cms_news_comment"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"Comment by {self.author_name or self.user} on {self.news_post}"
