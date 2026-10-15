
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.views import (
    PaymentListAPIView,
    UserDeleteAPIView,
    UserRegistrationAPIView,
    UserRetrieveAPIView,
    UserUpdateAPIView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("materials.urls")),

    path("api/payments/", PaymentListAPIView.as_view(), name="payment-list"),

    path("api/users/register/", UserRegistrationAPIView.as_view(), name="user-register"),
    path("api/users/me/", UserRetrieveAPIView.as_view(), name="user-detail"),
    path("api/users/me/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("api/users/me/delete/", UserDeleteAPIView.as_view(), name="user-delete"),

    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
