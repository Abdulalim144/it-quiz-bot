import asyncio
import logging
import os
import random
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from dotenv import load_dotenv


# ============================================================
# CONFIG
# ============================================================

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


# ============================================================
# CATEGORIES
# ============================================================

CATEGORY_NAMES = [
    "Python",
    "JavaScript",
    "HTML / CSS",
    "SQL",
    "Git",
    "Docker",
    "Linux",
    "HTTP / API",
    "Databases",
    "Algorithms",
]


DIFFICULTY_NAMES = {
    "easy": "🟢 EASY",
    "normal": "🟡 NORMAL",
    "hard": "🔴 HARD",
    "mixed": "🎲 MIXED",
}


# ============================================================
# QUESTIONS
# 10 categories
# 5 EASY + 5 NORMAL + 5 HARD
# TOTAL = 150 QUESTIONS
# ============================================================

QUESTIONS = [

    # ========================================================
    # PYTHON - EASY
    # ========================================================

    {
        "category": "Python",
        "difficulty": "easy",
        "question": "Which keyword defines a function in Python?",
        "answers": ["def", "func", "function", "define"],
        "correct": 0,
        "explanation": "Python uses def to define a function.",
    },
    {
        "category": "Python",
        "difficulty": "easy",
        "question": "Which symbol starts a Python comment?",
        "answers": ["#", "//", "--", "/*"],
        "correct": 0,
        "explanation": "Python comments begin with #.",
    },
    {
        "category": "Python",
        "difficulty": "easy",
        "question": "Which type stores True or False?",
        "answers": ["bool", "str", "list", "float"],
        "correct": 0,
        "explanation": "bool represents Boolean values.",
    },
    {
        "category": "Python",
        "difficulty": "easy",
        "question": "Which collection is ordered and mutable?",
        "answers": ["list", "tuple", "set", "frozenset"],
        "correct": 0,
        "explanation": "Lists are ordered and mutable.",
    },
    {
        "category": "Python",
        "difficulty": "easy",
        "question": "What does len() return?",
        "answers": [
            "The number of items",
            "The last item",
            "The data type",
            "A Boolean",
        ],
        "correct": 0,
        "explanation": "len() returns the number of items in a sequence or collection.",
    },

    # PYTHON - NORMAL

    {
        "category": "Python",
        "difficulty": "normal",
        "question": "What is the result of 7 // 2?",
        "answers": ["3", "3.5", "4", "2"],
        "correct": 0,
        "explanation": "// performs floor division.",
    },
    {
        "category": "Python",
        "difficulty": "normal",
        "question": "Which keyword handles an exception?",
        "answers": ["except", "catch", "error", "handle"],
        "correct": 0,
        "explanation": "Python uses except in try/except blocks.",
    },
    {
        "category": "Python",
        "difficulty": "normal",
        "question": "What does enumerate() provide?",
        "answers": [
            "Indexes and values",
            "Only indexes",
            "Only values",
            "Sorted values",
        ],
        "correct": 0,
        "explanation": "enumerate() yields index-value pairs.",
    },
    {
        "category": "Python",
        "difficulty": "normal",
        "question": "Which syntax creates a dictionary?",
        "answers": [
            "{'a': 1}",
            "('a'=1)",
            "['a':1]",
            "<'a':1>",
        ],
        "correct": 0,
        "explanation": "Dictionaries use key:value pairs inside braces.",
    },
    {
        "category": "Python",
        "difficulty": "normal",
        "question": "What does *args collect?",
        "answers": [
            "Positional arguments",
            "Keyword arguments",
            "Return values",
            "Exceptions",
        ],
        "correct": 0,
        "explanation": "*args collects extra positional arguments.",
    },

    # PYTHON - HARD

    {
        "category": "Python",
        "difficulty": "hard",
        "question": "What is a Python decorator used for?",
        "answers": [
            "Modifying or extending callable behavior",
            "Deleting classes",
            "Creating databases",
            "Compiling Python",
        ],
        "correct": 0,
        "explanation": "Decorators wrap functions or classes to modify behavior.",
    },
    {
        "category": "Python",
        "difficulty": "hard",
        "question": "What does a generator yield?",
        "answers": [
            "Values lazily over time",
            "All values immediately",
            "Only strings",
            "Only errors",
        ],
        "correct": 0,
        "explanation": "Generators produce values lazily, commonly with yield.",
    },
    {
        "category": "Python",
        "difficulty": "hard",
        "question": "Which method initializes an instance?",
        "answers": [
            "__init__",
            "__start__",
            "__new__",
            "__create__",
        ],
        "correct": 0,
        "explanation": "__init__ initializes an instance after object creation.",
    },
    {
        "category": "Python",
        "difficulty": "hard",
        "question": "What is a shallow copy?",
        "answers": [
            "A new outer object whose nested references may be shared",
            "A copy of only immutable objects",
            "No copy at all",
            "A serialized copy",
        ],
        "correct": 0,
        "explanation": "A shallow copy copies the outer container but can share nested objects.",
    },
    {
        "category": "Python",
        "difficulty": "hard",
        "question": "What does the GIL primarily affect in CPython?",
        "answers": [
            "Execution of Python bytecode by multiple threads",
            "Disk speed",
            "SQL queries",
            "Network routing",
        ],
        "correct": 0,
        "explanation": "The GIL affects simultaneous execution of Python bytecode by threads in CPython.",
    },


    # ========================================================
    # JAVASCRIPT
    # ========================================================

    {
        "category": "JavaScript",
        "difficulty": "easy",
        "question": "Which keyword declares a reassignable block-scoped variable?",
        "answers": ["let", "var", "const", "static"],
        "correct": 0,
        "explanation": "let declares a reassignable block-scoped variable.",
    },
    {
        "category": "JavaScript",
        "difficulty": "easy",
        "question": "Which keyword declares a constant binding?",
        "answers": ["const", "let", "var", "fixed"],
        "correct": 0,
        "explanation": "const creates a binding that cannot be reassigned.",
    },
    {
        "category": "JavaScript",
        "difficulty": "easy",
        "question": "Which method prints to the browser console?",
        "answers": [
            "console.log()",
            "print()",
            "echo()",
            "debug()",
        ],
        "correct": 0,
        "explanation": "console.log() writes to the console.",
    },
    {
        "category": "JavaScript",
        "difficulty": "easy",
        "question": "Which value commonly represents intentional absence?",
        "answers": ["null", "undefined", "empty", "NaN"],
        "correct": 0,
        "explanation": "null commonly represents an intentional absence of value.",
    },
    {
        "category": "JavaScript",
        "difficulty": "easy",
        "question": "Which operator checks strict equality?",
        "answers": ["===", "==", "=", "!="],
        "correct": 0,
        "explanation": "=== compares value and type without coercion.",
    },

    {
        "category": "JavaScript",
        "difficulty": "normal",
        "question": "What does Array.map() return?",
        "answers": [
            "A new transformed array",
            "A number",
            "A string",
            "Nothing",
        ],
        "correct": 0,
        "explanation": "map() creates a new array from callback results.",
    },
    {
        "category": "JavaScript",
        "difficulty": "normal",
        "question": "What does JSON.parse() do?",
        "answers": [
            "Converts JSON text to a JavaScript value",
            "Creates JSON text",
            "Encrypts JSON",
            "Validates HTML",
        ],
        "correct": 0,
        "explanation": "JSON.parse converts JSON text into a JavaScript value.",
    },
    {
        "category": "JavaScript",
        "difficulty": "normal",
        "question": "What is a Promise used for?",
        "answers": [
            "Representing an eventual asynchronous result",
            "Styling pages",
            "Declaring classes",
            "Sorting arrays",
        ],
        "correct": 0,
        "explanation": "Promises represent pending, fulfilled, or rejected asynchronous operations.",
    },
    {
        "category": "JavaScript",
        "difficulty": "normal",
        "question": "What does async make a function return?",
        "answers": [
            "A Promise",
            "A number",
            "A callback",
            "A generator only",
        ],
        "correct": 0,
        "explanation": "An async function returns a Promise.",
    },
    {
        "category": "JavaScript",
        "difficulty": "normal",
        "question": "What is a closure?",
        "answers": [
            "A function retaining access to its lexical scope",
            "A closed browser tab",
            "A syntax error",
            "A module",
        ],
        "correct": 0,
        "explanation": "A closure keeps access to variables from its lexical environment.",
    },

    {
        "category": "JavaScript",
        "difficulty": "hard",
        "question": "What is the event loop responsible for?",
        "answers": [
            "Coordinating asynchronous callbacks and tasks",
            "Compiling CSS",
            "Creating SQL tables",
            "Encrypting passwords",
        ],
        "correct": 0,
        "explanation": "The event loop coordinates JavaScript execution with asynchronous tasks.",
    },
    {
        "category": "JavaScript",
        "difficulty": "hard",
        "question": "What is hoisting?",
        "answers": [
            "Processing declarations before execution of their scope",
            "Moving HTML elements",
            "Compressing JavaScript",
            "Running code on a server",
        ],
        "correct": 0,
        "explanation": "Hoisting describes how declarations are processed before execution.",
    },
    {
        "category": "JavaScript",
        "difficulty": "hard",
        "question": "What does the spread syntax ... do with an iterable?",
        "answers": [
            "Expands its elements",
            "Encrypts it",
            "Sorts it",
            "Deletes it",
        ],
        "correct": 0,
        "explanation": "Spread syntax expands iterable elements into another context.",
    },
    {
        "category": "JavaScript",
        "difficulty": "hard",
        "question": "What is event delegation?",
        "answers": [
            "Handling events through a common ancestor",
            "Sending events to another server",
            "Creating custom CSS",
            "Blocking all events",
        ],
        "correct": 0,
        "explanation": "Event delegation uses event bubbling and a shared ancestor handler.",
    },
    {
        "category": "JavaScript",
        "difficulty": "hard",
        "question": "What does Promise.all() do?",
        "answers": [
            "Waits for all promises to fulfill or one to reject",
            "Runs only the first promise",
            "Converts promises to strings",
            "Cancels every promise",
        ],
        "correct": 0,
        "explanation": "Promise.all resolves when all promises fulfill and rejects when one rejects.",
    },


    # ========================================================
    # HTML / CSS
    # ========================================================

    {
        "category": "HTML / CSS",
        "difficulty": "easy",
        "question": "What does HTML stand for?",
        "answers": [
            "HyperText Markup Language",
            "HighText Machine Language",
            "HyperTool Multi Language",
            "HomeText Markup Language",
        ],
        "correct": 0,
        "explanation": "HTML stands for HyperText Markup Language.",
    },
    {
        "category": "HTML / CSS",
        "difficulty": "easy",
        "question": "Which HTML tag creates a hyperlink?",
        "answers": ["<a>", "<link>", "<href>", "<url>"],
        "correct": 0,
        "explanation": "The <a> element creates hyperlinks.",
    },
    {
        "category": "HTML / CSS",
        "difficulty": "easy",
        "question": "Which CSS property changes text color?",
        "answers": ["color", "font-color", "text-color", "foreground"],
        "correct": 0,
        "explanation": "The CSS color property controls text color.",
    },
    {
        "category": "HTML / CSS",
        "difficulty": "easy",
        "question": "Which HTML element represents the largest heading?",
        "answers": ["<h1>", "<h6>", "<head>", "<title>"],
        "correct": 0,
        "explanation": "<h1> is the highest-level heading.",
    },
    {
        "category": "HTML / CSS",
        "difficulty": "easy",
        "question": "Which CSS property controls the space inside an element?",
        "answers": ["padding", "margin", "spacing", "inside-space"],
        "correct": 0,
        "explanation": "padding controls the space inside the border.",
    },

    {
        "category": "HTML / CSS",
        "difficulty": "normal",
        "question": "What does CSS stand for?",
        "answers": [
            "Cascading Style Sheets",
            "Computer Style Syntax",
            "Creative Styling System",
            "Coded Style Sheets",
        ],
        "correct": 0,
        "explanation": "CSS stands for Cascading Style Sheets.",
    },
    {
        "category": "HTML / CSS",
        "difficulty": "normal",
        "question": "Which CSS layout system is designed for one-dimensional layouts?",
        "answers": ["Flexbox", "Grid", "Float", "Table"],
        "correct": 0,
        "explanation": "Flexbox is primarily designed for one-dimensional layouts.",
    },
    {
        "category": "HTML / CSS",
        "difficulty": "normal",
        "question": "Which CSS property changes the font size?",
        "answers": ["font-size", "text-size", "size", "font-height"],
        "correct": 0,
        "explanation": "font-size controls the size of text.",
    },
    {
        "category": "HTML / CSS",
        "difficulty": "normal",
        "question": "What does the alt attribute provide for an image?",
        "answers": [
            "Alternative text",
            "Image animation",
            "Image color",
            "Image size",
        ],
        "correct": 0,
        "explanation": "alt provides alternative text for accessibility and when images cannot load.",
    },
    {
        "category": "HTML / CSS",
        "difficulty": "normal",
        "question": "Which CSS selector targets an element by ID?",
        "answers": ["#id", ".id", "id:", "*id"],
        "correct": 0,
        "explanation": "The # selector targets an element by ID.",
    },

    {
        "category": "HTML / CSS",
        "difficulty": "hard",
        "question": "What is CSS specificity used for?",
        "answers": [
            "Determining which conflicting CSS rule wins",
            "Making pages load faster",
            "Compressing HTML",
            "Creating JavaScript objects",
        ],
        "correct": 0,
        "explanation": "Specificity determines which selector wins when CSS declarations conflict.",
    },
    {
        "category": "HTML / CSS",
        "difficulty": "hard",
        "question": "What does position: absolute position relative to?",
        "answers": [
            "The nearest positioned ancestor",
            "Always the viewport",
            "Always the body",
            "The nearest sibling",
        ],
        "correct": 0,
        "explanation": "An absolutely positioned element is positioned relative to its nearest positioned ancestor.",
    },
    {
        "category": "HTML / CSS",
        "difficulty": "hard",
        "question": "What is the CSS box model made of?",
        "answers": [
            "Content, padding, border, margin",
            "Text, image, link, button",
            "Header, body, footer, nav",
            "Grid, flex, block, inline",
        ],
        "correct": 0,
        "explanation": "The box model consists of content, padding, border, and margin.",
    },
    {
        "category": "HTML / CSS",
        "difficulty": "hard",
        "question": "What does display: grid provide?",
        "answers": [
            "A two-dimensional layout system",
            "Only text formatting",
            "Only animations",
            "Database access",
        ],
        "correct": 0,
        "explanation": "CSS Grid is designed for two-dimensional layouts.",
    },
    {
        "category": "HTML / CSS",
        "difficulty": "hard",
        "question": "What does the CSS cascade determine?",
        "answers": [
            "Which declarations apply when rules conflict",
            "How HTML is parsed",
            "How JavaScript executes",
            "How DNS works",
        ],
        "correct": 0,
        "explanation": "The cascade determines which CSS declarations are applied.",
    },


    # ========================================================
    # SQL
    # ========================================================

    {
        "category": "SQL",
        "difficulty": "easy",
        "question": "Which SQL command retrieves data?",
        "answers": ["SELECT", "GET", "FETCH", "READ"],
        "correct": 0,
        "explanation": "SELECT retrieves data from database tables or views.",
    },
    {
        "category": "SQL",
        "difficulty": "easy",
        "question": "Which SQL command adds a new row?",
        "answers": ["INSERT", "ADD", "CREATE", "APPEND"],
        "correct": 0,
        "explanation": "INSERT adds rows to a table.",
    },
    {
        "category": "SQL",
        "difficulty": "easy",
        "question": "Which SQL command modifies existing rows?",
        "answers": ["UPDATE", "CHANGE", "MODIFY", "ALTER"],
        "correct": 0,
        "explanation": "UPDATE modifies existing rows.",
    },
    {
        "category": "SQL",
        "difficulty": "easy",
        "question": "Which SQL command removes rows?",
        "answers": ["DELETE", "REMOVE", "DROP", "CLEAR"],
        "correct": 0,
        "explanation": "DELETE removes rows from a table.",
    },
    {
        "category": "SQL",
        "difficulty": "easy",
        "question": "Which clause filters rows?",
        "answers": ["WHERE", "FILTER", "HAVING", "LIMIT"],
        "correct": 0,
        "explanation": "WHERE filters rows before grouping.",
    },

    {
        "category": "SQL",
        "difficulty": "normal",
        "question": "Which clause sorts query results?",
        "answers": ["ORDER BY", "SORT BY", "GROUP BY", "ARRANGE BY"],
        "correct": 0,
        "explanation": "ORDER BY sorts query results.",
    },
    {
        "category": "SQL",
        "difficulty": "normal",
        "question": "Which clause groups rows for aggregation?",
        "answers": ["GROUP BY", "ORDER BY", "COLLECT BY", "MERGE BY"],
        "correct": 0,
        "explanation": "GROUP BY groups rows for aggregate calculations.",
    },
    {
        "category": "SQL",
        "difficulty": "normal",
        "question": "Which function counts rows?",
        "answers": ["COUNT()", "TOTAL()", "ROWS()", "NUMBER()"],
        "correct": 0,
        "explanation": "COUNT() returns the number of rows or non-null values depending on its argument.",
    },
    {
        "category": "SQL",
        "difficulty": "normal",
        "question": "Which JOIN returns matching rows from both tables?",
        "answers": ["INNER JOIN", "LEFT JOIN", "FULL JOIN", "CROSS JOIN"],
        "correct": 0,
        "explanation": "INNER JOIN returns rows where the join condition matches in both tables.",
    },
    {
        "category": "SQL",
        "difficulty": "normal",
        "question": "What does DISTINCT do?",
        "answers": [
            "Removes duplicate result rows",
            "Sorts rows",
            "Deletes table duplicates",
            "Creates an index",
        ],
        "correct": 0,
        "explanation": "DISTINCT removes duplicate rows from the result.",
    },

    {
        "category": "SQL",
        "difficulty": "hard",
        "question": "What is a SQL transaction?",
        "answers": [
            "A logical unit of database work",
            "A database column",
            "A table index",
            "A query comment",
        ],
        "correct": 0,
        "explanation": "A transaction groups database operations into a logical unit of work.",
    },
    {
        "category": "SQL",
        "difficulty": "hard",
        "question": "What does ACID stand for?",
        "answers": [
            "Atomicity, Consistency, Isolation, Durability",
            "Access, Control, Index, Data",
            "Atomic, Cache, Input, Delete",
            "Async, Consistent, Internal, Distributed",
        ],
        "correct": 0,
        "explanation": "ACID describes four important transaction properties.",
    },
    {
        "category": "SQL",
        "difficulty": "hard",
        "question": "What is a database index mainly used for?",
        "answers": [
            "Improving lookup performance",
            "Encrypting data",
            "Backing up tables",
            "Deleting duplicates",
        ],
        "correct": 0,
        "explanation": "Indexes can speed up data retrieval at the cost of storage and write overhead.",
    },
    {
        "category": "SQL",
        "difficulty": "hard",
        "question": "What is a foreign key?",
        "answers": [
            "A column referencing a key in another table",
            "An encrypted password",
            "A temporary table",
            "A database backup",
        ],
        "correct": 0,
        "explanation": "A foreign key represents a relationship to a key in another table.",
    },
    {
        "category": "SQL",
        "difficulty": "hard",
        "question": "What is normalization designed to reduce?",
        "answers": [
            "Data redundancy and update anomalies",
            "Network latency",
            "CPU temperature",
            "File size only",
        ],
        "correct": 0,
        "explanation": "Normalization structures data to reduce unnecessary redundancy and anomalies.",
    },


    # ========================================================
    # GIT
    # ========================================================

    {
        "category": "Git",
        "difficulty": "easy",
        "question": "Which command initializes a Git repository?",
        "answers": ["git init", "git start", "git create", "git new"],
        "correct": 0,
        "explanation": "git init creates a new Git repository.",
    },
    {
        "category": "Git",
        "difficulty": "easy",
        "question": "Which command shows the current repository status?",
        "answers": ["git status", "git check", "git state", "git info"],
        "correct": 0,
        "explanation": "git status shows modified, staged, and untracked files.",
    },
    {
        "category": "Git",
        "difficulty": "easy",
        "question": "Which command creates a commit?",
        "answers": ["git commit", "git save", "git snapshot", "git push"],
        "correct": 0,
        "explanation": "git commit records staged changes in repository history.",
    },
    {
        "category": "Git",
        "difficulty": "easy",
        "question": "Which command downloads remote changes?",
        "answers": ["git pull", "git download", "git receive", "git update"],
        "correct": 0,
        "explanation": "git pull fetches and integrates changes from a remote repository.",
    },
    {
        "category": "Git",
        "difficulty": "easy",
        "question": "Which command sends commits to a remote repository?",
        "answers": ["git push", "git send", "git upload", "git publish"],
        "correct": 0,
        "explanation": "git push sends local commits to a remote repository.",
    },

    {
        "category": "Git",
        "difficulty": "normal",
        "question": "What does git clone do?",
        "answers": [
            "Copies a remote repository locally",
            "Creates a commit",
            "Deletes a branch",
            "Merges two files",
        ],
        "correct": 0,
        "explanation": "git clone creates a local copy of a repository.",
    },
    {
        "category": "Git",
        "difficulty": "normal",
        "question": "What does git add do?",
        "answers": [
            "Stages changes",
            "Uploads changes",
            "Creates a branch",
            "Deletes changes",
        ],
        "correct": 0,
        "explanation": "git add places changes into the staging area.",
    },
    {
        "category": "Git",
        "difficulty": "normal",
        "question": "Which command creates a new branch?",
        "answers": [
            "git branch name",
            "git new name",
            "git create name",
            "git make name",
        ],
        "correct": 0,
        "explanation": "git branch name creates a new branch.",
    },
    {
        "category": "Git",
        "difficulty": "normal",
        "question": "What is a merge conflict?",
        "answers": [
            "Git cannot automatically reconcile competing changes",
            "A missing repository",
            "A deleted commit",
            "A broken remote server",
        ],
        "correct": 0,
        "explanation": "A conflict occurs when Git cannot automatically combine changes.",
    },
    {
        "category": "Git",
        "difficulty": "normal",
        "question": "What does git log show?",
        "answers": [
            "Commit history",
            "Remote servers only",
            "File permissions",
            "Current CPU usage",
        ],
        "correct": 0,
        "explanation": "git log displays commit history.",
    },

    {
        "category": "Git",
        "difficulty": "hard",
        "question": "What is git rebase primarily used for?",
        "answers": [
            "Replaying commits onto another base",
            "Deleting the repository",
            "Uploading binary files",
            "Creating database tables",
        ],
        "correct": 0,
        "explanation": "Rebase reapplies commits onto a new base commit.",
    },
    {
        "category": "Git",
        "difficulty": "hard",
        "question": "What does git reset --soft preserve?",
        "answers": [
            "Working tree and index changes while moving HEAD",
            "Nothing",
            "Only remote files",
            "Only untracked files",
        ],
        "correct": 0,
        "explanation": "--soft moves HEAD while leaving changes staged.",
    },
    {
        "category": "Git",
        "difficulty": "hard",
        "question": "What is a Git tag commonly used for?",
        "answers": [
            "Marking important commits such as releases",
            "Encrypting commits",
            "Creating passwords",
            "Deleting branches",
        ],
        "correct": 0,
        "explanation": "Tags commonly identify important points such as release versions.",
    },
    {
        "category": "Git",
        "difficulty": "hard",
        "question": "What does git cherry-pick do?",
        "answers": [
            "Applies a specific commit to the current branch",
            "Deletes one commit",
            "Renames a repository",
            "Creates a remote",
        ],
        "correct": 0,
        "explanation": "cherry-pick applies the changes from a specific commit.",
    },
    {
        "category": "Git",
        "difficulty": "hard",
        "question": "What is HEAD in Git?",
        "answers": [
            "A reference to the currently checked-out commit or branch",
            "The remote repository",
            "The first commit only",
            "A configuration file",
        ],
        "correct": 0,
        "explanation": "HEAD identifies the current position in the repository history.",
    },


    # ========================================================
    # DOCKER
    # ========================================================

    {
        "category": "Docker",
        "difficulty": "easy",
        "question": "What is Docker primarily used for?",
        "answers": [
            "Running applications in containers",
            "Editing images",
            "Managing spreadsheets",
            "Writing HTML only",
        ],
        "correct": 0,
        "explanation": "Docker packages and runs applications using containers.",
    },
    {
        "category": "Docker",
        "difficulty": "easy",
        "question": "Which command lists running containers?",
        "answers": [
            "docker ps",
            "docker list",
            "docker running",
            "docker containers",
        ],
        "correct": 0,
        "explanation": "docker ps lists running containers by default.",
    },
    {
        "category": "Docker",
        "difficulty": "easy",
        "question": "What is a Docker image?",
        "answers": [
            "A template used to create containers",
            "A running process only",
            "A network cable",
            "A database row",
        ],
        "correct": 0,
        "explanation": "Images contain the filesystem and metadata used to create containers.",
    },
    {
        "category": "Docker",
        "difficulty": "easy",
        "question": "Which file commonly defines Docker image build instructions?",
        "answers": ["Dockerfile", "docker.txt", "container.yml", "image.conf"],
        "correct": 0,
        "explanation": "A Dockerfile contains instructions for building an image.",
    },
    {
        "category": "Docker",
        "difficulty": "easy",
        "question": "Which command builds an image?",
        "answers": [
            "docker build",
            "docker make",
            "docker create-image",
            "docker compile",
        ],
        "correct": 0,
        "explanation": "docker build builds an image from a Dockerfile and build context.",
    },

    {
        "category": "Docker",
        "difficulty": "normal",
        "question": "What is a Docker container?",
        "answers": [
            "A running or stopped instance of an image",
            "A source code editor",
            "A Git branch",
            "A SQL table",
        ],
        "correct": 0,
        "explanation": "A container is an instance created from a Docker image.",
    },
    {
        "category": "Docker",
        "difficulty": "normal",
        "question": "What does docker run do?",
        "answers": [
            "Creates and starts a container",
            "Only builds an image",
            "Deletes all containers",
            "Starts Docker Desktop only",
        ],
        "correct": 0,
        "explanation": "docker run creates a container from an image and starts it.",
    },
    {
        "category": "Docker",
        "difficulty": "normal",
        "question": "What is a Docker volume used for?",
        "answers": [
            "Persistent data storage",
            "CPU acceleration",
            "Image compression",
            "Port scanning",
        ],
        "correct": 0,
        "explanation": "Volumes provide persistent storage independent of container lifecycle.",
    },
    {
        "category": "Docker",
        "difficulty": "normal",
        "question": "What does EXPOSE in a Dockerfile document?",
        "answers": [
            "A port the application is intended to use",
            "A secret password",
            "A database schema",
            "A CPU limit",
        ],
        "correct": 0,
        "explanation": "EXPOSE documents the intended network port used by the container.",
    },
    {
        "category": "Docker",
        "difficulty": "normal",
        "question": "What does docker exec allow you to do?",
        "answers": [
            "Run a command inside a running container",
            "Build an image",
            "Delete Docker",
            "Create a Git commit",
        ],
        "correct": 0,
        "explanation": "docker exec runs a command in an already running container.",
    },

    {
        "category": "Docker",
        "difficulty": "hard",
        "question": "What is a multi-stage Docker build useful for?",
        "answers": [
            "Creating smaller production images",
            "Running multiple databases automatically",
            "Replacing Git",
            "Encrypting all files",
        ],
        "correct": 0,
        "explanation": "Multi-stage builds allow build dependencies to be excluded from the final image.",
    },
    {
        "category": "Docker",
        "difficulty": "hard",
        "question": "What is the purpose of Docker Compose?",
        "answers": [
            "Defining and running multi-container applications",
            "Replacing the Linux kernel",
            "Compiling Python",
            "Managing Git history",
        ],
        "correct": 0,
        "explanation": "Docker Compose defines and manages multiple related containers.",
    },
    {
        "category": "Docker",
        "difficulty": "hard",
        "question": "What is a container namespace mainly used for?",
        "answers": [
            "Isolating process and system resources",
            "Encrypting images",
            "Storing passwords",
            "Compressing logs",
        ],
        "correct": 0,
        "explanation": "Linux namespaces provide isolation of processes and system resources.",
    },
    {
        "category": "Docker",
        "difficulty": "hard",
        "question": "What is a Docker layer?",
        "answers": [
            "A filesystem change stored as part of an image",
            "A network connection",
            "A running process",
            "A database index",
        ],
        "correct": 0,
        "explanation": "Docker images are built from filesystem layers representing changes.",
    },
    {
        "category": "Docker",
        "difficulty": "hard",
        "question": "Why should containers usually be treated as ephemeral?",
        "answers": [
            "Their writable state can disappear when replaced",
            "They cannot use networks",
            "They cannot run processes",
            "They are always encrypted",
        ],
        "correct": 0,
        "explanation": "Container writable state is not a reliable place for persistent application data.",
    },


    # ========================================================
    # LINUX
    # ========================================================

    {
        "category": "Linux",
        "difficulty": "easy",
        "question": "Which command lists files?",
        "answers": ["ls", "list", "dirfiles", "show"],
        "correct": 0,
        "explanation": "ls lists directory contents.",
    },
    {
        "category": "Linux",
        "difficulty": "easy",
        "question": "Which command changes the current directory?",
        "answers": ["cd", "change", "move", "dir"],
        "correct": 0,
        "explanation": "cd changes the current working directory.",
    },
    {
        "category": "Linux",
        "difficulty": "easy",
        "question": "Which command prints the current directory?",
        "answers": ["pwd", "where", "cwd", "path"],
        "correct": 0,
        "explanation": "pwd prints the current working directory.",
    },
    {
        "category": "Linux",
        "difficulty": "easy",
        "question": "Which command creates a directory?",
        "answers": ["mkdir", "makedir", "newdir", "createdir"],
        "correct": 0,
        "explanation": "mkdir creates directories.",
    },
    {
        "category": "Linux",
        "difficulty": "easy",
        "question": "Which command removes a file?",
        "answers": ["rm", "del", "remove", "erase"],
        "correct": 0,
        "explanation": "rm removes files and, with appropriate options, directories.",
    },

    {
        "category": "Linux",
        "difficulty": "normal",
        "question": "What does chmod change?",
        "answers": [
            "File permissions",
            "File contents",
            "IP addresses",
            "Processes",
        ],
        "correct": 0,
        "explanation": "chmod changes file and directory permission bits.",
    },
    {
        "category": "Linux",
        "difficulty": "normal",
        "question": "Which command shows running processes?",
        "answers": ["ps", "proc", "process", "jobsall"],
        "correct": 0,
        "explanation": "ps displays information about running processes.",
    },
    {
        "category": "Linux",
        "difficulty": "normal",
        "question": "What does grep do?",
        "answers": [
            "Searches text using patterns",
            "Deletes files",
            "Creates users",
            "Changes permissions",
        ],
        "correct": 0,
        "explanation": "grep searches input for lines matching a pattern.",
    },
    {
        "category": "Linux",
        "difficulty": "normal",
        "question": "Which command displays the first lines of a file?",
        "answers": ["head", "first", "top", "begin"],
        "correct": 0,
        "explanation": "head displays the beginning of files.",
    },
    {
        "category": "Linux",
        "difficulty": "normal",
        "question": "Which command displays the last lines of a file?",
        "answers": ["tail", "last", "bottom", "end"],
        "correct": 0,
        "explanation": "tail displays the end of files.",
    },

    {
        "category": "Linux",
        "difficulty": "hard",
        "question": "What does a Linux pipe | do?",
        "answers": [
            "Connects output of one command to input of another",
            "Runs a command as root",
            "Deletes output",
            "Encrypts input",
        ],
        "correct": 0,
        "explanation": "A pipe sends standard output from one command to standard input of another.",
    },
    {
        "category": "Linux",
        "difficulty": "hard",
        "question": "What is a symbolic link?",
        "answers": [
            "A filesystem entry pointing to another path",
            "A compressed file",
            "A process",
            "A user account",
        ],
        "correct": 0,
        "explanation": "A symbolic link references another filesystem path.",
    },
    {
        "category": "Linux",
        "difficulty": "hard",
        "question": "What is a daemon?",
        "answers": [
            "A background service process",
            "A shell alias",
            "A filesystem",
            "A network cable",
        ],
        "correct": 0,
        "explanation": "A daemon is a background process that provides a service.",
    },
    {
        "category": "Linux",
        "difficulty": "hard",
        "question": "What does sudo normally do?",
        "answers": [
            "Runs a command with elevated privileges",
            "Deletes the shell",
            "Changes the kernel",
            "Starts a container",
        ],
        "correct": 0,
        "explanation": "sudo allows authorized users to execute commands with elevated privileges.",
    },
    {
        "category": "Linux",
        "difficulty": "hard",
        "question": "What is a file descriptor?",
        "answers": [
            "A numeric handle for an open file or I/O resource",
            "A filename extension",
            "A user password",
            "A kernel module",
        ],
        "correct": 0,
        "explanation": "File descriptors are numeric handles used by processes for open files and I/O resources.",
    },


    # ========================================================
    # HTTP / API
    # ========================================================

    {
        "category": "HTTP / API",
        "difficulty": "easy",
        "question": "What does HTTP stand for?",
        "answers": [
            "HyperText Transfer Protocol",
            "High Transfer Text Process",
            "Hyperlink Transfer Program",
            "Host Transfer Protocol",
        ],
        "correct": 0,
        "explanation": "HTTP stands for HyperText Transfer Protocol.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "easy",
        "question": "Which HTTP method is commonly used to retrieve data?",
        "answers": ["GET", "POST", "DELETE", "PATCH"],
        "correct": 0,
        "explanation": "GET is commonly used to retrieve a resource.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "easy",
        "question": "Which status code means Not Found?",
        "answers": ["404", "200", "500", "301"],
        "correct": 0,
        "explanation": "HTTP 404 means the requested resource was not found.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "easy",
        "question": "Which status code means OK?",
        "answers": ["200", "201", "400", "500"],
        "correct": 0,
        "explanation": "HTTP 200 indicates a successful request.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "easy",
        "question": "What is JSON commonly used for?",
        "answers": [
            "Exchanging structured data",
            "Styling websites",
            "Compiling programs",
            "Managing CPUs",
        ],
        "correct": 0,
        "explanation": "JSON is widely used for structured data exchange.",
    },

    {
        "category": "HTTP / API",
        "difficulty": "normal",
        "question": "Which HTTP method is commonly used to create a resource?",
        "answers": ["POST", "GET", "HEAD", "OPTIONS"],
        "correct": 0,
        "explanation": "POST is commonly used to submit data and create resources.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "normal",
        "question": "What does HTTP 401 mean?",
        "answers": [
            "Unauthorized",
            "Forbidden",
            "Not Found",
            "Server Error",
        ],
        "correct": 0,
        "explanation": "401 indicates that authentication is required or has failed.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "normal",
        "question": "What does HTTP 403 mean?",
        "answers": [
            "Forbidden",
            "Unauthorized",
            "Not Found",
            "Bad Gateway",
        ],
        "correct": 0,
        "explanation": "403 means the server understood the request but refuses to authorize it.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "normal",
        "question": "What is an API endpoint?",
        "answers": [
            "A network-accessible location for an API operation",
            "A database password",
            "A CSS selector",
            "A Git commit",
        ],
        "correct": 0,
        "explanation": "An endpoint is a specific URL or network location through which an API can be accessed.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "normal",
        "question": "What does HTTPS add to HTTP?",
        "answers": [
            "TLS encryption and authentication",
            "A database",
            "A programming language",
            "A file system",
        ],
        "correct": 0,
        "explanation": "HTTPS uses TLS to protect HTTP communication.",
    },

    {
        "category": "HTTP / API",
        "difficulty": "hard",
        "question": "What does idempotent mean for an HTTP method?",
        "answers": [
            "Repeating the same request has the same intended effect",
            "The request is always encrypted",
            "The request is always cached",
            "The request never fails",
        ],
        "correct": 0,
        "explanation": "An idempotent operation has the same intended server-side effect when repeated.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "hard",
        "question": "What is the purpose of an HTTP ETag?",
        "answers": [
            "Identifying a specific representation for caching validation",
            "Encrypting passwords",
            "Creating DNS records",
            "Opening sockets",
        ],
        "correct": 0,
        "explanation": "ETag values help clients and servers validate cached representations.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "hard",
        "question": "What does HTTP 429 indicate?",
        "answers": [
            "Too Many Requests",
            "Bad Request",
            "Unauthorized",
            "Conflict",
        ],
        "correct": 0,
        "explanation": "429 indicates that the client has sent too many requests in a given period.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "hard",
        "question": "What is content negotiation?",
        "answers": [
            "Selecting a representation format acceptable to client and server",
            "Encrypting HTTP headers",
            "Creating API keys",
            "Choosing a DNS server",
        ],
        "correct": 0,
        "explanation": "Content negotiation lets client and server agree on an appropriate representation.",
    },
    {
        "category": "HTTP / API",
        "difficulty": "hard",
        "question": "What is CORS designed to control?",
        "answers": [
            "Cross-origin browser requests",
            "Database replication",
            "CPU scheduling",
            "Docker networking",
        ],
        "correct": 0,
        "explanation": "CORS controls whether browser-based cross-origin requests are allowed.",
    },


    # ========================================================
    # DATABASES
    # ========================================================

    {
        "category": "Databases",
        "difficulty": "easy",
        "question": "What is a database table?",
        "answers": [
            "A structured collection of rows and columns",
            "A network protocol",
            "A Python package",
            "A Git branch",
        ],
        "correct": 0,
        "explanation": "Relational tables organize data into rows and columns.",
    },
    {
        "category": "Databases",
        "difficulty": "easy",
        "question": "What is a primary key?",
        "answers": [
            "A column or set of columns that uniquely identifies rows",
            "A password",
            "A database server",
            "A backup file",
        ],
        "correct": 0,
        "explanation": "A primary key uniquely identifies each row in a table.",
    },
    {
        "category": "Databases",
        "difficulty": "easy",
        "question": "What is a row?",
        "answers": [
            "A single record in a table",
            "A database connection",
            "An index only",
            "A query",
        ],
        "correct": 0,
        "explanation": "A row represents one record in a relational table.",
    },
    {
        "category": "Databases",
        "difficulty": "easy",
        "question": "What is a column?",
        "answers": [
            "A field representing an attribute of records",
            "A complete database",
            "A transaction",
            "A server",
        ],
        "correct": 0,
        "explanation": "A column represents one attribute or field of the records.",
    },
    {
        "category": "Databases",
        "difficulty": "easy",
        "question": "What does CRUD stand for?",
        "answers": [
            "Create, Read, Update, Delete",
            "Copy, Run, Upload, Download",
            "Create, Remove, Undo, Deploy",
            "Connect, Read, Use, Drop",
        ],
        "correct": 0,
        "explanation": "CRUD describes the basic operations on stored data.",
    },

    {
        "category": "Databases",
        "difficulty": "normal",
        "question": "What is a foreign key used for?",
        "answers": [
            "Representing a relationship between tables",
            "Encrypting rows",
            "Sorting columns",
            "Backing up data",
        ],
        "correct": 0,
        "explanation": "Foreign keys represent relationships between tables.",
    },
    {
        "category": "Databases",
        "difficulty": "normal",
        "question": "What is an index?",
        "answers": [
            "A structure that can speed up data retrieval",
            "A table backup",
            "A password",
            "A query result",
        ],
        "correct": 0,
        "explanation": "Indexes can improve lookup performance.",
    },
    {
        "category": "Databases",
        "difficulty": "normal",
        "question": "What is a relational database?",
        "answers": [
            "A database organized around related tables",
            "A database with no structure",
            "A text file only",
            "A Git repository",
        ],
        "correct": 0,
        "explanation": "Relational databases organize information into related tables.",
    },
    {
        "category": "Databases",
        "difficulty": "normal",
        "question": "What is a database schema?",
        "answers": [
            "The structure defining database objects and relationships",
            "A database password",
            "A backup archive",
            "A network address",
        ],
        "correct": 0,
        "explanation": "A schema describes the structure of database objects and their relationships.",
    },
    {
        "category": "Databases",
        "difficulty": "normal",
        "question": "What is a transaction?",
        "answers": [
            "A group of operations treated as one logical unit",
            "A single database column",
            "A table name",
            "A server process",
        ],
        "correct": 0,
        "explanation": "Transactions group operations into a logical unit of work.",
    },

    {
        "category": "Databases",
        "difficulty": "hard",
        "question": "What is database normalization?",
        "answers": [
            "Structuring data to reduce redundancy and anomalies",
            "Encrypting every row",
            "Deleting all indexes",
            "Increasing duplicate data",
        ],
        "correct": 0,
        "explanation": "Normalization reduces redundancy and update anomalies.",
    },
    {
        "category": "Databases",
        "difficulty": "hard",
        "question": "What is a database deadlock?",
        "answers": [
            "Transactions waiting for resources held by each other",
            "A missing table",
            "A failed login",
            "A deleted database",
        ],
        "correct": 0,
        "explanation": "A deadlock occurs when transactions wait on each other's locked resources.",
    },
    {
        "category": "Databases",
        "difficulty": "hard",
        "question": "What is replication?",
        "answers": [
            "Maintaining copies of data on multiple database servers",
            "Deleting duplicate rows",
            "Compressing tables",
            "Creating indexes",
        ],
        "correct": 0,
        "explanation": "Replication maintains copies of data across multiple servers or nodes.",
    },
    {
        "category": "Databases",
        "difficulty": "hard",
        "question": "What is sharding?",
        "answers": [
            "Splitting data across multiple database nodes",
            "Encrypting a table",
            "Sorting rows",
            "Creating backups",
        ],
        "correct": 0,
        "explanation": "Sharding distributes portions of data across multiple nodes.",
    },
    {
        "category": "Databases",
        "difficulty": "hard",
        "question": "What is an isolation level?",
        "answers": [
            "A rule describing how transaction changes interact",
            "A password policy",
            "A backup format",
            "A network protocol",
        ],
        "correct": 0,
        "explanation": "Isolation levels define the visibility and interaction of concurrent transaction changes.",
    },


    # ========================================================
    # ALGORITHMS
    # ========================================================

    {
        "category": "Algorithms",
        "difficulty": "easy",
        "question": "What is an algorithm?",
        "answers": [
            "A step-by-step procedure for solving a problem",
            "A programming language",
            "A database",
            "A computer monitor",
        ],
        "correct": 0,
        "explanation": "An algorithm is a defined procedure for solving a problem.",
    },
    {
        "category": "Algorithms",
        "difficulty": "easy",
        "question": "Which structure follows FIFO?",
        "answers": ["Queue", "Stack", "Tree", "Graph"],
        "correct": 0,
        "explanation": "A queue follows First In, First Out.",
    },
    {
        "category": "Algorithms",
        "difficulty": "easy",
        "question": "Which structure follows LIFO?",
        "answers": ["Stack", "Queue", "Tree", "Heap"],
        "correct": 0,
        "explanation": "A stack follows Last In, First Out.",
    },
    {
        "category": "Algorithms",
        "difficulty": "easy",
        "question": "What does sorting mean?",
        "answers": [
            "Arranging elements according to an order",
            "Deleting elements",
            "Duplicating elements",
            "Encrypting elements",
        ],
        "correct": 0,
        "explanation": "Sorting arranges elements according to a chosen ordering.",
    },
    {
        "category": "Algorithms",
        "difficulty": "easy",
        "question": "What does searching mean?",
        "answers": [
            "Finding an element or value in a collection",
            "Deleting a collection",
            "Encrypting a collection",
            "Sorting only",
        ],
        "correct": 0,
        "explanation": "Searching finds a target element or value.",
    },

    {
        "category": "Algorithms",
        "difficulty": "normal",
        "question": "What is the average time complexity of binary search on a sorted array?",
        "answers": ["O(log n)", "O(n)", "O(n²)", "O(1)"],
        "correct": 0,
        "explanation": "Binary search halves the search space on each step.",
    },
    {
        "category": "Algorithms",
        "difficulty": "normal",
        "question": "What is the typical time complexity of linear search?",
        "answers": ["O(n)", "O(log n)", "O(1)", "O(n log n)"],
        "correct": 0,
        "explanation": "Linear search may inspect every element.",
    },
    {
        "category": "Algorithms",
        "difficulty": "normal",
        "question": "Which algorithm is commonly used to find shortest paths with non-negative edge weights?",
        "answers": [
            "Dijkstra's algorithm",
            "Binary search",
            "Bubble sort",
            "DFS only",
        ],
        "correct": 0,
        "explanation": "Dijkstra's algorithm finds shortest paths when edge weights are non-negative.",
    },
    {
        "category": "Algorithms",
        "difficulty": "normal",
        "question": "What is recursion?",
        "answers": [
            "A function calling itself",
            "Sorting data",
            "Encrypting data",
            "Creating a database",
        ],
        "correct": 0,
        "explanation": "Recursion occurs when a function calls itself directly or indirectly.",
    },
    {
        "category": "Algorithms",
        "difficulty": "normal",
        "question": "What is Big O notation used for?",
        "answers": [
            "Describing algorithm growth as input size increases",
            "Measuring screen resolution",
            "Counting programming languages",
            "Encrypting data",
        ],
        "correct": 0,
        "explanation": "Big O describes how resource usage grows with input size.",
    },

    {
        "category": "Algorithms",
        "difficulty": "hard",
        "question": "What is dynamic programming?",
        "answers": [
            "Solving overlapping subproblems while storing their results",
            "Writing code dynamically",
            "Running programs without memory",
            "Sorting only",
        ],
        "correct": 0,
        "explanation": "Dynamic programming stores solutions to subproblems to avoid repeated work.",
    },
    {
        "category": "Algorithms",
        "difficulty": "hard",
        "question": "What is the average-case complexity of quicksort?",
        "answers": ["O(n log n)", "O(n²)", "O(log n)", "O(1)"],
        "correct": 0,
        "explanation": "Quicksort has average-case O(n log n) complexity.",
    },
    {
        "category": "Algorithms",
        "difficulty": "hard",
        "question": "What is breadth-first search commonly used for?",
        "answers": [
            "Exploring a graph level by level",
            "Sorting numbers only",
            "Encrypting files",
            "Compressing images",
        ],
        "correct": 0,
        "explanation": "BFS explores nodes level by level and is useful for shortest paths in unweighted graphs.",
    },
    {
        "category": "Algorithms",
        "difficulty": "hard",
        "question": "What is depth-first search?",
        "answers": [
            "A graph traversal that explores deeply before backtracking",
            "A sorting algorithm",
            "A database query",
            "A compression method",
        ],
        "correct": 0,
        "explanation": "DFS explores a path deeply before backtracking.",
    },
    {
        "category": "Algorithms",
        "difficulty": "hard",
        "question": "What is a hash table generally optimized for?",
        "answers": [
            "Fast average-case key lookup",
            "Sorted traversal",
            "Sequential disk access",
            "Image rendering",
        ],
        "correct": 0,
        "explanation": "Hash tables provide fast average-case lookup by key.",
    },
]


