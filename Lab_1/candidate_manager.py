import pandas as pd
from config import DB_PATH, COLUMN_ALIASES
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Candidate:
    name: str
    language: List[str]
    level: str
    years: int
    format: List[str]
    salary: int

def find_column(df_cols: List[str], key: str) -> str:
    """Находит имя колонки в DataFrame по набору синонимов."""
    norm_cols = {col.lower().replace(" ", ""): col for col in df_cols}
    for alias in COLUMN_ALIASES.get(key, set()):
        norm_alias = alias.lower().replace(" ", "")
        if norm_alias in norm_cols:
            return norm_cols[norm_alias]
    raise KeyError(f"Не найдена колонка для '{key}' в файле {DB_PATH}.")

def load_candidates() -> List[Candidate]:
    """Загружает кандидатов из CSV файла."""
    try:
        df = pd.read_csv(DB_PATH, encoding='utf-8').dropna(how='all')
    except FileNotFoundError:
        print(f"Файл базы знаний не найден по пути: {DB_PATH}")
        print("Создайте файл и добавьте заголовки.")
        return []
    except Exception as e:
        print(f"Ошибка чтения CSV: {e}")
        return []

    cols = list(df.columns)
    col_name = find_column(cols, "name")
    col_lang = find_column(cols, "language")
    col_level = find_column(cols, "level")
    col_years = find_column(cols, "years")
    col_format = find_column(cols, "format")
    col_salary = find_column(cols, "salary")

    candidates = []
    for _, row in df.iterrows():
        name = str(row[col_name]).strip()
        if not name or name.lower() == "nan":
            continue

        # Язык и формат могут быть списками, разделяемыми запятой
        lang_str = str(row[col_lang])
        langs = [l.strip() for l in lang_str.split(',')] if pd.notna(row[col_lang]) else []
        fmt_str = str(row[col_format])
        formats = [f.strip() for f in fmt_str.split(',')] if pd.notna(row[col_format]) else []

        try:
            years = int(row[col_years])
        except (ValueError, TypeError):
            years = 0
        try:
            salary = int(row[col_salary])
        except (ValueError, TypeError):
            salary = 0

        level = str(row[col_level]).strip()

        candidates.append(Candidate(
            name=name,
            language=langs,
            level=level,
            years=years,
            format=formats,
            salary=salary
        ))
    return candidates

def save_candidate(candidate: Candidate):
    """Сохраняет нового кандидата в CSV файл."""
    import os
    # Проверяем, существует ли файл
    file_exists = os.path.isfile(DB_PATH)

    # Создаем DataFrame с новым кандидатом
    new_row = {
        "name": candidate.name,
        "language": ", ".join(candidate.language),
        "level": candidate.level,
        "years": candidate.years,
        "format": ", ".join(candidate.format),
        "salary": candidate.salary
    }
    df = pd.DataFrame([new_row])

    # Сохраняем в CSV
    df.to_csv(DB_PATH, mode='a', header=not file_exists, index=False, encoding='utf-8')
    print(f"Кандидат '{candidate.name}' успешно добавлен в базу знаний.")