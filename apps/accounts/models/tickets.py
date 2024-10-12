import uuid
import string
import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class TicketManager(models.Manager):
    def pending(self):
        return self.filter(status=Ticket.Status.PENDING)

    def answered(self):
        return self.filter(status=Ticket.Status.ANSWERED)

    def closed(self):
        return self.filter(status=Ticket.Status.CLOSED)


class Ticket(models.Model):
    class Status(models.TextChoices):
        PENDING = "P", _("Pending")
        ANSWERED = "A", _("Answered")
        CLOSED = "C", _("Closed")

    ticket_id = models.CharField(
        _("ticket id"),
        max_length=6,
        unique=True,
        db_index=True,
        editable=False,
        help_text="Unique 6-character alphanumeric Ticket ID",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name=_("User"),
    )
    subject = models.CharField(
        _("subject"),
        max_length=255,
    )
    description = models.TextField()
    status = models.CharField(
        max_length=1,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Status"),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = TicketManager()

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = self.generate_unique_ticket_id()
        super(Ticket, self).save(*args, **kwargs)

    @staticmethod
    def generate_unique_ticket_id():
        """
        Generates a unique 6-character alphanumeric ticket ID.
        Retries if a collision occurs.
        """
        while True:
            ticket_id = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=6)
            )
            if not Ticket.objects.filter(ticket_id=ticket_id).exists():
                return ticket_id

    def get_absolute_url(self):
        return reverse(
            "administrator:tickets_detail",
            args=[self.ticket_id],
        )


class Reply(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ticket_replies",
    )
    message = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = _("Reply")
        verbose_name_plural = _("Replies")

    def __str__(self):
        return f"Reply by {self.user.username} on Ticket #{self.ticket.id}"
