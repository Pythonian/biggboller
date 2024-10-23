from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.accounts.models.auth import Profile
from django.shortcuts import get_object_or_404
from paystack.api.signals import payment_verified
from apps.accounts.models import Deposit

from .tasks import payment_successful_email
from apps.accounts.utils import create_action


@receiver(payment_verified)
def on_payment_verified(sender, ref, amount, order, **kwargs):
    """
    ref: paystack reference sent back.
    amount: amount in Naira.
    order: paystack id tied to the user.
    """
    # Fetch the deposit record using the paystack_id
    deposit = get_object_or_404(Deposit, paystack_id=order)

    # Update the status to approved
    deposit.status = Deposit.Status.APPROVED
    deposit.save()

    # Add the user to the bundle participants
    deposit.bundle.participants.add(deposit.user)

    # Create an action for the user
    create_action(
        deposit.user,
        "New Bundle Purchased.",
        f"has just purchased the {deposit.bundle.name} bundle.",
        deposit.bundle,
    )

    # Send confirmation email to the user
    payment_successful_email(deposit.id)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
