from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "resonans_cms.apps.users"
    label = "resonans_cms_users"
    verbose_name = "Users"
