from typing import Any

import requests
from django.conf import settings


class TelegramAPIError(Exception):
    """Ошибка обращения к Telegram Bot API."""


class TelegramConfigurationError(TelegramAPIError):
    """Ошибка настроек Telegram-бота."""


def send_message(text: str) -> dict[str, Any]:
    """
    Отправляет сообщение сотруднику магазина.

    Возвращает объект отправленного Telegram-сообщения.
    """

    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    timeout = settings.TELEGRAM_API_TIMEOUT

    if not token:
        raise TelegramConfigurationError(
            "Не задан TELEGRAM_BOT_TOKEN."
        )

    if not chat_id:
        raise TelegramConfigurationError(
            "Не задан TELEGRAM_CHAT_ID."
        )

    if not text or not text.strip():
        raise TelegramAPIError(
            "Нельзя отправить пустое сообщение."
        )

    # Допустимая длина текста sendMessage — до 4096 символов.
    prepared_text = text.strip()

    if len(prepared_text) > 4096:
        prepared_text = prepared_text[:4093] + "..."

    url = (
        "https://api.telegram.org/"
        f"bot{token}/sendMessage"
    )

    payload = {
        "chat_id": chat_id,
        "text": prepared_text,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=timeout,
        )
    except requests.RequestException as error:
        raise TelegramAPIError(
            "Не удалось подключиться к Telegram Bot API."
        ) from error

    try:
        response_data = response.json()
    except ValueError as error:
        raise TelegramAPIError(
            "Telegram вернул ответ не в формате JSON."
        ) from error

    if response.status_code != 200:
        description = response_data.get(
            "description",
            "неизвестная ошибка",
        )

        raise TelegramAPIError(
            f"Telegram вернул HTTP "
            f"{response.status_code}: {description}"
        )

    if not response_data.get("ok"):
        description = response_data.get(
            "description",
            "Telegram отклонил запрос",
        )

        raise TelegramAPIError(description)

    result = response_data.get("result")

    if not isinstance(result, dict):
        raise TelegramAPIError(
            "Telegram не вернул объект сообщения."
        )

    return result