from django.contrib import admin
from apps.accounts.models import Bundle, Group, Ticket, Reply


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("status",)
    ordering = ("-created_at",)


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = (
        "group",
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
