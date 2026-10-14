from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User
from users.models import Payment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ("id", "email", "phone", "city", "is_staff", "is_active")
    search_fields = ("email", "phone", "city")
    list_filter = ("is_staff", "is_active")
    ordering = ("id",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личные данные", {"fields": ("phone", "city", "avatar")}),
        ("Права доступа", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active"),
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "payment_date",
        "course",
        "lesson",
        "amount",
        "payment_method",
    )
    list_filter = ("payment_method", "payment_date")
    search_fields = ("user__email",)