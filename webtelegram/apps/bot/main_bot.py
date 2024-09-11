import logging
import telebot

from django.conf import settings
from telebot.async_telebot import AsyncTeleBot


bot = AsyncTeleBot(settings.BOT_TOKEN, parse_mode="HTML")

telebot.logger.setLevel(settings.LOG_LEVEL)

logger = logging.getLogger(__name__)


@bot.chat_member_handler()
async def chat_member_handler_bot(message):
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
