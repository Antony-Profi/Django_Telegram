from django.db import models
from django.utils.translation import gettext as _


class BotUser(models.Model):
    """Пользователи чат-бота"""
    telegram_id = models.PositiveBigIntegerField(_("ID Telegram"), db_index=True, unique=True)
    username = models.CharField(_("Username"), max_length=150, blank=True, null=True)
    first_name = models.CharField(_("Имя"), max_length=150, blank=True, null=True)
    last_name = models.CharField(_("Фамилия"), max_length=150, blank=True, null=True)

    class Meta:
        verbose_name = "Пользователь бота"
        verbose_name_plural = "Пользователи бота"


class TelegramChat(models.Model):
    """Телеграм канал или чат"""
    bot_user = models.ForeignKey(BotUser, verbose_name=_("Пользователь бота"), on_delete=models.CASCADE)
    name = models.CharField(_("Имя канала"), max_length=150, blank=True, null=True)

    class Meta:
        verbose_name = "Телеграм канал"
        verbose_name_plural = "Телеграм каналы"


class InviteLink(models.Model):
    """Пригласительные ссылки"""
    telegram_chat = models.ForeignKey(TelegramChat, verbose_name=_("Телеграм канал"), on_delete=models.CASCADE)
    creates_join_request = models.BooleanField(_("Запрос на добавление"), default=False)
    creator = models.CharField(_("Создатель"), max_length=250, blank=True, null=True)
    expire_date = models.CharField(_("expire_date"), max_length=150, blank=True, null=True)
    link = models.CharField(_("Ссылка"), max_length=150, blank=True, null=True)
    is_primary = models.BooleanField(_("Is_primary"), blank=True, null=True)
    is_revoked = models.BooleanField(_("Is revoked"), blank=True, null=True)
    member_limit = models.IntegerField(_("Лимит подписок"), blank=True, null=True)
    name = models.CharField(_("name"), max_length=150, blank=True, null=True)
    pending_join_request_count = models.IntegerField(_("pending_join_request_count"), blank=True, null=True)

    class Meta:
        verbose_name = "Пригласительная ссылка"
        verbose_name_plural = "Пригласительные ссылки"


class TelegramSubscriber(models.Model):
    """Пользователи телеграм канала"""
    invite_link = models.ForeignKey(TelegramChat, verbose_name=_("Пригласительная ссылка"), on_delete=models.CASCADE)
    telegram_id = models.PositiveBigIntegerField(_("ID Telegram"), db_index=True, unique=True)
    username = models.CharField(_("Username"), max_length=150, blank=True, null=True)
    first_name = models.CharField(_("Имя"), max_length=150, blank=True, null=True)
    last_name = models.CharField(_("Фамилия"), max_length=150, blank=True, null=True)
    subscribed = models.BooleanField(_("Подписан"), default=False)
    datetime_subscribe = models.DateTimeField(_("Время подписки"), blank=True, null=True)
    datetime_unsubscribe = models.DateTimeField(_("Время отписки"), blank=True, null=True)

    class Meta:
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"
