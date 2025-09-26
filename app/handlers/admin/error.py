from aiogram import Router
from aiogram.types import ErrorEvent
from aiogram.filters import Command

import logging
import traceback
import html

from app.config import Config

router = Router()

@router.error()
async def error_handler(event: ErrorEvent, config: Config):
    bot = event.update.bot
    update = event.update
    exception = event.exception

    try:
        user_id = update.callback_query.from_user.id
        user_username = update.callback_query.from_user.username
        request = f"callback_data: <code>{update.callback_query.data}</code>"
    except AttributeError:
        user_id = update.message.from_user.id
        user_username = update.message.from_user.username
        request = f"text: <code>{update.message.text}</code>"

    last_frame = traceback.extract_tb(exception.__traceback__)[-1]

    formatted_traceback = (
        f"📁 Файл: <code>{html.escape(last_frame.filename)}</code>\n"
        f"📌 Строка: <code>{last_frame.lineno}</code>\n"
        f"⚡ Тип ошибки: <code>{html.escape(exception.__class__.__name__)}</code>\n"
        f"🛠 Функция: <code>{html.escape(last_frame.name)}</code>\n"
        f"💬 Сообщение: <code>{html.escape(str(exception))}</code>\n"
        f"📜 Код: <code>{html.escape(last_frame.line)}</code>"
    )

    debug_info = (
        f"👤 Пользователь: @{user_username} ({user_id})\n"
        f"{request}"
    )

    await bot.send_message(
        chat_id=config.settings.owner_id,
        text=(
            f"<b>❗ Информация об ошибке:</b>\n"
            f"<blockquote>{formatted_traceback}</blockquote>\n\n"
            f"<b>🖥 Отладка:</b>\n"
            f"<blockquote>{html.escape(debug_info)}</blockquote>"
        ),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

    logging.error(
        f"Ошибка пользователя @{user_username} ({user_id})\n"
        f"Запрос: {request}\n"
        f"Ошибка: {exception}\n"
        f"Traceback:\n{traceback.format_exc()}"
    )


@router.message(Command(commands=["error"]))
async def error_command_handler(message: ErrorEvent, config: Config):
    if message.from_user.id != config.settings.owner_id:
        return await message.answer("🚫 У вас нет доступа к этой команде.")

    raise Exception("🧪 Это тестовая ошибка для отладки.")
