from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import AiSetting, NewsletterSubscriber


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(ModelAdmin):
    list_display = ("email", "user", "favorite_category", "country_code", "subscribed_at", "is_active")
    list_filter = ("country_code", "favorite_category")
    search_fields = ("email", "user__username", "user__email")
    readonly_fields = ("subscribed_at",)


@admin.register(AiSetting)
class AiSettingAdmin(ModelAdmin):
    list_display = ("__str__", "gemini_model_version", "updated_at")

    def has_add_permission(self, request):
        return not AiSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
