from materials.tasks import send_course_update_notification
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from materials.models import Course, Lesson, Subscription
from materials.paginators import CoursePagination
from materials.permissions import IsOwnerOrModerator, is_moderator
from materials.serializers import (
    CourseSerializer,
    LessonSerializer,
    SubscriptionResponseSerializer,
)
from drf_spectacular.utils import extend_schema


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD для курсов с проверкой владельца и модератора."""

    serializer_class = CourseSerializer
    permission_classes = [IsOwnerOrModerator]
    pagination_class = CoursePagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Course.objects.none()

        user = self.request.user

        if is_moderator(user):
            return Course.objects.all().order_by("id")

        return Course.objects.filter(owner=user).order_by("id")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """Список уроков и создание урока."""

    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrModerator]
    pagination_class = CoursePagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Lesson.objects.none()

        user = self.request.user

        if is_moderator(user):
            return Lesson.objects.all().order_by("id")

        return Lesson.objects.filter(owner=user).order_by("id")

    def perform_create(self, serializer):
        lesson = serializer.save(owner=self.request.user)
        send_course_update_notification.delay(
            lesson.course_id,
            lesson.title,
        )


class LessonRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    """Просмотр, изменение и удаление отдельного урока."""

    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrModerator]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Lesson.objects.none()

        user = self.request.user

        if is_moderator(user):
            return Lesson.objects.all().order_by("id")

        return Lesson.objects.filter(owner=user).order_by("id")

    def perform_update(self, serializer):
        lesson = serializer.save()
        send_course_update_notification.delay(
            lesson.course_id,
            lesson.title,
        )


class SubscriptionAPIView(APIView):
    """Создание и отмена подписки на курс."""

    serializer_class = SubscriptionResponseSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: SubscriptionResponseSerializer},
    )
    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)

        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            course=course,
        )

        if created:
            message = "Подписка на курс оформлена."
        else:
            subscription.delete()
            message = "Подписка на курс отменена."

        return Response(
            {"message": message},
            status=status.HTTP_200_OK,
        )
