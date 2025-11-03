# fuzzy_main.py
import sys
import os

# Добавляем пути для импорта существующих модулей
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "Lab_1"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "Lab_2"))

from candidate_manager import load_candidates, save_candidate, Candidate
from expert_system import get_user_profile
from config import LANGUAGES, EXPERIENCE_LEVELS, WORK_FORMATS
from fuzzy_system import FuzzyExpertSystem, FuzzyLogicSystem

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
    print("7. Выход")
    print("-"*50)
    
    choice = input("Выберите действие (1-7): ").strip()
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
        if score >= 80:
            indicator = "🟢"
        elif score >= 60:
            indicator = "🟡" 
        elif score >= 40:
            indicator = "🟠"
        else:
            indicator = "🔴"
            
        print(f"{indicator} {i}. {result['candidate_name']} - {score:.1f}%")
        print(f"   📋 {result['recommendation']}")
        
        # Показываем детали для топ-кандидатов
        if i <= 5:
            fuzzy_vals = result.get('fuzzy_values', {})
            print(f"   📊 Детали: ", end="")
            details = []
            if fuzzy_vals.get('experience_middle', 0) > 0.5 or fuzzy_vals.get('experience_senior', 0) > 0.5:
                exp_detail = f"опыт:{max(fuzzy_vals.get('experience_middle',0), fuzzy_vals.get('experience_senior',0)):.2f}"
                details.append(exp_detail)
            if fuzzy_vals.get('skills_moderate', 0) > 0.5 or fuzzy_vals.get('skills_many', 0) > 0.5:
                skills_detail = f"навыки:{max(fuzzy_vals.get('skills_moderate',0), fuzzy_vals.get('skills_many',0)):.2f}"
                details.append(skills_detail)
            if fuzzy_vals.get('salary_medium', 0) > 0.5:
                salary_detail = f"зарплата:{fuzzy_vals.get('salary_medium',0):.2f}"
                details.append(salary_detail)
            if fuzzy_vals.get('flexibility_high', 0) > 0.5:
                flex_detail = f"гибкость:{fuzzy_vals.get('flexibility_high',0):.2f}"
                details.append(flex_detail)
                
            print(", ".join(details) if details else "недостаточно данных")
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

    print("\nВведите требования вакансии для анализа:")
    profile = get_user_profile()

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
    result = fuzzy_system.evaluate_candidate(candidate_dict, profile)
    
    print(f"\n🎯 ДЕТАЛЬНЫЙ АНАЛИЗ: {result['candidate_name']}")
    print("="*60)
    print(f"Финальная оценка: {result['final_score']:.1f}%")
    print(f"Рекомендация: {result['recommendation']}")
    print("\n📊 СТЕПЕНИ ПРИНАДЛЕЖНОСТИ:")
    
    fuzzy_vals = result['fuzzy_values']
    
    # Опыт
    print(f"  Опыт ({candidate_dict['years']} лет):")
    print(f"    Junior: {fuzzy_vals.get('experience_junior', 0):.3f}")
    print(f"    Middle: {fuzzy_vals.get('experience_middle', 0):.3f}")
    print(f"    Senior: {fuzzy_vals.get('experience_senior', 0):.3f}")
    
    # Навыки
    skills_count = len(candidate_dict['language'])
    print(f"  Навыки ({skills_count}): {', '.join(candidate_dict['language'])}")
    print(f"    Few: {fuzzy_vals.get('skills_few', 0):.3f}")
    print(f"    Moderate: {fuzzy_vals.get('skills_moderate', 0):.3f}")
    print(f"    Many: {fuzzy_vals.get('skills_many', 0):.3f}")
    
    # Зарплата
    print(f"  Зарплата ({candidate_dict['salary']} руб):")
    print(f"    Low: {fuzzy_vals.get('salary_low', 0):.3f}")
    print(f"    Medium: {fuzzy_vals.get('salary_medium', 0):.3f}")
    print(f"    High: {fuzzy_vals.get('salary_high', 0):.3f}")
    
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

    print("Введите требования вакансии для сравнения:")
    profile = get_user_profile()

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
    results = fuzzy_expert.fuzzy_recommend(candidate_dicts, profile)
    
    print(f"\n📈 СРАВНЕНИЕ {len(results)} КАНДИДАТОВ:")
    print("="*80)
    
    # Группируем по уровню оценки
    excellent = [r for r in results if r['final_score'] >= 80]
    good = [r for r in results if 60 <= r['final_score'] < 80]
    fair = [r for r in results if 40 <= r['final_score'] < 60]
    poor = [r for r in results if r['final_score'] < 40]
    
    if excellent:
        print("\n🏆 ОТЛИЧНОЕ СООТВЕТСТВИЕ (80-100%):")
        for result in excellent:
            print(f"  ✅ {result['candidate_name']} - {result['final_score']:.1f}%")
    
    if good:
        print("\n👍 ХОРОШЕЕ СООТВЕТСТВИЕ (60-79%):")
        for result in good:
            print(f"  ⚡ {result['candidate_name']} - {result['final_score']:.1f}%")
    
    if fair:
        print("\n⚠️  УДОВЛЕТВОРИТЕЛЬНОЕ СООТВЕТСТВИЕ (40-59%):")
        for result in fair:
            print(f"  📊 {result['candidate_name']} - {result['final_score']:.1f}%")
    
    if poor:
        print("\n❌ НИЗКОЕ СООТВЕТСТВИЕ (0-39%):")
        for result in poor:
            print(f"  🔴 {result['candidate_name']} - {result['final_score']:.1f}%")
    
    # Статистика
    print(f"\n📊 СТАТИСТИКА:")
    print(f"  Всего кандидатов: {len(results)}")
    print(f"  Отличных: {len(excellent)}")
    print(f"  Хороших: {len(good)}")
    print(f"  Удовлетворительных: {len(fair)}")
    print(f"  Низких: {len(poor)}")

