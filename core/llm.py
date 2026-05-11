from openai import AsyncOpenAI
from config import config

client = AsyncOpenAI(
    api_key=config.YANDEX_API_KEY,
    base_url="https://llm.api.cloud.yandex.net/v1",
    default_headers={"X-Folder-Id": config.YANDEX_FOLDER_ID}
)

# URI
MODEL_URI = f"gpt://{config.YANDEX_FOLDER_ID}/{config.YANDEX_QWEN_MODEL}"


async def get_qwen_response(messages: list[dict], temperature: float = 0.7) -> str:
    try:
        print(f"🔍 Запрос к модели: {MODEL_URI}")

        response = await client.chat.completions.create(
            model=MODEL_URI,
            messages=messages,
            temperature=temperature,
            max_tokens=3500,
            presence_penalty=0.1,
            # Дополнительные параметры, которые иногда помогают
            extra_body={"stream": False}
        )

        content = response.choices[0].message.content
        print(f"✅ Получен ответ, длина: {len(content) if content else 0}")

        return content.strip() if content else "Модель вернула пустой ответ."

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return "Извините, в данный момент сервис перегружен."