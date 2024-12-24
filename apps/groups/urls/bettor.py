from django.urls import path

from ..views import (
    bettor_groups_all,
    bettor_groups_available,
    bettor_bundle_detail,
    bettor_bundles_owned,
    bettor_bundles_purchase,
    bettor_bundle_purchase_pin,
    bettor_purchase_successful,
)

app_name = "bettor_groups"

urlpatterns = [
    path("bundles/owned/", bettor_bundles_owned, name="bundles_owned"),
    path("groups/available/", bettor_groups_available, name="groups_available"),
    path(
        "bundles/purchase/<uuid:bundle_id>/",
        bettor_bundles_purchase,
        name="bundles_detail",
    ),
    path(
        "bundles/purchase-pin/",
        bettor_bundle_purchase_pin,
        name="bundle_purchase_pin",
    ),
    path(
        "bundles/purchase/<uuid:purchase_id>/successful/",
        bettor_purchase_successful,
        name="purchase_successful",
    ),
    path("groups/", bettor_groups_all, name="groups_all"),
    path("bundle/<uuid:bundle_id>/", bettor_bundle_detail, name="bundle_detail"),
]
