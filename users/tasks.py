
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from users.models import User


@shared_task
def deactivate_inactive_users():
    """Деактивирует пользователей, не входивших в систему более месяца."""
    inactivity_limit = timezone.now() - timedelta(days=30)

    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=inactivity_limit,
    )

    deactivated_count = inactive_users.update(is_active=False)

    return f"Деактивировано пользователей: {deactivated_count}"
