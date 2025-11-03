# config.py
import os

# Путь к файлу базы знаний
DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "candidates.csv"
)

# Допустимые значения для атрибутов
LANGUAGES = [
    "Python",
    "Java",
    "C++",
    "JavaScript",
    "Go",
    "Rust",
    "Prolog",
    "C#",
    "Ruby",
    "TypeScript",
]

EXPERIENCE_LEVELS = ["junior", "middle", "senior", "lead"]

WORK_FORMATS = ["удалённый", "очно", "гибридный"]

# Соответствие названий столбцов в CSV - ДОБАВИМ ТОЧНЫЕ НАЗВАНИЯ КОЛОНОК
COLUMN_ALIASES = {
    "name": {"name", "имя", "name", "кандидат", "candidate"},
    "language": {
        "language",
        "язык",
        "язык программирования",
        "language",
        "programming language",
        "skills",
    },
    "level": {"level", "уровень", "уровень опыта", "level", "опыт", "experience level"},
    "years": {
        "years",
        "опыт работы",
        "years",
        "years_of_experience",
        "стаж",
        "experience",
        "опыт",
    },
    "format": {
        "format",
        "формат",
        "формат работы",
        "work_format",
        "work format",
        "формат",
    },
    "salary": {"salary", "зарплата", "ожидаемая зарплата", "salary", "expected salary"},
}

# Возможные флаги командной строки
FLAGS = {
    "relaxed": "--relaxed",
    "all": "--all",
    "why": "--why",
    "bayes": "--bayes",
}
