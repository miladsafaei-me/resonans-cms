from django.apps import AppConfig


class LinkingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "resonans_cms.apps.linking"
    label = "resonans_cms_linking"
    verbose_name = "Internal Linking"
