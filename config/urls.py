from django.contrib import admin
from django.urls import include, path

from users.views import PaymentListAPIView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("materials.urls")),
    path("api/payments/", PaymentListAPIView.as_view(), name="payment-list"),
]
