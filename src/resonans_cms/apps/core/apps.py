from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "resonans_cms.apps.core"
    label = "resonans_cms_core"
    verbose_name = "CMS Core"
