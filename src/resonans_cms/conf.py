"""
Settings helper: `apply_cms_defaults(globals())` from a Django settings module adds all
Resonans CMS apps, middleware, auth, and context processors with sensible defaults.

Consumers can override any setting by assigning after the call.
"""

from __future__ import annotations

import os
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent
_TEMPLATES_DIR = _PACKAGE_DIR / "templates"
_STATIC_DIR = _PACKAGE_DIR / "static"


def _env_truthy(key: str, default: str = "0") -> bool:
    return os.environ.get(key, default).strip().lower() in ("1", "true", "yes", "on")


DEFAULT_CMS_APPS = (
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "resonans_cms.apps.users",
    "resonans_cms.apps.core",
    "resonans_cms.apps.blog",
    "resonans_cms.apps.news",
    "resonans_cms.apps.linking",
    "resonans_cms.apps.ai_media",
    "resonans_cms.apps.cms_admin",
)

DEFAULT_MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)


def apply_cms_defaults(namespace: dict) -> None:
    """
    Merge Resonans CMS defaults into a Django settings `globals()` dict.

    Existing keys are respected (`setdefault` semantics); apps/middleware are extended
    rather than replaced so downstream projects can add their own.
    """
    apps = list(namespace.get("INSTALLED_APPS", []))
    for app in DEFAULT_CMS_APPS:
        if app not in apps:
            apps.append(app)
    namespace["INSTALLED_APPS"] = apps

    middleware = list(namespace.get("MIDDLEWARE", []))
    for mw in DEFAULT_MIDDLEWARE:
        if mw not in middleware:
            middleware.append(mw)
    namespace["MIDDLEWARE"] = middleware

    namespace.setdefault("AUTH_USER_MODEL", "resonans_cms_users.User")
    namespace.setdefault("SITE_ID", 1)
    namespace.setdefault("DEFAULT_AUTO_FIELD", "django.db.models.BigAutoField")

    namespace.setdefault(
        "AUTHENTICATION_BACKENDS",
        [
            "django.contrib.auth.backends.ModelBackend",
            "allauth.account.auth_backends.AuthenticationBackend",
        ],
    )
    namespace.setdefault("ACCOUNT_LOGIN_METHODS", {"email", "username"})
    namespace.setdefault(
        "ACCOUNT_SIGNUP_FIELDS",
        ["email*", "username*", "password1*", "password2*"],
    )
    namespace.setdefault("ACCOUNT_EMAIL_VERIFICATION", "optional")
    namespace.setdefault("ACCOUNT_ADAPTER", "resonans_cms.apps.users.adapters.AccountAdapter")
    namespace.setdefault(
        "SOCIALACCOUNT_ADAPTER", "resonans_cms.apps.users.adapters.SocialAccountAdapter"
    )
    namespace.setdefault("SOCIALACCOUNT_AUTO_SIGNUP", True)
    namespace.setdefault("SOCIALACCOUNT_QUERY_EMAIL", True)
    namespace.setdefault("SOCIALACCOUNT_EMAIL_REQUIRED", True)
    namespace.setdefault(
        "SOCIALACCOUNT_PROVIDERS",
        {
            "google": {
                "SCOPE": ["profile", "email"],
                "AUTH_PARAMS": {"access_type": "online"},
                "OAUTH_PKCE_ENABLED": True,
            }
        },
    )

    namespace.setdefault("LANGUAGE_CODE", "en-us")
    namespace.setdefault("TIME_ZONE", "UTC")
    namespace.setdefault("USE_I18N", True)
    namespace.setdefault("USE_TZ", True)

    namespace.setdefault(
        "UNFOLD",
        {
            "SITE_TITLE": os.environ.get("CMS_SITE_TITLE", "Resonans CMS"),
            "SITE_HEADER": os.environ.get("CMS_SITE_HEADER", "Resonans"),
            "SITE_ICON": {
                "light": lambda request: "/static/resonans_cms/img/logo-icon.svg",
                "dark": lambda request: "/static/resonans_cms/img/logo-icon.svg",
            },
            "SITE_FAVICONS": [
                {
                    "rel": "icon",
                    "type": "image/svg+xml",
                    "href": lambda request: "/static/resonans_cms/img/favicon.svg",
                },
            ],
            "COLORS": {
                "primary": {
                    "50": "254 242 244",
                    "100": "253 226 229",
                    "200": "251 199 206",
                    "300": "247 160 173",
                    "400": "240 107 129",
                    "500": "228 57 87",
                    "600": "216 5 42",
                    "700": "181 16 40",
                    "800": "152 20 42",
                    "900": "131 21 42",
                    "950": "73 8 17",
                },
            },
            "THEME": "light",
        },
    )

    templates = list(namespace.get("TEMPLATES", []))
    if not templates:
        templates = [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            }
        ]
    dirs = list(templates[0].get("DIRS", []))
    if str(_TEMPLATES_DIR) not in dirs:
        dirs.append(str(_TEMPLATES_DIR))
    templates[0]["DIRS"] = dirs
    namespace["TEMPLATES"] = templates

    staticfiles_dirs = list(namespace.get("STATICFILES_DIRS", []))
    if str(_STATIC_DIR) not in staticfiles_dirs:
        staticfiles_dirs.append(str(_STATIC_DIR))
    namespace["STATICFILES_DIRS"] = staticfiles_dirs
