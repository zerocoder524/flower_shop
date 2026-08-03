from datetime import time

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Order


class ShopClosedError(Exception):
    """Магазин сейчас не принимает заказы."""


def parse_time_setting(
    value: str,
    default: str,
) -> time:
    """Преобразует строку 09:00 в объект time."""

    try:
        return time.fromisoformat(value)
    except (TypeError, ValueError):
        return time.fromisoformat(default)


def get_shop_hours() -> tuple[time, time]:
    open_time = parse_time_setting(
        settings.SHOP_OPEN_TIME,
        "09:00",
    )

    close_time = parse_time_setting(
        settings.SHOP_CLOSE_TIME,
        "20:00",
    )

    return open_time, close_time


def is_shop_open(now=None) -> bool:
    """Проверяет, принимает ли магазин заказы."""

    current_datetime = timezone.localtime(
        now or timezone.now()
    )

    current_time = current_datetime.time().replace(
        tzinfo=None
    )

    open_time, close_time = get_shop_hours()

    if open_time <= close_time:
        return open_time <= current_time <= close_time

    # Поддержка графика, переходящего через полночь.
    return (
        current_time >= open_time
        or current_time <= close_time
    )


@transaction.atomic
def create_order(
    *,
    form,
    user,
    product,
) -> Order:
    """Проверяет и сохраняет заказ."""

    if not is_shop_open():
        raise ShopClosedError(
            "Сейчас магазин закрыт. "
            f"Заказы принимаются с "
            f"{settings.SHOP_OPEN_TIME} до "
            f"{settings.SHOP_CLOSE_TIME}."
        )

    if not product.is_available:
        raise ValidationError(
            "Выбранный товар больше недоступен."
        )

    order = form.save(commit=False)

    order.user = user
    order.product = product

    # Проверяет модель после добавления user и product.
    order.full_clean()
    order.save()

    return order