# ============================================================
# USER QUIZ STATE
# ============================================================

active_quizzes = {}


# ============================================================
# DATABASE
# ============================================================

def get_db():
    return sqlite3.connect(DB_NAME)


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                correct INTEGER DEFAULT 0,
                wrong INTEGER DEFAULT 0,
                total INTEGER DEFAULT 0,
                tests INTEGER DEFAULT 0,
                xp INTEGER DEFAULT 0
            )
            """
        )
        # Add XP to existing databases without deleting saved statistics.
        columns = {
            row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()
        }
        if "xp" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0")
        conn.commit()


def level_for_xp(xp):
    thresholds = [0, 100, 250, 450, 700, 1000, 1400, 1900, 2500, 3200]
    level = 1
    for index, threshold in enumerate(thresholds, start=1):
        if xp >= threshold:
            level = index
    return level


def xp_to_next_level(xp):
    thresholds = [0, 100, 250, 450, 700, 1000, 1400, 1900, 2500, 3200]
    level = level_for_xp(xp)
    if level >= len(thresholds):
        return None, None
    current_floor = thresholds[level - 1]
    next_floor = thresholds[level]
    return xp - current_floor, next_floor - current_floor


def get_xp(user_id):
    with get_db() as conn:
        row = conn.execute(
            "SELECT xp FROM users WHERE telegram_id = ?",
            (user_id,),
        ).fetchone()
    return row[0] if row else 0


def award_xp(user_id, amount):
    old_xp = get_xp(user_id)
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET xp = xp + ? WHERE telegram_id = ?",
            (amount, user_id),
        )
        conn.commit()
    new_xp = old_xp + amount
    return amount, level_for_xp(old_xp), level_for_xp(new_xp), new_xp


def add_user(user):
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO users (
                telegram_id,
                username,
                first_name
            )
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id)
            DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
            """,
            (
                user.id,
                user.username,
                user.first_name,
            ),
        )
        conn.commit()


