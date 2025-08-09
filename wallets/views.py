from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Wallet, WalletOperations
from .serializers import (RegisterSerializer, WalletOperationsListSerializer,
                          WalletOperationsSerializer, WalletSerializer)


class LogoutAPIView(APIView):
    """Принудительная отмена refresh-токена (выход)"""

    def post(self, request):
        try:
            refresh = request.data["refresh"]
            token = RefreshToken(refresh)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class WalletListAPIView(ListAPIView):
    """Вывод всех кошельков пользователя"""

    serializer_class = WalletSerializer

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)


class RegisterAPIView(APIView):
    """Эндпоинт регистрации"""

    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Регистрация прошла успешно."}, status=status.HTTP_201_CREATED
        )


class WalletCreateAPIView(APIView):
    """Эндпоинт создания кошелька"""

    @transaction.atomic  # Всё - одна транзакция, полный откат в случае ошибки
    def post(self, request):
        # Создание кошелька
        wallet = Wallet.objects.create(user=request.user)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WalletDetailAPIView(APIView):
    """Детальная информация кошелька / создание кошелька / удаление"""

    def get(self, request, wallet_id):
        # Информация о кошельке
        wallet = get_object_or_404(
            Wallet.objects.filter(user=request.user), id=wallet_id
        )
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

    @transaction.atomic  # Всё - одна транзакция, полный откат в случае ошибки
    def delete(self, request, wallet_id):
        # Удаление кошелька
        wallet = get_object_or_404(
            Wallet.objects.filter(user=request.user), id=wallet_id
        )
        wallet.delete()
        return Response({"detail": "Кошелёк удалён"})


class WalletOperationsAPIView(APIView):
    """Эндпоинт post-запросов для кошелька"""

    @transaction.atomic  # Всё - одна транзакция, полный откат в случае ошибки
    def post(self, request, wallet_id):
        wallet = get_object_or_404(
            Wallet.objects.filter(user=request.user).select_for_update(), id=wallet_id
        )  # С защитой от двойного запроса
        serializer = WalletOperationsSerializer(data=request.data)
        serializer.is_valid(
            raise_exception=True
        )  # Сначала вызывем валидацию с автоматическим raise ответом
        type = serializer.validated_data["type"]
        amount = serializer.validated_data["amount"]

        # Проводим операцию с кошельком
        if type == WalletOperations.Operations.DEPOSIT:
            wallet.balance += amount
        elif type == WalletOperations.Operations.WITHDRAW:
            if wallet.balance < amount:
                return Response(
                    {"detail": "Недостаточно средств!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            wallet.balance -= amount

        wallet.save()
        WalletOperations.objects.create(wallet=wallet, type=type, amount=amount)

        return Response({"detail": "Операция прошла успешно!"})


class WalletOperationsListAPIView(ListAPIView):
    """Список всех операций кошелька"""

    serializer_class = WalletOperationsListSerializer

    def get_queryset(self):
        wallet_id = self.kwargs.get("wallet_id")
        wallet = get_object_or_404(
            Wallet.objects.filter(user=self.request.user), id=wallet_id
        )
        return wallet.operations.all().order_by("-created_at")
