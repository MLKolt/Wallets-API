import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


class Wallet(models.Model):
    """Модель кошелька"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="wallets"
    )
    balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Кошелёк"
        verbose_name_plural = "Кошельки"
        ordering = ["id"]

    def __str__(self):
        return f"Кошелёк №{self.id} | Баланс: {self.balance}₽"

    # Дополнительная валидация на уровне модели
    # Если злоумышленник будет отправлять запрос по ней напрямую
    def clean(self):
        if self.balance < 0:
            raise ValidationError("Баланс не можем быть отрицательным!")

    def save(
        self,
        *args,
        **kwargs,
    ):
        self.clean()
        super().save(*args, **kwargs)


class WalletOperations(models.Model):
    """Класс post-опреаций над кошельком"""

    class Operations(models.TextChoices):
        DEPOSIT = "DEPOSIT", "Пополнение"
        WITHDRAW = "WITHDRAW", "Снятие"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(
        Wallet, related_name="operations", on_delete=models.CASCADE
    )
    type = models.CharField(max_length=10, choices=Operations.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Операция"
        verbose_name_plural = "Операции"
        ordering = ["-created_at"]

    def __str__(self):
        return f'Операция №{self.id} типа "{self.type}" на сумму {self.amount}₽ | Кошелёк: {self.wallet.id}'

    # Дополнительная валидация на уровне модели
    # Если злоумышленник будет отправлять запрос по ней напрямую
    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Сумма должна быть положительной!")
        if self.type == self.Operations.WITHDRAW and self.amount > self.wallet.balance:
            raise ValidationError("Недостаточно стредств на счету!")

    def save(
        self,
        *args,
        **kwargs,
    ):
        self.clean()
        super().save(*args, **kwargs)
