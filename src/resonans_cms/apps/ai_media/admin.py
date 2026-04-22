from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import GeneratedImage


@admin.register(GeneratedImage)
class GeneratedImageAdmin(ModelAdmin):
    list_display = ("kind", "model_name", "created_by", "created_at")
    list_filter = ("kind", "model_name")
    search_fields = ("prompt", "image_url")
    readonly_fields = ("created_at",)
