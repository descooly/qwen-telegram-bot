from sqlalchemy import insert, select, update
from database.session import AsyncSessionLocal
from database.models import Conversation, Appointment
from core.security import encrypt, decrypt

async def save_conversation(user_id: int, username: str, message: str, response: str):
    encrypted_message = encrypt(message)
    encrypted_response = encrypt(response)

    async with AsyncSessionLocal() as session:
        stmt = insert(Conversation).values(
            user_id=user_id,
            username=username,
            message=encrypted_message,
            response=encrypted_response
        )
        await session.execute(stmt)
        await session.commit()

async def save_appointment(user_id: int, username: str, fio: str, phone: str, comment: str = None):
    """Сохраняет заявку на консультацию"""
    encrypted_fio = encrypt(fio)
    encrypted_phone = encrypt(phone)
    encrypted_comment = encrypt(comment) if comment else None

    async with AsyncSessionLocal() as session:
        stmt = insert(Appointment).values(
            user_id=user_id,
            username=username,
            fio=encrypted_fio,
            phone=encrypted_phone,
            comment=encrypted_comment
        )
        await session.execute(stmt)
        await session.commit()


async def get_pending_appointments():
    """Получить все незавершённые заявки с расшифровкой данных"""
    async with AsyncSessionLocal() as session:
        stmt = select(Appointment).where(Appointment.status == "new").order_by(Appointment.timestamp.desc())
        result = await session.execute(stmt)
        appointments = result.scalars().all()

        # Расшифровываем данные перед возвратом
        for app in appointments:
            try:
                app.fio = decrypt(app.fio)
            except:
                app.fio = "[Ошибка расшифровки]"

            try:
                app.phone = decrypt(app.phone)
            except:
                app.phone = "[Ошибка расшифровки]"

            if app.comment:
                try:
                    app.comment = decrypt(app.comment)
                except:
                    app.comment = "[Ошибка расшифровки]"

        return appointments


async def mark_appointment_processed(appointment_id: int) -> bool:
    """Отметить заявку как обработанную"""
    async with AsyncSessionLocal() as session:
        stmt = update(Appointment).where(
            Appointment.id == appointment_id
        ).values(status="processed")

        result = await session.execute(stmt)
        await session.commit()

        return result.rowcount > 0