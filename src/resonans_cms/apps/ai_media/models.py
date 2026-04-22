import uuid

from django.conf import settings
from django.db import models


class GeneratedImage(models.Model):
    """Audit record for AI-generated images (featured or inline)."""

    class Kind(models.TextChoices):
        HERO = "hero", "Hero / Featured"
        INLINE = "inline", "Inline"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.HERO)
    prompt = models.TextField()
    model_name = models.CharField(max_length=128, blank=True)
    image_url = models.URLField(max_length=1024, blank=True)
    aspect_ratio = models.CharField(max_length=8, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_images",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "resonans_cms_ai_media_generated_image"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.kind} image ({self.created_at:%Y-%m-%d})"
