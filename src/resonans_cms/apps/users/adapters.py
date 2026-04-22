from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.utils.text import slugify


def _unique_username(base: str) -> str:
    User = get_user_model()
    candidate = slugify(base)[:150] or "user"
    orig = candidate
    n = 0
    while User.objects.filter(username=candidate).exists():
        n += 1
        candidate = f"{orig}{n}"[:150]
    return candidate


class AccountAdapter(DefaultAccountAdapter):
    """Auto-generate a unique username from email when not provided."""

    def save_user(self, request, user, form, commit=True):
        if not user.username:
            base = user.email.split("@")[0] if user.email else "user"
            user.username = _unique_username(base)
        return super().save_user(request, user, form, commit=commit)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Auto-generate a unique username for social signups (e.g. Google OAuth)."""

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not user.username:
            email = data.get("email") or ""
            name = data.get("name") or ""
            base = email.split("@")[0] if email else name or "user"
            user.username = _unique_username(base)
        return user
