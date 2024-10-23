from django.urls import path

from .views import home, dashboard

app_name = "core"

urlpatterns = [
    path("dashboard/", dashboard, name="dashboard"),
    path("", home, name="home"),
]
