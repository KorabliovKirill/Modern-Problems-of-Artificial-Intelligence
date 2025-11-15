# fuzzy_main.py
import numpy as np
import sys
import os

# Добавляем пути для импорта существующих модулей
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "Lab_1"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "Lab_2"))

from candidate_manager import load_candidates, save_candidate, Candidate
from config import LANGUAGES, EXPERIENCE_LEVELS, WORK_FORMATS
from fuzzy_system import FuzzyExpertSystem, FuzzyLogicSystem

def get_user_profile():
    """Альтернативная реализация функции get_user_profile для Lab_3"""
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
    
    return profile

def print_fuzzy_menu():
    """Главное меню с нечеткой логикой"""
    print("\n" + "="*50)
    print("      ЭКСПЕРТНАЯ СИСТЕМА ПОДБОРА КАНДИДАТОВ")
    print("              с нечеткой логикой")
    print("="*50)
    print("1. Добавить нового кандидата")
    print("2. Четкий подбор кандидатов (традиционный)")
    print("3. Нечеткий подбор кандидатов")
    print("4. Детальный нечеткий анализ кандидата")
    print("5. Сравнение кандидатов")
    print("6. Тестирование нечеткой системы")
    print("7. 📊 Диагностический режим (все этапы)")
    print("8. Выход")
    print("-"*50)
    
    choice = input("Выберите действие (1-8): ").strip()
    return choice

def add_candidate_flow():
    """Добавление нового кандидата (существующая функциональность)"""
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
    print(f"✓ Кандидат '{candidate.name}' успешно добавлен в базу знаний.")

def run_traditional_expert_system():
    """Запуск традиционной экспертной системы"""
    print("\n--- Традиционный подбор кандидатов ---")
    candidates = load_candidates()
    if not candidates:
        print("База знаний пуста. Добавьте кандидатов.")
        return

    profile = get_user_profile()
    
    # Используем существующую функцию recommend
    from expert_system import recommend
    
    # Создаем флаги для традиционного режима
    flags = {"relaxed": False, "all": False, "why": False}
    
    results = recommend(candidates, profile, flags)

    if not results:
        print("\n❌ Подходящих кандидатов не найдено.")
        return

    print(f"\n✅ Найдено {len(results)} подходящих кандидатов:")
    for i, c in enumerate(results, 1):
        print(f"{i}. {c.name}")
        print(f"   Языки: {', '.join(c.language) if c.language else 'не указаны'}")
        print(f"   Уровень: {c.level if c.level else 'не указан'}")
        print(f"   Стаж: {c.years} лет")
        print(f"   Формат: {', '.join(c.format) if c.format else 'не указан'}")
        print(f"   Зарплата: {c.salary} руб.")

def run_fuzzy_expert_system():
    """Запуск нечеткой экспертной системы"""
    print("\n--- Нечеткий подбор кандидатов ---")
    candidates = load_candidates()
    if not candidates:
        print("База знаний пуста. Добавьте кандидатов.")
        return

    print("Введите требования вакансии:")
    profile = get_user_profile()
    
    # Конвертируем кандидатов в словари
    candidate_dicts = []
    for candidate in candidates:
        candidate_dict = {
            "name": candidate.name,
            "language": candidate.language,
            "level": candidate.level,
            "years": candidate.years,
            "format": candidate.format,
            "salary": candidate.salary
        }
        candidate_dicts.append(candidate_dict)
    
    # Запускаем нечеткую систему
    fuzzy_expert = FuzzyExpertSystem()
    results = fuzzy_expert.fuzzy_recommend(candidate_dicts, profile)
    
    if not results:
        print("\n❌ Подходящих кандидатов не найдено.")
        return
    
    print(f"\n🎯 Результаты нечеткого подбора ({len(results)} кандидатов):")
    print("="*80)
    
    for i, result in enumerate(results, 1):
        score = result['final_score']
        # Цветовая индикация в зависимости от оценки
        if score >= 70:
            indicator = "🟢"
        elif score >= 40:
            indicator = "🟡" 
        else:
            indicator = "🔴"
            
        print(f"{indicator} {i}. {result['candidate_name']} - {score:.1f}%")
        print(f"   📋 {result['recommendation']}")
        
        # Показываем активированные правила для топ-кандидатов
        if i <= 3 and result.get('activated_rules'):
            print(f"   🔍 Активированные правила:")
            for rule in result['activated_rules'][:2]:  # Показываем первые 2 правила
                print(f"      - {rule['description']} (сила: {rule['strength']:.2f})")
        print()

