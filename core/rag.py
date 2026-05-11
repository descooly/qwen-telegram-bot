# core/rag.py
import aiofiles
import os
from typing import List, Dict

KNOWLEDGE_DIR = "knowledge_base"

# Приоритет файлов (чем выше — тем важнее)
FILE_PRIORITY = {
    "pricing.md": 10,
    "services.md": 9,
    "about.md": 8,
    "cases.md": 6,
    "faq.md": 5,
}

async def load_file_content(filename: str) -> str:
    """Загружает один файл"""
    path = os.path.join(KNOWLEDGE_DIR, filename)
    try:
        async with aiofiles.open(path, encoding="utf-8") as f:
            content = await f.read()
            return f"{content.strip()}\n"
    except Exception:
        return ""


async def get_relevant_knowledge(query: str) -> str:
    """
    Улучшенный RAG с расширенным словарем ключевых слов.
    """
    query_lower = query.lower()
    important_files = set()

    # Расширенный словарь (учитываем разные формы)
    keywords = {
        "услуга": ["services.md", "pricing.md"],
        "услуги": ["services.md", "pricing.md"],
        "услугах": ["services.md", "pricing.md"],
        "цена": ["pricing.md", "services.md"],
        "цены": ["services.md", "pricing.md"],
        "цен": ["services.md", "pricing.md"],
        "стоимость": ["pricing.md"],
        "сколько стоит": ["pricing.md"],
        "консультация": ["services.md", "pricing.md"],
        "записаться": ["services.md"],
        "запись": ["services.md"],
        "брендинг": ["services.md"],
        "позиционирование": ["services.md"],
        "стратегия": ["services.md"],
        "аудит": ["services.md"],
        "продажи": ["services.md"],
        "маркетинг": ["services.md"],
        "о нас": ["about.md"],
        "компания": ["about.md"],
        "отважный": ["about.md"],
        "ирина": ["about.md"],
        "отвагина": ["about.md"],
        "кейс": ["cases.md"],
        "пример": ["cases.md"],
        "вопрос": ["faq.md"]
    }

    for keyword, files in keywords.items():
        if keyword in query_lower:
            important_files.update(files)

    # Если запрос про услуги — приоритет pricing + services
    if any(word in query_lower for word in ["услуга", "услуги", "цена", "стоимость", "консультация"]):
        important_files.update(["pricing.md", "services.md"])

    # Если ничего не нашли — берём основные файлы
    if not important_files:
        important_files = {"pricing.md", "services.md", "about.md"}

    # Загружаем по приоритету
    relevant_parts = []
    for filename in sorted(FILE_PRIORITY.keys(), key=lambda x: FILE_PRIORITY[x], reverse=True):
        if filename in important_files:
            content = await load_file_content(filename)
            if content:
                relevant_parts.append(content)

    return "\n".join(relevant_parts)


async def load_all_knowledge() -> str:
    """Загружает всю базу знаний (используется редко)"""
    parts = []
    for filename in sorted(os.listdir(KNOWLEDGE_DIR)):
        if filename.endswith(".md"):
            content = await load_file_content(filename)
            if content:
                parts.append(content)
    return "\n".join(parts)