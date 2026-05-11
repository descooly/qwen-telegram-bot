from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")
    YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
    YANDEX_QWEN_MODEL = os.getenv("YANDEX_QWEN_MODEL")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot.db")

    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

config = Config()