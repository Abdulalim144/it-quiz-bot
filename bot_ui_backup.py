import asyncio
import os
import random
import sqlite3

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN was not found. "
        "Create a .env file and add your bot token."
    )

bot = Bot(token=TOKEN)
dp = Dispatcher()

DB_NAME = "quiz.db"

# ============================================================
# QUESTIONS
# ============================================================

QUESTIONS = [
    {
        "category": "Python",
        "difficulty": "easy",
        "question": "Which keyword is used to define a function in Python?",
        "options": ["func", "def", "function", "define"],
        "correct": 1,
        "explanation": "The 'def' keyword is used to define a function in Python.",
    },
    {
        "category": "Python",
        "difficulty": "medium",
        "question": "What is the output of: print(len([1, 2, 3, 4]))?",
        "options": ["3", "4", "5", "Error"],
        "correct": 1,
        "explanation": "The list contains four elements, so len() returns 4.",
    },
    {
        "category": "Python",
        "difficulty": "hard",
        "question": "Which Python data structure stores key-value pairs?",
        "options": ["List", "Tuple", "Dictionary", "Set"],
        "correct": 2,
        "explanation": "A dictionary stores data as key-value pairs.",
    },
    {
        "category": "JavaScript",
        "difficulty": "easy",
        "question": "Which keyword declares a variable that can be reassigned in JavaScript?",
        "options": ["const", "let", "fixed", "varonly"],
        "correct": 1,
        "explanation": "The 'let' keyword declares a block-scoped variable that can be reassigned.",
    },
    {
        "category": "JavaScript",
        "difficulty": "medium",
        "question": "Which method converts a JSON string into a JavaScript object?",
        "options": [
            "JSON.parse()",
            "JSON.stringify()",
            "JSON.convert()",
            "JSON.object()",
        ],
        "correct": 0,
        "explanation": "JSON.parse() converts a JSON string into a JavaScript value or object.",
    },
    {
        "category": "JavaScript",
        "difficulty": "hard",
        "question": "What does the === operator check in JavaScript?",
        "options": [
            "Value only",
            "Type only",
            "Value and type",
            "Object size",
        ],
        "correct": 2,
        "explanation": "The strict equality operator === checks both value and data type.",
    },
    {
        "category": "SQL",
        "difficulty": "easy",
        "question": "Which SQL command is used to retrieve data from a table?",
        "options": ["GET", "SELECT", "FETCH", "READ"],
        "correct": 1,
        "explanation": "SELECT is used to retrieve data from database tables.",
    },
    {
        "category": "SQL",
        "difficulty": "medium",
        "question": "Which clause is used to filter rows in SQL?",
        "options": ["ORDER BY", "GROUP BY", "WHERE", "FILTER"],
        "correct": 2,
        "explanation": "The WHERE clause filters rows based on a condition.",
    },
    {
        "category": "SQL",
        "difficulty": "hard",
        "question": "Which SQL operation combines rows from two or more tables?",
        "options": ["JOIN", "MERGE", "CONNECT", "LINK"],
        "correct": 0,
        "explanation": "JOIN combines related rows from multiple tables.",
    },
    {
        "category": "Git",
        "difficulty": "easy",
        "question": "Which command shows the current Git repository status?",
        "options": [
            "git check",
            "git status",
            "git show-status",
            "git current",
        ],
        "correct": 1,
        "explanation": "git status shows modified, staged, and untracked files.",
    },
    {
        "category": "Git",
        "difficulty": "medium",
        "question": "Which command creates a new Git commit?",
        "options": [
            "git save",
            "git push",
            "git commit",
            "git create",
        ],
        "correct": 2,
        "explanation": "git commit creates a new commit from staged changes.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "easy",
        "question": "Which HTTP status code means 'Not Found'?",
        "options": ["200", "301", "404", "500"],
        "correct": 2,
        "explanation": "HTTP 404 means that the requested resource was not found.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "medium",
        "question": "Which HTTP method is commonly used to create a new resource?",
        "options": ["GET", "POST", "DELETE", "HEAD"],
        "correct": 1,
        "explanation": "POST is commonly used to submit data and create a new resource.",
    },
    {
        "category": "Web",
        "difficulty": "easy",
        "question": "What does HTML stand for?",
        "options": [
            "HyperText Markup Language",
            "HighText Machine Language",
            "Hyper Transfer Markup Language",
            "Home Tool Markup Language",
        ],
        "correct": 0,
        "explanation": "HTML stands for HyperText Markup Language.",
    },
    {
        "category": "Web",
        "difficulty": "medium",
        "question": "Which technology is mainly used to style web pages?",
        "options": ["HTML", "CSS", "SQL", "Python"],
        "correct": 1,
        "explanation": "CSS is used to control the visual presentation and layout of web pages.",
    },
    {
        "category": "Docker",
        "difficulty": "easy",
        "question": "What is Docker mainly used for?",
        "options": [
            "Creating documents",
            "Containerizing applications",
            "Editing images",
            "Managing databases only",
        ],
        "correct": 1,
        "explanation": "Docker is mainly used to package and run applications in containers.",
    },
    {
        "category": "Docker",
        "difficulty": "medium",
        "question": "Which command lists running Docker containers?",
        "options": [
            "docker list",
            "docker ps",
            "docker running",
            "docker containers",
        ],
        "correct": 1,
        "explanation": "docker ps lists currently running containers.",
    },
    {
        "category": "Linux",
        "difficulty": "easy",
        "question": "Which command lists files in a Linux directory?",
        "options": ["dir", "ls", "show", "files"],
        "correct": 1,
        "explanation": "The ls command lists files and directories.",
    },
    {
        "category": "Linux",
        "difficulty": "medium",
        "question": "Which command changes the current directory in Linux?",
        "options": ["move", "cd", "change", "dir"],
        "correct": 1,
        "explanation": "The cd command changes the current working directory.",
    },
    {
        "category": "Databases",
        "difficulty": "easy",
        "question": "What is a database?",
        "options": [
            "A programming language",
            "A collection of organized data",
            "A web browser",
            "An operating system",
        ],
        "correct": 1,
        "explanation": "A database is an organized collection of data that can be stored and accessed.",
    },
    {
        "category": "Databases",
        "difficulty": "hard",
        "question": "What is a primary key used for?",
        "options": [
            "Encrypting a database",
            "Uniquely identifying a row",
            "Deleting a table",
            "Creating backups",
        ],
        "correct": 1,
        "explanation": "A primary key uniquely identifies each row in a table.",
    },
    {
        "category": "Algorithms",
        "difficulty": "easy",
        "question": "What does an algorithm describe?",
        "options": [
            "A sequence of steps to solve a problem",
            "A database table",
            "A programming language",
            "A computer monitor",
        ],
        "correct": 0,
        "explanation": "An algorithm is a defined sequence of steps used to solve a problem.",
    },
    {
        "category": "Algorithms",
        "difficulty": "medium",
        "question": "What is the average time complexity of binary search?",
        "options": ["O(n)", "O(log n)", "O(n²)", "O(1)"],
        "correct": 1,
        "explanation": "Binary search repeatedly divides the search space in half, giving O(log n) complexity.",
    },
]

