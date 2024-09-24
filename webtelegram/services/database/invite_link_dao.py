import logging

from asgiref.sync import sync_to_async
from telebot.types import Chat

from webtelegram.apps.bot.models import TelegramChat, InviteLink


logger = logging.getLogger(__name__)


async def update_invite_link(telegram_chat: TelegramChat, invite_link_data):
    defaults_dict = {
        "name": invite_link_data.name,
        "link": invite_link_data.invite_link,
        "creates_join_request": invite_link_data.creates_join_request,
        "creator": invite_link_data.creator,
        "expire_date": invite_link_data.expire_date,
        "member_limit": invite_link_data.member_limit,
        "pending_join_request_count": invite_link_data.pending_join_request_count,
    }
    try:
        invite_link, create_status = await InviteLink.objects.aupdate_or_create(telegram_chat=telegram_chat,
                                         link=invite_link_data.invite_link,
                                         defaults=defaults_dict)
        if create_status:
            logger.info(f"Успешно создана invite_link в БД для чата {telegram_chat.name}: {invite_link.link}")
        else:
            logger.info(f"Успешно обновлена invite_link в БД для чата {telegram_chat.name}: {invite_link.link}")

        return create_status

    except InviteLink.DoesNotexist:
        logger.error(f"Ошибка: не удалось найти invite_link для чата {telegram_chat.name}")
    except Exception as e:
        logger.error(f"Ошибка при обновлении/создании invite_link для чата {telegram_chat.name}: {str(e)}")
        return False


async def create_public_link(telegram_chat: TelegramChat):
    try:
        await InviteLink.objects.aget(telegram_chat=telegram_chat, public_link=True)
    except InviteLink.DoesNotExist:
        logger.info(f"Не нашёл ссылки для канала {telegram_chat.username}")
        await InviteLink.objects.acreate(telegram_chat=telegram_chat, public_link=True)
        return True

    return False
