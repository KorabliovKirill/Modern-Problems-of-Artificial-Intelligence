import os

# Путь к файлу базы знаний
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "candidates.csv")

# Допустимые значения для атрибутов
LANGUAGES = [
    "Python", "Java", "C++", "JavaScript", "Go", "Rust", "Prolog", "C#", "Ruby", "TypeScript"
]

EXPERIENCE_LEVELS = [
    "junior", "middle", "senior", "lead"
]

WORK_FORMATS = [
    "удалённый", "очно", "гибридный"
]

# Соответствие названий столбцов в CSV
COLUMN_ALIASES = {
    "name": {"имя", "name", "кандидат"},
    "language": {"язык", "язык программирования", "language"},
    "level": {"уровень", "уровень опыта", "level", "опыт"},
    "years": {"опыт работы", "years", "years_of_experience", "стаж"},
    "format": {"формат", "формат работы", "work_format"},
    "salary": {"зарплата", "ожидаемая зарплата", "salary"},
}

# Возможные флаги командной строки
FLAGS = {
    "relaxed": "--relaxed",
    "all": "--all",
    "why": "--why",
}