def detailed_fuzzy_analysis():
    """Детальный анализ конкретного кандидата"""
    print("\n--- Детальный нечеткий анализ кандидата ---")
    candidates = load_candidates()
    if not candidates:
        print("База знаний пуста. Добавьте кандидатов.")
        return

    # Выводим список кандидатов
    print("Доступные кандидаты:")
    for i, candidate in enumerate(candidates, 1):
        print(f"{i}. {candidate.name}")
    
    try:
        choice = int(input("\nВыберите кандидата для анализа: ").strip())
        if 1 <= choice <= len(candidates):
            selected_candidate = candidates[choice - 1]
        else:
            print("❌ Некорректный выбор.")
            return
    except ValueError:
        print("❌ Пожалуйста, введите число.")
        return

    # Конвертируем кандидата в словарь
    candidate_dict = {
        "name": selected_candidate.name,
        "language": selected_candidate.language,
        "level": selected_candidate.level,
        "years": selected_candidate.years,
        "format": selected_candidate.format,
        "salary": selected_candidate.salary
    }

    # Выполняем детальный анализ
    fuzzy_system = FuzzyLogicSystem()
    result = fuzzy_system.evaluate_candidate(candidate_dict)
    
    print(f"\n🎯 ДЕТАЛЬНЫЙ АНАЛИЗ: {result['candidate_name']}")
    print("="*60)
    print(f"Финальная оценка: {result['final_score']:.1f}%")
    print(f"Рекомендация: {result['recommendation']}")
    
    # Показываем активированные правила
    if result.get('activated_rules'):
        print(f"\n📋 АКТИВИРОВАННЫЕ ПРАВИЛА:")
        for rule in result['activated_rules']:
            print(f"  • {rule['description']} (сила: {rule['strength']:.2f})")
    
    print("\n📊 СТЕПЕНИ ПРИНАДЛЕЖНОСТИ:")
    
    fuzzy_vals = result['fuzzy_values']
    
    # Уровень опыта
    print(f"  Уровень опыта ({candidate_dict['years']} лет):")
    print(f"    Junior: {fuzzy_vals.get('level_junior', 0):.3f}")
    print(f"    Middle: {fuzzy_vals.get('level_middle', 0):.3f}")
    print(f"    Senior: {fuzzy_vals.get('level_senior', 0):.3f}")
    
    # Тип разработчика
    print(f"  Тип разработчика ({len(candidate_dict['language'])} языков): {', '.join(candidate_dict['language'])}")
    print(f"    Backend: {fuzzy_vals.get('backend_developer', 0):.3f}")
    print(f"    Frontend: {fuzzy_vals.get('frontend_developer', 0):.3f}")
    print(f"    Fullstack: {fuzzy_vals.get('fullstack_developer', 0):.3f}")
    
    # Гибкость
    formats_count = len(candidate_dict['format'])
    print(f"  Гибкость ({formats_count} форматов): {', '.join(candidate_dict['format'])}")
    print(f"    Low: {fuzzy_vals.get('flexibility_low', 0):.3f}")
    print(f"    Medium: {fuzzy_vals.get('flexibility_medium', 0):.3f}")
    print(f"    High: {fuzzy_vals.get('flexibility_high', 0):.3f}")

