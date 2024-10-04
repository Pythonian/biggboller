from django.urls import include, path

from apps.accounts.views import (
    bettor_dashboard,
)

app_name = "bettor"

urlpatterns = [
    path("dashboard/", bettor_dashboard, name="dashboard"),
]
