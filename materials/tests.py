from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from materials.models import Course, Lesson, Subscription


User = get_user_model()


class MaterialsAPITestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="TestPassword123!",
            phone="+79990000001",
            city="Москва",
        )
        self.other_user = User.objects.create_user(
            email="student@example.com",
            password="TestPassword123!",
            phone="+79990000002",
            city="Москва",
        )
        self.moderator = User.objects.create_user(
            email="moderator@example.com",
            password="TestPassword123!",
            phone="+79990000003",
            city="Москва",
        )

        moderator_group, _ = Group.objects.get_or_create(
            name="Модераторы"
        )
        self.moderator.groups.add(moderator_group)

        self.course = Course.objects.create(
            owner=self.owner,
            title="Python",
            description="Основы Python",
        )
        self.other_course = Course.objects.create(
            owner=self.other_user,
            title="Django",
            description="Основы Django",
        )
        self.lesson = Lesson.objects.create(
            owner=self.owner,
            course=self.course,
            title="Урок 1",
            description="Первый урок",
            video_url="https://www.youtube.com/watch?v=abc123",
        )

        self.client = APIClient()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_owner_can_list_own_lessons(self):
        self.authenticate(self.owner)

        response = self.client.get(reverse("lesson-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Урок 1")

    def test_user_cannot_see_another_users_lesson(self):
        self.authenticate(self.other_user)

        response = self.client.get(
            reverse("lesson-detail", kwargs={"pk": self.lesson.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_create_lesson(self):
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("lesson-list-create"),
            {
                "course": self.course.pk,
                "title": "Урок 2",
                "description": "Второй урок",
                "video_url": "https://www.youtube.com/watch?v=xyz123",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Lesson.objects.filter(title="Урок 2", owner=self.owner).exists()
        )

    def test_user_cannot_create_lesson_in_another_users_course(self):
        self.authenticate(self.other_user)

        response = self.client.post(
            reverse("lesson-list-create"),
            {
                "course": self.course.pk,
                "title": "Чужой урок",
                "description": "Попытка добавить урок",
                "video_url": "https://www.youtube.com/watch?v=xyz123",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_update_lesson(self):
        self.authenticate(self.owner)

        response = self.client.patch(
            reverse("lesson-detail", kwargs={"pk": self.lesson.pk}),
            {"title": "Обновлённый урок"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Обновлённый урок")

    def test_owner_can_delete_lesson(self):
        self.authenticate(self.owner)

        response = self.client.delete(
            reverse("lesson-detail", kwargs={"pk": self.lesson.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def test_moderator_can_view_any_lesson(self):
        self.authenticate(self.moderator)

        response = self.client.get(
            reverse("lesson-detail", kwargs={"pk": self.lesson.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_moderator_cannot_delete_lesson(self):
        self.authenticate(self.moderator)

        response = self.client.delete(
            reverse("lesson-detail", kwargs={"pk": self.lesson.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_list_lessons(self):
        response = self.client.get(reverse("lesson-list-create"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_video_url_is_rejected(self):
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("lesson-list-create"),
            {
                "course": self.course.pk,
                "title": "Урок с чужим видео",
                "description": "Проверка валидации",
                "video_url": "https://vimeo.com/123456",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_youtube_url_is_accepted(self):
        self.authenticate(self.owner)

        response = self.client.post(
            reverse("lesson-list-create"),
            {
                "course": self.course.pk,
                "title": "Урок с YouTube",
                "description": "Корректная ссылка",
                "video_url": "https://www.youtube.com/watch?v=abc123",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_subscription_can_be_created_and_cancelled(self):
        self.authenticate(self.other_user)
        url = reverse(
            "course-subscribe",
            kwargs={"course_id": self.course.pk},
        )

        first_response = self.client.post(url)

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            Subscription.objects.filter(
                user=self.other_user,
                course=self.course,
            ).exists()
        )

        second_response = self.client.post(url)

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Subscription.objects.filter(
                user=self.other_user,
                course=self.course,
            ).exists()
        )

    def test_subscription_to_missing_course_returns_404(self):
        self.authenticate(self.other_user)

        response = self.client.post(
            reverse(
                "course-subscribe",
                kwargs={"course_id": 999999},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_course_serializer_returns_subscription_status(self):
        Subscription.objects.create(
            user=self.other_user,
            course=self.other_course,
        )
        self.authenticate(self.other_user)

        response = self.client.get(reverse("course-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        course_data = next(
            item
            for item in response.data["results"]
            if item["id"] == self.other_course.pk
        )

        self.assertTrue(course_data["is_subscribed"])

    def test_course_list_is_paginated(self):
        self.authenticate(self.owner)

        response = self.client.get(reverse("course-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
