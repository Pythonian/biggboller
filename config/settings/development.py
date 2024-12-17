from .base import *
from decouple import Csv

DEBUG = True

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
