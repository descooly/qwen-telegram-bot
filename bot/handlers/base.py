# bot/handlers/base.py
import asyncio
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.states import Appointment
from core.history import get_history, add_to_history
from core.llm import get_qwen_response
from core.rag import get_relevant_knowledge, load_file_content
from database.repository import save_conversation, save_appointment

router = Router()

def get_main_keyboard():
    kb = [
        [KeyboardButton(text="📋 Услуги и цены")],
        [KeyboardButton(text="📅 Записаться на консультацию")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Напишите вопрос или выберите действие...")


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Здравствуйте! 👋\n\n"
        "Я — помощник агентства «Отважный маркетинг».\n"
        "Помогу подобрать услугу, показать цены и записать вас на консультацию.",
        reply_markup=get_main_keyboard()
    )


# ==================== КНОПКИ ====================
@router.message(F.text == "📋 Услуги и цены")
async def btn_services(message: Message):
    pricing_text = await load_file_content("pricing.md")
    if not pricing_text:
        pricing_text = "Информация о ценах временно недоступна."
    await message.answer(pricing_text, reply_markup=get_main_keyboard())


@router.message(F.text == "📅 Записаться на консультацию")
async def btn_appointment(message: Message, state: FSMContext):
    await state.set_state(Appointment.waiting_for_fio)
    await message.answer(
        "Отлично! Давайте запишем вас на консультацию.\n\n"
        "Напишите, пожалуйста, ваше ФИО полностью:",
        reply_markup=get_main_keyboard(),
    )


# ==================== FSM ====================
@router.message(Appointment.waiting_for_fio)
async def process_fio(message: Message, state: FSMContext):
    await state.update_data(fio=message.text.strip())
    await state.set_state(Appointment.waiting_for_phone)
    await message.answer("Теперь укажите ваш номер телефона (+7XXXXXXXXXX):")


@router.message(Appointment.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await state.set_state(Appointment.waiting_for_comment)
    await message.answer("Оставьте комментарий или описание задачи (можно пропустить):")


@router.message(Appointment.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text.strip())
    data = await state.get_data()

    confirm_text = (
        f"Проверим данные:\n\n"
        f"👤 ФИО: {data['fio']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"💬 Комментарий: {data.get('comment', '—')}\n\n"
        f"Всё верно?"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, подтверждаю", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Нет, заново", callback_data="confirm_no")
        ]
    ])

    await message.answer(confirm_text, reply_markup=keyboard)


# ==================== CALLBACKS ====================
@router.callback_query(F.data == "confirm_yes")
async def confirm_yes(callback, state: FSMContext):
    data = await state.get_data()

    await save_appointment(
        user_id=callback.from_user.id,
        username=callback.from_user.username or "unknown",
        fio=data.get('fio', ''),
        phone=data.get('phone', ''),
        comment=data.get('comment')
    )

    await callback.message.edit_text("✅ Заявка успешно сохранена!\nМы свяжемся с вами в ближайшее время.")
    await state.clear()


@router.callback_query(F.data == "confirm_no")
async def confirm_no(callback, state: FSMContext):
    await callback.message.edit_text("Хорошо, начнём заново.")
    await state.clear()
    await callback.message.answer(
        "Напишите, пожалуйста, ваше **ФИО** полностью:",
        reply_markup=get_main_keyboard()
    )
    await state.set_state(Appointment.waiting_for_fio)


# ==================== ОБРАБОТКА ЛЮБОГО ТЕКСТА (Qwen) ====================
@router.message(F.text & ~F.text.startswith('/'))
async def handle_user_message(message: Message):
    user_text = message.text.strip()
    user_id = message.from_user.id

    # Добавляем сообщение пользователя в историю
    add_to_history(user_id, "user", user_text)

    # Показываем анимацию
    thinking_msg = await message.answer("🤔 Думаю")

    animation_task = asyncio.create_task(animate_dots(thinking_msg))

    # Получаем историю + актуальные знания
    history = get_history(user_id, max_messages=12)
    knowledge = await get_relevant_knowledge(user_text)

    system_prompt = (
        "Ты — дружелюбный и профессиональный помощник агентства «Отважный маркетинг». "
        "Говори живым, естественным языком, как опытный консультант. "
        "Используй «Вы» с большой буквы только в начале предложения или при прямом обращении. "
        "Не говори фразами типа «Сотрудники агентства», «Мы помогаем» — говори от лица помощника агентства. "
        "Будь вежливым, но не сухим и не слишком официальным. "
        "Отвечай кратко и по делу (2–4 абзаца максимум) "
        "Избегай шаблонных канцелярских фраз. "
        "Названия услуг пиши в кавычках: «Быстрый старт», «Погружение». "
        "Если спрашивают об услугах — обязательно указывай цены. "
        "В конце ответа мягко предлагай дальнейшее действие: продолжить разговор, уточнить детали или записаться на консультацию."
        f"\n\nБаза знаний:\n{knowledge}"
    )

    messages = [{"role": "system", "content": system_prompt}] + history

    response = await get_qwen_response(messages, temperature=0.75)

    # Отменяем анимацию и показываем ответ
    if not animation_task.done():
        animation_task.cancel()


    await thinking_msg.edit_text(response, parse_mode="markdown")


    # Добавляем ответ бота в историю
    add_to_history(user_id, "assistant", response)

    # Сохраняем в базу
    await save_conversation(
        user_id=user_id,
        username=message.from_user.username or "unknown",
        message=user_text,
        response=response
    )


async def animate_dots(message: Message):
    dots = [".", "..", "...", ""]
    try:
        i = 0
        while True:
            await message.edit_text(f"🤔 Думаю{dots[i % 4]}")
            await asyncio.sleep(0.15)
            i += 1
    except asyncio.CancelledError:
        pass
    except Exception:
        pass