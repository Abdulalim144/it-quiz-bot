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
# SETTINGS
# =========================

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "TELEGRAM_BOT_TOKEN was not found. "
        "Create a .env file and add your bot token."
    )

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_NAME = "quiz.db"


# =========================
# DATABASE
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
# QUESTIONS
# =========================

QUESTIONS = [
    {
        "category": "Python",
        "question": "Which data type is used to store True or False in Python?",
        "answers": [
            "String",
            "Boolean",
            "List",
            "Integer"
        ],
        "correct": 1,
        "explanation": "In Python, True and False are Boolean values of type bool."
    },

    {
        "category": "Python",
        "question": "Which symbol is used for a comment in Python?",
        "answers": [
            "//",
            "/*",
            "#",
            "<!--"
        ],
        "correct": 2,
        "explanation": "A single-line comment in Python starts with the # symbol."
    },

    {
        "category": "JavaScript",
        "question": "How do you declare a variable whose value can be changed?",
        "answers": [
            "const",
            "let",
            "fixed",
            "static"
        ],
        "correct": 1,
        "explanation": "let is used to declare a variable whose value can be changed."
    },

    {
        "category": "JavaScript",
        "question": "Which operator is used for strict equality comparison?",
        "answers": [
            "=",
            "==",
            "===",
            "!="
        ],
        "correct": 2,
        "explanation": "The === operator compares both the value and the data type."
    },

    {
        "category": "SQL",
        "question": "How do you retrieve data from an SQL table?",
        "answers": [
            "GET",
            "SELECT",
            "TAKE",
            "READ"
        ],
        "correct": 1,
        "explanation": "The SELECT command is used to retrieve data from a table."
    },

    {
        "category": "SQL",
        "question": "Which command adds a new record to a table?",
        "answers": [
            "INSERT",
            "ADD",
            "CREATE",
            "PUSH"
        ],
        "correct": 0,
        "explanation": "INSERT INTO is used to add new records to a table."
    },

    {
        "category": "Git",
        "question": "Which command creates a new Git repository?",
        "answers": [
            "git start",
            "git init",
            "git create",
            "git new"
        ],
        "correct": 1,
        "explanation": "git init creates a new local Git repository."
    },

    {
        "category": "Git",
        "question": "Which command sends local changes to a remote repository?",
        "answers": [
            "git send",
            "git upload",
            "git push",
            "git transfer"
        ],
        "correct": 2,
        "explanation": "git push sends local commits to a remote repository."
    },

    {
        "category": "HTTP/API",
        "question": "What is an API?",
        "answers": [
            "A database",
            "An interface for communication between programs",
            "A programming language",
            "An operating system"
        ],
        "correct": 1,
        "explanation": "An API allows different programs to communicate with each other."
    },

    {
        "category": "Web",
        "question": "Which language is responsible for the structure of a web page?",
        "answers": [
            "HTML",
            "CSS",
            "SQL",
            "Python"
        ],
        "correct": 0,
        "explanation": "HTML defines the structure and content of a web page."
    },

    {
        "category": "Web",
        "question": "Which language is mainly used for styling a web page?",
        "answers": [
            "HTML",
            "CSS",
            "SQL",
            "Bash"
        ],
        "correct": 1,
        "explanation": "CSS is responsible for the appearance and styling of HTML elements."
    },

    {
        "category": "Docker",
        "question": "What is Docker?",
        "answers": [
            "A programming language",
            "A database management system",
            "A containerization platform",
            "A graphics editor"
        ],
        "correct": 2,
        "explanation": "Docker is used to create and run applications in containers."
    },

    {
        "category": "Linux",
        "question": "Which command shows the contents of the current directory in Linux?",
        "answers": [
            "cd",
            "ls",
            "show",
            "dirlist"
        ],
        "correct": 1,
        "explanation": "The ls command shows files and folders in the current directory."
    },

    {
        "category": "Databases",
        "question": "What is usually used to uniquely identify a record in a table?",
        "answers": [
            "Primary Key",
            "CSS",
            "API",
            "Cookie"
        ],
        "correct": 0,
        "explanation": "A Primary Key uniquely identifies records in a table."
    },

    {
        "category": "Algorithms",
        "question": "What is an algorithm?",
        "answers": [
            "A sequence of steps for solving a problem",
            "Only a programming language",
            "A type of computer",
            "A file"
        ],
        "correct": 0,
        "explanation": "An algorithm is a sequence of steps that leads to a solution to a problem."
    },
]


