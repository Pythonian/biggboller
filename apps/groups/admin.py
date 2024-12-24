from django.contrib import admin
from .models import Bundle, Group, Purchase, GroupRequest


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "created", "updated")
    search_fields = ("name",)
    list_filter = ("status",)


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "winning_percentage",
        "created",
        "updated",
    )
    search_fields = ("group__name",)
    list_filter = ("group__status",)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    pass


@admin.register(GroupRequest)
class GroupRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "group", "status", "created", "updated")
