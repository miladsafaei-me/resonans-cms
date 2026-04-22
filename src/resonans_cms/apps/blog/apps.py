from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "resonans_cms.apps.blog"
    label = "resonans_cms_blog"
    verbose_name = "Blog"

    def ready(self):
        from . import signals  # noqa: F401
