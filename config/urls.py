"""URL configuration for Bigg-Blogger project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(
        "admin/doc/",
        include("django.contrib.admindocs.urls"),
    ),
    path("admin/", admin.site.urls),
    path(
        "administrator/",
        include(
            "apps.accounts.urls.administrator",
            namespace="administrator",
        ),
    ),
    path(
        "administrator/manage/",
        include(
            "apps.groups.urls.administrator",
            namespace="groups",
        ),
    ),
    path(
        "bettor/manage/",
        include(
            "apps.groups.urls.bettor",
            namespace="bettor_groups",
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
        "bettor/wallet/",
        include(
            "apps.wallets.urls",
            namespace="wallet",
        ),
    ),
    path(
        "bettor/",
        include(
            "apps.accounts.urls.bettor",
            namespace="bettor",
        ),
    ),
    path("", include("apps.tickets.urls", namespace="ticket")),
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

admin.site.site_header = "Bigg-Boller Admin"
admin.site.index_title = "Bigg-Boller Admin"
admin.site.site_title = "Bigg-Boller Administration"

handler404 = "apps.core.views.error_404"
handler400 = "apps.core.views.error_400"
handler403 = "apps.core.views.error_403"
handler405 = "apps.core.views.error_405"
handler500 = "apps.core.views.error_500"
