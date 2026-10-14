
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError

from materials.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    help = "Создаёт тестовые платежи для LMS"

    def handle(self, *args, **options):
        user = User.objects.order_by("id").first()
        course = Course.objects.order_by("id").first()
        lesson = Lesson.objects.order_by("id").first()

        if not user:
            raise CommandError(
                "Нет пользователей. Сначала создайте пользователя."
            )

        if not course:
            raise CommandError(
                "Нет курсов. Сначала создайте курс в админке."
            )

        if not lesson:
            raise CommandError(
                "Нет уроков. Сначала создайте урок в админке."
            )

        payments = [
            {
                "user": user,
                "course": course,
                "lesson": None,
                "amount": Decimal("4990.00"),
                "payment_method": "transfer",
            },
            {
                "user": user,
                "course": None,
                "lesson": lesson,
                "amount": Decimal("990.00"),
                "payment_method": "cash",
            },
        ]

        for payment_data in payments:
            payment, created = Payment.objects.get_or_create(
                **payment_data
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Создан платёж №{payment.pk}"
                    )
                )
            else:
                self.stdout.write(
                    f"Платёж №{payment.pk} уже существует"
                )

        self.stdout.write(
            self.style.SUCCESS("Заполнение платежей завершено.")
        )
