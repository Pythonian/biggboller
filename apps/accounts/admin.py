from django.contrib import admin
from apps.accounts.models import (
    Action,
    Bundle,
    Group,
    Ticket,
    Reply,
    Profile,
    Deposit,
    Payout,
)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("status",)
    ordering = ("-created_at",)


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "potential_min_win",
        "potential_max_win",
        "created_at",
        "updated_at",
    )
    search_fields = ("group__name",)
    list_filter = ("group__status",)
    ordering = ("-created_at",)


class TicketReplyAdmin(admin.StackedInline):
    model = Reply
    extra = 0


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    inlines = [TicketReplyAdmin]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "email_confirmed",
    ]


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ["user", "verb", "target", "created"]
    list_filter = ["created"]
    search_fields = ["verb"]


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    pass


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    pass
