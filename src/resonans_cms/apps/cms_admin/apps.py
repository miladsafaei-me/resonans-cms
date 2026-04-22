from django.apps import AppConfig


class CmsAdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "resonans_cms.apps.cms_admin"
    label = "resonans_cms_admin"
    verbose_name = "CMS Admin"
