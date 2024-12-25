from django.contrib import admin
from apps.accounts.models import (
    Action,
    Profile,
    LoginHistory,
)


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


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    pass
