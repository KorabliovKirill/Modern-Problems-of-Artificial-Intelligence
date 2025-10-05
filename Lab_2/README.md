# Лабораторная работа №2

Суть этой лабораторной работы заключается в разработке онтологий и использование логического вывода на их основе

## Сборка проекта

1) Создать виртуальное окружение

```
python -m venv .venv
```

2) Активировать виртуальное окружение

```
.\.venv\Scripts\activate
```

> Примечание: для линукс активация виртуального окружения будет выглядеть так `source .venv/bin/activate`

3) Установить зависимости

```
pip install -r requirements.txt
```

4) Запуск проекта

```
python main.py
```

## Работа с данными

В корне проекта необходимо создать директорию `data` с файлом внутри `candidates.csv`

Его нужно заполнить данными в формате:
```
имя,язык программирования,уровень,опыт работы,формат работы,ожидаемая зарплата
Иванов Иван,Python,junior,1,удалённый,40000
Петров Пётр,Java,middle,3,гибридный,70000
```

## Особенности реализации

Программу можно запускать с 3 флагами: 

- `--relax` - мягкий режим
- `--all` - строгий режим
- `--why` - режим диагностики

> --why можно запускать и с другим режимом

Мягкий режим включает поиск по подстрокам: достаточно, чтобы выбранный пользователем вариант встречался как часть значения. Это расширяет охват кандидатов. 

В строгом режиме система требует, чтобы каждый выбранный пользователем пункт присутствовал у кандидата. Если хотя бы один не совпадает – вариант отбрасывается.

При запуске с флагом `--why` система дополнительно выводит списокпервых отсеянных объектов и причину, по которой они не прошлифильтрацию.

## Пример использования

### Запуск программы

```
python main.py
```

**Вывод программы:**

```
Создание новой онтологии...
Онтология сохранена в: data/ontology.ttl  
Экспертная система подбора кандидатов в IT

--- Меню ---
1. Добавить нового кандидата
2. Запустить подбор кандидатов
3. Онтологический анализ
4. Создать тестовые данные
5. Выход
Выберите действие (1-5):
```
### Добавление кандидатов в систему

Выбираем пункт **1** и добавляем нескольких кандидатов:

**Кандидат 1:**
```
--- Добавление нового кандидата ---
Введите имя кандидата: Иван Петров
Доступные языки: Python, Java, C++, JavaScript, Go, Rust, Prolog, C#, Ruby, TypeScript
Введите языки через запятую: Python, JavaScript
Доступные уровни: junior, middle, senior, lead
Введите уровень (junior/middle/senior/lead): middle
Введите стаж в годах: 3
Доступные форматы: удалённый, очно, гибридный
Введите форматы через запятую: удалённый, гибридный
Введите ожидаемую зарплату: 120000
Кандидат 'Иван Петров' успешно добавлен в базу знаний.
Кандидат Иван_Петров добавлен в онтологию
```

**Кандидат 2:**
```
--- Добавление нового кандидата ---
Введите имя кандидата: Анна Сидорова
Доступные языки: Python, Java, C++, JavaScript, Go, Rust, Prolog, C#, Ruby, TypeScript
Введите языки через запятую: Java, C++
Доступные уровни: junior, middle, senior, lead
Введите уровень (junior/middle/senior/lead): senior
Введите стаж в годах: 7
Доступные форматы: удалённый, очно, гибридный
Введите форматы через запятую: очно, гибридный
Введите ожидаемую зарплату: 200000
Кандидат 'Анна Сидорова' успешно добавлен в базу знаний.
Онтология сохранена в: data/ontology.ttl
Кандидат Анна Сидорова добавлен в онтологию
```

**Кандидат 3:**