# ============================================================
# DATABASE
# ============================================================


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            correct INTEGER DEFAULT 0,
            wrong INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0,
            tests INTEGER DEFAULT 0
        )
        """
    )

    conn.commit()
    conn.close()


def register_user(user):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (telegram_id, username, first_name)
        VALUES (?, ?, ?)
        """,
        (
            user.id,
            user.username,
            user.first_name,
        ),
    )

    cursor.execute(
        """
        UPDATE users
        SET username = ?, first_name = ?
        WHERE telegram_id = ?
        """,
        (
            user.username,
            user.first_name,
            user.id,
        ),
    )

    conn.commit()
    conn.close()


def update_user_stats(user_id, correct, wrong):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET correct = correct + ?,
            wrong = wrong + ?,
            total = total + ?,
            tests = tests + 1
        WHERE telegram_id = ?
        """,
        (
            correct,
            wrong,
            correct + wrong,
            user_id,
        ),
    )

    conn.commit()
    conn.close()


def get_user_stats(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT correct, wrong, total, tests
        FROM users
        WHERE telegram_id = ?
        """,
        (user_id,),
    )

    result = cursor.fetchone()
    conn.close()

    return result


# ============================================================
# KEYBOARDS
# ============================================================


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧠 Start Quiz",
                    callback_data="start_quiz",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 My Statistics",
                    callback_data="stats",
                ),
                InlineKeyboardButton(
                    text="ℹ️ Help",
                    callback_data="help",
                ),
            ],
        ]
    )


