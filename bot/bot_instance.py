# bot/bot_instance.py
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from config import config

from bot.handlers.base import router as base_router
from bot.handlers.admin import router as admin_router
# Если позже добавишь другие роутеры, подключишь их здесь

session = AiohttpSession()
bot = Bot(token=config.TELEGRAM_BOT_TOKEN, session=session)
dp = Dispatcher()

# Подключаем все роутеры
dp.include_router(admin_router)
dp.include_router(base_router)

# Middleware (логирование)
from bot.middleware import LoggingMiddleware
dp.message.middleware(LoggingMiddleware())
dp.callback_query.middleware(LoggingMiddleware())