import stripe

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from materials.models import Course
from users.models import Payment
from users.serializers import (
    PaymentCreateSerializer,
    PaymentSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from users.services import (
    create_checkout_session,
    create_stripe_price,
    create_stripe_product,
)

User = get_user_model()



class PaymentListAPIView(generics.ListAPIView):
    """Список платежей текущего пользователя с фильтрацией и сортировкой."""

    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Payment.objects.none()

        return Payment.objects.select_related(
            "user",
            "course",
            "lesson",
        ).filter(user=self.request.user)



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
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user



@extend_schema_view(
    post=extend_schema(
        summary="Создать платеж за курс",
        description=(
            "Создаёт платёж за выбранный курс и формирует "
            "ссылку на оплату через Stripe. Требуется JWT-авторизация."
        ),
        request=PaymentCreateSerializer,
        responses={
            201: PaymentSerializer,
            400: dict,
            404: dict,
            502: dict,
        },
    )
)

class PaymentCreateAPIView(generics.CreateAPIView):
    """Создание платежа и получение ссылки на оплату через Stripe."""

    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        course_id = request_serializer.validated_data["course_id"]
        course = get_object_or_404(Course, pk=course_id)

        if course.price <= 0:
            return Response(
                {"detail": "Цена курса должна быть больше нуля."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=course.price,
            payment_method="stripe",
            status="pending",
        )

        try:
            product = create_stripe_product(course)
            price = create_stripe_price(course, product["id"])
            session = create_checkout_session(
                price["id"],
                payment.id,
            )

            payment.stripe_product_id = product["id"]
            payment.stripe_price_id = price["id"]
            payment.stripe_session_id = session["id"]
            payment.payment_url = session["url"]
            payment.save(
                update_fields=[
                    "stripe_product_id",
                    "stripe_price_id",
                    "stripe_session_id",
                    "payment_url",
                ]
            )

        except stripe.StripeError:
            payment.status = "failed"
            payment.save(update_fields=["status"])
            return Response(
                {"detail": "Не удалось создать платеж в Stripe."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            PaymentSerializer(payment).data,
            status=status.HTTP_201_CREATED,
        )