def category_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🐍 Python",
                    callback_data="category:Python",
                ),
                InlineKeyboardButton(
                    text="💻 JavaScript",
                    callback_data="category:JavaScript",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗄 SQL",
                    callback_data="category:SQL",
                ),
                InlineKeyboardButton(
                    text="🔧 Git",
                    callback_data="category:Git",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🌐 HTTP / API",
                    callback_data="category:HTTP / API",
                ),
                InlineKeyboardButton(
                    text="🌍 Web",
                    callback_data="category:Web",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🐳 Docker",
                    callback_data="category:Docker",
                ),
                InlineKeyboardButton(
                    text="🐧 Linux",
                    callback_data="category:Linux",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🗃 Databases",
                    callback_data="category:Databases",
                ),
                InlineKeyboardButton(
                    text="⚙️ Algorithms",
                    callback_data="category:Algorithms",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎲 Random Category",
                    callback_data="category:random",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Back",
                    callback_data="back_main",
                )
            ],
        ]
    )


def difficulty_menu(category):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🟢 Easy",
                    callback_data=f"difficulty:{category}:easy",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🟡 Medium",
                    callback_data=f"difficulty:{category}:medium",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔴 Hard",
                    callback_data=f"difficulty:{category}:hard",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎲 Any Difficulty",
                    callback_data=f"difficulty:{category}:any",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Back",
                    callback_data="start_quiz",
                )
            ],
        ]
    )


def answer_menu(question_index):
    question = QUESTIONS[question_index]

    buttons = []

    for i, option in enumerate(question["options"]):
        buttons.append(
            [
                InlineKeyboardButton(
                    text=option,
                    callback_data=f"answer:{i}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def result_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧠 New Quiz",
                    callback_data="start_quiz",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 My Statistics",
                    callback_data="stats",
                ),
                InlineKeyboardButton(
                    text="🏠 Main Menu",
                    callback_data="back_main",
                ),
            ],
        ]
    )


# ============================================================
# USER QUIZ STATE
# ============================================================

active_quizzes = {}


# ============================================================
# START / MAIN MENU
# ============================================================


async def show_main_menu(message: Message):
    register_user(message.from_user)

    await message.answer(
        "👋 <b>Welcome to IT Quiz Bot!</b>\n\n"
        "Test your IT knowledge with questions about "
        "Python, JavaScript, SQL, Git, Web, Docker, Linux, "
        "Databases and Algorithms.\n\n"
        "Choose an option below:",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )


@dp.message(Command("start"))
async def start_command(message: Message):
    await show_main_menu(message)


# ============================================================
# QUIZ START
# ============================================================


async def start_quiz_process(
    user_id,
    target,
    edit=False,
):
    text = (
        "🧠 <b>Choose a category</b>\n\n"
        "Select the topic you want to practice:"
    )

    if edit:
        await target.edit_text(
            text,
            reply_markup=category_menu(),
            parse_mode="HTML",
        )
    else:
        await target.answer(
            text,
            reply_markup=category_menu(),
            parse_mode="HTML",
        )


@dp.message(Command("quiz"))
async def quiz_command(message: Message):
    register_user(message.from_user)

    await start_quiz_process(
        message.from_user.id,
        message,
        edit=False,
    )


