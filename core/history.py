from collections import defaultdict, deque
from typing import Dict, List, Deque

# user_id -> deque of messages (максимум 20 последних сообщений)
user_histories: Dict[int, Deque[dict]] = defaultdict(lambda: deque(maxlen=20))


def add_to_history(user_id: int, role: str, content: str):
    """Добавляем сообщение в историю пользователя"""
    user_histories[user_id].append({"role": role, "content": content})


def get_history(user_id: int, max_messages: int = 15) -> List[dict]:
    """Возвращаем последние N сообщений пользователя"""
    history = list(user_histories[user_id])
    # Оставляем только последние max_messages
    return history[-max_messages:]


def clear_history(user_id: int):
    """Очистка истории (если нужно)"""
    if user_id in user_histories:
        user_histories[user_id].clear()