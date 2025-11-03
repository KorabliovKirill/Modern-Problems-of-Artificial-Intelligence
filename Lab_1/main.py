# main.py
import sys
from config import FLAGS, LANGUAGES, EXPERIENCE_LEVELS, WORK_FORMATS
from candidate_manager import load_candidates, save_candidate, Candidate
from expert_system import recommend


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
    langs = [l.strip() for l in lang_input.split(",") if l.strip()]

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
    fmts = [f.strip() for f in fmt_input.split(",") if f.strip()]

    try:
        salary = int(input("Введите ожидаемую зарплату: ").strip())
    except ValueError:
        print("Некорректный ввод зарплаты. Должно быть число.")
        return

    candidate = Candidate(
        name=name, language=langs, level=level, years=years, format=fmts, salary=salary
    )
    save_candidate(candidate)


def run_expert_system_flow(flags):
    """Запуск экспертной системы с поддержкой Баесовского режима."""
    print("\n--- Запуск экспертной системы ---")
    candidates = load_candidates()
    if not candidates:
        print("База знаний пуста. Добавьте кандидатов.")
        return

    # Сбор профиля пользователя с выводом в main
    print("\n--- Профиль вакансии ---")
    print("Для пропуска критерия введите '0'. Можно выбрать несколько: 1,3,5")
    
    # Язык программирования
    print("\nВыберите требуемый(ые) язык(и) программирования:")
    for i, lang in enumerate(LANGUAGES, 1):
        print(f"{i}) {lang}")
    print("0) Пропустить")
    lang_input = input("> ").strip()
    selected_langs = []
    if lang_input != "0":
        indices = [
            int(x.strip()) - 1 for x in lang_input.split(",") if x.strip().isdigit()
        ]
        selected_langs = [LANGUAGES[i] for i in indices if 0 <= i < len(LANGUAGES)]
    
    # Уровень опыта
    print("\nВыберите требуемый уровень опыта:")
    for i, level in enumerate(EXPERIENCE_LEVELS, 1):
        print(f"{i}) {level}")
    print("0) Пропустить")
    level_input = input("> ").strip()
    selected_level = ""
    if level_input != "0" and level_input.isdigit():
        idx = int(level_input) - 1
        if 0 <= idx < len(EXPERIENCE_LEVELS):
            selected_level = EXPERIENCE_LEVELS[idx].lower()
    
    # Опыт работы
    print("\nВведите минимальный и максимальный опыт работы в годах (например, 2 5).")
    print("Если не важно, нажмите Enter.")
    years_input = input("> ").strip()
    min_years, max_years = 0, float("inf")
    if years_input:
        parts = years_input.split()
        if len(parts) >= 2:
            try:
                min_years, max_years = int(parts[0]), int(parts[1])
            except ValueError:
                pass
        elif len(parts) == 1:
            try:
                min_years = int(parts[0])
            except ValueError:
                pass
    
    # Формат работы
    print("\nВыберите требуемый формат работы:")
    for i, fmt in enumerate(WORK_FORMATS, 1):
        print(f"{i}) {fmt}")
    print("0) Пропустить")
    fmt_input = input("> ").strip()
    selected_fmts = []
    if fmt_input != "0":
        indices = [
            int(x.strip()) - 1 for x in fmt_input.split(",") if x.strip().isdigit()
        ]
        selected_fmts = [WORK_FORMATS[i] for i in indices if 0 <= i < len(WORK_FORMATS)]
    
    # Зарплата
    print("\nВведите минимальную и максимальную ожидаемую зарплату (например, 30000 50000).")
    print("Если не важно, нажмите Enter.")
    salary_input = input("> ").strip()
    min_salary, max_salary = 0, float("inf")
    if salary_input:
        parts = salary_input.split()
        if len(parts) >= 2:
            try:
                min_salary, max_salary = int(parts[0]), int(parts[1])
            except ValueError:
                pass
        elif len(parts) == 1:
            try:
                min_salary = int(parts[0])
            except ValueError:
                pass
    
    # Формируем профиль
    profile = {
        "languages": selected_langs,
        "level": selected_level,
        "years_range": (min_years, max_years),
        "formats": selected_fmts,
        "salary_range": (min_salary, max_salary),
    }
    
    results = recommend(candidates, profile, flags)

    # Байесовский режим - вывод здесь в main.py
    if flags.get("bayes"):
        if not results:
            print("\nПодходящих кандидатов не найдено (все ниже порога вероятности 0.3).")
        else:
            print("\nРейтинг кандидатов (Баесовская вероятность соответствия):")
            print("Показаны только кандидаты с вероятностью >= 0.3\n")
            for i, (c, prob) in enumerate(results, 1):
                print(f"{i}. {c.name} — вероятность {prob:.3f}")
                print(f"   Языки: {', '.join(c.language)} | Уровень: {c.level} | "
                      f"Стаж: {c.years} лет | Формат: {', '.join(c.format)} | Зарплата: {c.salary} руб.")
        return

    # Классический режим
    if not results:
        print("\nПодходящих кандидатов не найдено.")
        print("Попробуйте изменить критерии или запустить с --relaxed/--why.")
        return

    print(f"\nНайдено {len(results)} подходящих кандидатов:\n")
    for i, c in enumerate(results, 1):
        print(f"{i}. {c.name}")
        print(f"   Языки: {', '.join(c.language) if c.language else 'не указаны'} | "
              f"Уровень: {c.level if c.level else 'не указан'} | "
              f"Стаж: {c.years} лет | "
              f"Формат: {', '.join(c.format) if c.format else 'не указан'} | "
              f"Зарплата: {c.salary} руб.")


