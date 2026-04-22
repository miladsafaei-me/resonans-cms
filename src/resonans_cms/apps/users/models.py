import uuid

from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    social_links = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resonans_cms_users_user"

    def save(self, *args, **kwargs):
        if not self.slug and self.username:
            self.slug = self.username[:150]
        super().save(*args, **kwargs)


class Role(models.Model):
    """
    A named permission bundle. Each role maps to a Django ``Group`` so built-in permission
    checks (``user.has_perm``, ``@permission_required``) keep working unchanged.
    """

    name = models.CharField(max_length=100, unique=True)
    codename = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="cms_role",
        help_text="Django auth Group that backs this role's permissions.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "resonans_cms_users_role"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class UserRole(models.Model):
    """Through-model assigning a role to a user. Keeps the user's Group membership in sync."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "resonans_cms_users_user_role"
        unique_together = [["user", "role"]]
        ordering = ["-assigned_at"]

    def __str__(self) -> str:
        return f"{self.user} → {self.role}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.user.groups.add(self.role.group)

    def delete(self, *args, **kwargs):
        group = self.role.group
        super().delete(*args, **kwargs)
        if not UserRole.objects.filter(user=self.user, role__group=group).exists():
            self.user.groups.remove(group)
