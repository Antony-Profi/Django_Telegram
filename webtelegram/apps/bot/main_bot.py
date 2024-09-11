import logging
import telebot

from django.conf import settings
from telebot.async_telebot import AsyncTeleBot


bot = AsyncTeleBot(settings.BOT_TOKEN, parse_mode="HTML")

telebot.logger.setLevel(settings.LOG_LEVEL)

logger = logging.getLogger(__name__)


@bot.chat_member_handler()
async def chat_member_handler_bot(message):
    logger.info(f'Here: {message}')
    # await bot.send_message(message.chat.id, "New subscriber")


@bot.message_handler(commands=["help", "start"])
async def send_welcome(message):
    await bot.send_message(message.chat.id, 'Hi, I am EchoBot.\nJust write me something and I will repeat it!')


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, message.text)
