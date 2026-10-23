
import stripe
from django.conf import settings

from materials.models import Course


def create_stripe_product(course: Course) -> dict:
    """Создаёт продукт в Stripe для курса."""
    stripe.api_key = settings.STRIPE_SECRET_KEY

    product = stripe.Product.create(
        name=course.title,
        description=course.description[:500],
    )

    return product


def create_stripe_price(course: Course, product_id: str) -> dict:
    """Создаёт цену курса в Stripe. Цена передаётся в копейках."""
    stripe.api_key = settings.STRIPE_SECRET_KEY

    amount_in_kopecks = int(course.price * 100)

    price = stripe.Price.create(
        product=product_id,
        currency="rub",
        unit_amount=amount_in_kopecks,
    )

    return price


def create_checkout_session(price_id: str, payment_id: int) -> dict:
    """Создаёт сессию оплаты и возвращает ссылку Checkout."""
    stripe.api_key = settings.STRIPE_SECRET_KEY

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        success_url="http://localhost:8000/api/payments/success/",
        cancel_url="http://localhost:8000/api/payments/cancel/",
        metadata={"payment_id": str(payment_id)},
    )

    return session
