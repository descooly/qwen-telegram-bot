from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            print(f"📨 Сообщение от {event.from_user.id}: {event.text}")
        elif isinstance(event, CallbackQuery):
            print(f"🔘 Callback от {event.from_user.id}: {event.data}")
        return await handler(event, data)