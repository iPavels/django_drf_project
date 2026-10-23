from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from decimal import Decimal
from unittest.mock import patch

from materials.models import Course
from users.models import Payment


User = get_user_model()


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.password = "QwErty!7vB9#x"
        self.user = User.objects.create_user(
            email="student@example.com",
            password=self.password,
            phone="+79990000001",
            city="Москва",
        )

    def test_user_can_register(self):
        response = self.client.post(
            reverse("user-register"),
            {
                "email": "newstudent@example.com",
                "password": self.password,
                "phone": "+79990000002",
                "city": "Москва",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(email="newstudent@example.com").exists()
        )

    def test_registration_rejects_duplicate_email(self):
        response = self.client.post(
            reverse("user-register"),
            {
                "email": self.user.email,
                "password": self.password,
                "phone": "+79990000003",
                "city": "Москва",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_user_can_view_own_profile(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("user-detail"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_unauthenticated_user_cannot_view_profile(self):
        response = self.client.get(reverse("user-detail"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_update_own_profile(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            reverse("user-update"),
            {
                "phone": "+79990000004",
                "city": "Санкт-Петербург",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "+79990000004")
        self.assertEqual(self.user.city, "Санкт-Петербург")

    def test_user_can_delete_own_account(self):
        self.client.force_authenticate(user=self.user)
        user_id = self.user.pk

        response = self.client.delete(reverse("user-delete"))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=user_id).exists())


class PaymentAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.password = "QwErty!7vB9#x"
        self.user = User.objects.create_user(
            email="payment@example.com",
            password=self.password,
            phone="+79990000010",
            city="Москва",
        )
        self.course = Course.objects.create(
            owner=self.user,
            title="Python для начинающих",
            description="Тестовый курс",
            price=Decimal("1500.00"),
        )
        self.client.force_authenticate(user=self.user)

    def test_payment_creation_saves_stripe_data(self):
        fake_product = {"id": "prod_test123"}
        fake_price = {"id": "price_test123"}
        fake_session = {
            "id": "cs_test123",
            "url": "https://checkout.stripe.com/c/pay/cs_test123",
        }

        with (
            patch(
                "users.views.create_stripe_product",
                return_value=fake_product,
            ),
            patch(
                "users.views.create_stripe_price",
                return_value=fake_price,
            ),
            patch(
                "users.views.create_checkout_session",
                return_value=fake_session,
            ),
        ):
            response = self.client.post(
                reverse("payment-create"),
                {"course_id": self.course.pk},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        payment = Payment.objects.get(user=self.user, course=self.course)
        self.assertEqual(payment.stripe_product_id, "prod_test123")
        self.assertEqual(payment.stripe_price_id, "price_test123")
        self.assertEqual(payment.stripe_session_id, "cs_test123")
        self.assertEqual(
            payment.payment_url,
            fake_session["url"],
        )
        self.assertEqual(payment.amount, Decimal("1500.00"))

    def test_payment_creation_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(
            reverse("payment-create"),
            {"course_id": self.course.pk},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertFalse(Payment.objects.filter(course=self.course).exists())