def test_fuzzy_system():
    """Тестирование нечеткой системы на примерах"""
    print("\n--- Тестирование нечеткой системы ---")
    
    # Тестовые данные
    test_candidates = [
        {
            "name": "Тест: Идеальный Middle Python",
            "language": ["Python", "JavaScript"],
            "level": "middle",
            "years": 4,
            "format": ["удалённый", "гибридный"],
            "salary": 120000
        },
        {
            "name": "Тест: Senior Java с высокой зарплатой",
            "language": ["Java", "CPP"],
            "level": "senior",
            "years": 8,
            "format": ["очно"],
            "salary": 280000
        },
        {
            "name": "Тест: Junior с потенциалом",
            "language": ["Python"],
            "level": "junior", 
            "years": 1,
            "format": ["удалённый"],
            "salary": 60000
        }
    ]
    
    test_vacancy = {
        "languages": ["Python", "JavaScript"],
        "level": "middle",
        "years_range": (2, 6),
        "formats": ["удалённый", "гибридный"],
        "salary_range": (80000, 180000)
    }
    
    print("Тестовая вакансия: Middle Python Developer")
    print(f"  Языки: {test_vacancy['languages']}")
    print(f"  Опыт: {test_vacancy['years_range'][0]}-{test_vacancy['years_range'][1]} лет")
    print(f"  Зарплата: {test_vacancy['salary_range'][0]}-{test_vacancy['salary_range'][1]} руб.")
    print()
    
    fuzzy_expert = FuzzyExpertSystem()
    results = fuzzy_expert.fuzzy_recommend(test_candidates, test_vacancy)
    
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("="*60)
    
    for result in results:
        score = result['final_score']
        print(f"🎯 {result['candidate_name']}")
        print(f"   Оценка: {score:.1f}% - {result['recommendation']}")
        
        # Анализ причин оценки
        fv = result['fuzzy_values']
        print(f"   Анализ: ", end="")
        
        strengths = []
        if fv.get('experience_middle', 0) > 0.7:
            strengths.append("опыт")
        if fv.get('skills_moderate', 0) > 0.7:
            strengths.append("навыки")
        if fv.get('salary_medium', 0) > 0.7:
            strengths.append("зарплата")
        if fv.get('flexibility_high', 0) > 0.7:
            strengths.append("гибкость")
            
        if strengths:
            print(f"сильные стороны: {', '.join(strengths)}")
        else:
            print("нет явных сильных сторон")
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
            elif choice == "7":
                print("\n👋 До свидания! Спасибо за использование экспертной системы.")
                break
            else:
                print("❌ Некорректный выбор. Пожалуйста, введите число от 1 до 7.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Программа прервана пользователем. До свидания!")
            break
        except Exception as e:
            print(f"\n❌ Произошла ошибка: {e}")
            print("Пожалуйста, попробуйте еще раз.")

if __name__ == "__main__":
    main()