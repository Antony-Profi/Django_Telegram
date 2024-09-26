import logging
from typing import Optional
from telebot.types import ChatInviteLink, ChatMemberUpdated

from webtelegram.apps.bot.models import TelegramChat, InviteLink


logger = logging.getLogger(__name__)


def member_is_subscriber(chat_member_updated: ChatMemberUpdated) -> Optional[bool]:
    """Если человек подписался, проверяем статус подписки"""
    status = chat_member_updated.difference.get("status")
    current_subscriber_status = status[1]

    if current_subscriber_status == "member":
        return True
    elif current_subscriber_status == "left":
        return False
    logger.warning("Статус подписчика не определён")
    return False
