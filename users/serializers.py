from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from users.models import Payment, User


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""

    class Meta:
        model = User
        fields = ("id", "email", "phone", "city", "avatar")
        read_only_fields = ("id", "email")


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = ("id", "email", "password", "phone", "city", "avatar")
        read_only_fields = ("id",)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже зарегистрирован."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class PaymentCreateSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(min_value=1)