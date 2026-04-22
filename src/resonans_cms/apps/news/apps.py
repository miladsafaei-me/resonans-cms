from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "resonans_cms.apps.news"
    label = "resonans_cms_news"
    verbose_name = "News"

    def ready(self):
        from . import signals  # noqa: F401