@dp.callback_query(F.data == "start_quiz")
async def start_quiz_callback(callback: CallbackQuery):
    await callback.answer()

    await start_quiz_process(
        callback.from_user.id,
        callback.message,
        edit=True,
    )


# ============================================================
# CATEGORY
# ============================================================


@dp.callback_query(F.data.startswith("category:"))
async def category_selected(callback: CallbackQuery):
    await callback.answer()

    category = callback.data.split(":", 1)[1]

    await callback.message.edit_text(
        f"🧠 <b>Category:</b> {category}\n\n"
        "Choose the difficulty level:",
        reply_markup=difficulty_menu(category),
        parse_mode="HTML",
    )


# ============================================================
# DIFFICULTY
# ============================================================


@dp.callback_query(F.data.startswith("difficulty:"))
async def difficulty_selected(callback: CallbackQuery):
    await callback.answer()

    _, category, difficulty = callback.data.split(":", 2)

    available = QUESTIONS.copy()

    if category != "random":
        available = [
            q for q in available
            if q["category"] == category
        ]

    if difficulty != "any":
        available = [
            q for q in available
            if q["difficulty"] == difficulty
        ]

    if not available:
        await callback.message.edit_text(
            "❌ No questions are available for this selection.",
            reply_markup=category_menu(),
        )
        return

    random.shuffle(available)

    selected_questions = available[: min(3, len(available))]

    active_quizzes[callback.from_user.id] = {
        "questions": selected_questions,
        "current": 0,
        "score": 0,
        "answered": 0,
    }

    await send_question(
        callback.message,
        callback.from_user.id,
        edit=True,
    )


# ============================================================
# SEND QUESTION
# ============================================================


async def send_question(
    target,
    user_id,
    edit=True,
):
    quiz = active_quizzes.get(user_id)

    if not quiz:
        return

    current = quiz["current"]
    questions = quiz["questions"]

    if current >= len(questions):
        await finish_quiz(
            target,
            user_id,
            edit=edit,
        )
        return

    question = questions[current]

    text = (
        f"🧠 <b>Question {current + 1}/{len(questions)}</b>\n\n"
        f"<b>{question['question']}</b>\n\n"
        "Choose the correct answer:"
    )

    keyboard = answer_menu(
        QUESTIONS.index(question)
    )

    if edit:
        await target.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    else:
        await target.answer(
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )


# ============================================================
# ANSWER
# ============================================================


@dp.callback_query(F.data.startswith("answer:"))
async def answer_selected(callback: CallbackQuery):
    user_id = callback.from_user.id

    quiz = active_quizzes.get(user_id)

    if not quiz:
        await callback.answer(
            "This quiz is no longer active.",
            show_alert=True,
        )
        return

    answer_index = int(
        callback.data.split(":", 1)[1]
    )

    current = quiz["current"]
    question = quiz["questions"][current]

    correct_index = question["correct"]

    if answer_index == correct_index:
        quiz["score"] += 1
        result = "✅ <b>Correct!</b>"
    else:
        result = (
            "❌ <b>Incorrect.</b>\n"
            f"Correct answer: "
            f"<b>{question['options'][correct_index]}</b>"
        )

    explanation = question["explanation"]

    quiz["answered"] += 1
    quiz["current"] += 1

    await callback.answer()

    await callback.message.edit_text(
        f"{result}\n\n"
        f"💡 <b>Explanation:</b>\n{explanation}",
        parse_mode="HTML",
    )

    await asyncio.sleep(1.5)

    await send_question(
        callback.message,
        user_id,
        edit=True,
    )


# ============================================================
# FINISH QUIZ
# ============================================================