def compare_candidates_flow():
    """Сравнение нескольких кандидатов"""
    print("\n--- Сравнение кандидатов ---")
    candidates = load_candidates()
    if not candidates:
        print("База знаний пуста. Добавьте кандидатов.")
        return

    if len(candidates) < 2:
        print("❌ Для сравнения нужно как минимум 2 кандидата.")
        return

    # Конвертируем всех кандидатов
    candidate_dicts = []
    for candidate in candidates:
        candidate_dict = {
            "name": candidate.name,
            "language": candidate.language,
            "level": candidate.level,
            "years": candidate.years,
            "format": candidate.format,
            "salary": candidate.salary
        }
        candidate_dicts.append(candidate_dict)

    # Оцениваем всех кандидатов
    fuzzy_expert = FuzzyExpertSystem()
    results = fuzzy_expert.fuzzy_recommend(candidate_dicts)
    
    print(f"\n📈 СРАВНЕНИЕ {len(results)} КАНДИДАТОВ:")
    print("="*80)
    
    # Группируем по уровню оценки
    excellent = [r for r in results if r['final_score'] >= 70]
    good = [r for r in results if 40 <= r['final_score'] < 70]
    poor = [r for r in results if r['final_score'] < 40]
    
    if excellent:
        print("\n🏆 ОТЛИЧНОЕ СООТВЕТСТВИЕ (70-100%):")
        for result in excellent:
            print(f"  ✅ {result['candidate_name']} - {result['final_score']:.1f}%")
    
    if good:
        print("\n👍 ХОРОШЕЕ СООТВЕТСТВИЕ (40-69%):")
        for result in good:
            print(f"  ⚡ {result['candidate_name']} - {result['final_score']:.1f}%")
    
    if poor:
        print("\n❌ НИЗКОЕ СООТВЕТСТВИЕ (0-39%):")
        for result in poor:
            print(f"  🔴 {result['candidate_name']} - {result['final_score']:.1f}%")
    
    # Статистика
    print(f"\n📊 СТАТИСТИКА:")
    print(f"  Всего кандидатов: {len(results)}")
    print(f"  Отличных: {len(excellent)}")
    print(f"  Хороших: {len(good)}")
    print(f"  Низких: {len(poor)}")

def test_fuzzy_system():
    """Тестирование нечеткой системы на примерах"""
    print("\n--- Тестирование нечеткой системы ---")
    
    # Тестовые данные
    test_candidates = [
        {
            "name": "Тест: Идеальный Middle Fullstack",
            "language": ["Python", "JavaScript", "TypeScript"],
            "level": "middle",
            "years": 4,
            "format": ["удалённый", "гибридный", "очно"],
            "salary": 120000
        },
        {
            "name": "Тест: Senior Backend с низкой гибкостью",
            "language": ["Java", "C++"],
            "level": "senior",
            "years": 8,
            "format": ["очно"],
            "salary": 200000
        },
        {
            "name": "Тест: Junior Backend",
            "language": ["Python"],
            "level": "junior", 
            "years": 1,
            "format": ["удалённый"],
            "salary": 60000
        }
    ]
    
    print("Тестовые кандидаты созданы. Запуск нечеткой оценки...")
    print()
    
    fuzzy_expert = FuzzyExpertSystem()
    results = fuzzy_expert.fuzzy_recommend(test_candidates)
    
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("="*60)
    
    for result in results:
        score = result['final_score']
        print(f"🎯 {result['candidate_name']}")
        print(f"   Оценка: {score:.1f}% - {result['recommendation']}")
        
        # Показываем ключевые правила
        if result.get('activated_rules'):
            top_rule = result['activated_rules'][0]
            print(f"   Главное правило: {top_rule['description']} (сила: {top_rule['strength']:.2f})")
        print()

def main():
    """Главная функция программы"""
    print("🚀 Загрузка экспертной системы с нечеткой логикой...")
    
    # Проверяем наличие кандидатов
    candidates = load_candidates()
    if candidates:
        print(f"✅ Загружено {len(candidates)} кандидатов из базы знаний")
    else:
        print("ℹ️  База знаний пуста. Вы можете добавить кандидатов через меню.")
    
    fuzzy_expert = FuzzyExpertSystem()
    print("✅ Нечеткая экспертная система инициализирована")
    
    while True:
        try:
            choice = print_fuzzy_menu()
            
            if choice == "1":
                add_candidate_flow()
            elif choice == "2":
                run_traditional_expert_system()
            elif choice == "3":
                run_fuzzy_expert_system()
            elif choice == "4":
                detailed_fuzzy_analysis()
            elif choice == "5":
                compare_candidates_flow()
            elif choice == "6":
                test_fuzzy_system()
            elif choice == "7":  # Новый диагностический режим
                diagnostic_mode()
            elif choice == "8":
                print("\n👋 До свидания! Спасибо за использование экспертной системы.")
                break
            else:
                print("❌ Некорректный выбор. Пожалуйста, введите число от 1 до 8.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Программа прервана пользователем. До свидания!")
            break
        except Exception as e:
            print(f"\n❌ Произошла ошибка: {e}")
            import traceback
            traceback.print_exc()
            print("Пожалуйста, попробуйте еще раз.")

