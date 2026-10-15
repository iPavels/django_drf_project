from rest_framework import generics, viewsets
from materials.models import Course, Lesson
from materials.permissions import IsOwnerOrModerator, is_moderator
from materials.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD для курсов с проверкой владельца и модератора."""

    serializer_class = CourseSerializer
    permission_classes = [IsOwnerOrModerator]

    def get_queryset(self):
        user = self.request.user

        if is_moderator(user):
            return Course.objects.all()

        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """Список уроков и создание урока."""

    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrModerator]

    def get_queryset(self):
        user = self.request.user

        if is_moderator(user):
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    """Просмотр, изменение и удаление отдельного урока."""

    serializer_class = LessonSerializer
    permission_classes = [IsOwnerOrModerator]

    def get_queryset(self):
        user = self.request.user

        if is_moderator(user):
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)

