# test_qwen.py
import asyncio

from config import config
from core.llm import get_qwen_response

async def test_qwen():
    print(f"🔍 Тестируем {config.YANDEX_QWEN_MODEL}...\n")

    messages = [
        {"role": "system", "content": "Ты — высококвалифицированный маркетинговый консультант агентства «Отважный маркетинг». Отвечай профессионально, точно и по делу."},
        {"role": "user", "content": "Привет! Расскажи, какие основные услуги предлагает ваше агентство и в чём ваше главное преимущество."}
    ]

    response = await get_qwen_response(messages, temperature=0.7)
    print("✅ Ответ от модели:\n")
    print(response)

if __name__ == "__main__":
    asyncio.run(test_qwen())