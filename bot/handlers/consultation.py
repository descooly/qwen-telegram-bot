from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states import Consultation
from core.llm import get_qwen_response
from core.rag import get_knowledge

router = Router()

@router.message(F.text)
async def handle_any_message(message: Message, state: FSMContext):
    user_text = message.text

    # Простой RAG + LLM
    knowledge = get_knowledge(user_text)
    system_prompt = f"Ты — эксперт маркетингового консалтинга агентства «Отважный маркетинг». Используй следующую информацию:\n{knowledge}\n\nОтвечай профессионально, по делу, на русском языке."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text}
    ]

    response = await get_qwen_response(messages)
    await message.answer(response)