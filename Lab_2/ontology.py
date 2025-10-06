import os
from typing import List, Dict, Set, Any, Optional
from dataclasses import dataclass
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD
from rdflib.term import URIRef, Literal

@dataclass
class OntologyClass:
    """Класс онтологии с именем и свойствами."""
    name: str
    parent: Optional[str] = None
    properties: Dict[str, str] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}

@dataclass
class OntologyIndividual:
    """Экземпляр онтологии."""
    name: str
    class_type: str
    properties: Dict[str, Any]

class OntologyManager:
    """Менеджер для создания и работы с онтологиями."""
    
    def __init__(self, ontology_path: str = "data/ontology.ttl"):
        self.ontology_path = ontology_path
        self.graph = Graph()
        self.base_ns = Namespace("http://example.org/it_recruitment#")
        self.init_namespaces()
        self.classes: Dict[str, OntologyClass] = {}
        self.individuals: Dict[str, OntologyIndividual] = {}
        
    def init_namespaces(self):
        """Инициализация пространств имен."""
        self.graph.bind("rec", self.base_ns)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("owl", OWL)
        self.graph.bind("xsd", XSD)
    
    def define_base_ontology(self):
        """Определяет базовую структуру онтологии для IT-рекрутмента."""
        # Базовые классы
        base_classes = {
            "Candidate": OntologyClass("Candidate"),
            "Vacancy": OntologyClass("Vacancy"),
            "Skill": OntologyClass("Skill"),
            "ProgrammingLanguage": OntologyClass("ProgrammingLanguage", parent="Skill"),
            "ExperienceLevel": OntologyClass("ExperienceLevel"),
            "WorkFormat": OntologyClass("WorkFormat"),
            "Company": OntologyClass("Company")
        }
        
        # Свойства классов
        base_classes["Candidate"].properties = {
            "hasSkill": "ProgrammingLanguage",
            "hasExperienceLevel": "ExperienceLevel", 
            "prefersWorkFormat": "WorkFormat",
            "hasYearsOfExperience": "xsd:integer",
            "expectedSalary": "xsd:integer",
            "appliedFor": "Vacancy"
        }
        
        base_classes["Vacancy"].properties = {
            "requiresSkill": "ProgrammingLanguage",
            "requiresExperienceLevel": "ExperienceLevel",
            "offersWorkFormat": "WorkFormat", 
            "minYearsOfExperience": "xsd:integer",
            "maxSalary": "xsd:integer",
            "offeredBy": "Company"
        }
        
        self.classes = base_classes
        self._create_ontology_structure()
    
    def _create_ontology_structure(self):
        """Создает структуру онтологии в RDF графе."""
        # Создание классов
        for class_name, ontology_class in self.classes.items():
            class_uri = self.base_ns[class_name]
            self.graph.add((class_uri, RDF.type, OWL.Class))
            self.graph.add((class_uri, RDFS.label, Literal(class_name)))
            
            if ontology_class.parent:
                parent_uri = self.base_ns[ontology_class.parent]
                self.graph.add((class_uri, RDFS.subClassOf, parent_uri))
        
        # Создание свойств
        for class_name, ontology_class in self.classes.items():
            for prop_name, prop_range in ontology_class.properties.items():
                prop_uri = self.base_ns[prop_name]
                domain_uri = self.base_ns[class_name]
                
                self.graph.add((prop_uri, RDF.type, OWL.ObjectProperty 
                              if not prop_range.startswith('xsd:') else OWL.DatatypeProperty))
                self.graph.add((prop_uri, RDFS.domain, domain_uri))
                
                if prop_range.startswith('xsd:'):
                    range_uri = getattr(XSD, prop_range.split(':')[1])
                else:
                    range_uri = self.base_ns[prop_range]
                self.graph.add((prop_uri, RDFS.range, range_uri))
    def update_ontology(self, sparql_update: str) -> bool:
        """Выполняет SPARQL UPDATE запрос к онтологии."""
        try:
            self.graph.update(sparql_update)
            return True
        except Exception as e:
            print(f"Ошибка выполнения SPARQL UPDATE запроса: {e}")
            return False
    def add_individual(self, individual: OntologyIndividual) -> bool:
        """Добавляет экземпляр в онтологию."""
        try:
            individual_uri = self.base_ns[individual.name.replace(" ", "_")]
            class_uri = self.base_ns[individual.class_type]
            
            # Указываем тип индивида
            self.graph.add((individual_uri, RDF.type, class_uri))
            self.graph.add((individual_uri, RDFS.label, Literal(individual.name)))
            
            # Добавляем свойства
            for prop_name, prop_value in individual.properties.items():
                prop_uri = self.base_ns[prop_name]
                
                if isinstance(prop_value, list):
                    for value in prop_value:
                        if value:  # Проверяем, что значение не пустое
                            if prop_name == "hasSkill":
                                value_uri = self.base_ns[value.replace(" ", "_")]
                            elif prop_name == "prefersWorkFormat":
                                value_uri = self.base_ns[value.replace(" ", "_")]
                            else:
                                value_uri = self.base_ns[value.replace(" ", "_")] if isinstance(value, str) else Literal(value)
                            self.graph.add((individual_uri, prop_uri, value_uri))
                elif prop_value:  # Проверяем, что значение не пустое
                    if prop_name in ["hasExperienceLevel"]:
                        value_uri = self.base_ns[prop_value.replace(" ", "_")]
                    elif isinstance(prop_value, str) and not prop_value.startswith('http'):
                        value_uri = self.base_ns[prop_value.replace(" ", "_")]
                    else:
                        value_uri = Literal(prop_value)
                    self.graph.add((individual_uri, prop_uri, value_uri))
            
            self.individuals[individual.name] = individual
            return True
            
        except Exception as e:
            print(f"Ошибка при добавлении индивида {individual.name}: {e}")
            return False
    
    def save_ontology(self):
        """Сохраняет онтологию в файл."""
        os.makedirs(os.path.dirname(self.ontology_path), exist_ok=True)
        self.graph.serialize(destination=self.ontology_path, format='turtle')
        print(f"Онтология сохранена в: {self.ontology_path}")
    
    def load_ontology(self):
        """Загружает онтологию из файла."""
        if os.path.exists(self.ontology_path):
            self.graph.parse(self.ontology_path, format='turtle')
            print(f"Онтология загружена из: {self.ontology_path}")
            return True
        return False
    
    def query_ontology(self, sparql_query: str) -> List[Dict]:
        """Выполняет SPARQL запрос к онтологии."""
        try:
            results = []
            query_result = self.graph.query(sparql_query)
            
            for row in query_result:
                result_row = {}
                for var in query_result.vars:
                    value = row[var]
                    if value:
                        result_row[str(var)] = str(value)
                results.append(result_row)
            
            return results
        except Exception as e:
            print(f"Ошибка выполнения SPARQL запроса: {e}")
            return []