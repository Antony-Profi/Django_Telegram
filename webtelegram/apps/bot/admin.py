from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.db.models import ManyToOneRel

from .models import BotUser, TelegramChat, InviteLink, TelegramSubscriber


admin.site.unregister(User)
admin.site.unregister(Group)


def get_fields_for_model(db_model) -> list[str]:
    fields = []
    for field in db_model._meta.get_fields():
        if isinstance(field, ManyToOneRel):
            continue
        fields.append(field.name)
    return fields


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = get_fields_for_model(BotUser)
    search_fields = ["telegram_id", "username", "first_name", "last_name"]
    list_editable = ["telegram_id", "first_name"]
    list_filter = ["first_name"]


@admin.register(TelegramChat)
class TelegramChatAdmin(admin.ModelAdmin):
    list_display = get_fields_for_model(TelegramChat)


@admin.register(InviteLink)
class InviteLinkAdmin(admin.ModelAdmin):
    list_display = get_fields_for_model(InviteLink)


@admin.register(TelegramSubscriber)
class TelegramSubscriberAdmin(admin.ModelAdmin):
    list_display = get_fields_for_model(TelegramSubscriber)
