from django.db import models


class UserIntent(models.Model):
    """A user intent with a target URL for internal linking."""

    name = models.CharField(max_length=255, verbose_name="Intent name")
    target_url = models.URLField(max_length=500, unique=True, verbose_name="Target URL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resonans_cms_linking_user_intent"
        verbose_name = "User intent"
        verbose_name_plural = "User intents"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Keyword(models.Model):
    """A keyword phrase tied to a user intent for automated internal linking."""

    intent = models.ForeignKey(
        UserIntent,
        on_delete=models.CASCADE,
        related_name="keywords",
        verbose_name="User intent",
    )
    phrase = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="Keyword phrase",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resonans_cms_linking_keyword"
        verbose_name = "Keyword"
        verbose_name_plural = "Keywords"
        ordering = ["phrase"]

    def __str__(self) -> str:
        return f"{self.phrase} → {self.intent.name}"
