"""
URL configuration for config project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "administrator/",
        include(
            "apps.accounts.urls.administrator",
            namespace="administrator",
        ),
    ),
    path(
        "auth/",
        include(
            "apps.accounts.urls.auth",
            namespace="auth",
        ),
    ),
    path(
        "bettor/",
        include(
            "apps.accounts.urls.bettor",
            namespace="bettor",
        ),
    ),
    path("", include("apps.core.urls", namespace="core")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
