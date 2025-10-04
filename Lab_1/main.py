import sys
from config import FLAGS, LANGUAGES, EXPERIENCE_LEVELS, WORK_FORMATS
from candidate_manager import load_candidates, save_candidate, Candidate
from expert_system import get_user_profile, recommend


def print_menu():
    print("\n--- Меню ---")
    print("1. Добавить нового кандидата")
    print("2. Запустить подбор кандидатов")
    print("3. Выход")
    choice = input("Выберите действие (1-3): ").strip()
    return choice

def add_candidate_flow():
    print("\n--- Добавление нового кандидата ---")
    name = input("Введите имя кандидата: ").strip()
    if not name:
        print("Имя не может быть пустым.")
        return

    print("Доступные языки:", ", ".join(LANGUAGES))
    lang_input = input("Введите языки через запятую: ").strip()
    langs = [l.strip() for l in lang_input.split(',') if l.strip()]

    print("Доступные уровни:", ", ".join(EXPERIENCE_LEVELS))
    level = input("Введите уровень (junior/middle/senior/lead): ").strip()
    if level not in EXPERIENCE_LEVELS:
        print("Некорректный уровень. Используйте один из:", EXPERIENCE_LEVELS)
        return

    try:
        years = int(input("Введите стаж в годах: ").strip())
    except ValueError:
        print("Некорректный ввод стажа. Должно быть число.")
        return

    print("Доступные форматы:", ", ".join(WORK_FORMATS))
    fmt_input = input("Введите форматы через запятую: ").strip()
    fmts = [f.strip() for f in fmt_input.split(',') if f.strip()]

    try:
        salary = int(input("Введите ожидаемую зарплату: ").strip())
    except ValueError:
        print("Некорректный ввод зарплаты. Должно быть число.")
        return

    candidate = Candidate(name=name, language=langs, level=level, years=years, format=fmts, salary=salary)
    save_candidate(candidate)

def run_expert_system_flow(flags):
    print("\n--- Запуск экспертной системы ---")
    candidates = load_candidates()
    if not candidates:
        print("База знаний пуста. Добавьте кандидатов.")
        return

    profile = get_user_profile()
    results = recommend(candidates, profile, flags)

    if not results:
        print("\nПодходящих кандидатов не найдено.")
        print("Попробуйте изменить критерии или запустить с --relaxed/--why.")
        return

    print(f"\nНайдено {len(results)} подходящих кандидатов:")
    for i, c in enumerate(results, 1):
        print(f"{i}. {c.name}")
        print(f"   Языки: {', '.join(c.language) if c.language else 'не указаны'}")
        print(f"   Уровень: {c.level if c.level else 'не указан'}")
        print(f"   Стаж: {c.years} лет")
        print(f"   Формат: {', '.join(c.format) if c.format else 'не указан'}")
        print(f"   Зарплата: {c.salary} руб.")


def main():
    # Разбор флагов командной строки
    flags = {
        "relaxed": FLAGS["relaxed"] in sys.argv,
        "all": FLAGS["all"] in sys.argv,
        "why": FLAGS["why"] in sys.argv,
    }

    print("Экспертная система подбора кандидатов в IT")
    if flags["relaxed"]:
        print("Режим: МЯГКИЙ (поиск по подстроке).")
    if flags["all"]:
        print("Условие: КАЖДЫЙ выбранный пункт обязателен.")
    if flags["why"]:
        print("Режим: ДИАГНОСТИКА (причины отсева).")

    while True:
        choice = print_menu()
        if choice == "1":
            add_candidate_flow()
        elif choice == "2":
            run_expert_system_flow(flags)
        elif choice == "3":
            print("До свидания!")
            break
        else:
            print("Некорректный выбор. Пожалуйста, введите 1, 2 или 3.")


if __name__ == "__main__":
    main()