def update_answer(user_id, is_correct):
    with get_db() as conn:
        if is_correct:
            conn.execute(
                """
                UPDATE users
                SET correct = correct + 1,
                    total = total + 1
                WHERE telegram_id = ?
                """,
                (user_id,),
            )
        else:
            conn.execute(
                """
                UPDATE users
                SET wrong = wrong + 1,
                    total = total + 1
                WHERE telegram_id = ?
                """,
                (user_id,),
            )

        conn.commit()


def finish_test(user_id):
    with get_db() as conn:
        conn.execute(
            """
            UPDATE users
            SET tests = tests + 1
            WHERE telegram_id = ?
            """,
            (user_id,),
        )
        conn.commit()


def get_stats(user_id):
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT correct, wrong, total, tests
            FROM users
            WHERE telegram_id = ?
            """,
            (user_id,),
        ).fetchone()

    if not row:
        return 0, 0, 0, 0

    return row


# ============================================================
# MAIN MENU
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
                    text="👤 My Profile",
                    callback_data="profile",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 My Statistics",
                    callback_data="statistics",
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Help",
                    callback_data="help",
                )
            ],
        ]
    )


# ============================================================
# CATEGORY MENU
# ============================================================

def category_keyboard():
    rows = []

    for i in range(0, len(CATEGORY_NAMES), 2):
        rows.append(
            [
                InlineKeyboardButton(
                    text=CATEGORY_NAMES[i],
                    callback_data=f"category:{CATEGORY_NAMES[i]}",
                ),
                InlineKeyboardButton(
                    text=CATEGORY_NAMES[i + 1],
                    callback_data=f"category:{CATEGORY_NAMES[i + 1]}",
                ),
            ]
        )

    rows.append(
        [
            InlineKeyboardButton(
                text="🎲 Mixed Quiz",
                callback_data="category:Mixed",
            )
        ]
    )

    rows.append(
        [
            InlineKeyboardButton(
                text="🏠 Main Menu",
                callback_data="menu",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=rows)


# ============================================================
# DIFFICULTY MENU
# ============================================================

def difficulty_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🟢 EASY",
                    callback_data="difficulty:easy",
                ),
                InlineKeyboardButton(
                    text="🟡 NORMAL",
                    callback_data="difficulty:normal",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔴 HARD",
                    callback_data="difficulty:hard",
                ),
                InlineKeyboardButton(
                    text="🎲 MIXED",
                    callback_data="difficulty:mixed",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Back",
                    callback_data="start_quiz",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Main Menu",
                    callback_data="menu",
                )
            ],
        ]
    )


# ============================================================
# GET QUESTIONS
# ============================================================

def get_questions(category, difficulty):
    if category == "Mixed":
        pool = QUESTIONS
    else:
        pool = [
            q
            for q in QUESTIONS
            if q["category"] == category
        ]

    if difficulty != "mixed":
        pool = [
            q
            for q in pool
            if q["difficulty"] == difficulty
        ]

    return pool


# ============================================================
# SHOW CATEGORIES
# ============================================================

async def show_categories(message, edit=True):
    text = (
        "📚 Choose a category:\n\n"
        "Each category has 15 questions:\n"
        "🟢 5 Easy\n"
        "🟡 5 Normal\n"
        "🔴 5 Hard\n\n"
        "🎲 Mixed gives 5 random questions."
    )

    if edit:
        await message.edit_text(
            text,
            reply_markup=category_keyboard(),
        )
    else:
        await message.answer(
            text,
            reply_markup=category_keyboard(),
        )


# ============================================================
# /START
# ============================================================

@dp.message(Command("start"))
async def start_handler(message: Message):
    add_user(message.from_user)

    await message.answer(
        "👋 Hello!\n\n"
        "Welcome to IT Quiz Bot 🧠\n\n"
        "Test your IT knowledge and track your progress.\n\n"
        "Choose an option:",
        reply_markup=main_menu(),
    )


# ============================================================
# /QUIZ
# ============================================================

@dp.message(Command("quiz"))
async def quiz_command(message: Message):
    add_user(message.from_user)

    await show_categories(
        message,
        edit=False,
    )


# ============================================================
# START QUIZ CALLBACK
# ============================================================

@dp.callback_query(F.data == "start_quiz")
async def start_quiz_callback(callback: CallbackQuery):
    add_user(callback.from_user)

    active_quizzes.pop(
        callback.from_user.id,
        None,
    )

    await callback.answer()

    await show_categories(
        callback.message,
        edit=True,
    )


# ============================================================
# CATEGORY CALLBACK
# ============================================================

@dp.callback_query(F.data.startswith("category:"))
async def category_callback(callback: CallbackQuery):
    category = callback.data.split(
        ":",
        1,
    )[1]

    active_quizzes[callback.from_user.id] = {
        "category": category,
    }

    await callback.answer()

    await callback.message.edit_text(
        f"📚 Category: {category}\n\n"
        "Choose difficulty:",
        reply_markup=difficulty_keyboard(),
    )


# ============================================================
# DIFFICULTY CALLBACK
# ============================================================

@dp.callback_query(F.data.startswith("difficulty:"))
async def difficulty_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    quiz = active_quizzes.get(user_id)

    if not quiz or "category" not in quiz:
        await callback.answer(
            "Please choose a category first.",
            show_alert=True,
        )
        return

    difficulty = callback.data.split(
        ":",
        1,
    )[1]

    pool = get_questions(
        quiz["category"],
        difficulty,
    )

    if len(pool) < 5:
        await callback.answer(
            "Not enough questions for this mode.",
            show_alert=True,
        )
        return

    active_quizzes[user_id] = {
        "category": quiz["category"],
        "difficulty": difficulty,
        "questions": random.sample(
            pool,
            5,
        ),
        "current": 0,
        "correct": 0,
        "xp_earned": 0,
        "answered": False,
    }

    await callback.answer()

    await send_question(
        callback.message,
        user_id,
    )


# ============================================================
# SEND QUESTION
# ============================================================

async def send_question(message, user_id):
    quiz = active_quizzes.get(user_id)

    if not quiz or "questions" not in quiz:
        return

    current = quiz["current"]

    question = quiz["questions"][current]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=answer,
                    callback_data=f"answer:{index}",
                )
            ]
            for index, answer in enumerate(
                question["answers"]
            )
        ]
    )

    text = (
        f"🧠 Question {current + 1}/5\n\n"
        f"📚 {question['category']}\n"
        f"🎯 {DIFFICULTY_NAMES[quiz['difficulty']]}\n\n"
        f"{question['question']}"
    )

    await message.edit_text(
        text,
        reply_markup=keyboard,
    )


# ============================================================
# ANSWER CALLBACK
# ============================================================

@dp.callback_query(F.data.startswith("answer:"))
async def answer_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    quiz = active_quizzes.get(user_id)

    if not quiz or "questions" not in quiz:
        await callback.answer(
            "This quiz has already finished.",
            show_alert=True,
        )
        return

    if quiz["answered"]:
        await callback.answer(
            "Choose Next Question.",
            show_alert=True,
        )
        return

    selected = int(
        callback.data.split(
            ":",
            1,
        )[1]
    )

    question = quiz["questions"][quiz["current"]]

    correct = question["correct"]

    is_correct = selected == correct

    quiz["answered"] = True

    if is_correct:
        quiz["correct"] += 1

        update_answer(
            user_id,
            True,
        )

        xp_values = {"easy": 10, "normal": 20, "hard": 30}
        question_difficulty = question.get("difficulty", quiz["difficulty"])
        xp_amount = xp_values.get(question_difficulty, 10)
        _, old_level, new_level, new_xp = award_xp(user_id, xp_amount)
        quiz["xp_earned"] = quiz.get("xp_earned", 0) + xp_amount
        level_message = (
            f"\n\n🎉 Level up! You are now Level {new_level}!"
            if new_level > old_level else ""
        )

        result = (
            "✅ Correct!\n"
            f"⭐ +{xp_amount} XP (total: {new_xp} XP)"
            + level_message
            + "\n\n"
            + question["explanation"]
        )

    else:
        update_answer(
            user_id,
            False,
        )

        result = (
            "❌ Incorrect.\n\n"
            f"Correct answer: "
            f"{question['answers'][correct]}\n\n"
            f"{question['explanation']}"
        )

    # ========================================================
    # LAST QUESTION
    # ========================================================

    if quiz["current"] == 4:

        score = quiz["correct"]

        wrong = 5 - score

        percent = round(
            score / 5 * 100,
            1,
        )

        finish_test(user_id)

        category = quiz["category"]

        difficulty = quiz["difficulty"]

        del active_quizzes[user_id]

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 Take Another Quiz",
                        callback_data="start_quiz",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="📊 My Statistics",
                        callback_data="statistics",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🏠 Main Menu",
                        callback_data="menu",
                    )
                ],
            ]
        )

        await callback.message.edit_text(
            result
            + "\n\n"
            + "🎉 Quiz completed!\n\n"
            + f"📚 Category: {category}\n"
            + f"🎯 Difficulty: "
            + f"{DIFFICULTY_NAMES[difficulty]}\n\n"
            + f"✅ Correct: {score}\n"
            + f"❌ Incorrect: {wrong}\n"
            + f"🎯 Accuracy: {percent}%\n"
            + f"⭐ XP earned this quiz: {quiz.get('xp_earned', 0)}\n"
            + f"⭐ Total XP: {get_xp(user_id)}\n"
            + f"🏅 Level: {level_for_xp(get_xp(user_id))}",
            reply_markup=keyboard,
        )

    else:

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="➡️ Next Question",
                        callback_data="next_question",
                    )
                ]
            ]
        )

        await callback.message.edit_text(
            result,
            reply_markup=keyboard,
        )

    await callback.answer()


# ============================================================
# NEXT QUESTION
# ============================================================

@dp.callback_query(F.data == "next_question")
async def next_question_callback(
    callback: CallbackQuery,
):
    user_id = callback.from_user.id

    if user_id not in active_quizzes:
        await callback.answer(
            "Quiz finished.",
            show_alert=True,
        )
        return

    active_quizzes[user_id]["current"] += 1

    active_quizzes[user_id]["answered"] = False

    await callback.answer()

    await send_question(
        callback.message,
        user_id,
    )


# ============================================================
# STATISTICS
# ============================================================

async def show_statistics(
    message,
    user_id,
    edit=True,
):
    correct, wrong, total, tests = get_stats(
        user_id
    )

    accuracy = (
        round(correct / total * 100, 1)
        if total
        else 0
    )

    text = (
        "📊 Your Statistics\n\n"
        f"🧪 Quizzes completed: {tests}\n"
        f"✅ Correct answers: {correct}\n"
        f"❌ Incorrect answers: {wrong}\n"
        f"📝 Total answers: {total}\n"
        f"🎯 Accuracy: {accuracy}%"
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
                    callback_data="menu",
                )
            ],
        ]
    )

    if edit:
        await message.edit_text(
            text,
            reply_markup=keyboard,
        )
    else:
        await message.answer(
            text,
            reply_markup=keyboard,
        )


# ============================================================
# PROFILE
# ============================================================

async def show_profile(message, user_id, edit=True):
    xp = get_xp(user_id)
    level = level_for_xp(xp)
    progress, needed = xp_to_next_level(xp)

    if needed is None:
        progress_text = "Maximum level reached! 🏆"
    else:
        progress_text = f"Progress to next level: {progress}/{needed} XP"

    with get_db() as conn:
        row = conn.execute(
            "SELECT first_name, correct, wrong, total, tests FROM users WHERE telegram_id = ?",
            (user_id,),
        ).fetchone()

    first_name, correct, wrong, total, tests = row or ("Player", 0, 0, 0, 0)
    accuracy = round(correct / total * 100, 1) if total else 0
    text = (
        "👤 MY PROFILE\n\n"
        f"Player: {first_name or 'Player'}\n"
        f"🏅 Level: {level}\n"
        f"⭐ Total XP: {xp}\n"
        f"📈 {progress_text}\n\n"
        f"🧪 Quizzes completed: {tests}\n"
        f"✅ Correct answers: {correct}\n"
        f"❌ Incorrect answers: {wrong}\n"
        f"🎯 Accuracy: {accuracy}%"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Start Quiz", callback_data="start_quiz")],
        [InlineKeyboardButton(text="📊 My Statistics", callback_data="statistics")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="menu")],
    ])
    if edit:
        await message.edit_text(text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)


@dp.message(Command("profile"))
async def profile_command(message: Message):
    add_user(message.from_user)
    await show_profile(message, message.from_user.id, edit=False)


@dp.callback_query(F.data == "profile")
async def profile_callback(callback: CallbackQuery):
    add_user(callback.from_user)
    await callback.answer()
    await show_profile(callback.message, callback.from_user.id, edit=True)


# ============================================================
# /STATS
# ============================================================

@dp.message(Command("stats"))
async def stats_command(message: Message):
    add_user(message.from_user)

    await show_statistics(
        message,
        message.from_user.id,
        edit=False,
    )


# ============================================================
# STATISTICS CALLBACK
# ============================================================

@dp.callback_query(F.data == "statistics")
async def statistics_callback(
    callback: CallbackQuery,
):
    add_user(callback.from_user)

    await callback.answer()

    await show_statistics(
        callback.message,
        callback.from_user.id,
        edit=True,
    )


# ============================================================
# HELP CALLBACK
# ============================================================

@dp.callback_query(F.data == "help")
async def help_callback(
    callback: CallbackQuery,
):
    await callback.answer()

    await callback.message.edit_text(
        "ℹ️ How to use IT Quiz Bot\n\n"
        "1. Choose a category.\n"
        "2. Choose Easy, Normal, Hard or Mixed.\n"
        "3. Answer 5 questions.\n"
        "4. See your result.\n"
        "5. Track your statistics.\n\n"
        "Every category has 15 questions:\n"
        "🟢 5 Easy\n"
        "🟡 5 Normal\n"
        "🔴 5 Hard\n\n"
        "Commands:\n"
        "/start — Main menu\n"
        "/quiz — Start quiz\n"
        "/stats — Statistics\n"
        "/profile — My profile and XP\n"
        "/help — Help",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🏠 Main Menu",
                        callback_data="menu",
                    )
                ]
            ]
        ),
    )


# ============================================================
# /HELP
# ============================================================

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "ℹ️ Choose a category, select difficulty, "
        "answer 5 questions, earn XP, level up and track your statistics.",
        reply_markup=main_menu(),
    )


# ============================================================
# MAIN MENU CALLBACK
# ============================================================

@dp.callback_query(F.data == "menu")
async def menu_callback(
    callback: CallbackQuery,
):
    active_quizzes.pop(
        callback.from_user.id,
        None,
    )

    await callback.answer()

    await callback.message.edit_text(
        "🏠 Main Menu\n\n"
        "Choose an option:",
        reply_markup=main_menu(),
    )


# ============================================================
# MAIN
# ============================================================

async def main():
    init_db()

    logging.info(
        "IT Quiz Bot started. Questions: %s",
        len(QUESTIONS),
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())