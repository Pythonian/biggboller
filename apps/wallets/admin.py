from django.contrib import admin

from .models import Wallet, Deposit, AuditLog, Withdrawal


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "wallet_id",
        "balance",
        "updated",
    ]


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "paystack_id",
        "amount",
        "status",
        "gateway_response",
    ]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = [
        "transaction_type",
        "amount",
        "wallet__user",
        "balance_before",
        "balance_after",
        "timestamp",
    ]


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "amount",
        "status",
        "processed_at",
        "created",
    ]
