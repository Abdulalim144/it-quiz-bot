import asyncio
import logging
import os
import sqlite3
import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv


# =========================
# НАСТРОЙКИ
# =========================

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "Не найден TELEGRAM_BOT_TOKEN. "
        "Создай файл .env и добавь туда токен."
    )

logging.basicConfig(level=logging.INFO)

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
            total INTEGER DEFAULT 0,
            tests INTEGER DEFAULT 0
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


def update_answer(user_id, is_correct):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if is_correct:
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


def finish_test(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET tests = tests + 1
        WHERE telegram_id = ?
    """, (user_id,))

    conn.commit()
    conn.close()


def get_stats(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT correct, wrong, total, tests
        FROM users
        WHERE telegram_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    if result is None:
        return 0, 0, 0, 0

    return result


# =========================
# ВОПРОСЫ
# =========================

QUESTIONS = [
    {
        "category": "Python",
        "question": "Какой тип данных используется для хранения True или False в Python?",
        "answers": [
            "String",
            "Boolean",
            "List",
            "Integer"
        ],
        "correct": 1,
        "explanation": "В Python логические значения True и False имеют тип bool."
    },

    {
        "category": "Python",
        "question": "Какой символ используется для комментария в Python?",
        "answers": [
            "//",
            "/*",
            "#",
            "<!--"
        ],
        "correct": 2,
        "explanation": "Однострочный комментарий в Python начинается с символа #."
    },

    {
        "category": "JavaScript",
        "question": "Как объявить переменную, значение которой можно изменить?",
        "answers": [
            "const",
            "let",
            "fixed",
            "static"
        ],
        "correct": 1,
        "explanation": "let используется для объявления переменной, значение которой можно изменить."
    },

    {
        "category": "JavaScript",
        "question": "Какой оператор используется для строгого сравнения?",
        "answers": [
            "=",
            "==",
            "===",
            "!="
        ],
        "correct": 2,
        "explanation": "Оператор === сравнивает и значение, и тип данных."
    },

    {
        "category": "SQL",
        "question": "Как получить данные из таблицы SQL?",
        "answers": [
            "GET",
            "SELECT",
            "TAKE",
            "READ"
        ],
        "correct": 1,
        "explanation": "Команда SELECT используется для получения данных из таблицы."
    },

    {
        "category": "SQL",
        "question": "Какая команда добавляет новую запись в таблицу?",
        "answers": [
            "INSERT",
            "ADD",
            "CREATE",
            "PUSH"
        ],
        "correct": 0,
        "explanation": "INSERT INTO используется для добавления новых записей."
    },

    {
        "category": "Git",
        "question": "Какая команда создаёт новый Git-репозиторий?",
        "answers": [
            "git start",
            "git init",
            "git create",
            "git new"
        ],
        "correct": 1,
        "explanation": "git init создаёт новый локальный Git-репозиторий."
    },

    {
        "category": "Git",
        "question": "Какая команда отправляет локальные изменения на удалённый репозиторий?",
        "answers": [
            "git send",
            "git upload",
            "git push",
            "git transfer"
        ],
        "correct": 2,
        "explanation": "git push отправляет локальные commits в удалённый репозиторий."
    },

    {
        "category": "HTTP/API",
        "question": "Что такое API?",
        "answers": [
            "База данных",
            "Интерфейс взаимодействия программ",
            "Язык программирования",
            "Операционная система"
        ],
        "correct": 1,
        "explanation": "API позволяет различным программам взаимодействовать друг с другом."
    },

    {
        "category": "Web",
        "question": "Какой язык отвечает за структуру веб-страницы?",
        "answers": [
            "HTML",
            "CSS",
            "SQL",
            "Python"
        ],
        "correct": 0,
        "explanation": "HTML определяет структуру и содержимое веб-страницы."
    },

    {
        "category": "Web",
        "question": "Какой язык используется главным образом для стилизации веб-страницы?",
        "answers": [
            "HTML",
            "CSS",
            "SQL",
            "Bash"
        ],
        "correct": 1,
        "explanation": "CSS отвечает за внешний вид элементов HTML."
    },

    {
        "category": "Docker",
        "question": "Что такое Docker?",
        "answers": [
            "Язык программирования",
            "Система управления базами данных",
            "Платформа контейнеризации",
            "Графический редактор"
        ],
        "correct": 2,
        "explanation": "Docker используется для создания и запуска приложений в контейнерах."
    },

    {
        "category": "Linux",
        "question": "Какая команда показывает содержимое текущей директории в Linux?",
        "answers": [
            "cd",
            "ls",
            "show",
            "dirlist"
        ],
        "correct": 1,
        "explanation": "Команда ls показывает файлы и папки текущей директории."
    },

    {
        "category": "Базы данных",
        "question": "Что обычно используется для уникальной идентификации записи в таблице?",
        "answers": [
            "Primary Key",
            "CSS",
            "API",
            "Cookie"
        ],
        "correct": 0,
        "explanation": "Primary Key уникально идентифицирует записи таблицы."
    },

    {
        "category": "Алгоритмы",
        "question": "Что такое алгоритм?",
        "answers": [
            "Набор последовательных действий для решения задачи",
            "Только язык программирования",
            "Тип компьютера",
            "Файл"
        ],
        "correct": 0,
        "explanation": "Алгоритм — последовательность действий, которая приводит к решению задачи."
    },
]


# =========================
# СОСТОЯНИЕ ТЕСТОВ
# =========================

active_quizzes = {}


# =========================
# ГЛАВНОЕ МЕНЮ
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
            ]
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
        "Проверяй свои знания в IT, "
        "проходи тесты и следи за статистикой.\n\n"
        "Выбери действие:",
        reply_markup=main_menu()
    )


# =========================
# КОМАНДА QUIZ
# =========================

@dp.message(Command("quiz"))
async def quiz_command(message: Message):

    add_user(message.from_user)

    await start_quiz_process(
        message,
        message.from_user.id
    )


# =========================
# НАЧАЛО ТЕСТА
# =========================

async def start_quiz_process(message, user_id):

    questions = random.sample(
        QUESTIONS,
        min(3, len(QUESTIONS))
    )

    active_quizzes[user_id] = {
        "questions": questions,
        "current": 0,
        "correct": 0
    }

    await send_question(
        message,
        user_id
    )


@dp.callback_query(F.data == "start_quiz")
async def start_quiz_callback(callback: CallbackQuery):

    add_user(callback.from_user)

    await callback.answer()

    await start_quiz_process(
        callback.message,
        callback.from_user.id
    )


# =========================
# ПОКАЗ ВОПРОСА
# =========================

async def send_question(message, user_id):

    quiz = active_quizzes.get(user_id)

    if not quiz:
        return

    current = quiz["current"]

    question = quiz["questions"][current]

    buttons = []

    for index, answer in enumerate(question["answers"]):

        buttons.append([
            InlineKeyboardButton(
                text=answer,
                callback_data=f"answer:{index}"
            )
        ])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons
    )

    text = (
        f"🧠 Вопрос {current + 1}/"
        f"{len(quiz['questions'])}\n\n"
        f"📚 Категория: {question['category']}\n\n"
        f"{question['question']}"
    )

    await message.edit_text(
        text,
        reply_markup=keyboard
    )


# =========================
# ПРОВЕРКА ОТВЕТА
# =========================

@dp.callback_query(F.data.startswith("answer:"))
async def answer_handler(callback: CallbackQuery):

    user_id = callback.from_user.id

    quiz = active_quizzes.get(user_id)

    if not quiz:
        await callback.answer(
            "Этот тест уже завершён.",
            show_alert=True
        )
        return

    selected_answer = int(
        callback.data.split(":")[1]
    )

    question = quiz["questions"][
        quiz["current"]
    ]

    correct_answer = question["correct"]

    is_correct = (
        selected_answer == correct_answer
    )

    if is_correct:

        quiz["correct"] += 1

        update_answer(
            user_id,
            True
        )

        result_text = (
            "✅ Правильно!\n\n"
            f"{question['explanation']}"
        )

    else:

        update_answer(
            user_id,
            False
        )

        result_text = (
            "❌ Неправильно.\n\n"
            f"Правильный ответ: "
            f"{question['answers'][correct_answer]}\n\n"
            f"{question['explanation']}"
        )

    quiz["current"] += 1

    # Тест закончен
    if quiz["current"] >= len(quiz["questions"]):

        total_questions = len(
            quiz["questions"]
        )

        correct = quiz["correct"]

        wrong = (
            total_questions - correct
        )

        percent = round(
            correct / total_questions * 100,
            1
        )

        finish_test(user_id)

        del active_quizzes[user_id]

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 Ещё один тест",
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
                ]
            ]
        )

        await callback.message.edit_text(
            result_text
            + "\n\n"
            + "🎉 Тест завершён!\n\n"
            + f"✅ Правильных: {correct}\n"
            + f"❌ Неправильных: {wrong}\n"
            + f"🎯 Точность: {percent}%",
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
            result_text,
            reply_markup=keyboard
        )

    await callback.answer()


# =========================
# СЛЕДУЮЩИЙ ВОПРОС
# =========================

@dp.callback_query(F.data == "next_question")
async def next_question(callback: CallbackQuery):

    user_id = callback.from_user.id

    if user_id not in active_quizzes:

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

@dp.message(Command("stats"))
async def stats_command(message: Message):

    add_user(message.from_user)

    await show_statistics(
        message,
        message.from_user.id
    )


@dp.callback_query(F.data == "statistics")
async def statistics_callback(callback: CallbackQuery):

    await callback.answer()

    await show_statistics(
        callback.message,
        callback.from_user.id
    )


async def show_statistics(message, user_id):

    correct, wrong, total, tests = get_stats(
        user_id
    )

    if total > 0:
        percent = round(
            correct / total * 100,
            1
        )
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
            ]
        ]
    )

    await message.edit_text(
        "📊 ТВОЯ СТАТИСТИКА\n\n"
        f"Всего вопросов: {total}\n\n"
        f"✅ Правильных: {correct}\n"
        f"❌ Неправильных: {wrong}\n\n"
        f"🎯 Точность: {percent}%\n\n"
        f"🏆 Пройдено тестов: {tests}",
        reply_markup=keyboard
    )


# =========================
# ПОМОЩЬ
# =========================

@dp.message(Command("help"))
async def help_command(message: Message):

    await send_help(
        message
    )


@dp.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):

    await callback.answer()

    await send_help(
        callback.message
    )


async def send_help(message):

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

    await message.edit_text(
        "ℹ️ ПОМОЩЬ\n\n"
        "🧠 Начать тест\n"
        "Проходи тест из 3 случайных вопросов.\n\n"
        "📊 Статистика\n"
        "Смотри свои результаты и точность.\n\n"
        "Каждый вопрос имеет 4 варианта ответа.\n"
        "После ответа бот показывает объяснение.",
        reply_markup=keyboard
    )


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

@dp.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery):

    await callback.answer()

    await callback.message.edit_text(
        "🏠 Главное меню\n\n"
        "Выбери действие:",
        reply_markup=main_menu()
    )


# =========================
# ЗАПУСК
# =========================

async def main():

    init_db()

    logging.info(
        "IT Quiz Bot запускается..."
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
