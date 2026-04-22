"""
Demo Django project settings for Resonans CMS.

Uses SQLite by default so the demo runs with zero external services. A `.env` file
at the repo root is loaded automatically if present.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent

load_dotenv(REPO_ROOT / ".env")

DEBUG = os.environ.get("DJANGO_DEBUG", "1").strip() in ("1", "true", "yes", "on")
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "demo-secret-key-do-not-use-in-production-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
).strip()
ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

ROOT_URLCONF = "demo_project.urls"
WSGI_APPLICATION = "demo_project.wsgi.application"

from resonans_cms.conf import apply_cms_defaults

apply_cms_defaults(globals())

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

ACCOUNT_FORMS = {
    "login": "resonans_cms.apps.users.forms.CustomLoginForm",
    "signup": "resonans_cms.apps.users.forms.CustomSignupForm",
}

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/cms/"
LOGOUT_REDIRECT_URL = "/"

EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@example.com")

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
