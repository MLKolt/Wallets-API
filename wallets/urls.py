from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import (LogoutAPIView, RegisterAPIView, WalletCreateAPIView,
                    WalletDetailAPIView, WalletListAPIView,
                    WalletOperationsAPIView, WalletOperationsListAPIView)

urlpatterns = [
    path("api/v1/wallet/", WalletCreateAPIView.as_view(), name="wallet-create"),
    path("api/v1/wallets/all/", WalletListAPIView.as_view(), name="wallet-list"),
    path(
        "api/v1/wallets/<uuid:wallet_id>/",
        WalletDetailAPIView.as_view(),
        name="wallet-detail",
    ),
    path(
        "api/v1/wallets/<uuid:wallet_id>/operation/",
        WalletOperationsAPIView.as_view(),
        name="wallet-operation",
    ),
    path(
        "api/v1/wallets/<uuid:wallet_id>/operations/",
        WalletOperationsListAPIView.as_view(),
        name="wallet-operations",
    ),

    path("api/v1/register/", RegisterAPIView.as_view(), name="register"),
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token-access"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/v1/logout/", LogoutAPIView.as_view(), name="blacklist"),
]
