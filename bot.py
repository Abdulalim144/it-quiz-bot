import asyncio
import logging
import os
import random
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN не найден")


bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_NAME = "quiz.db"


# =========================
# БАЗА ДАННЫХ
# =========================

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            correct INTEGER DEFAULT 0,
            wrong INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def add_user(user):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (telegram_id, username, first_name)
        VALUES (?, ?, ?)
    """, (
        user.id,
        user.username,
        user.first_name
    ))

    conn.commit()
    conn.close()


def update_statistics(user_id, correct):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if correct:
        cursor.execute("""
            UPDATE users
            SET correct = correct + 1,
                total = total + 1
            WHERE telegram_id = ?
        """, (user_id,))
    else:
        cursor.execute("""
            UPDATE users
            SET wrong = wrong + 1,
                total = total + 1
            WHERE telegram_id = ?
        """, (user_id,))

    conn.commit()
    conn.close()


def get_statistics(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT correct, wrong, total
        FROM users
        WHERE telegram_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    return result or (0, 0, 0)


# =========================
# ВОПРОСЫ
# =========================

QUESTIONS = [
    {
        "question": "Что делает команда git pull?",
        "answers": [
            "Удаляет репозиторий",
            "Получает изменения из удалённого репозитория",
            "Создаёт новую ветку",
            "Удаляет последний commit",
        ],
        "correct": 1,
        "explanation": "git pull получает изменения из удалённого репозитория и интегрирует их в текущую ветку."
    },

    {
        "question": "Какой язык обычно используется для создания интерактивности на веб-странице?",
        "answers": [
            "HTML",
            "CSS",
            "JavaScript",
            "SQL",
        ],
        "correct": 2,
        "explanation": "JavaScript используется для добавления интерактивного поведения веб-страниц."
    },

    {
        "question": "Что означает SQL?",
        "answers": [
            "Structured Query Language",
            "Simple Question Language",
            "System Query Logic",
            "Server Question Language",
        ],
        "correct": 0,
        "explanation": "SQL расшифровывается как Structured Query Language."
    },

    {
        "question": "Какой тип данных используется для хранения True или False в Python?",
        "answers": [
            "String",
            "Boolean",
            "List",
            "Integer",
        ],
        "correct": 1,
        "explanation": "В Python логические значения True и False имеют тип bool."
    },

    {
        "question": "Что такое API?",
        "answers": [
            "Графический редактор",
            "Интерфейс взаимодействия программ",
            "Тип базы данных",
            "Операционная система",
        ],
        "correct": 1,
        "explanation": "API — это интерфейс, через который программы могут взаимодействовать друг с другом."
    },

    {
        "question": "Что делает CSS?",
        "answers": [
            "Хранит данные",
            "Стилизует веб-страницу",
            "Создаёт SQL-запросы",
            "Запускает сервер",
        ],
        "correct": 1,
        "explanation": "CSS отвечает за внешний вид и оформление HTML-страницы."
    },

    {
        "question": "Что такое Docker?",
        "answers": [
            "Среда для запуска приложений в контейнерах",
            "Язык программирования",
            "База данных",
            "Редактор изображений",
        ],
        "correct": 0,
        "explanation": "Docker позволяет запускать приложения в изолированных контейнерах."
    },

    {
        "question": "Какая команда создаёт новый Git-репозиторий?",
        "answers": [
            "git start",
            "git create",
            "git init",
            "git new",
        ],
        "correct": 2,
        "explanation": "Команда git init создаёт новый локальный Git-репозиторий."
    },

    {
        "question": "Что такое HTTP?",
        "answers": [
            "Протокол передачи данных в вебе",
            "Язык программирования",
            "База данных",
            "Операционная система",
        ],
        "correct": 0,
        "explanation": "HTTP — протокол, используемый для передачи данных между клиентом и веб-сервером."
    },

    {
        "question": "Какой тег HTML используется для создания ссылки?",
        "answers": [
            "<link>",
            "<a>",
            "<url>",
            "<href>",
        ],
        "correct": 1,
        "explanation": "Для создания гиперссылки в HTML используется тег <a>."
    },
]


# =========================
# СОСТОЯНИЕ ТЕСТОВ
# =========================

user_quizzes = {}


# =========================
# КЛАВИАТУРА
# =========================

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧠 Начать тест",
                    callback_data="start_quiz"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="statistics"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Помощь",
                    callback_data="help"
                )
            ],
        ]
    )


# =========================
# START
# =========================

@dp.message(Command("start"))
async def start_handler(message: Message):
    add_user(message.from_user)

    await message.answer(
        "👋 Привет!\n\n"
        "Добро пожаловать в IT Quiz Bot 🧠\n\n"
        "Здесь ты можешь проверять знания по программированию, "
        "Git, SQL, Web, API и другим IT-темам.\n\n"
        "Выбери действие:",
        reply_markup=main_menu()
    )


# =========================
# НАЧАЛО ТЕСТА
# =========================

@dp.callback_query(F.data == "start_quiz")
async def start_quiz(callback: CallbackQuery):
    questions = random.sample(
        QUESTIONS,
        min(3, len(QUESTIONS))
    )

    user_quizzes[callback.from_user.id] = {
        "questions": questions,
        "current": 0,
        "correct": 0,
    }

    await callback.answer()

    await send_question(callback.message, callback.from_user.id)


async def send_question(message: Message, user_id: int):
    quiz = user_quizzes[user_id]

    current = quiz["current"]
    questions = quiz["questions"]

    question = questions[current]

    buttons = []

    for i, answer in enumerate(question["answers"]):
        buttons.append([
            InlineKeyboardButton(
                text=answer,
                callback_data=f"answer:{i}"
            )
        ])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )

    await message.edit_text(
        f"🧠 Вопрос {current + 1}/{len(questions)}\n\n"
        f"{question['question']}",
        reply_markup=keyboard
    )


# =========================
# ОТВЕТ
# =========================

@dp.callback_query(F.data.startswith("answer:"))
async def answer_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in user_quizzes:
        await callback.answer(
            "Начни новый тест.",
            show_alert=True
        )
        return

    quiz = user_quizzes[user_id]

    selected = int(callback.data.split(":")[1])

    question = quiz["questions"][quiz["current"]]

    correct_answer = question["correct"]

    if selected == correct_answer:
        quiz["correct"] += 1
        update_statistics(user_id, True)

        text = (
            "✅ Правильно!\n\n"
            f"{question['explanation']}"
        )
    else:
        update_statistics(user_id, False)

        text = (
            "❌ Неправильно.\n\n"
            f"Правильный ответ: "
            f"{question['answers'][correct_answer]}\n\n"
            f"{question['explanation']}"
        )

    quiz["current"] += 1

    if quiz["current"] >= len(quiz["questions"]):

        total = len(quiz["questions"])
        correct = quiz["correct"]

        percent = round(correct / total * 100, 1)

        del user_quizzes[user_id]

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 Пройти ещё раз",
                        callback_data="start_quiz"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📊 Статистика",
                        callback_data="statistics"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🏠 Главное меню",
                        callback_data="menu"
                    )
                ],
            ]
        )

        await callback.message.edit_text(
            f"{text}\n\n"
            "🎉 Тест завершён!\n\n"
            f"✅ Правильных: {correct}\n"
            f"❌ Неправильных: {total - correct}\n"
            f"🎯 Точность: {percent}%",
            reply_markup=keyboard
        )

    else:

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="➡️ Следующий вопрос",
                        callback_data="next_question"
                    )
                ]
            ]
        )

        await callback.message.edit_text(
            text,
            reply_markup=keyboard
        )

    await callback.answer()


# =========================
# СЛЕДУЮЩИЙ ВОПРОС
# =========================

@dp.callback_query(F.data == "next_question")
async def next_question(callback: CallbackQuery):
    user_id = callback.from_user.id

    if user_id not in user_quizzes:
        await callback.answer(
            "Тест уже завершён.",
            show_alert=True
        )
        return

    await callback.answer()

    await send_question(
        callback.message,
        user_id
    )


# =========================
# СТАТИСТИКА
# =========================

@dp.callback_query(F.data == "statistics")
async def statistics_handler(callback: CallbackQuery):
    correct, wrong, total = get_statistics(
        callback.from_user.id
    )

    if total > 0:
        percent = round(correct / total * 100, 1)
    else:
        percent = 0

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧠 Начать тест",
                    callback_data="start_quiz"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="menu"
                )
            ],
        ]
    )

    await callback.message.edit_text(
        "📊 ТВОЯ СТАТИСТИКА\n\n"
        f"Всего вопросов: {total}\n\n"
        f"✅ Правильных: {correct}\n"
        f"❌ Неправильных: {wrong}\n\n"
        f"🎯 Точность: {percent}%",
        reply_markup=keyboard
    )

    await callback.answer()


# =========================
# ПОМОЩЬ
# =========================

@dp.callback_query(F.data == "help")
async def help_handler(callback: CallbackQuery):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="menu"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "ℹ️ ПОМОЩЬ\n\n"
        "🧠 Начать тест — пройти 3 IT-вопроса.\n\n"
        "📊 Статистика — посмотреть свой результат.\n\n"
        "Каждый вопрос имеет несколько вариантов ответа.\n"
        "После ответа бот покажет объяснение.",
        reply_markup=keyboard
    )

    await callback.answer()


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

@dp.callback_query(F.data == "menu")
async def menu_handler(callback: CallbackQuery):

    await callback.message.edit_text(
        "🏠 Главное меню\n\n"
        "Выбери действие:",
        reply_markup=main_menu()
    )

    await callback.answer()


# =========================
# ЗАПУСК
# =========================

async def main():
    init_db()

    logging.info("IT Quiz Bot запускается...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
