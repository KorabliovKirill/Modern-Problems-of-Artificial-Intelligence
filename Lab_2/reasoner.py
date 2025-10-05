from typing import List, Dict, Any, Set, Tuple
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from rdflib.plugins.sparql import prepareQuery
from ontology import OntologyManager, OntologyIndividual


class OntologyReasoner:
    """Логический выводчик на основе онтологии."""
    
    def __init__(self, ontology_manager: OntologyManager):
        self.om = ontology_manager
        self.inferred_facts: List[Dict] = []
    
    def reason_about_candidate(self, candidate_name: str) -> List[Dict]:
        """Выполняет логический вывод для конкретного кандидата."""
        inferred_facts = []
        
        # Проверяем, существует ли кандидат
        candidate_query = """
        PREFIX rec: <http://example.org/it_recruitment#>
        SELECT ?property ?value WHERE {
            rec:%s ?property ?value .
        }
        """ % candidate_name.replace(" ", "_")
        
        candidate_data = self.om.query_ontology(candidate_query)
        
        if not candidate_data:
            return [{"type": "error", "message": f"Кандидат {candidate_name} не найден в онтологии"}]
        
        # Анализ навыков
        skill_analysis = self._analyze_skills(candidate_name)
        inferred_facts.extend(skill_analysis)
        
        # Анализ соответствия вакансиям
        vacancy_matches = self._find_vacancy_matches(candidate_name)
        inferred_facts.extend(vacancy_matches)
        
        # Анализ уровня опыта
        experience_analysis = self._analyze_experience(candidate_name)
        inferred_facts.extend(experience_analysis)
        
        self.inferred_facts = inferred_facts
        return inferred_facts
    
    def _analyze_skills(self, candidate_name: str) -> List[Dict]:
        """Анализирует навыки кандидата."""
        analysis = []
        
        query = """
        PREFIX rec: <http://example.org/it_recruitment#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?skillName WHERE {
            rec:%s rec:hasSkill ?skill .
            ?skill rdfs:label ?skillName .
        }
        """ % candidate_name.replace(" ", "_")
        
        skills = self.om.query_ontology(query)
        
        if skills:
            skill_list = [skill['skillName'] for skill in skills if 'skillName' in skill]
            if skill_list:
                analysis.append({
                    "type": "skills_analysis",
                    "message": f"Кандидат обладает навыками: {', '.join(skill_list)}",
                    "skills": skill_list,
                    "skill_count": len(skill_list)
                })
                
                # Анализ популярных навыков
                popular_skills = {"Python", "Java", "JavaScript"}
                candidate_skills_set = set(skill_list)
                popular_skills_owned = popular_skills & candidate_skills_set
                
                if popular_skills_owned:
                    analysis.append({
                        "type": "popular_skills",
                        "message": f"Кандидат обладает востребованными навыками: {', '.join(popular_skills_owned)}",
                        "skills": list(popular_skills_owned)
                    })
        
        return analysis
    
    def _find_vacancy_matches(self, candidate_name: str) -> List[Dict]:
        """Находит подходящие вакансии для кандидата."""
        matches = []
        
        # Упрощенный запрос для демонстрации
        query = """
        PREFIX rec: <http://example.org/it_recruitment#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?vacancy ?vacancyName ?requiredSkill ?requiredLevel ?minYears ?maxSalary WHERE {
            ?vacancy rdf:type rec:Vacancy .
            ?vacancy rdfs:label ?vacancyName .
            OPTIONAL { ?vacancy rec:requiresSkill ?requiredSkill . }
            OPTIONAL { ?vacancy rec:requiresExperienceLevel ?requiredLevel . }
            OPTIONAL { ?vacancy rec:minYearsOfExperience ?minYears . }
            OPTIONAL { ?vacancy rec:maxSalary ?maxSalary . }
        }
        """
        
        vacancies = self.om.query_ontology(query)
        
        # Получаем данные кандидата
        candidate_query = """
        PREFIX rec: <http://example.org/it_recruitment#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?skill ?level ?years ?salary WHERE {
            rec:%s rec:hasSkill ?skill ;
                rec:hasExperienceLevel ?level ;
                rec:hasYearsOfExperience ?years ;
                rec:expectedSalary ?salary .
        }
        """ % candidate_name.replace(" ", "_")
        
        candidate_data = self.om.query_ontology(candidate_query)
        
        if not candidate_data:
            return matches
        
        candidate_skills = set()
        candidate_level = ""
        candidate_years = 0
        candidate_salary = 0
        
        for data in candidate_data:
            if 'skill' in data:
                skill_name = data['skill'].split('#')[-1] if '#' in data['skill'] else data['skill']
                candidate_skills.add(skill_name)
            if 'level' in data and not candidate_level:
                candidate_level = data['level'].split('#')[-1] if '#' in data['level'] else data['level']
            if 'years' in data and not candidate_years:
                try:
                    candidate_years = int(data['years'])
                except:
                    candidate_years = 0
            if 'salary' in data and not candidate_salary:
                try:
                    candidate_salary = int(data['salary'])
                except:
                    candidate_salary = 0
        
        # Проверяем соответствие вакансиям
        for vacancy in vacancies:
            vacancy_name = vacancy.get('vacancyName', 'Unknown')
            match_score = 0
            
            # Проверка навыков
            required_skill = vacancy.get('requiredSkill')
            if required_skill:
                skill_name = required_skill.split('#')[-1] if '#' in required_skill else required_skill
                if skill_name in candidate_skills:
                    match_score += 30
            
            # Проверка уровня
            required_level = vacancy.get('requiredLevel')
            if required_level and candidate_level:
                level_name = required_level.split('#')[-1] if '#' in required_level else required_level
                if level_name.lower() == candidate_level.lower():
                    match_score += 30
            
            # Проверка опыта
            min_years = vacancy.get('minYears')
            if min_years:
                try:
                    if candidate_years >= int(min_years):
                        match_score += 20
                except:
                    pass
            
            # Проверка зарплаты
            max_salary = vacancy.get('maxSalary')
            if max_salary:
                try:
                    if candidate_salary <= int(max_salary):
                        match_score += 20
                except:
                    pass
            
            if match_score > 0:
                matches.append({
                    "type": "vacancy_match",
                    "message": f"Кандидат подходит для вакансии '{vacancy_name}' (совпадение: {match_score}%)",
                    "vacancy": vacancy_name,
                    "match_score": match_score
                })
        
        return sorted(matches, key=lambda x: x["match_score"], reverse=True)
    
    def _calculate_match_score(self, candidate_name: str, vacancy: Dict) -> float:
        """Вычисляет процент совпадения кандидата с вакансией."""
        score = 0
        max_score = 100
        
        # Проверка навыков
        required_skill = vacancy.get('requiredSkill')
        if required_skill:
            skill_query = """
            PREFIX rec: <http://example.org/it_recruitment#>
            ASK {
                rec:%s rec:hasSkill rec:%s .
            }
            """ % (candidate_name.replace(" ", "_"), required_skill.split('#')[-1])
            
            # Упрощенная проверка - в реальной системе нужно использовать SPARQL ASK
            # Здесь для демонстрации считаем, что навык есть
            score += 30
        
        # Проверка уровня опыта
        required_level = vacancy.get('requiredLevel')
        if required_level:
            level_query = """
            PREFIX rec: <http://example.org/it_recruitment#>
            SELECT ?level WHERE {
                rec:%s rec:hasExperienceLevel ?level .
            }
            """ % candidate_name.replace(" ", "_")
            
            candidate_levels = self.om.query_ontology(level_query)
            if candidate_levels and any(required_level in str(level) for level in candidate_levels):
                score += 30
        
        # Проверка минимального опыта
        min_years = vacancy.get('minYears')
        if min_years:
            experience_query = """
            PREFIX rec: <http://example.org/it_recruitment#>
            SELECT ?years WHERE {
                rec:%s rec:hasYearsOfExperience ?years .
            }
            """ % candidate_name.replace(" ", "_")
            
            candidate_experience = self.om.query_ontology(experience_query)
            if candidate_experience:
                candidate_years = int(list(candidate_experience[0].values())[0])
                if candidate_years >= int(min_years):
                    score += 20
        
        # Проверка зарплаты
        max_salary = vacancy.get('maxSalary')
        if max_salary:
            salary_query = """
            PREFIX rec: <http://example.org/it_recruitment#>
            SELECT ?salary WHERE {
                rec:%s rec:expectedSalary ?salary .
            }
            """ % candidate_name.replace(" ", "_")
            
            candidate_salary = self.om.query_ontology(salary_query)
            if candidate_salary:
                candidate_salary_val = int(list(candidate_salary[0].values())[0])
                if candidate_salary_val <= int(max_salary):
                    score += 20
        
        return score
    
    def _analyze_experience(self, candidate_name: str) -> List[Dict]:
        """Анализирует опыт кандидата."""
        analysis = []
        
        query = """
        PREFIX rec: <http://example.org/it_recruitment#>
        SELECT ?years ?level WHERE {
            rec:%s rec:hasYearsOfExperience ?years .
            OPTIONAL { rec:%s rec:hasExperienceLevel ?level . }
        }
        """ % (candidate_name.replace(" ", "_"), candidate_name.replace(" ", "_"))
        
        experience_data = self.om.query_ontology(query)
        
        if experience_data:
            for data in experience_data:
                years = data.get('years')
                level = data.get('level', 'Не указан')
                
                if years:
                    years_int = int(years)
                    if years_int < 2:
                        recommendation = "Рекомендуется рассматривать junior позиции"
                    elif years_int < 5:
                        recommendation = "Подходит для middle позиций"
                    else:
                        recommendation = "Может претендовать на senior позиции"
                    
                    analysis.append({
                        "type": "experience_analysis",
                        "message": f"Опыт работы: {years} лет, уровень: {level}",
                        "recommendation": recommendation,
                        "years": years_int,
                        "level": level
                    })
        
        return analysis
    
    def get_inference_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по результатам логического вывода."""
        if not self.inferred_facts:
            return {"total_inferences": 0}
        
        summary = {
            "total_inferences": len(self.inferred_facts),
            "vacancy_matches": len([f for f in self.inferred_facts if f["type"] == "vacancy_match"]),
            "skill_analyses": len([f for f in self.inferred_facts if f["type"] == "skills_analysis"]),
            "experience_analyses": len([f for f in self.inferred_facts if f["type"] == "experience_analysis"])
        }
        
        return summary