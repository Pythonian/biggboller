from django.urls import reverse
from django.shortcuts import redirect


class BettorOnboardingMiddleware:
    """Middleware to enforce mandatory transaction PIN and bank info for bettors"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            profile = getattr(request.user, "profile", None)

            # Consider bettors as non-staff/non-superuser with a Profile
            if (
                profile
                and not request.user.is_staff
                and not request.user.is_superuser
                and not (profile.transaction_pin and profile.payout_information)
            ):
                allowed_paths = [
                    reverse("bettor:onboarding_form"),
                    reverse("auth:logout"),
                ]
                if request.path not in allowed_paths:
                    return redirect("bettor:onboarding_form")

        response = self.get_response(request)
        return response
