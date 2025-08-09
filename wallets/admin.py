from django.contrib import admin

from .models import Wallet, WalletOperations


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    """Админ-класс модели Wallet"""

    list_display = ("id", "balance", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("id",)


@admin.register(WalletOperations)
class WalletOperationsAdmin(admin.ModelAdmin):
    """Админ-класс модели WalletOperations"""

    list_display = ("id", "wallet", "type", "amount", "created_at")
    readonly_fields = ("created_at",)
    search_fields = ("wallet__id",)
