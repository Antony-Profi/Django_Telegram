import logging

from asgiref.sync import sync_to_async
from telebot.types import Chat, User
from typing import Union

from webtelegram.apps.bot.models import BotUser

logger = logging.getLogger(__name__)


@sync_to_async
def update_or_create_tg_user(data: Union[Chat, User]):
    try:
        data = getattr(data, "chat")
    except AttributeError:
        data = data

    first_name = data.first_name
    if data.first_name is None:
        first_name = ""

    last_name = data.last_name
    if data.last_name is None:
        last_name = ""

    username = data.username
    if data.username is None:
        username = ""

    defaults_dict = {
        "first_name": first_name,
        "last_name": last_name,
        "username": username
    }
    telegram_user, create_status = BotUser.objects.update_or_create(telegram_id=data.id, defaults=defaults_dict)

    if create_status is False:
        logger.info(f"Успешно обновлен user в БД {first_name} {last_name} {username}")
    else:
        logger.info(f"Успешно создан user в БД {first_name} {last_name} {username}")
    return create_status
