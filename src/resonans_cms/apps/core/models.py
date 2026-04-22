from typing import Any

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class NewsletterSubscriber(models.Model):
    """Newsletter subscriber. Email always stored; user linked when logged in or matched."""

    email = models.EmailField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="newsletter_subscriptions",
    )
    country_code = models.CharField(
        max_length=2,
        blank=True,
        help_text="ISO 3166-1 alpha-2 country code (optional).",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    favorite_category = models.ForeignKey(
        "resonans_cms_blog.Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="newsletter_subscribers",
        help_text="Topic inferred from the page where the user subscribed.",
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "resonans_cms_core_newsletter_subscriber"
        ordering = ["-subscribed_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=Q(unsubscribed_at__isnull=True),
                name="resonans_cms_active_subscriber_email_uniq",
            )
        ]
        verbose_name = "Newsletter subscriber"
        verbose_name_plural = "Newsletter subscribers"

    def __str__(self) -> str:
        return self.email

    @property
    def is_active(self) -> bool:
        return self.unsubscribed_at is None


class AiSetting(models.Model):
    """Singleton configuration for text and image AI pipelines (row id is always 1)."""

    class GeminiModelVersion(models.TextChoices):
        GEMINI_FLASH_LATEST = "gemini-flash-latest", "gemini-flash-latest"
        GEMINI_PRO_LATEST = "gemini-pro-latest", "gemini-pro-latest"

    class ImageAiModelVersion(models.TextChoices):
        GEMINI_25_FLASH_IMAGE = "gemini-2.5-flash-image", "gemini-2.5-flash-image"
        IMAGEN_40_ULTRA = "imagen-4.0-ultra-generate-001", "imagen-4.0-ultra-generate-001"

    class AspectRatio(models.TextChoices):
        R_16_9 = "16:9", "16:9"
        R_4_3 = "4:3", "4:3"
        R_1_1 = "1:1", "1:1"

    gemini_api_key = models.CharField(max_length=512, blank=True, default="")
    gemini_use_paid_api = models.BooleanField(default=False)
    gemini_paid_api_key = models.CharField(max_length=512, blank=True, default="")
    text_ai_endpoint_url = models.URLField(max_length=2048, blank=True, default="")
    gemini_model_version = models.CharField(
        max_length=64,
        choices=GeminiModelVersion.choices,
        default=GeminiModelVersion.GEMINI_FLASH_LATEST,
    )
    system_meta_prompt = models.TextField(blank=True, default="")
    gemini_temperature = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
    )
    image_ai_api_key = models.CharField(max_length=512, blank=True, default="")
    image_ai_use_paid_api = models.BooleanField(default=False)
    image_ai_paid_api_key = models.CharField(max_length=512, blank=True, default="")
    image_ai_endpoint_url = models.URLField(max_length=2048, blank=True, default="")
    hero_image_model = models.CharField(
        max_length=64,
        choices=ImageAiModelVersion.choices,
        default=ImageAiModelVersion.GEMINI_25_FLASH_IMAGE,
    )
    inline_image_model = models.CharField(
        max_length=64,
        choices=ImageAiModelVersion.choices,
        default=ImageAiModelVersion.IMAGEN_40_ULTRA,
    )
    hero_image_system_prompt = models.TextField(blank=True, default="")
    inline_image_system_prompt = models.TextField(blank=True, default="")
    default_aspect_ratio = models.CharField(
        max_length=8,
        choices=AspectRatio.choices,
        default=AspectRatio.R_16_9,
    )
    default_primary_color = models.CharField(max_length=7, default="#111827")
    default_secondary_color = models.CharField(max_length=7, default="#2563EB")
    auto_generate_on_save = models.BooleanField(default=False)
    images_upload_path = models.CharField(max_length=1024, blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resonans_cms_core_ai_setting"
        verbose_name = "AI setting"
        verbose_name_plural = "AI settings"

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "AiSetting":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def resolved_gemini_api_key(self) -> str:
        paid = (self.gemini_paid_api_key or "").strip()
        if self.gemini_use_paid_api and paid:
            return paid
        return (self.gemini_api_key or "").strip()

    def resolved_image_ai_api_key(self) -> str:
        paid = (self.image_ai_paid_api_key or "").strip()
        if self.image_ai_use_paid_api and paid:
            return paid
        return (self.image_ai_api_key or "").strip()

    def __str__(self) -> str:
        return "AI settings"
