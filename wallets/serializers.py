from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Wallet, WalletOperations

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        return User.objects.create_user(
            **validated_data
        )  # Автоматом хешируем пароль и активируем пользователя


class WalletSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Wallet"""

    class Meta:
        model = Wallet
        fields = ["id", "balance"]


class WalletOperationsListSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Wallet"""

    class Meta:
        model = WalletOperations
        fields = ["created_at", "id", "type", "amount"]


class WalletOperationsSerializer(serializers.Serializer):
    """Сериализатор для модели WalletOperations"""

    type = serializers.ChoiceField(choices=WalletOperations.Operations.choices)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма должна быть положительной!")
        return value
