from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class WalletTests(TestCase):
    """Тесты эндпоинтов приложения wallets"""

    def setUp(self):
        """Исходные данные"""
        # Задаём пользователей
        self.u1 = User.objects.create_user(username="u1", password="u1password")
        self.u2 = User.objects.create_user(username="u2", password="u2password")

        # Неавторизованный клиент
        self.client = APIClient()
        # Токен для u1
        token_response = self.client.post(
            reverse("token-access"),
            {"username": "u1", "password": "u1password"},
            format="json",
        )
        # Тест создания access-токена
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)

        self.u1_token_access = token_response.data["access"]
        self.u1_token_refresh = token_response.data["refresh"]

        # Создаём авторизированного пользователя
        self.auth = APIClient()
        self.auth.credentials(HTTP_AUTHORIZATION=f"Bearer {self.u1_token_access}")

    def test_register(self):
        """Тест регистрации"""
        resp = self.client.post(
            reverse("register"),
            {"username": "u3", "password": "u3password"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="u3").exists())

    def test_token_refresh(self):
        """Тест refresh-токена"""
        resp = self.client.post(
            reverse("token-refresh"), {"refresh": self.u1_token_refresh}
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)

    def test_create_wallet(self):
        """Тест создания кошелька"""
        # Неавторизованная попытка
        resp1 = self.client.post(reverse("wallet-create"), format="json")
        self.assertIn(
            resp1.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )

        # Авторизованная попытка
        resp2 = self.auth.post(reverse("wallet-create"), format="json")
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", resp2.data)
        self.assertEqual(resp2.data["balance"], "0.00")

    def test_list_wallets(self):
        """Тест списка кошельков"""
        self.auth.post(reverse("wallet-create"), format="json")
        self.auth.post(reverse("wallet-create"), format="json")

        resp = self.auth.get(reverse("wallet-list"), format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 4)

    def test_wallet_detail(self):
        """Тест детального представления кошелька"""
        resp1 = self.auth.post(reverse("wallet-create"), format="json")
        wallet_id = resp1.data["id"]

        # Просмотр собественником
        resp2 = self.auth.get(reverse("wallet-detail", kwargs={"wallet_id": wallet_id}))
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.data["balance"], "0.00")

        # Просмотр не собственником
        token_u2 = self.client.post(
            reverse("token-access"),
            {"username": "u2", "password": "u2password"},
            format="json",
        )
        self.auth2 = APIClient()
        self.auth2.credentials(HTTP_AUTHORIZATION=f'Bearer {token_u2.data["access"]}')
        resp3 = self.auth2.get(
            reverse("wallet-detail", kwargs={"wallet_id": wallet_id})
        )
        self.assertEqual(resp3.status_code, status.HTTP_404_NOT_FOUND)

    def test_deposit_withdraw_balance(self):
        """Тест снятия и пополнения"""
        resp = self.auth.post(reverse("wallet-create"), format="json")
        wallet_id = resp.data["id"]

        # Пополнение 1000
        resp1 = self.auth.post(
            reverse("wallet-operation", kwargs={"wallet_id": wallet_id}),
            {"type": "DEPOSIT", "amount": "1000.00"},
            format="json",
        )
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)

        # Снятие 300
        resp2 = self.auth.post(
            reverse("wallet-operation", kwargs={"wallet_id": wallet_id}),
            {"type": "WITHDRAW", "amount": "300.00"},
            format="json",
        )
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)

        # Баланс
        resp3 = self.auth.get(reverse("wallet-detail", kwargs={"wallet_id": wallet_id}))
        self.assertEqual(resp3.status_code, status.HTTP_200_OK)
        self.assertEqual(resp3.data["balance"], "700.00")

        # История операций
        resp4 = self.auth.get(
            reverse("wallet-operations", kwargs={"wallet_id": wallet_id})
        )
        self.assertEqual(resp4.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp4.data["results"]), 2)

        # Операция не собственником
        token_u2 = self.client.post(
            reverse("token-access"),
            {"username": "u2", "password": "u2password"},
            format="json",
        )
        self.auth2 = APIClient()
        self.auth2.credentials(HTTP_AUTHORIZATION=f'Bearer {token_u2.data["access"]}')
        resp5 = self.auth2.post(
            reverse("wallet-operation", kwargs={"wallet_id": wallet_id}),
            {"type": "WITHDRAW", "amount": "300.00"},
            format="json",
        )
        self.assertIn(
            resp5.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)
        )

    def test_withdraw_balance(self):
        """Тест некорректного снятия"""
        resp = self.auth.post(reverse("wallet-create"), format="json")
        wallet_id = resp.data["id"]

        # Снятие - ниже баланса
        resp1 = self.auth.post(
            reverse("wallet-operation", kwargs={"wallet_id": wallet_id}),
            {"type": "WITHDRAW", "amount": "300.00"},
            format="json",
        )
        self.assertEqual(resp1.status_code, status.HTTP_400_BAD_REQUEST)

        # Снятие - невалидный type
        resp3 = self.auth.post(
            reverse("wallet-operation", kwargs={"wallet_id": wallet_id}),
            {"type": "MINUS", "amount": "300.00"},
            format="json",
        )
        self.assertEqual(resp3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_blacklist(self):
        """Тест blacklist"""
        # Logout без авторизации
        resp1 = self.client.post(
            reverse("blacklist"), {"refresh": self.u1_token_refresh}, format="json"
        )
        self.assertIn(
            resp1.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )

        # Не передан refresh
        resp2 = self.auth.post(reverse("blacklist"), {}, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)

        # Нормальный blacklist
        resp3 = self.auth.post(
            reverse("blacklist"), {"refresh": self.u1_token_refresh}, format="json"
        )
        self.assertEqual(resp3.status_code, status.HTTP_205_RESET_CONTENT)
        resp4 = self.client.post(
            reverse("token-refresh"), {"refresh": self.u1_token_refresh}, format="json"
        )
        self.assertIn(
            resp4.status_code,
            (status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED),
        )
