# bot/handlers/admin.py
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.states import AdminStates
from database.repository import get_pending_appointments, mark_appointment_processed
from config import config

router = Router()


def get_admin_keyboard():
    kb = [
        [InlineKeyboardButton(text="📋 Незавершённые заявки", callback_data="show_pending")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    await message.answer("🔐 Введите пароль для входа в панель сотрудника:")
    await state.set_state(AdminStates.waiting_for_password)


@router.message(AdminStates.waiting_for_password)
async def admin_login(message: Message, state: FSMContext):
    if message.text.strip() == config.ADMIN_PASSWORD:
        await state.clear()
        await message.answer(
            "✅ Доступ разрешён!\n\n"
            "Выберите действие:",
            reply_markup=get_admin_keyboard()
        )
    else:
        await message.answer("❌ Неверный пароль.")


@router.callback_query(F.data == "show_pending")
async def show_pending(callback: CallbackQuery):
    appointments = await get_pending_appointments()

    if not appointments:
        await callback.message.edit_text("✅ На данный момент все заявки обработаны.")
        await callback.answer()
        return

    await callback.message.edit_text("📋 Незавершённые заявки:")

    for app in appointments:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="✅ Отметить как обработанную",
                callback_data=f"done_{app.id}"
            )
        ]])

        text = (
            f"🆔 Заявка #{app.id}\n"
            f"👤 {app.fio}\n"
            f"📞 {app.phone}\n"
            f"💬 {app.comment or '—'}\n"
            f"🕒 {app.timestamp.strftime('%d.%m.%Y %H:%M')}"
        )

        await callback.message.answer(text, reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data.startswith("done_"))
async def mark_done(callback: CallbackQuery):
    app_id = int(callback.data.replace("done_", ""))

    success = await mark_appointment_processed(app_id)

    if success:
        # Редактируем сообщение с заявкой
        await callback.message.edit_text(
            callback.message.text + "\n\n✅ Заявка обработана"
        )
        await callback.answer("Заявка отмечена как обработанная ✅")
    else:
        await callback.answer("❌ Не удалось найти заявку")