from django.contrib.auth.backends import BaseBackend

from django.contrib.auth import get_user_model

User = get_user_model()


class EmailAuthenticationBackend(BaseBackend):
    """Authenticate using e-mail account."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        if user.is_active and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
