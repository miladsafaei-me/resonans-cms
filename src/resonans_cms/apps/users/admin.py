from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin

from .models import Role, User, UserRole


@admin.action(description="Activate selected users")
def activate_users(modeladmin, request, queryset):
    n = queryset.update(is_active=True)
    messages.success(request, f"{n} user(s) activated.")


@admin.action(description="Deactivate selected users")
def deactivate_users(modeladmin, request, queryset):
    n = queryset.exclude(pk=request.user.pk).exclude(is_superuser=True).update(is_active=False)
    messages.success(request, f"{n} user(s) deactivated.")


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = ("username", "email", "slug", "is_staff", "is_active")
    search_fields = ("username", "email", "slug")
    ordering = ("-date_joined",)
    filter_horizontal = ("groups", "user_permissions")
    actions = [activate_users, deactivate_users, "delete_selected"]

    fieldsets = BaseUserAdmin.fieldsets + (
        ("CMS Profile", {"fields": ("slug", "bio", "avatar_url", "social_links")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("CMS Profile", {"fields": ("slug", "bio", "avatar_url", "social_links")}),
    )


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ("name", "codename", "group")
    search_fields = ("name", "codename")


@admin.register(UserRole)
class UserRoleAdmin(ModelAdmin):
    list_display = ("user", "role", "assigned_at")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email", "role__name")
    autocomplete_fields = ("user", "role")
