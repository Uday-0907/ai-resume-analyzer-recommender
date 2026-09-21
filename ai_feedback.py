"""
Optional Advanced Feature (PDF Section 13): LLM-generated resume feedback
using a controlled prompt.

This module is intentionally optional and safe-by-default:
- If no GEMINI_API_KEY is set, `generate_ai_feedback` returns None and the
  app simply skips this section — no crash, no requirement to use it.
- The prompt is "controlled": it only ever receives the extracted skill list,
  the target role, and the missing skills — never the raw resume text, and
  never any personal/identifying information. This keeps the feature aligned
  with the Responsible AI rules in Module 12 of the project brief.
"""

import os


def _get_api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY", "").strip() or None


def is_ai_feedback_available() -> bool:
    """Lets the UI check whether it should even show the feature toggle."""
    return _get_api_key() is not None


def generate_ai_feedback(
    target_role: str,
    matching_skills: list,
    missing_skills: list,
    match_score: float,
) -> str | None:
    """
    Generates a short, encouraging feedback paragraph using Gemini.

    Returns None if no API key is configured, or a short error string if the
    call fails, so the caller can display it gracefully rather than crash.
    """
    api_key = _get_api_key()
    if not api_key:
        return None

    # Controlled prompt: fixed structure, only skill-level data, explicit
    # constraints on tone and scope so the model can't be steered into
    # commenting on anything outside job-related skills.
    prompt = f"""You are a career coaching assistant helping a student improve
their resume for a specific job role. You are given only skill-level data,
never the resume text itself or any personal information.

Target role: {target_role}
Overall match score: {match_score}%
Skills already present: {", ".join(matching_skills) if matching_skills else "none detected"}
Missing skills for this role: {", ".join(missing_skills) if missing_skills else "none"}

Write a short (4-6 sentence), encouraging, constructive piece of feedback for
the student. Rules:
- Only discuss job-related skills, projects, and learning suggestions.
- Do not mention or speculate about gender, age, name, nationality, ethnicity,
  religion, marital status, disability, or any personal characteristic.
- Do not claim the student is unqualified — frame missing skills as growth
  areas, not deficiencies.
- Do not guarantee job placement or interview outcomes.
- Keep it plain text, no markdown headers.
"""

    try:
        import google.generativeai as genai
        from google.generativeai.types import RequestOptions
        from google.api_core import retry as _retry

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            request_options=RequestOptions(
                timeout=15, retry=_retry.Retry(initial=1, maximum=5, multiplier=2, deadline=15)
            ),
        )
        return response.text.strip()
    except Exception as exc:  # noqa: BLE001 - surface any failure to the UI, don't crash
        return f"⚠️ AI feedback unavailable right now ({exc.__class__.__name__}). Showing rule-based results only."
