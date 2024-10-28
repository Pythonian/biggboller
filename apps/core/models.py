from django.db import models
from django.utils.translation import gettext_lazy as _


class FrequentlyAskedQuestion(models.Model):
    """Questions and Answers that may be commonly asked."""

    question = models.CharField(
        _("question"),
        max_length=255,
    )
    answer = models.TextField(
        _("answer"),
    )
    is_published = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.question
