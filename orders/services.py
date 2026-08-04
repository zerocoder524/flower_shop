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
    """
    Преобразует строку времени формата 09:00
    в объект datetime.time.

    При неправильном значении использует значение
    по умолчанию.
    """

    try:
        return time.fromisoformat(value)
    except (TypeError, ValueError):
        return time.fromisoformat(default)


def get_shop_hours() -> tuple[time, time]:
    """Возвращает время открытия и закрытия магазина."""

    open_time_value = getattr(
        settings,
        "SHOP_OPEN_TIME",
        "09:00",
    )

    close_time_value = getattr(
        settings,
        "SHOP_CLOSE_TIME",
        "20:00",
    )

    open_time = parse_time_setting(
        open_time_value,
        "09:00",
    )

    close_time = parse_time_setting(
        close_time_value,
        "20:00",
    )

    return open_time, close_time


def is_shop_open(now=None) -> bool:
    """
    Проверяет, принимает ли магазин заказы
    в указанный момент времени.

    Если now не передан, используется текущее время.
    """

    current_datetime = timezone.localtime(
        now or timezone.now()
    )

    current_time = current_datetime.time().replace(
        tzinfo=None
    )

    open_time, close_time = get_shop_hours()

    # Обычный график, например с 09:00 до 20:00.
    if open_time <= close_time:
        return open_time <= current_time <= close_time

    # График, переходящий через полночь,
    # например с 20:00 до 02:00.
    return (
        current_time >= open_time
        or current_time <= close_time
    )


def schedule_order_notification(order_id: int) -> None:
    """
    Планирует отправку Telegram-уведомления после
    успешной фиксации заказа в базе данных.
    """

    def send_notification() -> None:
        # Импорт выполняется здесь, чтобы снизить риск
        # циклического импорта между приложениями.
        from telegram_bot.services import notify_new_order

        notify_new_order(order_id)

    transaction.on_commit(
        send_notification,
        robust=True,
    )


@transaction.atomic
def create_order(
    *,
    form,
    user,
    product,
) -> Order:
    """
    Проверяет данные, сохраняет заказ и планирует
    отправку уведомления сотруднику через Telegram.
    """

    if not is_shop_open():
        open_time, close_time = get_shop_hours()

        raise ShopClosedError(
            "Сейчас магазин закрыт. "
            "Заказы принимаются с "
            f"{open_time.strftime('%H:%M')} до "
            f"{close_time.strftime('%H:%M')}."
        )

    if not product.is_available:
        raise ValidationError(
            "Выбранный товар больше недоступен."
        )

    # Создаём объект Order из формы, но пока
    # не сохраняем его в базе данных.
    order = form.save(commit=False)

    # Эти поля определяются сервером и не должны
    # передаваться покупателем через HTML-форму.
    order.user = user
    order.product = product

    # Проверяем модель после добавления пользователя
    # и выбранного товара.
    order.full_clean()

    # Сохраняем заказ в базе данных.
    # После этой строки order.pk содержит ID заказа.
    order.save()

    # Регистрируем Telegram-уведомление только тогда,
    # когда отправка включена в настройках проекта.
    if getattr(
        settings,
        "TELEGRAM_NOTIFICATIONS_ENABLED",
        False,
    ):
        schedule_order_notification(order.pk)

    return order
