import sys
sys.path.append("../Lab_1/")

from typing import List, Dict, Any
from ontology import OntologyManager, OntologyIndividual
from reasoner import OntologyReasoner
from config import LANGUAGES, EXPERIENCE_LEVELS, WORK_FORMATS


class OntologyInterface:
    """Интерактивный интерфейс для работы с онтологиями."""
    
    def __init__(self):
        self.om = OntologyManager()
        self.reasoner = OntologyReasoner(self.om)
        self._initialize_ontology()
    
    def _initialize_ontology(self):
        """Инициализирует онтологию при запуске."""
        if not self.om.load_ontology():
            print("Создание новой онтологии...")
            self.om.define_base_ontology()
            self._add_base_individuals()
            self.om.save_ontology()
    
    def _add_base_individuals(self):
        """Добавляет базовые экземпляры в онтологию."""
        # Добавляем языки программирования как экземпляры
        for lang in LANGUAGES:
            lang_individual = OntologyIndividual(
                name=lang.replace(" ", "_"),
                class_type="ProgrammingLanguage",
                properties={"rdfs:label": lang}
            )
            self.om.add_individual(lang_individual)
        
        # Добавляем уровни опыта
        for level in EXPERIENCE_LEVELS:
            level_individual = OntologyIndividual(
                name=level.replace(" ", "_"),
                class_type="ExperienceLevel", 
                properties={"rdfs:label": level}
            )
            self.om.add_individual(level_individual)
        
        # Добавляем форматы работы
        for fmt in WORK_FORMATS:
            fmt_individual = OntologyIndividual(
                name=fmt.replace(" ", "_"),
                class_type="WorkFormat",
                properties={"rdfs:label": fmt}
            )
            self.om.add_individual(fmt_individual)
    
    def convert_candidate_to_individual(self, candidate_data: Dict[str, Any]) -> OntologyIndividual:
        """Конвертирует данные кандидата в экземпляр онтологии."""
        properties = {
            "hasSkill": candidate_data.get("language", []),
            "hasExperienceLevel": candidate_data.get("level", ""),
            "prefersWorkFormat": candidate_data.get("format", []),
            "hasYearsOfExperience": candidate_data.get("years", 0),
            "expectedSalary": candidate_data.get("salary", 0)
        }
        
        return OntologyIndividual(
            name=candidate_data["name"].replace(" ", "_"),
            class_type="Candidate",
            properties=properties
        )
    
    def add_candidate_to_ontology(self, candidate_data: Dict[str, Any]) -> bool:
        """Добавляет кандидата в онтологию."""
        individual = self.convert_candidate_to_individual(candidate_data)
        success = self.om.add_individual(individual)
        
        if success:
            self.om.save_ontology()
            print(f"Кандидат {candidate_data['name']} добавлен в онтологию")
        
        return success
    
    def interactive_reasoning(self):
        """Интерактивный режим логического вывода."""
        print("\n--- Логический вывод на основе онтологии ---")
        
        # Получаем список кандидатов из онтологии
        candidates_query = """
        PREFIX rec: <http://example.org/it_recruitment#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?candidate ?name WHERE {
            ?candidate rdf:type rec:Candidate .
            ?candidate rdfs:label ?name .
        }
        """
        
        candidates = self.om.query_ontology(candidates_query)
        
        if not candidates:
            print("В онтологии нет кандидатов для анализа.")
            return
        
        print("\nДоступные кандидаты:")
        for i, candidate in enumerate(candidates, 1):
            candidate_name = candidate.get('name', 'Unknown')
            print(f"{i}. {candidate_name}")
        
        print(f"{len(candidates) + 1}. Все кандидаты")
        
        try:
            choice = int(input("\nВыберите кандидата для анализа: ").strip())
            
            if 1 <= choice <= len(candidates):
                candidate_name = list(candidates[choice - 1].values())[1]
                self._analyze_single_candidate(candidate_name)
            elif choice == len(candidates) + 1:
                self._analyze_all_candidates()
            else:
                print("Некорректный выбор.")
                
        except ValueError:
            print("Пожалуйста, введите число.")
    
    def create_sample_vacancies(self):
        """Создает тестовые вакансии для демонстрации."""
        print("Создание тестовых вакансий...")
        
        # Сначала создадим базовые индивиды, если их нет
        self._add_base_individuals()
        
        # Теперь создаем вакансии одним запросом
        vacancies_query = """
        PREFIX rec: <http://example.org/it_recruitment#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        INSERT DATA {
            rec:Python_Developer rdf:type rec:Vacancy ;
                rdfs:label "Python Developer" ;
                rec:requiresSkill rec:Python ;
                rec:requiresExperienceLevel rec:middle ;
                rec:minYearsOfExperience 2 ;
                rec:maxSalary 150000 ;
                rec:offersWorkFormat rec:удалённый .
                
            rec:Senior_Java_Engineer rdf:type rec:Vacancy ;
                rdfs:label "Senior Java Engineer" ;
                rec:requiresSkill rec:Java ;
                rec:requiresExperienceLevel rec:senior ;
                rec:minYearsOfExperience 5 ;
                rec:maxSalary 250000 ;
                rec:offersWorkFormat rec:гибридный .
                
            rec:Fullstack_Developer rdf:type rec:Vacancy ;
                rdfs:label "Fullstack Developer" ;
                rec:requiresSkill rec:JavaScript ;
                rec:requiresSkill rec:Python ;
                rec:requiresExperienceLevel rec:middle ;
                rec:minYearsOfExperience 3 ;
                rec:maxSalary 180000 ;
                rec:offersWorkFormat rec:удалённый .
        }
        """
        
        try:
            success = self.om.update_ontology(vacancies_query)
            if success:
                self.om.save_ontology()
                print("Тестовые вакансии успешно созданы!")
            else:
                print("Ошибка при создании вакансий")
        except Exception as e:
            print(f"Ошибка при создании вакансий: {e}")

    def _analyze_single_candidate(self, candidate_name: str):
        """Анализирует одного кандидата."""
        print(f"\n--- Анализ кандидата: {candidate_name} ---")
        
        inferences = self.reasoner.reason_about_candidate(candidate_name)
        
        if inferences and inferences[0].get("type") == "error":
            print(inferences[0]["message"])
            return
        
        print("\nРезультаты логического вывода:")
        for i, inference in enumerate(inferences, 1):
            print(f"{i}. {inference['message']}")
            
            # Дополнительная информация для определенных типов выводов
            if inference["type"] == "vacancy_match":
                print(f"   Совпадение: {inference['match_score']}%")
        
        # Вывод сводки
        summary = self.reasoner.get_inference_summary()
        print(f"\nСводка: найдено {summary['total_inferences']} выводов, "
              f"{summary['vacancy_matches']} совпадений с вакансиями")
    
    def _analyze_all_candidates(self):
        """Анализирует всех кандидатов."""
        print("\n--- Анализ всех кандидатов ---")
        
        candidates_query = """
        PREFIX rec: <http://example.org/it_recruitment#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?name WHERE {
            ?candidate rdf:type rec:Candidate .
            ?candidate rdfs:label ?name .
        }
        """
        
        candidates = self.om.query_ontology(candidates_query)
        
        if not candidates:
            print("Кандидаты не найдены.")
            return
        
        all_inferences = []
        for candidate in candidates:
            candidate_name = candidate.get('name')
            print(f"\nАнализ {candidate_name}...")
            
            inferences = self.reasoner.reason_about_candidate(candidate_name)
            all_inferences.extend(inferences)
            
            # Показываем только основные выводы для каждого кандидата
            vacancy_matches = [inf for inf in inferences if inf["type"] == "vacancy_match"]
            if vacancy_matches:
                best_match = max(vacancy_matches, key=lambda x: x["match_score"])
                print(f"  Лучшая вакансия: {best_match['vacancy']} ({best_match['match_score']}%)")
        
        print(f"\nОбщий анализ завершен. Обработано {len(candidates)} кандидатов.")
    
    def show_ontology_statistics(self):
        """Показывает статистику онтологии."""
        print("\n--- Статистика онтологии ---")
        
        try:
            # 1. Подсчет классов
            classes_query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            
            SELECT (COUNT(DISTINCT ?class) as ?count) WHERE {
                ?class rdf:type owl:Class .
            }
            """
            
            classes_result = self.om.query_ontology(classes_query)
            if classes_result and 'count' in classes_result[0]:
                print(f"Количество классов: {classes_result[0]['count']}")
            else:
                print("Количество классов: 0")
            
            # 2. Подсчет экземпляров по типам
            individuals_query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            SELECT ?type (COUNT(DISTINCT ?individual) as ?count) WHERE {
                ?individual rdf:type ?type .
                FILTER (!isBlank(?individual))
            } GROUP BY ?type
            ORDER BY ?type
            """
            
            individuals_result = self.om.query_ontology(individuals_query)
            
            if individuals_result:
                print("\nЭкземпляры по типам:")
                # Словарь для красивого отображения имен классов
                class_names = {
                    "http://example.org/it_recruitment#Candidate": "Candidate",
                    "http://example.org/it_recruitment#Vacancy": "Vacancy", 
                    "http://example.org/it_recruitment#ProgrammingLanguage": "ProgrammingLanguage",
                    "http://example.org/it_recruitment#ExperienceLevel": "ExperienceLevel",
                    "http://example.org/it_recruitment#WorkFormat": "WorkFormat",
                    "http://example.org/it_recruitment#Skill": "Skill",
                    "http://example.org/it_recruitment#Company": "Company"
                }
                
                for result in individuals_result:
                    type_uri = result.get('type', '')
                    count = result.get('count', '0')
                    
                    # Преобразуем URI в читаемое имя
                    short_name = class_names.get(type_uri, type_uri.split('#')[-1] if '#' in type_uri else type_uri)
                    print(f"  {short_name}: {count}")
            else:
                print("\nЭкземпляры по типам: не найдено")
            
            # 3. Подсчет кандидатов (отдельный запрос для надежности)
            candidates_query = """
            PREFIX rec: <http://example.org/it_recruitment#>
            
            SELECT (COUNT(DISTINCT ?candidate) as ?count) WHERE {
                ?candidate rdf:type rec:Candidate .
            }
            """
            
            candidates_result = self.om.query_ontology(candidates_query)
            if candidates_result and 'count' in candidates_result[0]:
                print(f"Количество кандидатов: {candidates_result[0]['count']}")
            else:
                print("Количество кандидатов: 0")
                
            # 4. Подсчет вакансий
            vacancies_query = """
            PREFIX rec: <http://example.org/it_recruitment#>
            
            SELECT (COUNT(DISTINCT ?vacancy) as ?count) WHERE {
                ?vacancy rdf:type rec:Vacancy .
            }
            """
            
            vacancies_result = self.om.query_ontology(vacancies_query)
            if vacancies_result and 'count' in vacancies_result[0]:
                print(f"Количество вакансий: {vacancies_result[0]['count']}")
            else:
                print("Количество вакансий: 0")
                
            # 5. Общее количество троек
            total_query = """
            SELECT (COUNT(*) as ?count) WHERE {
                ?s ?p ?o .
            }
            """
            
            total_result = self.om.query_ontology(total_query)
            if total_result and 'count' in total_result[0]:
                print(f"Всего троек в онтологии: {total_result[0]['count']}")
                    
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            import traceback
            traceback.print_exc()
    
    def run_interactive_mode(self):
        """Запускает интерактивный режим работы с онтологией."""
        while True:
            print("\n=== Онтологическая экспертная система ===")
            print("1. Логический вывод для кандидата")
            print("2. Показать статистику онтологии")
            print("3. Выполнить SPARQL запрос")
            print("4. Вернуться в главное меню")
            
            choice = input("Выберите действие (1-4): ").strip()
            
            if choice == "1":
                self.interactive_reasoning()
            elif choice == "2":
                self.show_ontology_statistics()
            elif choice == "3":
                self._run_sparql_query()
            elif choice == "4":
                break
            else:
                print("Некорректный выбор. Пожалуйста, введите число от 1 до 4.")
    
    def _run_sparql_query(self):
        """Выполняет пользовательский SPARQL запрос с поддержкой многострочного ввода."""
        print("\n--- Выполнение SPARQL запроса ---")
        print("Поддерживаются SELECT (поиск) и INSERT/UPDATE (изменение) запросы")
        print("Вводите запрос построчно. Для выполнения введите 'END' на отдельной строке.")
        print("Для выхода введите 'exit':")
        
        query_lines = []
        
        while True:
            try:
                line = input("SPARQL> " if not query_lines else "...     ").strip()
                
                if line.lower() == 'exit':
                    return
                elif line.lower() == 'end':
                    # Собираем полный запрос
                    full_query = '\n'.join(query_lines)
                    if full_query.strip():
                        self._execute_sparql_query(full_query)
                    query_lines = []  # Сбрасываем для следующего запроса
                    print()  # Пустая строка для разделения
                else:
                    query_lines.append(line)
                    
            except EOFError:
                # Обработка Ctrl+D / Ctrl+Z
                if query_lines:
                    full_query = '\n'.join(query_lines)
                    self._execute_sparql_query(full_query)
                break
            except KeyboardInterrupt:
                print("\nЗапрос отменен")
                query_lines = []
                print()
    def _execute_sparql_query(self, query: str):
        """Выполняет собранный SPARQL запрос."""
        try:
            # Очищаем запрос от лишних пробелов и переносов
            query = query.strip()
            
            if not query:
                print("Пустой запрос")
                return
            
            def contains_word(input_string, word_list):
                # Приводим строку к нижнему регистру
                input_string_lower = input_string.lower()
                
                # Проверяем наличие каждого слова из списка в строке
                for word in word_list:
                    if word.lower() in input_string_lower:
                        return True
                        
                return False

            # Определяем тип запроса по первому слову
            first_word_one = contains_word(query, ['SELECT', 'ASK', 'CONSTRUCT', 'DESCRIBE'])
            first_word_two = contains_word(query, ['INSERT', 'DELETE', 'UPDATE', 'WITH', 'CLEAR', 'DROP', 'CREATE', 'LOAD'])
        
            
            if first_word_one:
                # Запросы чтения
                results = self.om.query_ontology(query)
                
                if results:
                    print(f"Найдено результатов: {len(results)}")
                    for i, result in enumerate(results, 1):
                        # Форматируем вывод для лучшей читаемости
                        formatted_result = {}
                        for key, value in result.items():
                            # Укорачиваем URI для читаемости
                            if 'it_recruitment#' in value:
                                formatted_value = value.split('#')[-1]
                            else:
                                formatted_value = value
                            formatted_result[key] = formatted_value
                        print(f"{i}. {formatted_result}")
                else:
                    print("Результаты не найдены.")
                    
            elif first_word_two:
                # Запросы изменения
                success = self.om.update_ontology(query)
                if success:
                    self.om.save_ontology()
                    print("✓ Запрос успешно выполнен и онтология сохранена")
                else:
                    print("✗ Ошибка выполнения запроса")
                    
            else:
                print("Поддерживаются: SELECT, INSERT, DELETE, UPDATE, ASK, CONSTRUCT, DESCRIBE")
                
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            import traceback
            traceback.print_exc()  # Для отладки