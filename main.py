import asyncio
import logging
from bot.bot_instance import bot, dp
from database.session import init_db

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()          # создаём таблицы
    print("🚀 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())