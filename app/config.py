# sourcery skip: avoid-builtin-shadow
import os
from dataclasses import MISSING, dataclass, fields

import toml


@dataclass
class ConfigBot:
    token: str  # Токен бота


@dataclass
class ConfigDatabase:
    models: list[str]  # Список моделей базы данных
    protocol: str = "sqlite"  # Протокол базы (sqlite, postgresql и т.д.)
    file_name: str = "production-database.sqlite3"  # Имя файла БД для sqlite
    user: str = None  # Пользователь БД
    password: str = None  # Пароль БД
    host: str = None  # Хост БД
    port: str = None  # Порт БД

    def get_db_url(self):
        if self.protocol == "sqlite":
            return f"{self.protocol}://{self.file_name}"
        return f"{self.protocol}://{self.user}:{self.password}@{self.host}:{self.port}"

    def get_tortoise_config(self):
        return {
            "connections": {"default": self.get_db_url()},
            "apps": {
                "models": {
                    "models": self.models,
                    "default_connection": "default",
                },
            },
        }


@dataclass
class ConfigSettings:
    owner_id: int  # ID владельца бота
    throttling_rate: float = 0.5  # Ограничение скорости обработки запросов
    drop_pending_updates: bool = True  # Сбрасывать ли обновления при старте


@dataclass
class ConfigApi:
    id: int = 2040  # ID API
    hash: str = "b18441a1ff607e10a989891a5462e627"  # Хеш API
    bot_api_url: str = "https://api.telegram.org"  # URL API Telegram
    host: str = "localhost:4454"  # Локальный хост

    @property
    def is_local(self):
        return self.bot_api_url != "https://api.telegram.org"  # Проверка, используется ли локальный API


@dataclass
class Config:
    bot: ConfigBot
    database: ConfigDatabase
    settings: ConfigSettings
    api: ConfigApi

    @classmethod
    def parse(cls, data: dict) -> "Config":
        sections = {}

        for section in fields(cls):
            pre = {}
            current = data[section.name]

            for field in fields(section.type):
                if field.name in current:
                    pre[field.name] = current[field.name]
                elif field.default is not MISSING:
                    pre[field.name] = field.default
                else:
                    raise ValueError(
                        f"Отсутствует поле {field.name} в секции {section.name}"
                    )

            sections[section.name] = section.type(**pre)

        return cls(**sections)


def parse_config(config_file: str = "config.toml") -> Config:
    if not os.path.isfile(config_file) and not config_file.endswith(".toml"):
        config_file += ".toml"

    if not os.path.isfile(config_file):
        raise FileNotFoundError(f"Файл конфигурации не найден: {config_file}")

    with open(config_file, "r") as f:
        data = toml.load(f)

    return Config.parse(dict(data))
