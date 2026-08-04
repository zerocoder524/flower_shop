import logging
from decimal import Decimal, InvalidOperation
from html import escape
from typing import Any

from django.utils import timezone

from orders.models import Order

from .bot import TelegramAPIError, send_message


logger = logging.getLogger(__name__)


def safe_text(value: Any) -> str:
    """Подготавливает пользовательский текст для Telegram HTML."""

    if value is None:
        return "—"

    prepared_value = str(value).strip()

    if not prepared_value:
        return "—"

    return escape(prepared_value)


def format_date(value: Any) -> str:
    """Форматирует дату доставки."""

    if value is None:
        return "—"

    if hasattr(value, "strftime"):
        return value.strftime("%d.%m.%Y")

    return safe_text(value)


def format_time(value: Any) -> str:
    """Форматирует время доставки."""

    if value is None:
        return "—"

    if hasattr(value, "strftime"):
        return value.strftime("%H:%M")

    return safe_text(value)


def format_money(value: Any) -> str:
    """Форматирует денежное значение."""

    if value is None:
        return "—"

    try:
        return f"{Decimal(str(value)):.2f} ₽"
    except (InvalidOperation, TypeError, ValueError):
        return safe_text(value)


def get_order_total(order: Order) -> Any:
    """Получает итоговую стоимость заказа."""

    total_price = getattr(order, "total_price", None)

    # Если total_price реализован как метод модели.
    if callable(total_price):
        total_price = total_price()

    if total_price is not None:
        return total_price

    product = getattr(order, "product", None)
    product_price = getattr(product, "price", None)
    quantity = getattr(order, "quantity", 1)

    if product_price is None:
        return None

    try:
        return Decimal(str(product_price)) * Decimal(str(quantity))
    except (InvalidOperation, TypeError, ValueError):
        return None


def build_order_message(order: Order) -> str:
    """Формирует сообщение Telegram с данными заказа."""

    product = getattr(order, "product", None)
    user = getattr(order, "user", None)

    product_name = getattr(product, "name", "Товар не указан")
    product_price = getattr(product, "price", None)

    quantity = getattr(order, "quantity", 1)
    total_price = get_order_total(order)

    username = getattr(user, "username", "—") if user else "—"

    customer_name = getattr(
        order,
        "customer_name",
        getattr(order, "full_name", ""),
    )

    phone = getattr(order, "phone", "")

    recipient_name = getattr(
        order,
        "recipient_name",
        "",
    )

    delivery_address = getattr(
        order,
        "delivery_address",
        getattr(order, "address", ""),
    )

    delivery_date = getattr(
        order,
        "delivery_date",
        None,
    )

    delivery_time = getattr(
        order,
        "delivery_time",
        None,
    )

    comment = getattr(
        order,
        "comment",
        "",
    )

    lines = [
        f"<b>🌸 Новый заказ №{order.pk}</b>",
        "",
        f"<b>Букет:</b> {safe_text(product_name)}",
        f"<b>Количество:</b> {safe_text(quantity)}",
        f"<b>Цена:</b> {format_money(product_price)}",
        f"<b>Итого:</b> {format_money(total_price)}",
        "",
        f"<b>Заказчик:</b> {safe_text(customer_name)}",
        f"<b>Телефон:</b> {safe_text(phone)}",
        f"<b>Получатель:</b> {safe_text(recipient_name)}",
        "",
        f"<b>Дата доставки:</b> {format_date(delivery_date)}",
        f"<b>Время доставки:</b> {format_time(delivery_time)}",
        f"<b>Адрес:</b> {safe_text(delivery_address)}",
        f"<b>Комментарий:</b> {safe_text(comment)}",
        "",
        f"<b>Пользователь сайта:</b> {safe_text(username)}",
    ]

    return "\n".join(lines)


def update_telegram_fields(
    order: Order,
    **values: Any,
) -> None:
    """
    Обновляет Telegram-поля, если они присутствуют в модели Order.

    Благодаря этой проверке функция работает и до добавления
    полей telegram_notification_status и telegram_message_id.
    """

    model_fields = {
        field.name
        for field in order._meta.fields
    }

    update_fields = []

    for field_name, field_value in values.items():
        if field_name not in model_fields:
            continue

        setattr(order, field_name, field_value)
        update_fields.append(field_name)

    if update_fields:
        order.save(update_fields=update_fields)


def notify_new_order(order_id: int) -> bool:
    """
    Отправляет заказ сотруднику через Telegram.

    Возвращает True при успешной отправке и False при ошибке.
    """

    try:
        order = (
            Order.objects
            .select_related("user", "product")
            .get(pk=order_id)
        )
    except Order.DoesNotExist:
        logger.error(
            "Заказ с ID %s не найден.",
            order_id,
        )
        return False

    update_telegram_fields(
        order,
        telegram_notification_status="pending",
        telegram_error="",
    )

    message = build_order_message(order)

    try:
        telegram_message = send_message(message)

    except TelegramAPIError as error:
        update_telegram_fields(
            order,
            telegram_notification_status="failed",
            telegram_message_id=None,
            telegram_sent_at=None,
            telegram_error=str(error)[:2000],
        )

        logger.warning(
            "Ошибка отправки заказа %s в Telegram: %s",
            order_id,
            error,
        )

        return False

    except Exception as error:
        update_telegram_fields(
            order,
            telegram_notification_status="failed",
            telegram_message_id=None,
            telegram_sent_at=None,
            telegram_error=str(error)[:2000],
        )

        logger.exception(
            "Непредвиденная ошибка отправки заказа %s.",
            order_id,
        )

        return False

    update_telegram_fields(
        order,
        telegram_notification_status="sent",
        telegram_message_id=telegram_message.get(
            "message_id"
        ),
        telegram_sent_at=timezone.now(),
        telegram_error="",
    )

    logger.info(
        "Заказ %s отправлен в Telegram.",
        order_id,
    )

    return True