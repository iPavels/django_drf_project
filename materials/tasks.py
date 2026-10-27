from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

from materials.models import Course, Subscription


@shared_task
def send_course_update_notification(course_id, lesson_title):
    """Отправляет подписчикам курса уведомление не чаще раза в 4 часа."""
    cache_key = f"course_update_notification:{course_id}"

    # Атомарно резервируем отправку на 4 часа.
    if not cache.add(cache_key, True, timeout=4 * 60 * 60):
        return "Уведомление уже отправлялось за последние 4 часа."

    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        cache.delete(cache_key)
        return "Курс не найден."

    subscriptions = (
        Subscription.objects
        .filter(course=course)
        .select_related("user")
    )

    sent_count = 0

    try:
        for subscription in subscriptions:
            email = subscription.user.email
            if not email:
                continue

            send_mail(
                subject=f"Обновление курса: {course.title}",
                message=(
                    f'В курсе "{course.title}" '
                    f'обновлён урок "{lesson_title}".'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            sent_count += 1
    except Exception:
        # Если отправка не удалась, разрешаем повторную попытку.
        cache.delete(cache_key)
        raise

    return f"Отправлено уведомлений: {sent_count}"