# =========================
# QUIZ STATE
# =========================

active_quizzes = {}


# =========================
# MAIN MENU
# =========================

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧠 Start Quiz",
                    callback_data="start_quiz"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Statistics",
                    callback_data="statistics"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Help",
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
        "👋 Hello!\n\n"
        "Welcome to IT Quiz Bot 🧠\n\n"
        "Test your IT knowledge, take quizzes "
        "and track your statistics.\n\n"
        "Choose an action:",
        reply_markup=main_menu()
    )


# =========================
# QUIZ COMMAND
# =========================

@dp.message(Command("quiz"))
async def quiz_command(message: Message):

    add_user(message.from_user)

    await start_quiz_process(
        message,
        message.from_user.id
    )


# =========================
# START QUIZ
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
# SHOW QUESTION
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
        f"🧠 Question {current + 1}/"
        f"{len(quiz['questions'])}\n\n"
        f"📚 Category: {question['category']}\n\n"
        f"{question['question']}"
    )

    await message.edit_text(
        text,
        reply_markup=keyboard
    )


# =========================
# CHECK ANSWER
# =========================

@dp.callback_query(F.data.startswith("answer:"))
async def answer_handler(callback: CallbackQuery):

    user_id = callback.from_user.id

    quiz = active_quizzes.get(user_id)

    if not quiz:
        await callback.answer(
            "This quiz has already been completed.",
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
            "✅ Correct!\n\n"
            f"{question['explanation']}"
        )

    else:

        update_answer(
            user_id,
            False
        )

        result_text = (
            "❌ Incorrect.\n\n"
            f"Correct answer: "
            f"{question['answers'][correct_answer]}\n\n"
            f"{question['explanation']}"
        )

    quiz["current"] += 1

    # Quiz finished
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
                        text="🔄 Another Quiz",
                        callback_data="start_quiz"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📊 Statistics",
                        callback_data="statistics"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🏠 Main Menu",
                        callback_data="menu"
                    )
                ]
            ]
        )

        await callback.message.edit_text(
            result_text
            + "\n\n"
            + "🎉 Quiz Completed!\n\n"
            + f"✅ Correct: {correct}\n"
            + f"❌ Incorrect: {wrong}\n"
            + f"🎯 Accuracy: {percent}%",
            reply_markup=keyboard
        )

    else:

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="➡️ Next Question",
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
# NEXT QUESTION
# =========================

@dp.callback_query(F.data == "next_question")
async def next_question(callback: CallbackQuery):

    user_id = callback.from_user.id

    if user_id not in active_quizzes:

        await callback.answer(
            "The quiz has already been completed.",
            show_alert=True
        )

        return

    await callback.answer()

    await send_question(
        callback.message,
        user_id
    )


# =========================
# STATISTICS
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
                    text="🧠 Start Quiz",
                    callback_data="start_quiz"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Main Menu",
                    callback_data="menu"
                )
            ]
        ]
    )

    await message.edit_text(
        "📊 YOUR STATISTICS\n\n"
        f"Total questions: {total}\n\n"
        f"✅ Correct: {correct}\n"
        f"❌ Incorrect: {wrong}\n\n"
        f"🎯 Accuracy: {percent}%\n\n"
        f"🏆 Quizzes completed: {tests}",
        reply_markup=keyboard
    )


# =========================
# HELP
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
                    text="🏠 Main Menu",
                    callback_data="menu"
                )
            ]
        ]
    )

    await message.edit_text(
        "ℹ️ HELP\n\n"
        "🧠 Start Quiz\n"
        "Take a quiz with 3 random questions.\n\n"
        "📊 Statistics\n"
        "View your results and accuracy.\n\n"
        "Each question has 4 answer options.\n"
        "After answering, the bot shows an explanation.",
        reply_markup=keyboard
    )


# =========================
# MAIN MENU
# =========================

@dp.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery):

    await callback.answer()

    await callback.message.edit_text(
        "🏠 Main Menu\n\n"
        "Choose an action:",
        reply_markup=main_menu()
    )


# =========================
# RUN BOT
# =========================

async def main():

    init_db()

    logging.info(
        "IT Quiz Bot is starting..."
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())