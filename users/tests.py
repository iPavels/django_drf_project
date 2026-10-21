from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


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
