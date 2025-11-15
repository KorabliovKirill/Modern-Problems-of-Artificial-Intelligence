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
    membership_function: str  # 'triangular', 'trapezoidal'

class FuzzyLogicSystem:
    """Система нечеткой логики для подбора IT-кандидатов с категориальными правилами"""
    
    def __init__(self):
        self.fuzzy_sets = self._define_fuzzy_sets()
        self.rules = self._define_rules()
        self.output_universe = np.linspace(0, 100, 1001)  # Универсум для выхода
    
    def _define_fuzzy_sets(self) -> Dict[str, FuzzySet]:
        """Определяет нечеткие множества с ПРАВИЛЬНЫМИ перекрывающимися функциями"""
        return {
            # Уровень опыта - ПЕРЕКРЫВАЮЩИЕСЯ функции
            "level_junior": FuzzySet("level_junior", [0, 0, 2, 4], "trapezoidal"),
            "level_middle": FuzzySet("level_middle", [1, 3, 5, 7], "trapezoidal"),
            "level_senior": FuzzySet("level_senior", [4, 6, 10, 10], "trapezoidal"),
            
            # Тип разработчика - ПЕРЕКРЫВАЮЩИЕСЯ функции
            "backend_developer": FuzzySet("backend_developer", [0, 0, 0.4, 0.6], "trapezoidal"),
            "frontend_developer": FuzzySet("frontend_developer", [0.3, 0.5, 0.7, 0.9], "trapezoidal"),
            "fullstack_developer": FuzzySet("fullstack_developer", [0.6, 0.8, 1.0, 1.0], "trapezoidal"),
            
            # Гибкость работы - ПЕРЕКРЫВАЮЩИЕСЯ функции
            "flexibility_low": FuzzySet("flexibility_low", [0, 0, 0.2, 0.5], "trapezoidal"),
            "flexibility_medium": FuzzySet("flexibility_medium", [0.3, 0.5, 0.7, 0.9], "trapezoidal"),
            "flexibility_high": FuzzySet("flexibility_high", [0.6, 0.8, 1.0, 1.0], "trapezoidal"),
            
            # Выходная переменная - соответствие вакансии
            "match_poor": FuzzySet("match_poor", [0, 0, 20, 40], "trapezoidal"),
            "match_average": FuzzySet("match_average", [25, 40, 60, 75], "trapezoidal"),
            "match_excellent": FuzzySet("match_excellent", [60, 80, 100, 100], "trapezoidal"),
        }
    
    def _define_rules(self) -> List[Dict[str, Any]]:
        """Определяет категориальные правила как в примере с рекомендациями контента"""
        return [
            # Правила для Junior разработчиков
            {
                "name": "junior_any_flexibility",
                "conditions": {"level": "level_junior"},
                "conclusion": ("match_score", "match_average"),
                "description": "Junior разработчики подходят для базовых задач"
            },
            {
                "name": "junior_high_flexibility", 
                "conditions": {"level": "level_junior", "flexibility": "flexibility_high"},
                "conclusion": ("match_score", "match_excellent"),
                "description": "Junior с высокой гибкостью - отличный кандидат"
            },
            {
                "name": "junior_fullstack",
                "conditions": {"level": "level_junior", "developer_type": "fullstack_developer"},
                "conclusion": ("match_score", "match_excellent"),
                "description": "Junior fullstack - многообещающий кандидат"
            },
            
            # Правила для Middle разработчиков
            {
                "name": "middle_backend",
                "conditions": {"level": "level_middle", "developer_type": "backend_developer"},
                "conclusion": ("match_score", "match_excellent"),
                "description": "Middle backend разработчики высоко ценятся"
            },
            {
                "name": "middle_frontend",
                "conditions": {"level": "level_middle", "developer_type": "frontend_developer"},
                "conclusion": ("match_score", "match_excellent"),
                "description": "Middle frontend разработчики востребованы"
            },
            {
                "name": "middle_fullstack",
                "conditions": {"level": "level_middle", "developer_type": "fullstack_developer"},
                "conclusion": ("match_score", "match_excellent"),
                "description": "Middle fullstack - универсальные кандидаты"
            },
            {
                "name": "middle_low_flexibility",
                "conditions": {"level": "level_middle", "flexibility": "flexibility_low"},
                "conclusion": ("match_score", "match_average"),
                "description": "Middle с низкой гибкостью - среднее соответствие"
            },
            
            # Правила для Senior разработчиков
            {
                "name": "senior_any_type",
                "conditions": {"level": "level_senior"},
                "conclusion": ("match_score", "match_excellent"),
                "description": "Senior разработчики подходят для сложных задач"
            },
            {
                "name": "senior_low_flexibility",
                "conditions": {"level": "level_senior", "flexibility": "flexibility_low"},
                "conclusion": ("match_score", "match_average"),
                "description": "Senior с низкой гибкостью - ограниченное применение"
            },
            
            # Универсальные правила по гибкости
            {
                "name": "any_level_high_flexibility",
                "conditions": {"flexibility": "flexibility_high"},
                "conclusion": ("match_score", "match_excellent"),
                "description": "Высокая гибкость ценится для любого уровня"
            },
            {
                "name": "any_level_low_flexibility",
                "conditions": {"flexibility": "flexibility_low"},
                "conclusion": ("match_score", "match_poor"),
                "description": "Низкая гибкость снижает привлекательность кандидата"
            },
            
            # Правила по типу разработчика
            {
                "name": "any_level_fullstack",
                "conditions": {"developer_type": "fullstack_developer"},
                "conclusion": ("match_score", "match_excellent"),
                "description": "Fullstack разработчики всегда востребованы"
            },
            {
                "name": "junior_backend_only",
                "conditions": {"level": "level_junior", "developer_type": "backend_developer"},
                "conclusion": ("match_score", "match_poor"),
                "description": "Junior backend без других навыков - низкое соответствие"
            },
        ]
    
    def triangular_mf(self, x: float, params: List[float]) -> float:
        """Треугольная функция принадлежности"""
        if len(params) != 3:
            return 0.0
            
        a, b, c = params
        
        if x <= a or x >= c:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a)
        elif b < x < c:
            return (c - x) / (c - b)
        else:
            return 1.0 if x == b else 0.0
    
    def trapezoidal_mf(self, x: float, params: List[float]) -> float:
        """Трапецевидная функция принадлежности"""
        if len(params) != 4:
            return 0.0
            
        a, b, c, d = params
        
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
    
    def calculate_membership(self, x: float, fuzzy_set: FuzzySet) -> float:
        """Вычисляет степень принадлежности значения нечеткому множеству"""
        if fuzzy_set.membership_function == "triangular":
            return self.triangular_mf(x, fuzzy_set.values)
        elif fuzzy_set.membership_function == "trapezoidal":
            return self.trapezoidal_mf(x, fuzzy_set.values)
        else:
            return 0.0
    
    def _calculate_developer_type(self, languages: List[str]) -> float:
        """Вычисляет тип разработчика на основе навыков с плавными переходами"""
        backend_skills = {"Python", "Java", "C++", "C#", "Go", "Rust"}
        frontend_skills = {"JavaScript", "TypeScript", "HTML", "CSS"}
        
        candidate_skills = set(languages)
        
        backend_count = len(candidate_skills & backend_skills)
        frontend_count = len(candidate_skills & frontend_skills)
        total_relevant = backend_count + frontend_count
        
        if total_relevant == 0:
            return 0.5  # нейтральное значение
            
        # Вычисляем баланс между backend и frontend
        # 0.0 = чистый backend, 0.5 = сбалансированный, 1.0 = чистый frontend
        if backend_count > 0 and frontend_count > 0:
            # Fullstack - зависит от баланса
            balance = frontend_count / total_relevant
            # Сдвигаем к fullstack диапазону (0.6-0.8)
            return 0.6 + (balance * 0.2)
        elif backend_count > 0:
            # В основном backend, но может быть near-fullstack
            backend_ratio = backend_count / len(backend_skills) if backend_skills else 0
            return 0.2 + (backend_ratio * 0.3)  # 0.2-0.5
        else:
            # В основном frontend
            frontend_ratio = frontend_count / len(frontend_skills) if frontend_skills else 0
            return 0.7 + (frontend_ratio * 0.3)  # 0.7-1.0
    
    def fuzzify_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, float]:
        """Фаззификация данных кандидата"""
        fuzzy_values = {}
        
        # Уровень опыта
        experience = candidate_data.get("years", 0)
        fuzzy_values["level_junior"] = self.calculate_membership(
            experience, self.fuzzy_sets["level_junior"])
        fuzzy_values["level_middle"] = self.calculate_membership(
            experience, self.fuzzy_sets["level_middle"])
        fuzzy_values["level_senior"] = self.calculate_membership(
            experience, self.fuzzy_sets["level_senior"])
        
        # Тип разработчика
        developer_type_score = self._calculate_developer_type(candidate_data.get("language", []))
        fuzzy_values["backend_developer"] = self.calculate_membership(
            developer_type_score, self.fuzzy_sets["backend_developer"])
        fuzzy_values["frontend_developer"] = self.calculate_membership(
            developer_type_score, self.fuzzy_sets["frontend_developer"])
        fuzzy_values["fullstack_developer"] = self.calculate_membership(
            developer_type_score, self.fuzzy_sets["fullstack_developer"])
        
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
        
        return fuzzy_values
    
    def apply_rules(self, fuzzy_values: Dict[str, float]) -> Dict[str, np.ndarray]:
        """Применяет категориальные правила нечеткой логики"""
        # Инициализируем выходные функции принадлежности
        output_membership = {
            "match_poor": np.zeros_like(self.output_universe),
            "match_average": np.zeros_like(self.output_universe),
            "match_excellent": np.zeros_like(self.output_universe)
        }
        
        activated_rules = []
        
        for rule in self.rules:
            rule_strength = 1.0
            
            # Вычисляем силу правила (MIN всех условий)
            for var_name, set_name in rule["conditions"].items():
                membership = fuzzy_values.get(set_name, 0.0)
                rule_strength = min(rule_strength, membership)
            
            # Если правило активировано (сила > 0)
            if rule_strength > 0:
                output_var, output_set = rule["conclusion"]
                
                # Получаем базовую функцию принадлежности для вывода
                base_mf = self._get_output_membership(output_set)
                
                # Обрезаем по силе правила (MIN-композиция)
                clipped_mf = np.minimum(base_mf, rule_strength)
                
                # Объединяем с предыдущими выводами (MAX-композиция)
                output_membership[output_set] = np.maximum(
                    output_membership[output_set], clipped_mf
                )
                
                activated_rules.append({
                    "name": rule["name"],
                    "strength": rule_strength,
                    "description": rule["description"],
                    "conclusion": output_set
                })
        
        return output_membership, activated_rules
    
    def _get_output_membership(self, set_name: str) -> np.ndarray:
        """Возвращает базовую функцию принадлежности для выходной переменной"""
        fuzzy_set = self.fuzzy_sets[set_name]
        if fuzzy_set.membership_function == "triangular":
            return np.array([self.triangular_mf(x, fuzzy_set.values) for x in self.output_universe])
        else:  # trapezoidal
            return np.array([self.trapezoidal_mf(x, fuzzy_set.values) for x in self.output_universe])
    
    def defuzzify(self, output_membership: Dict[str, np.ndarray]) -> float:
        """Дефаззификация методом центра тяжести"""
        # Объединяем все выходные функции принадлежности (MAX)
        aggregated_mf = np.zeros_like(self.output_universe)
        for mf in output_membership.values():
            aggregated_mf = np.maximum(aggregated_mf, mf)
        
        # Метод центра тяжести
        if np.sum(aggregated_mf) > 0:
            centroid = np.sum(self.output_universe * aggregated_mf) / np.sum(aggregated_mf)
            return float(centroid)
        else:
            return 0.0
    
    def evaluate_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """Оценивает кандидата с использованием нечеткой логики"""
        # Фаззификация входных данных
        fuzzy_values = self.fuzzify_candidate(candidate_data)
        
        # Применение правил
        output_membership, activated_rules = self.apply_rules(fuzzy_values)
        
        # Дефаззификация
        final_score = self.defuzzify(output_membership)
        
        # Формирование результата
        result = {
            "candidate_name": candidate_data.get("name", "Unknown"),
            "fuzzy_values": fuzzy_values,
            "final_score": final_score,
            "activated_rules": activated_rules,
            "recommendation": self._get_recommendation(final_score),
            "output_membership": {k: v.tolist() for k, v in output_membership.items()}
        }
        
        return result
    
    def _get_recommendation(self, score: float) -> str:
        """Генерирует текстовую рекомендацию на основе оценки"""
        if score >= 70:
            return "Отличное соответствие - высокий приоритет"
        elif score >= 40:
            return "Хорошее соответствие - рекомендован к рассмотрению"
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
                       profile: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Нечеткий подбор кандидатов"""
        # Оцениваем кандидатов с помощью нечеткой логики
        fuzzy_results = self.fuzzy_system.batch_evaluate(candidates)
        
        return fuzzy_results