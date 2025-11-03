# fuzzy_system.py
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import math

@dataclass
class FuzzySet:
    """Нечеткое множество с функцией принадлежности"""
    name: str
    values: List[float]
    membership_function: str  # 'triangular', 'trapezoidal', 'gaussian'

class FuzzyLogicSystem:
    """Система нечеткой логики для подбора кандидатов"""
    
    def __init__(self):
        self.fuzzy_sets = self._define_fuzzy_sets()
        self.rules = self._define_rules()
    
    def _define_fuzzy_sets(self) -> Dict[str, FuzzySet]:
        """Определяет нечеткие множества с оптимальными функциями"""
        return {
            # Треугольные - для параметров с оптимальной точкой
            "experience_junior": FuzzySet("experience_junior", [0, 1, 3], "triangular"),
            "experience_middle": FuzzySet("experience_middle", [2, 4, 6], "triangular"),
            "experience_senior": FuzzySet("experience_senior", [5, 8, 15], "triangular"),
            
            "salary_low": FuzzySet("salary_low", [0, 50000, 100000], "triangular"),
            "salary_medium": FuzzySet("salary_medium", [80000, 150000, 220000], "triangular"),
            "salary_high": FuzzySet("salary_high", [180000, 250000, 400000], "triangular"),
            
            "skills_few": FuzzySet("skills_few", [0, 1, 3], "triangular"),
            "skills_moderate": FuzzySet("skills_moderate", [2, 4, 6], "triangular"),
            "skills_many": FuzzySet("skills_many", [5, 8, 15], "triangular"),
            
            # Трапецевидные - для параметров с диапазоном хороших значений
            "match_poor": FuzzySet("match_poor", [0, 0, 25, 45], "trapezoidal"),
            "match_fair": FuzzySet("match_fair", [35, 50, 60, 75], "trapezoidal"),
            "match_good": FuzzySet("match_good", [65, 75, 85, 95], "trapezoidal"),
            "match_excellent": FuzzySet("match_excellent", [85, 95, 100, 100], "trapezoidal"),
            
            "flexibility_low": FuzzySet("flexibility_low", [0, 0, 0.3, 0.5], "trapezoidal"),
            "flexibility_medium": FuzzySet("flexibility_medium", [0.4, 0.6, 0.8, 0.9], "trapezoidal"),
            "flexibility_high": FuzzySet("flexibility_high", [0.8, 0.9, 1.0, 1.0], "trapezoidal"),
            
            # Гауссовы - для плавных изменений
            "demand_low": FuzzySet("demand_low", [0.2, 0.15], "gaussian"),
            "demand_medium": FuzzySet("demand_medium", [0.5, 0.15], "gaussian"),
            "demand_high": FuzzySet("demand_high", [0.8, 0.15], "gaussian"),
        }
    
    def _define_rules(self) -> List[Dict[str, Any]]:
        """Определяет правила нечеткой логики на основе онтологии"""
        return [
            # Правила для Python разработчиков
            {
                "name": "python_junior_rule",
                "conditions": [
                    ("hasSkill", "Python", 1.0),
                    ("experience", "experience_junior", 0.7),
                    ("salary", "salary_low", 0.8)
                ],
                "conclusion": ("match_score", "match_fair"),
                "weight": 0.8
            },
            {
                "name": "python_senior_rule", 
                "conditions": [
                    ("hasSkill", "Python", 1.0),
                    ("experience", "experience_senior", 0.9),
                    ("skills", "skills_many", 0.8),
                    ("salary", "salary_high", 0.7)
                ],
                "conclusion": ("match_score", "match_excellent"),
                "weight": 0.9
            },
            
            # Правила для Fullstack разработчиков
            {
                "name": "fullstack_rule",
                "conditions": [
                    ("hasSkills", ["JavaScript", "Python"], 0.8),
                    ("experience", "experience_middle", 0.8),
                    ("flexibility", "flexibility_high", 0.7)
                ],
                "conclusion": ("match_score", "match_good"),
                "weight": 0.85
            },
            
            # Правила для Enterprise Java
            {
                "name": "enterprise_java_rule",
                "conditions": [
                    ("hasSkills", ["Java", "CPP"], 0.9),
                    ("experience", "experience_senior", 0.9),
                    ("skills", "skills_many", 0.8)
                ],
                "conclusion": ("match_score", "match_excellent"),
                "weight": 0.95
            },
            
            # Правила для высокоценных кандидатов
            {
                "name": "high_value_candidate_rule",
                "conditions": [
                    ("experience", "experience_senior", 0.9),
                    ("skills", "skills_many", 0.9),
                    ("demand", "demand_high", 0.8),
                    ("salary", "salary_medium", 0.7)
                ],
                "conclusion": ("match_score", "match_excellent"),
                "weight": 0.9
            },
            
            # Правила с учетом мягких навыков
            {
                "name": "soft_skills_rule",
                "conditions": [
                    ("hasSoftSkill", ["Коммуникабельный", "Ответственный"], 0.8),
                    ("flexibility", "flexibility_high", 0.7)
                ],
                "conclusion": ("match_adjustment", "match_good"),
                "weight": 0.6
            },
            
            # Универсальные правила
            {
                "name": "good_experience_fit",
                "conditions": [
                    ("experience", "experience_middle", 0.8),
                    ("salary", "salary_medium", 0.7)
                ],
                "conclusion": ("match_score", "match_good"),
                "weight": 0.7
            },
            {
                "name": "overqualified_rule",
                "conditions": [
                    ("experience", "experience_senior", 0.9),
                    ("salary", "salary_high", 0.9)
                ],
                "conclusion": ("match_score", "match_fair"),
                "weight": 0.6
            }
        ]
    
    def triangular_mf(self, x: float, params: List[float]) -> float:
        """Улучшенная треугольная функция с проверкой параметров"""
        if len(params) != 3:
            return 0.0
            
        a, b, c = params
        
        # Проверка на вырожденные случаи
        if a == b == c:
            return 1.0 if x == a else 0.0
        if b == c:
            return self._trapezoidal_mf_improved(x, [a, b, b, c])
        if a == b:
            return self._trapezoidal_mf_improved(x, [a, a, c, c])
        
        if x <= a or x >= c:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a)
        elif b < x < c:
            return (c - x) / (c - b)
        else:
            return 1.0 if x == b else 0.0
    
    def trapezoidal_mf(self, x: float, params: List[float]) -> float:
        """Улучшенная трапецевидная функция"""
        if len(params) != 4:
            return 0.0
            
        a, b, c, d = params
        
        # Проверка вырожденных случаев
        if a == b == c == d:
            return 1.0 if x == a else 0.0
        if b == c:
            return self._triangular_mf_improved(x, [a, b, d])
        
        if x <= a:
            return 0.0
        elif a < x < b:
            return (x - a) / (b - a)
        elif b <= x <= c:
            return 1.0
        elif c < x < d:
            return (d - x) / (d - c)
        else:
            return 0.0
    
    def gaussian_mf(self, x: float, params: List[float]) -> float:
        """Улучшенная гауссова функция"""
        if len(params) != 2:
            return 0.0
            
        mean, sigma = params
        if sigma <= 0:
            return 1.0 if x == mean else 0.0
            
        return math.exp(-((x - mean) ** 2) / (2 * sigma ** 2))
    
    def calculate_membership(self, x: float, fuzzy_set: FuzzySet) -> float:
        """Вычисляет степень принадлежности значения нечеткому множеству"""
        if fuzzy_set.membership_function == "triangular":
            return self.triangular_mf(x, fuzzy_set.values)
        elif fuzzy_set.membership_function == "trapezoidal":
            return self.trapezoidal_mf(x, fuzzy_set.values)
        elif fuzzy_set.membership_function == "gaussian":
            return self.gaussian_mf(x, fuzzy_set.values)
        else:
            return 0.0
    
    def fuzzify_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, float]:
        """Фаззификация данных кандидата"""
        fuzzy_values = {}
        
        # Опыт работы
        experience = candidate_data.get("years", 0)
        fuzzy_values["experience_junior"] = self.calculate_membership(
            experience, self.fuzzy_sets["experience_junior"])
        fuzzy_values["experience_middle"] = self.calculate_membership(
            experience, self.fuzzy_sets["experience_middle"])
        fuzzy_values["experience_senior"] = self.calculate_membership(
            experience, self.fuzzy_sets["experience_senior"])
        
        # Зарплата
        salary = candidate_data.get("salary", 0)
        fuzzy_values["salary_low"] = self.calculate_membership(
            salary, self.fuzzy_sets["salary_low"])
        fuzzy_values["salary_medium"] = self.calculate_membership(
            salary, self.fuzzy_sets["salary_medium"])
        fuzzy_values["salary_high"] = self.calculate_membership(
            salary, self.fuzzy_sets["salary_high"])
        
        # Навыки
        skills_count = len(candidate_data.get("language", []))
        fuzzy_values["skills_few"] = self.calculate_membership(
            skills_count, self.fuzzy_sets["skills_few"])
        fuzzy_values["skills_moderate"] = self.calculate_membership(
            skills_count, self.fuzzy_sets["skills_moderate"])
        fuzzy_values["skills_many"] = self.calculate_membership(
            skills_count, self.fuzzy_sets["skills_many"])
        
        # Гибкость (количество поддерживаемых форматов работы)
        formats_count = len(candidate_data.get("format", []))
        max_formats = 3  # удалённый, очно, гибридный
        flexibility = formats_count / max_formats if max_formats > 0 else 0
        fuzzy_values["flexibility_low"] = self.calculate_membership(
            flexibility, self.fuzzy_sets["flexibility_low"])
        fuzzy_values["flexibility_medium"] = self.calculate_membership(
            flexibility, self.fuzzy_sets["flexibility_medium"])
        fuzzy_values["flexibility_high"] = self.calculate_membership(
            flexibility, self.fuzzy_sets["flexibility_high"])
        
        # Востребованность навыков (упрощенный расчет)
        candidate_skills = set(candidate_data.get("language", []))
        high_demand_skills = {"Python", "JavaScript", "Java", "Go"}
        demand_ratio = len(candidate_skills & high_demand_skills) / len(high_demand_skills) if high_demand_skills else 0
        fuzzy_values["demand_low"] = self.calculate_membership(
            demand_ratio, self.fuzzy_sets["demand_low"])
        fuzzy_values["demand_medium"] = self.calculate_membership(
            demand_ratio, self.fuzzy_sets["demand_medium"])
        fuzzy_values["demand_high"] = self.calculate_membership(
            demand_ratio, self.fuzzy_sets["demand_high"])
        
        return fuzzy_values
    
    def apply_rules(self, fuzzy_values: Dict[str, float], 
                   candidate_data: Dict[str, Any]) -> Dict[str, float]:
        """Применяет правила нечеткой логики"""
        rule_outputs = {}
        
        for rule in self.rules:
            rule_strength = 1.0
            
            # Вычисляем силу правила
            for condition in rule["conditions"]:
                condition_type, condition_value, weight = condition
                membership = 0.0
                
                if condition_type == "hasSkill":
                    # Проверка наличия конкретного навыка
                    candidate_skills = candidate_data.get("language", [])
                    has_skill = condition_value in candidate_skills
                    membership = 1.0 if has_skill else 0.0
                    
                elif condition_type == "hasSkills":
                    # Проверка наличия нескольких навыков
                    required_skills = condition_value
                    candidate_skills = candidate_data.get("language", [])
                    matched_skills = sum(1 for skill in required_skills if skill in candidate_skills)
                    membership = matched_skills / len(required_skills) if required_skills else 0.0
                    
                elif condition_type == "hasSoftSkill":
                    # Проверка мягких навыков (упрощенно)
                    # В реальной системе здесь была бы проверка мягких навыков
                    membership = 0.5  # Базовая оценка
                    
                else:
                    # Используем фаззифицированные значения
                    membership = fuzzy_values.get(condition_value, 0.0)
                
                rule_strength = min(rule_strength, membership * weight)
            
            # Сохраняем выход правила
            output_var, output_set = rule["conclusion"]
            if output_var not in rule_outputs:
                rule_outputs[output_var] = {}
            
            # Используем максимум из всех правил для данного вывода
            current_strength = rule_outputs[output_var].get(output_set, 0.0)
            rule_outputs[output_var][output_set] = max(
                current_strength,
                rule_strength * rule["weight"]
            )
        
        return rule_outputs
    
    def defuzzify(self, rule_outputs: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Дефаззификация - преобразование нечетких выходов в четкие значения"""
        crisp_values = {}
        
        for output_var, sets in rule_outputs.items():
            if output_var == "match_score":
                # Используем метод центра тяжести для дефаззификации
                numerator = 0.0
                denominator = 0.0
                
                for set_name, membership in sets.items():
                    # Определяем репрезентативное значение для каждого множества
                    if set_name == "match_poor":
                        rep_value = 20.0
                    elif set_name == "match_fair":
                        rep_value = 50.0
                    elif set_name == "match_good":
                        rep_value = 75.0
                    elif set_name == "match_excellent":
                        rep_value = 90.0
                    else:
                        rep_value = 50.0
                    
                    numerator += rep_value * membership
                    denominator += membership
                
                if denominator > 0:
                    crisp_values[output_var] = min(100.0, max(0.0, numerator / denominator))
                else:
                    crisp_values[output_var] = 0.0
            elif output_var == "match_adjustment":
                # Для корректировочных правил используем среднее
                values = list(sets.values())
                if values:
                    crisp_values[output_var] = sum(values) / len(values)
        
        return crisp_values
    
    def evaluate_candidate(self, candidate_data: Dict[str, Any], 
                          vacancy_requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """Оценивает кандидата с использованием нечеткой логики"""
        # Фаззификация входных данных
        fuzzy_values = self.fuzzify_candidate(candidate_data)
        
        # Применение правил
        rule_outputs = self.apply_rules(fuzzy_values, candidate_data)
        
        # Дефаззификация
        crisp_values = self.defuzzify(rule_outputs)
        
        # Формирование результата
        result = {
            "candidate_name": candidate_data.get("name", "Unknown"),
            "fuzzy_values": fuzzy_values,
            "rule_outputs": rule_outputs,
            "final_score": crisp_values.get("match_score", 0.0),
            "recommendation": self._get_recommendation(crisp_values.get("match_score", 0.0))
        }
        
        # Применяем корректировки если есть
        adjustment = crisp_values.get("match_adjustment", 0.0)
        if adjustment > 0:
            result["final_score"] = min(100.0, result["final_score"] + adjustment * 10)
            result["recommendation"] = self._get_recommendation(result["final_score"])
        
        return result
    
    def _get_recommendation(self, score: float) -> str:
        """Генерирует текстовую рекомендацию на основе оценки"""
        if score >= 80:
            return "Отличное соответствие - высокий приоритет"
        elif score >= 60:
            return "Хорошее соответствие - рекомендован к рассмотрению"
        elif score >= 40:
            return "Удовлетворительное соответствие - рассмотреть при отсутствии лучших кандидатов"
        else:
            return "Низкое соответствие - не рекомендуется"
    
    def batch_evaluate(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Оценивает нескольких кандидатов"""
        results = []
        for candidate in candidates:
            result = self.evaluate_candidate(candidate)
            results.append(result)
        
        # Сортировка по убыванию оценки
        return sorted(results, key=lambda x: x["final_score"], reverse=True)

# Интеграция с существующей системой
class FuzzyExpertSystem:
    """Экспертная система с нечеткой логикой, интегрированная с основной системой"""
    
    def __init__(self):
        self.fuzzy_system = FuzzyLogicSystem()
    
    def fuzzy_recommend(self, candidates: List[Dict[str, Any]], 
                       profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Нечеткий подбор кандидатов с учетом профиля вакансии"""
        
        # Обогащаем данные кандидатов информацией о соответствии профилю
        enriched_candidates = []
        for candidate in candidates:
            enriched_candidate = candidate.copy()
            
            # Вычисляем дополнительные метрики для нечеткой системы
            match_metrics = self._calculate_match_metrics(candidate, profile)
            enriched_candidate.update(match_metrics)
            
            enriched_candidates.append(enriched_candidate)
        
        # Оцениваем кандидатов с помощью нечеткой логики
        fuzzy_results = self.fuzzy_system.batch_evaluate(enriched_candidates)
        
        return fuzzy_results
    
    def _calculate_match_metrics(self, candidate: Dict[str, Any], 
                                profile: Dict[str, Any]) -> Dict[str, Any]:
        """Вычисляет метрики соответствия кандидата профилю вакансии"""
        metrics = {}
        
        # Соответствие языков программирования
        candidate_langs = set(candidate.get("language", []))
        required_langs = set(profile.get("languages", []))
        if required_langs:
            lang_match_ratio = len(candidate_langs & required_langs) / len(required_langs)
            metrics["language_match"] = lang_match_ratio
        
        # Соответствие уровня опыта
        candidate_level = candidate.get("level", "").lower()
        required_level = profile.get("level", "").lower()
        if required_level:
            if candidate_level == required_level:
                level_match = 1.0
            elif (candidate_level == "senior" and required_level == "middle") or \
                 (candidate_level == "middle" and required_level == "junior"):
                level_match = 0.7  # Кандидат превышает требования
            elif (candidate_level == "junior" and required_level == "middle") or \
                 (candidate_level == "middle" and required_level == "senior"):
                level_match = 0.3  # Кандидат не дотягивает
            else:
                level_match = 0.1
            metrics["level_match"] = level_match
        
        # Соответствие формата работы
        candidate_formats = set(candidate.get("format", []))
        required_formats = set(profile.get("formats", []))
        if required_formats:
            format_match_ratio = len(candidate_formats & required_formats) / len(required_formats)
            metrics["format_match"] = format_match_ratio
        
        # Соответствие зарплатных ожиданий
        candidate_salary = candidate.get("salary", 0)
        min_salary, max_salary = profile.get("salary_range", (0, float('inf')))
        if max_salary == float('inf'):
            salary_match = 1.0 if candidate_salary >= min_salary else 0.0
        else:
            if min_salary <= candidate_salary <= max_salary:
                salary_match = 1.0
            else:
                # Штраф за выход за пределы диапазона
                salary_match = max(0.0, 1.0 - abs(candidate_salary - (min_salary + max_salary)/2) / max_salary)
        metrics["salary_match"] = salary_match
        
        return metrics

# Утилиты для тестирования
def create_sample_candidates() -> List[Dict[str, Any]]:
    """Создает тестовых кандидатов для демонстрации"""
    return [
        {
            "name": "Иван Петров",
            "language": ["Python", "JavaScript"],
            "level": "middle",
            "years": 3,
            "format": ["удалённый", "гибридный"],
            "salary": 120000
        },
        {
            "name": "Анна Сидорова", 
            "language": ["Java", "CPP"],
            "level": "senior",
            "years": 7,
            "format": ["очно", "гибридный"],
            "salary": 200000
        },
        {
            "name": "Алексей Козлов",
            "language": ["Python", "Go", "Rust"],
            "level": "junior", 
            "years": 1,
            "format": ["удалённый"],
            "salary": 80000
        },
        {
            "name": "Мария Иванова",
            "language": ["Python", "JavaScript", "TypeScript", "Java"],
            "level": "senior",
            "years": 5,
            "format": ["удалённый", "очно", "гибридный"],
            "salary": 180000
        }
    ]

def create_sample_vacancy() -> Dict[str, Any]:
    """Создает тестовую вакансию для демонстрации"""
    return {
        "languages": ["Python", "JavaScript"],
        "level": "middle",
        "years_range": (2, 5),
        "formats": ["удалённый", "гибридный"],
        "salary_range": (80000, 150000)
    }

if __name__ == "__main__":
    # Демонстрация работы системы
    print("🔍 Демонстрация нечеткой экспертной системы")
    print("=" * 50)
    
    # Создаем тестовые данные
    candidates = create_sample_candidates()
    vacancy = create_sample_vacancy()
    
    # Запускаем систему
    expert = FuzzyExpertSystem()
    results = expert.fuzzy_recommend(candidates, vacancy)
    
    print("Результаты оценки кандидатов:")
    print("-" * 50)
    
    for result in results:
        print(f"👤 {result['candidate_name']}")
        print(f"   Оценка: {result['final_score']:.1f}%")
        print(f"   Рекомендация: {result['recommendation']}")
        print()