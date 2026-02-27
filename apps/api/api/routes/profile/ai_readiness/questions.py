"""Quiz question definitions, scoring logic, and weak-category detection."""

from __future__ import annotations

QUIZ_VERSION = 1

QUIZ_QUESTIONS = [
    {"id": "q1_ai_coding_assistants", "categories": ["AI"]},
    {"id": "q2_prompt_writing", "categories": ["AI"]},
    {"id": "q3_agentic_workflows", "categories": ["AI"]},
    {"id": "q4_ai_code_review", "categories": ["AI", "tech"]},
    {"id": "q5_ai_api_integration", "categories": ["AI", "backend"]},
    {"id": "q6_ai_output_evaluation", "categories": ["ML"]},
    {"id": "q7_rag_systems", "categories": ["AI", "ML"]},
    {"id": "q8_prompt_engineering", "categories": ["AI"]},
]

VALID_QUESTION_IDS = {q["id"] for q in QUIZ_QUESTIONS}
QUESTION_CATEGORY_MAP = {q["id"]: q["categories"] for q in QUIZ_QUESTIONS}


def compute_score(answers: dict[str, int]) -> tuple[int, str]:
    """Compute percentage score and readiness level from quiz answers.

    Args:
        answers: Dict mapping question ID to answer value (0-4).

    Returns:
        Tuple of (percentage 0-100, level string).
    """
    raw = sum(answers.values())
    max_score = len(QUIZ_QUESTIONS) * 4
    percentage = round(raw / max_score * 100)
    if percentage <= 25:
        level = "beginner"
    elif percentage <= 50:
        level = "intermediate"
    elif percentage <= 75:
        level = "advanced"
    else:
        level = "expert"
    return percentage, level


def get_weak_categories(answers: dict[str, int], threshold: int = 2) -> list[str]:
    """Identify course categories where the user scored below threshold.

    Args:
        answers: Dict mapping question ID to answer value (0-4).
        threshold: Score below which a question is considered weak (default 2).

    Returns:
        Deduplicated list of category strings where the user needs improvement.
    """
    weak_cats: set[str] = set()
    for qid, score in answers.items():
        if score < threshold and qid in QUESTION_CATEGORY_MAP:
            weak_cats.update(QUESTION_CATEGORY_MAP[qid])
    return sorted(weak_cats)