def main():
    # Разбор флагов командной строки
    flags = {
        "relaxed": FLAGS["relaxed"] in sys.argv,
        "all": FLAGS["all"] in sys.argv,
        "why": FLAGS["why"] in sys.argv,
        "bayes": FLAGS.get("bayes", "--bayes") in sys.argv,
    }

    print("=" * 70)
    print("Экспертная система подбора кандидатов в IT")
    print("=" * 70)

    # Отображение активных режимов с подробными объяснениями
    print("\n📋 Активные флаги:")
    
    if flags["bayes"]:
        print("\n🔹 --bayes: БАЙЕСОВСКАЯ ЛОГИКА")
        print("   Использует вероятностный подход для оценки соответствия кандидатов.")
        print("   Каждый кандидат получает оценку от 0 до 1 (нормализованная вероятность).")
        print("   Показываются только кандидаты с вероятностью >= 0.3 (30%).")
        print("   Учитываются частичные совпадения с уменьшением вероятности.")
    else:
        print("\n🔹 Классический режим (по умолчанию)")
        print("   Использует строгую логику: все критерии должны быть выполнены полностью.")
        print("   Кандидат либо подходит (все условия выполнены), либо нет.")
        
    if flags["relaxed"]:
        print("\n🔹 --relaxed: МЯГКИЙ РЕЖИМ")
        print("   Поиск по подстроке для языков и форматов работы.")
        print("   Например, если выбран Python, подойдут кандидаты со знанием Python.")
        print("   Хотя бы одно совпадение из списка считается успешным.")
    
    if flags["all"]:
        print("\n🔹 --all: СТРОГИЙ РЕЖИМ")
        print("   Требуется совпадение ВСЕХ выбранных пунктов.")
        print("   Если выбрано несколько языков/форматов, кандидат должен знать ВСЕ.")
        print("   Работает вместе с --relaxed для более гибкого поиска.")
    
    if flags["why"]:
        print("\n🔹 --why: РЕЖИМ ДИАГНОСТИКИ")
        print("   Показывает причины, по которым кандидаты были отсеяны.")
        print("   Полезно для понимания, почему не найдено подходящих кандидатов.")
        print("   Помогает скорректировать критерии поиска.")
    
    if not any([flags["bayes"], flags["relaxed"], flags["all"], flags["why"]]):
        print("   Нет активных флагов. Используется стандартный режим.")
        print("   Доступные флаги: --bayes, --relaxed, --all, --why")
    
    print("\n" + "=" * 70)

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
