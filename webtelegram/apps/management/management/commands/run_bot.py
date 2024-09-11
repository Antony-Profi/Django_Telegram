import asyncio
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from telebot import util
from webtelegram.apps.bot.main_bot import bot


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Запуск бота"

    def handle(self, *args, **options):
        try:
            asyncio.run(bot.infinity_polling(logger_level=settings.LOG_LEVEL, allowed_updates=util.update_types))
        except Exception as e:
            logger.error(f"Ошибка: {e}")
