"""GeminiAdvisor service — AI-powered job matching and career recommendations.

Uses the google-genai SDK to call Gemini models for:
- Job matching: scores user profile against job listings
- Career recommendations: personalized advice with course/article suggestions
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

import structlog

logger = structlog.get_logger()

# Prompt templates directory
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def _load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts directory."""
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8")


class GeminiAdvisor:
    """Singleton service for AI-powered job matching and career advice."""

    _instance: GeminiAdvisor | None = None
    _lock = threading.Lock()

    def __new__(cls) -> GeminiAdvisor:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True

        self._api_key = os.getenv("GOOGLE_API_KEY")
        self._model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self._client = None

        if self._api_key:
            try:
                from google import genai

                self._client = genai.Client(api_key=self._api_key)
                logger.info("gemini_advisor_initialized", model=self._model)
            except Exception as e:
                logger.error("gemini_advisor_init_failed", error=str(e))
                self._client = None
        else:
            logger.warning("gemini_advisor_no_api_key", msg="GOOGLE_API_KEY not set — AI features disabled")

    @property
    def is_available(self) -> bool:
        """True if API key is set and client initialized."""
        return self._client is not None and self._api_key is not None

    @property
    def model_name(self) -> str:
        """Public accessor for the model name."""
        return self._model

    def _call_gemini(self, prompt: str) -> str | None:
        """Call Gemini and return the raw text response, or None on failure."""
        if not self.is_available:
            logger.warning("gemini_call_skipped", reason="client not available")
            return None

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=4096,
                response_mime_type="application/json",
            )
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=config,
            )
            return response.text
        except Exception as e:
            logger.error("gemini_call_failed", error=str(e))
            return None

    def _parse_json(self, text: str | None, fallback=None):
        """Parse JSON from Gemini response with fallback."""
        if text is None:
            return fallback
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError) as e:
            logger.error("gemini_json_parse_failed", error=str(e), text_snippet=text[:200] if text else "")
            return fallback

    def match_jobs(self, user_profile_dict: dict, jobs_list: list[dict]) -> list[dict] | None:
        """Match user profile against job listings using Gemini.

        Args:
            user_profile_dict: User profile data (skills, experience_level, etc.)
            jobs_list: List of job dicts (title, company, tags, etc.)

        Returns:
            List of {job_id, score, reasons} dicts, or None on failure.
        """
        if not self.is_available:
            return None

        try:
            template = _load_prompt("job_matcher.md")
            # Use .replace() instead of .format() to prevent prompt injection
            # via user-controlled fields containing curly braces
            prompt = template.replace(
                "{user_profile}", json.dumps(user_profile_dict, ensure_ascii=False, indent=2)
            ).replace(
                "{jobs_list}", json.dumps(jobs_list, ensure_ascii=False, indent=2)
            )

            logger.info("gemini_match_jobs_start", jobs_count=len(jobs_list))
            raw = self._call_gemini(prompt)
            result = self._parse_json(raw, fallback=None)

            if result is None:
                return None

            # Validate structure: must be a list of dicts with job_id, score, reasons
            if not isinstance(result, list):
                logger.error("gemini_match_jobs_invalid_structure", result_type=type(result).__name__)
                return None

            validated = []
            for item in result:
                if isinstance(item, dict) and "job_id" in item and "score" in item:
                    validated.append({
                        "job_id": str(item["job_id"]),
                        "score": max(0, min(100, int(item.get("score", 0)))),
                        "reasons": item.get("reasons", []),
                    })

            logger.info("gemini_match_jobs_done", matches_count=len(validated))
            return validated

        except Exception as e:
            logger.error("gemini_match_jobs_error", error=str(e))
            return None

    def career_recommendations(
        self,
        user_profile_dict: dict,
        top_jobs: list[dict],
        courses_list: list[dict],
        news_list: list[dict],
    ) -> dict | None:
        """Generate career recommendations using Gemini.

        Args:
            user_profile_dict: User profile data
            top_jobs: Top matched jobs (up to 5)
            courses_list: Available courses
            news_list: Recent news articles

        Returns:
            Dict with career_direction, recommended_courses, recommended_articles, skill_gaps.
            Or None on failure.
        """
        if not self.is_available:
            return None

        try:
            template = _load_prompt("career_advisor.md")
            # Use .replace() instead of .format() to prevent prompt injection
            prompt = template.replace(
                "{user_profile}", json.dumps(user_profile_dict, ensure_ascii=False, indent=2)
            ).replace(
                "{top_jobs}", json.dumps(top_jobs, ensure_ascii=False, indent=2)
            ).replace(
                "{courses_list}", json.dumps(courses_list, ensure_ascii=False, indent=2)
            ).replace(
                "{news_list}", json.dumps(news_list, ensure_ascii=False, indent=2)
            )

            logger.info("gemini_career_recommendations_start")
            raw = self._call_gemini(prompt)
            result = self._parse_json(raw, fallback=None)

            if result is None:
                return None

            # Validate structure: must be a dict with expected keys
            if not isinstance(result, dict):
                logger.error("gemini_career_recommendations_invalid_structure", result_type=type(result).__name__)
                return None

            validated = {
                "career_direction": str(result.get("career_direction", "")),
                "recommended_courses": result.get("recommended_courses", []),
                "recommended_articles": result.get("recommended_articles", []),
                "skill_gaps": result.get("skill_gaps", []),
            }

            logger.info("gemini_career_recommendations_done")
            return validated

        except Exception as e:
            logger.error("gemini_career_recommendations_error", error=str(e))
            return None


    def skill_gap_analysis(
        self,
        user_profile_dict: dict,
        user_skills_status: list[dict],
        missing_skills_data: list[dict],
        market_trends_data: list[dict],
        news_list: list[dict],
    ) -> dict | None:
        """Generate personalized skill gap insights using Gemini.

        The algorithmic demand data is already computed. Gemini adds:
        - A personalized narrative summary (2-3 paragraphs in Italian)
        - Reasons why each missing skill matters for this specific user

        Returns:
            Dict with "personalized_insights" (str) and "missing_skill_reasons" (dict).
            Or None on failure.
        """
        if not self.is_available:
            return None

        try:
            template = _load_prompt("skill_gap_analyzer.md")
            prompt = template.replace(
                "{user_profile}", json.dumps(user_profile_dict, ensure_ascii=False, indent=2)
            ).replace(
                "{user_skills_status}", json.dumps(user_skills_status, ensure_ascii=False, indent=2)
            ).replace(
                "{missing_skills}", json.dumps(missing_skills_data, ensure_ascii=False, indent=2)
            ).replace(
                "{market_trends}", json.dumps(market_trends_data, ensure_ascii=False, indent=2)
            ).replace(
                "{news_list}", json.dumps(news_list, ensure_ascii=False, indent=2)
            )

            logger.info("gemini_skill_gap_analysis_start")
            raw = self._call_gemini(prompt)
            result = self._parse_json(raw, fallback=None)

            if result is None:
                return None

            if not isinstance(result, dict):
                logger.error("gemini_skill_gap_invalid_structure", result_type=type(result).__name__)
                return None

            validated = {
                "personalized_insights": str(result.get("personalized_insights", "")),
                "missing_skill_reasons": result.get("missing_skill_reasons", {}),
            }

            logger.info("gemini_skill_gap_analysis_done")
            return validated

        except Exception as e:
            logger.error("gemini_skill_gap_analysis_error", error=str(e))
            return None


def get_advisor() -> GeminiAdvisor:
    """Get the GeminiAdvisor singleton instance."""
    return GeminiAdvisor()
