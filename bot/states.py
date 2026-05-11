from aiogram.fsm.state import State, StatesGroup

class Consultation(StatesGroup):
    waiting_for_industry = State()
    waiting_for_budget = State()
    waiting_for_problem = State()
    waiting_for_details = State()

class Appointment(StatesGroup):
    waiting_for_fio = State()  # Ожидаем ФИО
    waiting_for_phone = State()  # Ожидаем телефон
    waiting_for_comment = State()  # Ожидаем комментарий (опционально)
    confirmation = State()  # Подтверждение данных

class AdminStates(StatesGroup):
    waiting_for_password = State()