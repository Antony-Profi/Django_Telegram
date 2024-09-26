import logging
import telebot

from django.conf import settings
from telebot.async_telebot import AsyncTeleBot
from os import environ

from telebot.types import Message, ChatMemberUpdated
from webtelegram.apps.bot.middleware import CustomMiddleware
from webtelegram.services.database.bot_user_dao import update_or_create_tg_user
from webtelegram.services.database.invite_link_dao import update_invite_link, create_or_get_public_link
from webtelegram.services.database.telegram_chat_dao import update_telegram_chat, get_all_channels, \
    get_telegram_chat_by_chat_id
from webtelegram.services.database.telegram_subscriber_dao import (
    check_exist_subscriber_in_channel,
    update_or_create_subscriber
)
from webtelegram.services.utils.subscriber_status_parser import member_is_subscriber

bot = AsyncTeleBot(settings.BOT_TOKEN, parse_mode="HTML")

telebot.logger.setLevel(settings.LOG_LEVEL)

logger = logging.getLogger(__name__)

bot.setup_middleware(CustomMiddleware())


@bot.chat_member_handler()
async def chat_member_handler_bot(message: ChatMemberUpdated):
    channels_ids = [channel.chat_id async for channel in await get_all_channels()]
    if message.chat.id not in channels_ids:
        logger.info(f"!!! Канала {message.chat.id} нет в списке разрешённых")
        return None

    telegram_chat = await update_telegram_chat(chat_data=message.chat)
    if not telegram_chat:
        logger.warning(f"Чат с ID {message.chat.id} не найден")
        return None

    invite_link = message.invite_link
    logger.info(f"{invite_link=}")

    full_name = message.from_user.full_name
    logger.info(f"{full_name=}")

    username = message.from_user.username
    logger.info(f"{username=}")

    id = message.from_user.id
    logger.info(f"{id=}")

    invite_link_name = ""
    invite_link_url = ""

    try:
        invite_link_name = getattr(invite_link, "name")
        logger.info(f"{invite_link_name=}")

        invite_link_url = getattr(invite_link, "invite_link")
        logger.info(f"{invite_link_url=}")
    except AttributeError as err:
        logger.info(f"Не получил пригласительную ссылку: {err}")
        # Не получил пригласительную ссылку, значит ссылка общая, создаём её
        invite_link_db = await create_or_get_public_link(
            telegram_chat=telegram_chat,
            chat_username=message.chat.username)
        # Но надо проверить, для тех кто уже когда-то заходил по пригласительной.
        # У них тоже может не быть ссылки
    else:
        # Запомнить пригласительную ссылку для этого канала
        invite_link_db, create_status = await update_invite_link(
            telegram_chat=telegram_chat,
            chat_invite_link_data=message.invite_link)

    subscribed = member_is_subscriber(chat_member_updated=message)
    subscriber_exist = await check_exist_subscriber_in_channel(chat_data=message.chat, user_data=message.from_user)
    if subscriber_exist is True:
        """Если пользователь есть в базе, то не трогаем ссылку к которой он привязан"""
        await update_or_create_subscriber(
            chat_data=message.chat,
            user_data=message.from_user,
            subscribed=subscribed,
            invite_link=None)
    else:
        """Если пользователя нет в базе, то привязываем его к ссылке публичной или приватной"""
        await update_or_create_subscriber(
            chat_data=message.chat,
            user_data=message.from_user,
            subscribed=subscribed,
            invite_link=invite_link_db)

    if subscriber_exist is True:
        status_text = "🚀 Подписались"
    elif subscribed is False:
        status_text = "🫤 Отписались"
    else:
        status_text = "😯 Неизвестно"

    text_message = (f"Канал: {telegram_chat.name}\n"
                    f"Статус: {status_text}\n"
                    f"Имя: {full_name}\n"
                    f"ID: {id}")

    if username:
        text_message += f"\n<b>Никнейм</b>: @{username}"
    if invite_link_name:
        text_message += f"\nНазвание ссылки: {invite_link_name}"
    if invite_link_url:
        text_message += f"\n<b>URL</b>: {invite_link_url}"
    if invite_link_db.notification is True:
        await bot.send_message(chat_id=settings.TELEGRAM_ID_ADMIN, text=text_message)


@bot.message_handler(commands=["help", "start"])
async def send_welcome(message):
    await bot.send_message(message.chat.id, 'Hi, I am EchoBot.\nJust write me something and I will repeat it!')
    await bot.send_message(message.chat.id, message.chat.id)


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)
