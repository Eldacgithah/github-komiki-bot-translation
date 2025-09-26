from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError

from app.db.functions import User, Chat
from app.config import Config

router = Router()

@router.message(Command(commands=["mail"]))
async def mail_handler(message: Message, bot: Bot, config: Config):
    if message.chat.id != config.settings.owner_id:
        return await message.answer("🚫 Эта команда доступна только владельцу бота.")

    args = message.text.split(maxsplit=2)

    if len(args) < 2:
        return await message.answer("ℹ️ Использование:\n/mail [users|chats|all] <сообщение>")

    target = args[1].lower()
    text = args[2] if len(args) > 2 else ""

    if not text:
        return await message.answer("⚠️ Вы должны указать сообщение для отправки.")

    if target not in ["users", "chats", "all"]:
        return await message.answer("❌ Неверный параметр. Используйте 'users', 'chats' или 'all'.")

    users = await User.all() if target in ["users", "all"] else []
    chats = await Chat.all() if target in ["chats", "all"] else []

    recipients_users = [u.telegram_id for u in users]
    recipients_chats = [{"id": c.chat_id, "topic": c.topic_id} for c in chats]

    await message.answer(f"📢 Рассылка начата.\nВсего получателей: {len(recipients_users) + len(recipients_chats)}")

    sent_users = 0
    sent_chats = 0
    for tg_id in recipients_users:
        try:
            await bot.send_message(
                chat_id=tg_id, text=text, disable_web_page_preview=True
            )
            sent_users += 1
        except TelegramAPIError:
            continue

    for chat in recipients_chats:
        try:
            await bot.send_message(
                chat_id=chat["id"],
                text=text,
                disable_web_page_preview=True,
                message_thread_id=chat.get("topic", None) if chat.get("topic") else None,
            )
            sent_chats += 1
        except TelegramAPIError:
            continue

    await message.answer(f"✅ Рассылка завершена.\nУспешно отправлено: {sent_users} пользователям и {sent_chats} чатам.")