def diagnostic_mode():
    """Режим диагностики с подробным показом всех этапов нечеткой системы"""
    print("\n--- ДИАГНОСТИЧЕСКИЙ РЕЖИМ ---")
    print("Подробный показ фаззификации, логического вывода и дефаззификации")
    print("=" * 70)
    
    candidates = load_candidates()
    if not candidates:
        print("База знаний пуста. Добавьте кандидатов.")
        return

    # Выбираем кандидата для анализа
    print("Доступные кандидаты:")
    for i, candidate in enumerate(candidates, 1):
        print(f"{i}. {candidate.name}")
    
    try:
        choice = int(input("\nВыберите кандидата для диагностики: ").strip())
        if 1 <= choice <= len(candidates):
            selected_candidate = candidates[choice - 1]
        else:
            print("❌ Некорректный выбор.")
            return
    except ValueError:
        print("❌ Пожалуйста, введите число.")
        return

    # Конвертируем кандидата
    candidate_dict = {
        "name": selected_candidate.name,
        "language": selected_candidate.language,
        "level": selected_candidate.level,
        "years": selected_candidate.years,
        "format": selected_candidate.format,
        "salary": selected_candidate.salary
    }

    print(f"\n🎯 ДИАГНОСТИКА КАНДИДАТА: {selected_candidate.name}")
    print("=" * 70)

    # Создаем экземпляр системы для диагностики
    fuzzy_system = FuzzyLogicSystem()
    
    # ЭТАП 1: ФАЗЗИФИКАЦИЯ
    print("\n1. 📊 ЭТАП ФАЗЗИФИКАЦИИ")
    print("-" * 50)
    
    fuzzy_values = fuzzy_system.fuzzify_candidate(candidate_dict)
    
    print("Входные данные кандидата:")
    print(f"  • Опыт: {candidate_dict['years']} лет")
    print(f"  • Навыки: {', '.join(candidate_dict['language'])} ({len(candidate_dict['language'])} языков)")
    print(f"  • Форматы: {', '.join(candidate_dict['format'])} ({len(candidate_dict['format'])} из 3)")
    print(f"  • Уровень: {candidate_dict['level']}")
    
    print("\nСтепени принадлежности к нечетким множествам:")
    
    # Уровень опыта
    print(f"\n  📈 УРОВЕНЬ ОПЫТА:")
    print(f"    Junior:  {fuzzy_values['level_junior']:.3f}")
    print(f"    Middle:  {fuzzy_values['level_middle']:.3f}")
    print(f"    Senior:  {fuzzy_values['level_senior']:.3f}")
    
    # Тип разработчика
    print(f"\n  💻 ТИП РАЗРАБОТЧИКА:")
    print(f"    Backend:   {fuzzy_values['backend_developer']:.3f}")
    print(f"    Frontend:  {fuzzy_values['frontend_developer']:.3f}")
    print(f"    Fullstack: {fuzzy_values['fullstack_developer']:.3f}")
    
    # Гибкость
    flexibility = len(candidate_dict['format']) / 3
    print(f"\n  🔄 ГИБКОСТЬ ({flexibility:.2f}):")
    print(f"    Low:    {fuzzy_values['flexibility_low']:.3f}")
    print(f"    Medium: {fuzzy_values['flexibility_medium']:.3f}")
    print(f"    High:   {fuzzy_values['flexibility_high']:.3f}")

    # ЭТАП 2: ЛОГИЧЕСКИЙ ВЫВОД
    print("\n\n2. 🧠 ЭТАП ЛОГИЧЕСКОГО ВЫВОДА")
    print("-" * 50)
    
    output_membership, activated_rules = fuzzy_system.apply_rules(fuzzy_values)
    
    print("АКТИВИРОВАННЫЕ ПРАВИЛА:")
    print("-" * 30)
    
    for i, rule in enumerate(activated_rules, 1):
        print(f"{i}. {rule['name']}")
        print(f"   Описание: {rule['description']}")
        print(f"   Сила правила: {rule['strength']:.3f}")
        print(f"   Вывод: {rule['conclusion']}")
        print()

    # Показываем выходные функции принадлежности
    print("\nВЫХОДНЫЕ ФУНКЦИИ ПРИНАДЛЕЖНОСТИ:")
    print("-" * 35)
    
    for set_name, membership_array in output_membership.items():
        max_membership = np.max(membership_array)
        if max_membership > 0:
            print(f"  {set_name}: макс. принадлежность = {max_membership:.3f}")

    # ЭТАП 3: ДЕФАЗЗИФИКАЦИЯ
    print("\n\n3. 📐 ЭТАП ДЕФАЗЗИФИКАЦИИ")
    print("-" * 50)
    
    # Показываем агрегированную функцию принадлежности
    aggregated_mf = np.zeros_like(fuzzy_system.output_universe)
    for mf in output_membership.values():
        aggregated_mf = np.maximum(aggregated_mf, mf)
    
    print("АГРЕГИРОВАННАЯ ФУНКЦИЯ ПРИНАДЛЕЖНОСТИ:")
    print("(объединение всех активированных выходных множеств)")
    
    # Находим центр тяжести вручную для демонстрации
    if np.sum(aggregated_mf) > 0:
        numerator = np.sum(fuzzy_system.output_universe * aggregated_mf)
        denominator = np.sum(aggregated_mf)
        centroid = numerator / denominator
        
        print(f"\nМетод центра тяжести:")
        print(f"  Числитель = Σ(x * μ(x)) = {numerator:.2f}")
        print(f"  Знаменатель = Σ(μ(x)) = {denominator:.2f}")
        print(f"  Центроид = {numerator:.2f} / {denominator:.2f} = {centroid:.2f}")
    else:
        centroid = 0
        print("  Нет активированных правил - центроид = 0")

    # ФИНАЛЬНЫЙ РЕЗУЛЬТАТ
    final_score = fuzzy_system.defuzzify(output_membership)
    
    print("\n" + "🎯" * 20)
    print(f"ФИНАЛЬНАЯ ОЦЕНКА: {final_score:.1f}%")
    print(f"РЕКОМЕНДАЦИЯ: {fuzzy_system._get_recommendation(final_score)}")
    print("🎯" * 20)

    # ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ
    print("\n📋 СВОДКА ПО КАНДИДАТУ:")
    print("-" * 25)
    
    # Определяем основные характеристики
    main_level = ""
    if fuzzy_values['level_junior'] > 0.5:
        main_level = "Junior"
    elif fuzzy_values['level_middle'] > 0.5:
        main_level = "Middle" 
    elif fuzzy_values['level_senior'] > 0.5:
        main_level = "Senior"
    
    main_type = ""
    if fuzzy_values['backend_developer'] > 0.5:
        main_type = "Backend"
    elif fuzzy_values['frontend_developer'] > 0.5:
        main_type = "Frontend"
    elif fuzzy_values['fullstack_developer'] > 0.5:
        main_type = "Fullstack"
    
    main_flexibility = ""
    if fuzzy_values['flexibility_low'] > 0.5:
        main_flexibility = "Низкая"
    elif fuzzy_values['flexibility_medium'] > 0.5:
        main_flexibility = "Средняя"
    elif fuzzy_values['flexibility_high'] > 0.5:
        main_flexibility = "Высокая"
    
    print(f"  • Основной уровень: {main_level}")
    print(f"  • Основной тип: {main_type}")
    print(f"  • Гибкость: {main_flexibility}")
    print(f"  • Активировано правил: {len(activated_rules)}")

if __name__ == "__main__":
    main()