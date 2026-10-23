
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class UserManager(BaseUserManager):
    """Менеджер для создания пользователей по email."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("У пользователя должен быть email")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=35, blank=True, verbose_name="Телефон")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Платёж пользователя за курс или урок."""

    PAYMENT_METHODS = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счет"),
        ("stripe", "Stripe"),
    ]

    PAYMENT_STATUSES = [
        ("pending", "Ожидает оплаты"),
        ("paid", "Оплачен"),
        ("failed", "Ошибка оплаты"),
        ("expired", "Ссылка истекла"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата оплаты",
    )
    course = models.ForeignKey(
        "materials.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Оплаченный курс",
    )
    lesson = models.ForeignKey(
        "materials.Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Оплаченный урок",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты",
    )
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHODS,
        verbose_name="Способ оплаты",
    )
    status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUSES,
        default="pending",
        verbose_name="Статус платежа",
    )
    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ID продукта Stripe",
    )
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ID цены Stripe",
    )
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ID сессии Stripe",
    )
    payment_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="Ссылка на оплату",
    )

    def __str__(self):
        return f"{self.user.email} — {self.amount}"

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]
