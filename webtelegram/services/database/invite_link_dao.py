import logging
from typing import Optional
from telebot.types import ChatInviteLink

from webtelegram.apps.bot.models import TelegramChat, InviteLink


logger = logging.getLogger(__name__)


async def update_invite_link(telegram_chat: TelegramChat, chat_invite_link_data: ChatInviteLink):
    defaults_dict = {
        "telegram_chat": telegram_chat,
        "creates_join_request": chat_invite_link_data.creates_join_request,
        "creator_full_name": chat_invite_link_data.creator.full_name,
        "creator_telegram_id": chat_invite_link_data.creator.id,
        "creator_username": chat_invite_link_data.creator.username,
        "expire_date": chat_invite_link_data.expire_date,
        "is_primary": chat_invite_link_data.is_primary,
        "is_revoked": chat_invite_link_data.is_revoked,
        "member_limit": chat_invite_link_data.member_limit,
        "name": chat_invite_link_data.name,
        "pending_join_request_count": chat_invite_link_data.pending_join_request_count,
        "link": chat_invite_link_data.invite_link,
        "creator": chat_invite_link_data.creator,
    }
    try:
        invite_link, create_status = await InviteLink.objects.aupdate_or_create(telegram_chat=telegram_chat,
                                         link=chat_invite_link_data.invite_link,
                                         defaults=defaults_dict)
        if create_status:
            logger.info(f"Успешно создана invite_link в БД для чата {telegram_chat.name}: {invite_link.link}")
        else:
            logger.info(f"Успешно обновлена invite_link в БД для чата {telegram_chat.name}: {invite_link.link}")

        return invite_link, create_status

    except InviteLink.DoesNotexist:
        logger.error(f"Ошибка: не удалось найти invite_link для чата {telegram_chat.name}")
    except Exception as e:
        logger.error(f"Ошибка при обновлении/создании invite_link для чата {telegram_chat.name}: {str(e)}")
        return False


async def create_or_get_public_link(telegram_chat: TelegramChat, chat_username: Optional[str]) -> InviteLink:
    link = None
    if chat_username:
        link = f"https://t.me/{chat_username}"
    try:
        invite_link = await InviteLink.objects.aget(telegram_chat=telegram_chat, public_link=True)
    except InviteLink.DoesNotExist:
        logger.info(f"Не нашёл ссылки для канала {telegram_chat.username}")
        invite_link = await InviteLink.objects.acreate(
            telegram_chat=telegram_chat,
            link=link,
            public_link=True)
        return invite_link
    return invite_link
