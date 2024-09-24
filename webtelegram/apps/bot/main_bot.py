import logging
import telebot

from django.conf import settings
from telebot.async_telebot import AsyncTeleBot
from os import environ

from telebot.types import Message
from webtelegram.apps.bot.middleware import CustomMiddleware
from webtelegram.services.database.invite_link_dao import update_invite_link, create_public_link
from webtelegram.services.database.telegram_chat_dao import update_telegram_chat


bot = AsyncTeleBot(settings.BOT_TOKEN, parse_mode="HTML")

telebot.logger.setLevel(settings.LOG_LEVEL)

logger = logging.getLogger(__name__)

bot.setup_middleware(CustomMiddleware())

MY_CHANNELS = [int(environ.get("MY_CHANNELS"))]


@bot.chat_member_handler()
async def chat_member_handler_bot(message: Message):
    if message.chat.id not in MY_CHANNELS:
        return None
    telegram_chat = await update_telegram_chat(chat_data=message.chat)
    status = message.difference.get("status")
    logger.info(f"{status=}")

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
        await create_public_link(telegram_chat=telegram_chat)
        # Но надо проверить, для тех кто уже когда-то заходил по пригласительной.
        # У них тоже может не быть ссылки
    else:
        # Запомнить пригласительную ссылку для этого канала
        await update_invite_link(telegram_chat=telegram_chat, invite_link_url=invite_link_url)

    current_subscriber_status = status[1]
    if current_subscriber_status == "member":
        status_text = "🚀 Подписались"
    elif current_subscriber_status == "left":
        status_text = "🫤 Отписались"
    else:
        status_text = "😯 Неизвестно"

    text_message = (f"Статус: {status_text}\n"
                    f"Имя: {full_name}\n"
                    f"ID: {id}")

    if username:
        text_message += f"\n<b>Никнейм</b>: @{username}"
    if invite_link_name:
        text_message += f"\nНазвание ссылки: {invite_link_name}"
    if invite_link_url:
        text_message += f"\n<b>URL</b>: {invite_link_url}"

    await bot.send_message(chat_id=settings.TELEGRAM_ID_ADMIN, text=text_message)


@bot.message_handler(commands=["help", "start"])
async def send_welcome(message):
    await bot.send_message(message.chat.id, 'Hi, I am EchoBot.\nJust write me something and I will repeat it!')
    await bot.send_message(message.chat.id, message.chat.id)


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)
