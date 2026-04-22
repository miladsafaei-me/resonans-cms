from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Keyword, UserIntent


class KeywordInline(admin.TabularInline):
    model = Keyword
    extra = 1


@admin.register(UserIntent)
class UserIntentAdmin(ModelAdmin):
    list_display = ("name", "target_url", "created_at")
    search_fields = ("name", "target_url")
    inlines = [KeywordInline]


@admin.register(Keyword)
class KeywordAdmin(ModelAdmin):
    list_display = ("phrase", "intent", "created_at")
    list_filter = ("intent",)
    search_fields = ("phrase", "intent__name")
    autocomplete_fields = ("intent",)
