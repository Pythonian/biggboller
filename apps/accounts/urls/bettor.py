from django.urls import path

from apps.accounts.views import (
    bettor_dashboard,
    bettor_bundles_all,
    bettor_profile,
    bettor_settings,
)

app_name = "bettor"

urlpatterns = [
    path("dashboard/", bettor_dashboard, name="dashboard"),
    path("bundles/", bettor_bundles_all, name="bundles_all"),
    path("profile/", bettor_profile, name="profile"),
    path("settings/", bettor_settings, name="settings"),
]
