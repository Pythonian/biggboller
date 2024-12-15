from django.urls import path

from ..views import (
    bettor_groups_all,
    bettor_bundle_detail,
)

app_name = "bettor_groups"

urlpatterns = [
    path("groups/", bettor_groups_all, name="groups_all"),
    path("bundle/<uuid:bundle_id>/", bettor_bundle_detail, name="bundle_detail"),
]
