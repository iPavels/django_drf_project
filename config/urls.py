from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from users.views import (
    PaymentCreateAPIView,
    PaymentListAPIView,
    UserDeleteAPIView,
    UserRegistrationAPIView,
    UserRetrieveAPIView,
    UserUpdateAPIView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Документация API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # Курсы и уроки
    path("api/", include("materials.urls")),
    path(
        "api/payments/create/",
        PaymentCreateAPIView.as_view(),
        name="payment-create",
),

    # Платежи
    path("api/payments/", PaymentListAPIView.as_view(), name="payment-list"),

    # Пользователи
    path("api/users/register/", UserRegistrationAPIView.as_view(), name="user-register"),
    path("api/users/me/", UserRetrieveAPIView.as_view(), name="user-detail"),
    path("api/users/me/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("api/users/me/delete/", UserDeleteAPIView.as_view(), name="user-delete"),

    # JWT-аутентификация
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
