"""Django settings for config project."""

from pathlib import Path
from decouple import Csv, config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")

DEBUG = config("DEBUG", cast=bool, default=True)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default=["localhost"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
    "apps.accounts.apps.AccountsConfig",
    "apps.core.apps.CoreConfig",
    "widget_tweaks",
    "paystack.frameworks.django",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

SITE_ID = 1

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "libraries": {
                "paystack": "paystack.frameworks.django.templatetags.paystack",
            },
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {"default": dj_database_url.parse(config("DATABASE_URL"))}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Lagos"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "assets"

STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "media/"

MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "core:dashboard"
LOGOUT_REDIRECT_URL = "core:home"
LOGIN_URL = "auth:login"
LOGOUT_URL = "auth:logout"

ADMINS = (("Admin", "admin@example.com"),)

PAYSTACK_PUBLIC_KEY = config("PAYSTACK_PUBLIC_KEY")
PAYSTACK_SECRET_KEY = config("PAYSTACK_SECRET_KEY")

# Email server configuration
EMAIL_BACKEND = config("EMAIL_BACKEND")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")
MAILJET_API_KEY = config("MJ_APIKEY_PUBLIC")
MAILJET_SECRET_KEY = config("MJ_APIKEY_PRIVATE")
MAILJET_SENDER_NAME = config("MAILJET_SENDER_NAME")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "apps.accounts.utils": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "apps.accounts.authentication.EmailAuthenticationBackend",
]
