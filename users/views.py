from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import Payment
from users.serializers import (
    PaymentSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


class PaymentListAPIView(generics.ListAPIView):
    """Список платежей с фильтрацией и сортировкой."""

    queryset = Payment.objects.select_related(
        "user",
        "course",
        "lesson",
    ).all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]


class UserRegistrationAPIView(generics.CreateAPIView):
    """Регистрация доступна без авторизации."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """Получение профиля только самого авторизованного пользователя."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserUpdateAPIView(generics.UpdateAPIView):
    """Обновление профиля только самого авторизованного пользователя."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDeleteAPIView(generics.DestroyAPIView):
    """Удаление аккаунта только самим авторизованным пользователем."""

    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