```
--- Добавление нового кандидата ---
Введите имя кандидата: Алексей Козлов
Доступные языки: Python, Java, C++, JavaScript, Go, Rust, Prolog, C#, Ruby, TypeScript
Введите языки через запятую: Python, Go, Rust
Доступные уровни: junior, middle, senior, lead
Введите уровень (junior/middle/senior/lead): junior
Введите стаж в годах: 1
Доступные форматы: удалённый, очно, гибридный
Введите форматы через запятую: удалённый
Введите ожидаемую зарплату: 80000
Кандидат 'Алексей Козлов' успешно добавлен в базу знаний.
Онтология сохранена в: data/ontology.ttl
Кандидат Алексей Козлов добавлен в онтологию
```

### Добавление вакансий в онтологию

Давайте добавим несколько вакансий через SPARQL запросы. Выбираем пункт **3** → **3**:

```
SPARQL> PREFIX rec: <http://example.org/it_recruitment#>
...     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
...
...     INSERT DATA {
...       rec:Python_Developer rdf:type rec:Vacancy ;
...         rdfs:label "Python Developer" ;
...         rec:requiresSkill rec:Python ;
...         rec:requiresExperienceLevel rec:middle ;
...         rec:minYearsOfExperience 2 ;
...         rec:maxSalary 150000 ;
...         rec:offersWorkFormat rec:удалённый .
...     }
...     END 
Онтология сохранена в: data/ontology.ttl
✓ Запрос успешно выполнен и онтология сохранена
```

**Добавим еще вакансии:**
```
SPARQL> PREFIX rec: <http://example.org/it_recruitment#>
...     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
...
...     INSERT DATA {
...       rec:Senior_Java_Engineer rdf:type rec:Vacancy ;
...         rdfs:label "Senior Java Engineer" ;
...         rec:requiresSkill rec:Java ;
...         rec:requiresExperienceLevel rec:senior ;
...         rec:minYearsOfExperience 5 ;
...         rec:maxSalary 250000 ;
...         rec:offersWorkFormat rec:гибридный .
...
...       rec:Fullstack_Developer rdf:type rec:Vacancy ;
...         rdfs:label "Fullstack Developer" ;
...         rec:requiresSkill rec:JavaScript ;
...         rec:requiresSkill rec:Python ;
...         rec:requiresExperienceLevel rec:middle ;
...         rec:minYearsOfExperience 3 ;
...         rec:maxSalary 180000 ;
...         rec:offersWorkFormat rec:удалённый .
...     }
...     END 
Онтология сохранена в: data/ontology.ttl
✓ Запрос успешно выполнен и онтология сохранена
```
### Просмотр статистики онтологии
Выбираем пункт **3** → **2**:
```
--- Статистика онтологии ---
Количество классов: 7

Экземпляры по типам:
  Candidate: 3
  ExperienceLevel: 4
  ProgrammingLanguage: 10
  Vacancy: 3
  WorkFormat: 3
  Class: 7
  DatatypeProperty: 4
  ObjectProperty: 8
Количество кандидатов: 3
```

### Логический вывод для конкретного кандидата

Выбираем пункт **3** → **1**:

```
--- Логический вывод на основе онтологии ---

Доступные кандидаты:
1. Иван_Петров
2. Анна_Сидорова
3. Алексей_Козлов
4. Все кандидаты

Выберите кандидата для анализа: 1

--- Анализ кандидата: Иван_Петров ---

Результаты логического вывода:
1. Кандидат обладает навыками: Python, JavaScript
2. Кандидат обладает востребованными навыками: Python, JavaScript
3. Кандидат подходит для вакансии 'Python Developer' (совпадение: 100%)
   Совпадение: 100%
4. Кандидат подходит для вакансии 'Fullstack Developer' (совпадение: 100%)
   Совпадение: 100%
5. Кандидат подходит для вакансии 'Fullstack Developer' (совпадение: 100%)
   Совпадение: 100%
6. Кандидат подходит для вакансии 'Senior Java Engineer' (совпадение: 20%)
   Совпадение: 20%
7. Опыт работы: 3 лет, уровень: http://example.org/it_recruitment#middle

Сводка: найдено 7 выводов, 4 совпадений с вакансиями
```

