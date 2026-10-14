
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend

from users.models import Payment
from users.serializers import PaymentSerializer


class PaymentListAPIView(generics.ListAPIView):
    """Список платежей с фильтрацией и сортировкой."""

    queryset = Payment.objects.select_related(
        "user",
        "course",
        "lesson",
    ).all()
    serializer_class = PaymentSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "course",
        "lesson",
        "payment_method",
    ]

    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]

