from django.contrib.auth import views as auth_views
from django.urls import include, path

app_name = "auth"

urlpatterns = [
    path("", include("django.contrib.auth.urls")),
]