async def finish_quiz(
    target,
    user_id,
    edit=True,
):
    quiz = active_quizzes.get(user_id)

    if not quiz:
        return

    score = quiz["score"]
    total = len(quiz["questions"])
    wrong = total - score

    update_user_stats(
        user_id,
        score,
        wrong,
    )

    percentage = round(
        (score / total) * 100
    ) if total else 0

    if percentage == 100:
        emoji = "🏆"
        message = "Perfect score!"
    elif percentage >= 67:
        emoji = "🎉"
        message = "Great job!"
    elif percentage >= 34:
        emoji = "👍"
        message = "Good effort!"
    else:
        emoji = "📚"
        message = "Keep practicing!"

    text = (
        f"{emoji} <b>Quiz Completed!</b>\n\n"
        f"📊 Score: <b>{score}/{total}</b>\n"
        f"📈 Accuracy: <b>{percentage}%</b>\n\n"
        f"{message}\n\n"
        "Try another quiz to improve your score!"
    )

    del active_quizzes[user_id]

    if edit:
        await target.edit_text(
            text,
            reply_markup=result_menu(),
            parse_mode="HTML",
        )
    else:
        await target.answer(
            text,
            reply_markup=result_menu(),
            parse_mode="HTML",
        )


# ============================================================
# STATISTICS
# ============================================================


async def show_stats(
    target,
    user_id,
    edit=False,
):
    stats = get_user_stats(user_id)

    if not stats:
        text = (
            "📊 <b>My Statistics</b>\n\n"
            "No statistics yet.\n"
            "Complete your first quiz!"
        )
    else:
        correct, wrong, total, tests = stats

        accuracy = (
            round((correct / total) * 100)
            if total
            else 0
        )

        text = (
            "📊 <b>My Statistics</b>\n\n"
            f"🧠 Quizzes completed: <b>{tests}</b>\n"
            f"📝 Questions answered: <b>{total}</b>\n"
            f"✅ Correct answers: <b>{correct}</b>\n"
            f"❌ Wrong answers: <b>{wrong}</b>\n"
            f"📈 Accuracy: <b>{accuracy}%</b>"
        )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧠 Start Quiz",
                    callback_data="start_quiz",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Main Menu",
                    callback_data="back_main",
                )
            ],
        ]
    )

    if edit:
        await target.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    else:
        await target.answer(
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )


@dp.message(Command("stats"))
async def stats_command(message: Message):
    register_user(message.from_user)

    await show_stats(
        message,
        message.from_user.id,
        edit=False,
    )


@dp.callback_query(F.data == "stats")
async def stats_callback(callback: CallbackQuery):
    await callback.answer()

    await show_stats(
        callback.message,
        callback.from_user.id,
        edit=True,
    )


# ============================================================
# HELP
# ============================================================


async def show_help(
    target,
    edit=False,
):
    text = (
        "ℹ️ <b>How to use IT Quiz Bot</b>\n\n"
        "1️⃣ Press <b>Start Quiz</b>.\n"
        "2️⃣ Choose a category.\n"
        "3️⃣ Choose a difficulty level.\n"
        "4️⃣ Answer the questions.\n"
        "5️⃣ Check your final score.\n\n"
        "<b>Commands:</b>\n"
        "/start — Open the main menu\n"
        "/quiz — Start a new quiz\n"
        "/stats — View your statistics\n"
        "/help — Show this help message\n\n"
        "Your statistics are saved separately for your "
        "Telegram account."
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 Main Menu",
                    callback_data="back_main",
                )
            ]
        ]
    )

    if edit:
        await target.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    else:
        await target.answer(
            text,
            reply_markup=keyboard,
            parse_mode="HTML",
        )


@dp.message(Command("help"))
async def help_command(message: Message):
    await show_help(
        message,
        edit=False,
    )


@dp.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    await callback.answer()

    await show_help(
        callback.message,
        edit=True,
    )


# ============================================================
# BACK TO MAIN MENU
# ============================================================


@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.answer()

    await callback.message.edit_text(
        "👋 <b>IT Quiz Bot</b>\n\n"
        "Choose an option below:",
        reply_markup=main_menu(),
        parse_mode="HTML",
    )


# ============================================================
# START BOT
# ============================================================


async def main():
    init_db()

    print("====================================")
    print("IT Quiz Bot is starting...")
    print("Bot is running.")
    print("Press Ctrl+C to stop the bot.")
    print("====================================")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())