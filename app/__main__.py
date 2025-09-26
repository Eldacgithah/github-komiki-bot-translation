import asyncio  
import logging  
import threading  

import coloredlogs  
from aiogram import Bot, Dispatcher  
from aiogram.client.session.aiohttp import AiohttpSession  
from aiogram.client.telegram import TelegramAPIServer  
from aiogram.fsm.storage.memory import MemoryStorage  
from aiogram.client.default import DefaultBotProperties  
from aiogram.enums import ParseMode  

from app import db  
from app.arguments import parse_arguments  
from app.config import Config, parse_config  
from app.db import close_orm, init_orm  
from app.handlers import get_handlers_router  
from app.middlewares import register_middlewares  
from app.commands import remove_bot_commands, setup_bot_commands  
from app.webhook import dispatcher as webhook_dispatcher  


async def on_startup(dispatcher: Dispatcher, bot: Bot, config: Config):  
    register_middlewares(dp=dispatcher, config=config)  

    dispatcher.include_router(get_handlers_router())  

    await setup_bot_commands(bot, config)  

    await bot.delete_webhook(drop_pending_updates=config.settings.drop_pending_updates)  

    tortoise_config = config.database.get_tortoise_config()  
    await init_orm(tortoise_config)  

    bot_info = await bot.get_me()  

    logging.info(f"🤖 Имя бота: {bot_info.full_name}")  
    logging.info(f"📛 Юзернейм: @{bot_info.username}")  
    logging.info(f"🆔 ID: {bot_info.id}")  

    states = {True: "Включено ✅", False: "Выключено ❌"}  

    logging.debug(f"👥 Режим групп: {states[bot_info.can_join_groups]}")  
    logging.debug(f"🔒 Режим приватности: {states[not bot_info.can_read_all_group_messages]}")  
    logging.debug(f"💬 Инлайн-режим: {states[bot_info.supports_inline_queries]}")  

    logging.error("🚀 Бот успешно запущен!")


async def on_shutdown(dispatcher: Dispatcher, bot: Bot, config: Config):  
    logging.warning("⚠️ Останавливаем бота...")  
    await remove_bot_commands(bot, config)  
    await bot.delete_webhook(drop_pending_updates=config.settings.drop_pending_updates)  
    await dispatcher.fsm.storage.close()  
    await bot.session.close()  
    await close_orm()  


async def main():  
    coloredlogs.install(level=logging.INFO)  
    logging.warning("🔄 Запуск бота...")  

    arguments = parse_arguments()  
    config = parse_config(arguments.config)  

    tortoise_config = config.database.get_tortoise_config()  
    try:  
        await db.create_models(tortoise_config)  
    except FileExistsError:  
        await db.migrate_models(tortoise_config)  

    session = AiohttpSession(api=TelegramAPIServer.from_base(config.api.bot_api_url, is_local=config.api.is_local))  
    token = config.bot.token  
    bot_settings = {  
        "session": session,  
        "default": DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True),  
    }  

    bot = Bot(token, **bot_settings)  

    storage = MemoryStorage()  

    dp = Dispatcher(storage=storage)  
    dp.startup.register(on_startup)  
    dp.shutdown.register(on_shutdown)  

    context_kwargs = {"config": config}  

    await dp.start_polling(bot, **context_kwargs)  


if __name__ == "__main__":  
    try:  
        threading.Thread(target=webhook_dispatcher).start()  
        asyncio.run(main())  
    except (KeyboardInterrupt, SystemExit):  
        logging.error("🛑 Бот остановлен пользователем")
