from typing import List, Dict, Any, Tuple
from config import FLAGS, LANGUAGES, EXPERIENCE_LEVELS, WORK_FORMATS
from candidate_manager import Candidate


def get_user_profile() -> Dict[str, Any]:
    """Собирает профиль пользователя через интерактивный опрос."""
    print("\n--- Профиль вакансии ---")
    print("Для пропуска критерия введите '0'. Можно выбрать несколько: 1,3,5")

    # Язык программирования
    print("\nВыберите требуемый(ые) язык(и) программирования:")
    for i, lang in enumerate(LANGUAGES, 1):
        print(f"{i}) {lang}")
    print("0) Пропустить")
    lang_input = input("> ").strip() # Добавлен пробел после >
    selected_langs = []
    if lang_input != "0":
        indices = [int(x.strip()) - 1 for x in lang_input.split(",") if x.strip().isdigit()]
        selected_langs = [LANGUAGES[i] for i in indices if 0 <= i < len(LANGUAGES)]

    # Уровень опыта
    print("\nВыберите требуемый уровень опыта:")
    for i, level in enumerate(EXPERIENCE_LEVELS, 1):
        print(f"{i}) {level}")
    print("0) Пропустить")
    level_input = input("> ").strip() # Добавлен пробел после >
    selected_level = ""
    if level_input != "0" and level_input.isdigit():
        idx = int(level_input) - 1
        if 0 <= idx < len(EXPERIENCE_LEVELS):
            # Сохраняем уровень в нижнем регистре
            selected_level = EXPERIENCE_LEVELS[idx].lower()

    # Опыт работы (диапазон)
    print("\nВведите минимальный и максимальный опыт работы в годах (например, 2 5).")
    print("Если не важно, нажмите Enter.")
    years_input = input("> ").strip() # Добавлен пробел после >
    min_years, max_years = 0, float('inf')
    if years_input:
        parts = years_input.split()
        if len(parts) >= 2:
            try:
                min_years, max_years = int(parts[0]), int(parts[1])
            except ValueError:
                pass # Используем значения по умолчанию
        elif len(parts) == 1:
             try:
                 min_years = int(parts[0])
                 # Если ввели одно число, считаем его как минимум, максимум неограничен
                 max_years = float('inf')
             except ValueError:
                 pass # Используем значения по умолчанию


    # Формат работы
    print("\nВыберите требуемый формат работы:")
    for i, fmt in enumerate(WORK_FORMATS, 1):
        print(f"{i}) {fmt}")
    print("0) Пропустить")
    fmt_input = input("> ").strip() # Добавлен пробел после >
    selected_fmts = []
    if fmt_input != "0":
        indices = [int(x.strip()) - 1 for x in fmt_input.split(",") if x.strip().isdigit()]
        selected_fmts = [WORK_FORMATS[i] for i in indices if 0 <= i < len(WORK_FORMATS)]

    # Зарплата (диапазон)
    print("\nВведите минимальную и максимальную ожидаемую зарплату (например, 30000 50000).")
    print("Если не важно, нажмите Enter.")
    salary_input = input("> ").strip() # Добавлен пробел после >
    min_salary, max_salary = 0, float('inf')
    if salary_input:
        parts = salary_input.split()
        if len(parts) >= 2:
            try:
                min_salary, max_salary = int(parts[0]), int(parts[1])
            except ValueError:
                pass # Используем значения по умолчанию
        elif len(parts) == 1:
             try:
                 min_salary = int(parts[0])
                 # Если ввели одно число, считаем его как минимум, максимум неограничен
                 max_salary = float('inf')
             except ValueError:
                 pass # Используем значения по умолчанию

    return {
        "languages": selected_langs,
        "level": selected_level,
        "years_range": (min_years, max_years),
        "formats": selected_fmts,
        "salary_range": (min_salary, max_salary),
    }

def has_match(item_list: List[str], prefs: List[str], relaxed: bool) -> bool:
    """Проверяет, есть ли совпадение между списком у кандидата и предпочтениями."""
    if not prefs:
        return True
    if relaxed:
        for p in prefs:
            for x in item_list:
                if p.lower() in x.lower():
                    return True
        return False
    return bool(set(prefs) & set(item_list))

def contains_all(item_list: List[str], prefs: List[str], relaxed: bool) -> bool:
    """Проверяет, содержит ли список кандидата ВСЕ выбранные пользователем значения."""
    if not prefs:
        return True
    if relaxed:
        for p in prefs:
            found = False
            for x in item_list:
                if p.lower() in x.lower():
                    found = True
                    break
            if not found:
                return False
        return True
    return set(prefs).issubset(set(item_list))

def check_pref(item_list: List[str], prefs: List[str], relaxed: bool, require_all: bool) -> bool:
    """Универсальная проверка списка атрибутов (язык, формат)."""
    if require_all:
        return contains_all(item_list, prefs, relaxed)
    else:
        return has_match(item_list, prefs, relaxed)

def recommend(candidates: List[Candidate], profile: Dict[str, Any], flags: Dict[str, bool]):
    """Фильтрует и возвращает список подходящих кандидатов."""
    results = []
    debug_info = []

    for c in candidates:
        reasons = []

        # 1. Проверка языка
        if not check_pref(c.language, profile["languages"], flags["relaxed"], flags["all"]):
            reasons.append("язык не совпал")
        # 2. Проверка уровня
        if profile["level"] and profile["level"] != c.level.lower():
            reasons.append("уровень не совпал")
        # 3. Проверка лет опыта
        if not (profile["years_range"][0] <= c.years <= profile["years_range"][1]):
            reasons.append(f"опыт {c.years} лет не подходит под [{profile['years_range'][0]}, {profile['years_range'][1]}]")
        # 4. Проверка формата
        if not check_pref(c.format, profile["formats"], flags["relaxed"], flags["all"]):
            reasons.append("формат не совпал")
        # 5. Проверка зарплаты
        if not (profile["salary_range"][0] <= c.salary <= profile["salary_range"][1]):
            reasons.append(f"зарплата {c.salary} не подходит под [{profile['salary_range'][0]}, {profile['salary_range'][1]}]")

        if reasons:
            if flags["why"]:
                debug_info.append((c.name, reasons))
        else:
            results.append(c)

    if flags["why"] and debug_info:
        print("\n[Диагностика] Причины отсева:")
        for name, reasons in debug_info:
            print(f"  - {name}: {', '.join(reasons)}")

    return results