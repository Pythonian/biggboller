from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import Profile
from .models import Wallet, AuditLog


@receiver(post_save, sender=Profile)
def create_user_wallet(sender, instance, created, **kwargs):
    """
    Signal to create a Wallet when a user's email is confirmed.
    """
    # Check if the email has just been confirmed
    if instance.email_confirmed and not hasattr(instance.user, "wallet"):
        # Create a Wallet linked to the user
        wallet = Wallet.objects.create(user=instance.user)

        # Log the wallet creation event in AuditLog
        AuditLog.objects.create(
            wallet=wallet,
            transaction_type=AuditLog.TransactionType.WALLET_CREATION,
            amount=0.00,
            balance_before=0.00,
            balance_after=0.00,
        )