### Анализ всех кандидатов

Выбираем пункт **3** → **1** → **4**:
```
--- Анализ всех кандидатов ---

Анализ Иван_Петров...
  Лучшая вакансия: Python Developer (100%)

Анализ Анна_Сидорова...
  Лучшая вакансия: Senior Java Engineer (100%)

Анализ Алексей_Козлов...
  Лучшая вакансия: Python Developer (50%)

Общий анализ завершен. Обработано 3 кандидатов.
```

## Построенная онтология

### Визуальное представление онтологии:

```
Классы:
├── Candidate
├── Vacancy  
├── Skill
│   └── ProgrammingLanguage
├── ExperienceLevel
├── WorkFormat
└── Company

Свойства:
Candidate:
  ├── hasSkill → ProgrammingLanguage
  ├── hasExperienceLevel → ExperienceLevel
  ├── prefersWorkFormat → WorkFormat
  ├── hasYearsOfExperience → xsd:integer
  ├── expectedSalary → xsd:integer
  └── appliedFor → Vacancy

Vacancy:
  ├── requiresSkill → ProgrammingLanguage
  ├── requiresExperienceLevel → ExperienceLevel
  ├── offersWorkFormat → WorkFormat
  ├── minYearsOfExperience → xsd:integer
  ├── maxSalary → xsd:integer
  └── offeredBy → Company
```

## Логический вывод Reasoner в действии

### Примеры выводов, которые делает система:
**1. Анализ навыков:**

```python
#Reasoner определяет, что Иван Петров обладает востребованными навыками
"Кандидат обладает востребованными навыками: Python, JavaScript"
```

**2. Сопоставление с вакансиями:**
```python
# Для Python Developer:
- Навык Python: ✓ (30 баллов)
- Уровень middle: ✓ (30 баллов)  
- Опыт 3 ≥ 2: ✓ (20 баллов)
- Зарплата 120000 ≤ 150000: ✓ (20 баллов)
Итого: 80% совпадение
```
**3. Анализ уровня опыта:**
```python
# Для Алексея Козлов (1 год опыта):
"Опыт работы: 1 лет, уровень: junior"
"Рекомендуется рассматривать junior позиции"
```

**4. Обнаружение несоответствий:**
```python
# Почему Анна Сидорова не полностью подходит для Fullstack Developer:
- Не хватает навыка JavaScript: -30 баллов
- Итоговое совпадение: 50%
```

## Что такое SPARQL?
**SPARQL** (SPARQL Protocol and RDF Query Language) - это язык запросов для RDF данных (которые лежат в основе онтологий). Это аналог SQL для реляционных баз данных, но для семантических данных.

## Базовая структура SPARQL запроса

### 1. SELECT запрос (получение данных)
```sparql
PREFIX rec: <http://example.org/it_recruitment#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?candidate ?name 
WHERE {
    ?candidate rdf:type rec:Candidate .
    ?candidate rdfs:label ?name .
}
```

**Разбор:**
- `PREFIX` - определяет сокращения для URI
- `SELECT` - какие переменные мы хотим получить
- `WHERE` - условия (паттерны) для поиска
- `?variable` - переменные, которые будут заполняться

### 2. INSERT запрос (добавление данных)

```sparql
PREFIX rec: <http://example.org/it_recruitment#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

INSERT DATA {
    rec:Python_Developer rdf:type rec:Vacancy ;
        rdfs:label "Python Developer" ;
        rec:requiresSkill rec:Python ;
        rec:requiresExperienceLevel rec:middle ;
        rec:minYearsOfExperience 2 ;
        rec:maxSalary 150000 .
}
```

**Разбор:**
- `INSERT DATA` - добавляет конкретные данные
- `;` - разделяет свойства одного ресурса
- `rec:Python_Developer` - URI нового ресурса
- `rdf:type` - указывает класс ресурса
- `rdfs:label` - человеко-читаемое имя