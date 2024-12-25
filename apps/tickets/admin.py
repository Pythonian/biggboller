from django.contrib import admin

from .models import Ticket, Reply


class TicketReplyAdmin(admin.StackedInline):
    model = Reply
    extra = 0


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    inlines = [TicketReplyAdmin]
