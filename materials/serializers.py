from rest_framework import serializers
from materials.models import Course, Lesson, Subscription
from materials.validators import validate_youtube_url
from drf_spectacular.utils import extend_schema_field
from materials.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(
        validators=[validate_youtube_url]
    )

    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ("owner",)

    def validate_course(self, course):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            is_course_owner = course.owner_id == request.user.pk
            is_course_moderator = request.user.groups.filter(
                name="Модераторы"
            ).exists()

            if not is_course_owner and not is_course_moderator:
                raise serializers.ValidationError(
                    "Можно добавлять уроки только в свой курс."
                )

        return course


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ("owner",)

    @extend_schema_field(serializers.IntegerField())
    def get_lessons_count(self, obj) -> int:
        return obj.lessons.count()

    @extend_schema_field(serializers.BooleanField())
    def get_is_subscribed(self, obj) -> bool:
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        return Subscription.objects.filter(
            user=request.user,
            course=obj,
        ).exists()

class SubscriptionResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
