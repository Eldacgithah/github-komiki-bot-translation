from tortoise import fields
from tortoise.models import Model

from enum import Enum


class EventType(str, Enum):
    ping = "ping"  "Событие ping"
    push = "push"  "Событие push"
    issues = "issues"  "Событие issues (вопросы/проблемы)"
    star = "star"  "Событие star (звезда)"
    create = "create"  "Событие create (создание)"
    pull_request = "pull_request"  "Событие pull_request (запрос на изменение)"


class User(Model):
    id = fields.BigIntField(pk=True)  "ID пользователя"
    telegram_id = fields.BigIntField()  "ID Telegram пользователя"
    token = fields.CharField(max_length=255, null=True)  "Токен пользователя"
    created_at = fields.DatetimeField(auto_now_add=True)  "Дата создания записи"


class Eventsetting(Model):
    id = fields.BigIntField(pk=True)  "ID настройки события"
    chat_id = fields.BigIntField()  "ID чата"
    event_type = fields.CharField(max_length=50)  "Тип события"
    enabled = fields.BooleanField(default=True)  "Включено ли событие"


class Chat(Model):
    id = fields.BigIntField(pk=True)  "ID чата"
    chat_id = fields.BigIntField()  "Telegram ID чата"
    topic_id = fields.BigIntField(null=True)  "ID темы чата (опционально)"
    floodwait = fields.IntField(default=0)  "Время задержки (floodwait)"


class Integration(Model):
    id = fields.BigIntField(pk=True)  "ID интеграции"
    repository_name = fields.CharField(max_length=255, null=True)  "Имя репозитория"
    integration_token = fields.CharField(max_length=255, null=True)  "Токен интеграции"

    chat = fields.ForeignKeyField(
        "models.Chat", related_name="integrations", on_delete=fields.CASCADE
    )  "Связь с чатом"
    user = fields.ForeignKeyField(
        "models.User", related_name="integrations", on_delete=fields.CASCADE
    )  "Связь с пользователем"

    created_at = fields.DatetimeField(auto_now_add=True)  "Дата создания записи"
