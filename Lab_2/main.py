import sys
sys.path.append("../Lab_1/")

from config import FLAGS, LANGUAGES, EXPERIENCE_LEVELS, WORK_FORMATS
from candidate_manager import load_candidates, save_candidate, Candidate
from expert_system import get_user_profile, recommend
from ontology_interface import OntologyInterface

# !!! UPDATED
def print_menu():
    print("\n--- Меню ---")
    print("1. Добавить нового кандидата")
    print("2. Запустить подбор кандидатов")
    print("3. Онтологический анализ")
    print("4. Создать тестовые данные")
    print("5. Выход")
    choice = input("Выберите действие (1-5): ").strip()
    return choice

# !!! UPDATED
def add_candidate_flow(ontology_interface: OntologyInterface):
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
    
    # Добавляем кандидата в онтологию
    candidate_data = {
        "name": name,
        "language": langs,
        "level": level,
        "years": years,
        "format": fmts,
        "salary": salary
    }
    ontology_interface.add_candidate_to_ontology(candidate_data)

# !!! UPDATED
def run_expert_system_flow(flags, ontology_interface: OntologyInterface):
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
    
    # Предлагаем онтологический анализ для найденных кандидатов
    if results and input("\nВыполнить онтологический анализ для найденных кандидатов? (y/n): ").lower() == 'y':
        for candidate in results:
            print(f"\n--- Анализ кандидата: {candidate.name} ---")
            ontology_interface.reasoner.reason_about_candidate(candidate.name.replace(" ", "_"))


# !!! UPDATED
def main():
    # Разбор флагов командной строки
    flags = {
        "relaxed": FLAGS["relaxed"] in sys.argv,
        "all": FLAGS["all"] in sys.argv,
        "why": FLAGS["why"] in sys.argv,
    }

    # Инициализация онтологического интерфейса
    ontology_interface = OntologyInterface()

    print("Экспертная система подбора кандидатов в IT")
    if flags["relaxed"]:
        print("Режим: МЯГКИЙ (поиск по подстроке).")
    if flags["all"]:
        print("Условие: КАЖДЫЙ выбранный пункт обязателен.")
    if flags["why"]:
        print("Режим: ДИАГНОСТИКА (причины отсева).")

    while True:
        choice = print_menu()  # Нужно обновить функцию print_menu
        
        if choice == "1":
            add_candidate_flow(ontology_interface)  # Обновленная функция
        elif choice == "2":
            run_expert_system_flow(flags, ontology_interface)  # Обновленная функция
        elif choice == "3":
            ontology_interface.run_interactive_mode()
        elif choice == "4":
            ontology_interface.create_sample_vacancies()
        elif choice == "5":
            print("До свидания!")
            break
        else:
            print("Некорректный выбор. Пожалуйста, введите 1, 2, 3 или 4.")


if __name__ == "__main__":
    main()