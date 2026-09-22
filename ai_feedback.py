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
        from google import genai
        from google.genai import types, errors

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                http_options=types.HttpOptions(
                    timeout=15_000,  # milliseconds
                    retry_options=types.HttpRetryOptions(
                        attempts=3,
                        initial_delay=1.0,
                        max_delay=5.0,
                        http_status_codes=[429, 500, 502, 503, 504],
                    ),
                )
            ),
        )

        text = (response.text or "").strip()
        if not text:
            # The call succeeded but returned nothing usable (e.g. the
            # response was blocked by safety filters) — fail gracefully
            # instead of showing an empty box.
            return (
                "⚠️ AI feedback unavailable right now (empty response). "
                "Showing rule-based results only."
            )
        return text

    except errors.ClientError as exc:
        # 4xx: bad key, bad model name, quota exceeded, etc. Give a specific,
        # actionable reason instead of a raw exception name.
        if exc.code in (401, 403):
            reason = "invalid or unauthorized API key"
        elif exc.code == 404:
            reason = "model not found — check the model name is current"
        elif exc.code == 429:
            reason = "rate limit or quota exceeded"
        else:
            reason = exc.message or "request rejected"
        return f"⚠️ AI feedback unavailable right now ({reason}). Showing rule-based results only."

    except errors.ServerError:
        # 5xx: transient issue on Google's side, already retried above.
        return (
            "⚠️ AI feedback unavailable right now (Gemini is temporarily "
            "unreachable). Showing rule-based results only."
        )

    except TimeoutError:
        return (
            "⚠️ AI feedback unavailable right now (request timed out). "
            "Showing rule-based results only."
        )

    except Exception as exc:  # noqa: BLE001 - last-resort safety net, never crash the app
        return f"⚠️ AI feedback unavailable right now ({exc.__class__.__name__}). Showing rule-based results only."
