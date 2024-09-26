import logging

from typing import Optional
from telebot.types import Chat

from webtelegram.apps.bot.models import TelegramChat


logger = logging.getLogger(__name__)


async def update_telegram_chat(chat_data: Chat):
    defaults_dict = {
        "name": chat_data.title,
        "username": chat_data.username
    }
    telegram_chat, create_status = await TelegramChat.objects.aupdate_or_create(
        chat_id=chat_data.id,
        defaults=defaults_dict)

    return telegram_chat


async def get_telegram_chat_by_chat_id(telegram_chat_id: int) -> Optional[TelegramChat]:
    """Получить данные чата/канала по его telegram_id"""
    try:
        telegram_chat = await TelegramChat.objects.aget(chat_id=telegram_chat_id)
    except TelegramChat.DoesNotExist as err:
        logger.error(f"Ошибка получения телеграм чата: {err}")
        return None
    return telegram_chat


async def get_all_channels():
    """Получаем id каналов, которые есть в БД"""
    return TelegramChat.objects.all()
