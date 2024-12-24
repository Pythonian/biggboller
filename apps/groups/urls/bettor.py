from django.urls import path

from ..views import (
    bettor_groups_all,
    bettor_groups_available,
    bettor_bundle_detail,
    bettor_bundles_owned,
)

app_name = "bettor_groups"

urlpatterns = [
    path("bundles/owned/", bettor_bundles_owned, name="bundles_owned"),
    path("groups/available/", bettor_groups_available, name="groups_available"),
    path("groups/", bettor_groups_all, name="groups_all"),
    path("bundle/<uuid:bundle_id>/", bettor_bundle_detail, name="bundle_detail"),
]
