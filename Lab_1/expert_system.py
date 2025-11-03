# expert_system.py
from typing import List, Dict, Any, Tuple
from candidate_manager import Candidate


# ---------------------------------------------------------------------------
# БАЙЕСОВСКАЯ ЛОГИКА
# ---------------------------------------------------------------------------


def bayesian_score(c: Candidate, profile: Dict[str, Any]) -> float:
    """Вычисляет баесовскую вероятность соответствия кандидата профилю."""
    p = 1.0

    # Язык
    if profile["languages"]:
        match = any(
            lang.lower() in [l.lower() for l in c.language]
            for lang in profile["languages"]
        )
        p *= 0.9 if match else 0.5

    # Уровень
    if profile["level"]:
        p *= 0.8 if c.level.lower() == profile["level"].lower() else 0.6

    # Опыт
    min_y, max_y = profile["years_range"]
    if min_y <= c.years <= max_y:
        p *= 0.9
    elif abs(c.years - min_y) <= 2 or abs(c.years - max_y) <= 2:
        p *= 0.7
    else:
        p *= 0.5

    # Формат
    if profile["formats"]:
        match = any(
            fmt.lower() in [f.lower() for f in c.format] for fmt in profile["formats"]
        )
        p *= 0.8 if match else 0.6

    # Зарплата
    min_s, max_s = profile["salary_range"]
    if min_s <= c.salary <= max_s:
        p *= 0.9
    else:
        if max_s == float("inf"):
            diff_factor = 0.7 if c.salary >= min_s else 0.4
        else:
            diff = abs(c.salary - min_s if c.salary < min_s else c.salary - max_s)
            diff_factor = 0.7 if diff / max_s < 0.2 else 0.4
        p *= diff_factor

    return p


def bayesian_recommend(candidates: List[Candidate], profile: Dict[str, Any], threshold: float = 0.3) -> List[Tuple[Candidate, float]]:
    """Рекомендация кандидатов на основе Баесовского подхода.
    
    Возвращает список кортежей (Candidate, вероятность) только для кандидатов,
    которые прошли порог threshold.
    """
    scored = [(c, bayesian_score(c, profile)) for c in candidates]

    # Нормализация (чтобы лучший был = 1.0)
    max_prob = max((p for _, p in scored), default=1e-6)
    scored = [(c, p / max_prob) for c, p in scored]

    # Сортировка по убыванию вероятности
    scored.sort(key=lambda x: x[1], reverse=True)

    # Возвращаем только тех, кто набрал >= threshold
    return [(c, p) for c, p in scored if p >= threshold]


# ---------------------------------------------------------------------------
# КЛАССИЧЕСКАЯ ЛОГИКА
# ---------------------------------------------------------------------------


def check_pref(
    item_list: List[str], prefs: List[str], relaxed: bool, require_all: bool
) -> bool:
    if not prefs:
        return True
    if require_all:
        return set(prefs).issubset(set(item_list))
    else:
        return bool(set(prefs) & set(item_list))


def classic_recommend(
    candidates: List[Candidate], profile: Dict[str, Any], flags: Dict[str, bool]
):
    results = []
    for c in candidates:
        if not check_pref(
            c.language, profile["languages"], flags["relaxed"], flags["all"]
        ):
            continue
        if profile["level"] and profile["level"] != c.level.lower():
            continue
        if not (profile["years_range"][0] <= c.years <= profile["years_range"][1]):
            continue
        if not check_pref(c.format, profile["formats"], flags["relaxed"], flags["all"]):
            continue
        if not (profile["salary_range"][0] <= c.salary <= profile["salary_range"][1]):
            continue
        results.append(c)
    return results


# ---------------------------------------------------------------------------
# ОБЩАЯ ТОЧКА ВХОДА
# ---------------------------------------------------------------------------


def recommend(
    candidates: List[Candidate], profile: Dict[str, Any], flags: Dict[str, bool]
):
    """Выбор режима подбора — классический или Баесовский.
    
    Для байесовского режима возвращает список кортежей (Candidate, вероятность).
    Для классического режима возвращает список Candidate.
    """
    if flags.get("bayes"):
        return bayesian_recommend(candidates, profile, threshold=0.3)
    else:
        return classic_recommend(candidates, profile, flags)
