# utils/workout_generator.py
"""
Reusable helper functions for AI-powered workout plan generation.
Uses Google Gemini API to generate personalised workout plans based on
user profile and workout preferences.

Follows the same architecture as diet_generator.py.
"""

from __future__ import annotations

import json
import logging
import re
import textwrap
from typing import Any

import google.generativeai as genai

# Reuse shared helpers from diet_generator (no code duplication)
from utils.diet_generator import _get_gemini_client, _extract_json

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_workout_prompt(
    *,
    # Profile fields
    name: str,
    age: int,
    gender: str,
    weight_kg: float,
    height_cm: float,
    fitness_goal: str,
    activity_level: str,
    # Workout-planner-specific inputs
    workout_days: int,
    workout_duration: int,
    workout_location: str,
    experience_level: str,
    equipment: str,
    primary_goal: str,
    focus_areas: list[str],
    injuries: str,
) -> str:
    """
    Build a structured prompt for Gemini to generate a weekly workout plan.
    Returns a plain string prompt.
    """
    injury_note = injuries.strip() or "None"
    focus_note = ", ".join(focus_areas) if focus_areas else "Full Body"

    # Build the day keys for the schema example
    day_keys = [f"day_{i}" for i in range(1, workout_days + 1)]
    day_schema_entries = ",\n        ".join(
        f'"{dk}": {{'
        f'"title": "Day {i} title",'
        f'"target_muscles": "target muscle groups",'
        f'"duration_minutes": {workout_duration},'
        f'"warmup": ["exercise 1", "exercise 2"],'
        f'"main_workout": ['
        f'{{"exercise": "exercise name", "sets": 3, "reps": "10-12", "rest_seconds": 60}}'
        f'],'
        f'"cooldown": ["stretch 1", "stretch 2"]'
        f'}}'
        for i, dk in enumerate(day_keys, 1)
    )

    prompt = textwrap.dedent(f"""
    You are an expert certified personal trainer and exercise scientist.
    Generate a completely personalised, science-backed weekly workout plan
    for the following person:

    === USER PROFILE ===
    Name            : {name}
    Age             : {age} years
    Gender          : {gender}
    Weight          : {weight_kg} kg
    Height          : {height_cm} cm
    Fitness Goal    : {fitness_goal}
    Activity Level  : {activity_level}

    === WORKOUT PREFERENCES ===
    Workout Days/Week   : {workout_days}
    Session Duration    : {workout_duration} minutes
    Workout Location    : {workout_location}
    Experience Level    : {experience_level}
    Equipment Available : {equipment}
    Primary Goal        : {primary_goal}
    Focus Areas         : {focus_note}
    Injuries/Limitations: {injury_note}

    === OUTPUT FORMAT (STRICT JSON) ===
    Return ONLY a valid JSON object — no markdown fences, no explanations.
    The JSON must follow this exact schema:

    {{
      "plan_summary": "Brief overview of the plan rationale (max 80 words)",
      "weekly_schedule": {{
        {day_schema_entries}
      }},
      "tips": [
        "Tip 1 specific to this user",
        "Tip 2",
        "Tip 3"
      ],
      "progression_advice": "Short advice on how to progress (max 60 words)"
    }}

    Rules:
    - Generate exactly {workout_days} days in the weekly_schedule.
    - Each day key must be day_1, day_2, … day_{workout_days}.
    - Each day's value must be a JSON object, NOT HTML.
    - warmup MUST be an array of strings (3-4 items, each under 10 words).
    - main_workout MUST be an array of exercise objects (4-6 exercises).
    - cooldown MUST be an array of strings (2-3 items, each under 10 words).
    - STRICT PROHIBITION: NO HTML tags may appear anywhere in your response. Do not generate <div>, <table>, <span>, or any HTML.
    - Keep exercise names short (under 8 words).
    - Sets must be realistic integers (2-5).
    - Reps must be a string like "8-10", "12-15", "30 sec", or "to failure".
    - Rest_seconds must be a realistic integer (30-120).
    - Duration_minutes must equal {workout_duration} for every day.
    - Respect ALL injuries and limitations strictly — avoid exercises that
      could aggravate them.
    - Only include exercises possible with "{equipment}".
    - If location is "Home", no gym-only machines.
    - Include exactly 3 workout tips.
    - "plan_summary" must be UNDER 80 words.
    - "progression_advice" must be UNDER 60 words.
    - Return valid JSON only. Do not truncate. Do not use markdown.
    - Output ONLY the JSON. Do not wrap it in triple backticks or any prose.
    """)
    return prompt.strip()


# ---------------------------------------------------------------------------
# Plan generator
# ---------------------------------------------------------------------------

def generate_workout_plan(prompt: str) -> dict[str, Any]:
    """
    Call Gemini with the given prompt and return the parsed workout plan dict.

    Returns a dict with keys: plan_summary, weekly_schedule, tips,
    progression_advice.

    Uses structured JSON generation (response_mime_type) for reliability,
    an increased token limit to avoid truncation, and one automatic retry
    if JSON parsing fails on the first attempt.

    Raises:
        RuntimeError: if the API call fails or JSON cannot be parsed
                      after retry.
    """
    model = _get_gemini_client()

    generation_config = genai.types.GenerationConfig(
        temperature=0.7,
        max_output_tokens=8192,
        response_mime_type="application/json",
    )

    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
        )
    except Exception as exc:
        raise RuntimeError(f"Gemini API error: {exc}") from exc

    raw_text = response.text.strip()
    logger.info("Gemini workout response length: %d characters", len(raw_text))

    # Strip any accidental markdown fences that the model may add
    raw_text = re.sub(r"^```(?:json)?", "", raw_text, flags=re.MULTILINE).strip()
    raw_text = re.sub(r"```$", "", raw_text, flags=re.MULTILINE).strip()

    # Extract the JSON object safely
    json_text = _extract_json(raw_text)

    try:
        plan = json.loads(json_text)
        return plan
    except json.JSONDecodeError as first_err:
        logger.warning(
            "First workout JSON parse failed (%s). Retrying with stricter prompt…",
            first_err,
        )

    # ── Retry: one additional call with an explicit instruction ────────────
    retry_prompt = (
        prompt
        + "\n\nIMPORTANT: Return valid JSON only. Do not truncate. "
        "Do not use markdown. Keep all text values short and concise."
    )

    try:
        response = model.generate_content(
            retry_prompt,
            generation_config=generation_config,
        )
    except Exception as exc:
        raise RuntimeError(f"Gemini API error on retry: {exc}") from exc

    raw_text = response.text.strip()
    logger.info("Gemini workout RETRY response length: %d characters", len(raw_text))

    raw_text = re.sub(r"^```(?:json)?", "", raw_text, flags=re.MULTILINE).strip()
    raw_text = re.sub(r"```$", "", raw_text, flags=re.MULTILINE).strip()

    json_text = _extract_json(raw_text)

    try:
        plan = json.loads(json_text)
        return plan
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Could not parse Gemini workout response as JSON after retry.\n"
            f"Parse error: {exc}\n"
            f"Raw response (first 500 chars): {json_text[:500]}"
        ) from exc


# ---------------------------------------------------------------------------
# Convenience wrapper
# ---------------------------------------------------------------------------

def get_personalized_workout_plan(
    profile: dict,
    workout_inputs: dict,
) -> dict[str, Any]:
    """
    High-level helper that combines profile + workout inputs, builds the
    prompt, calls Gemini, and returns the parsed plan dict.

    Args:
        profile       : st.session_state.profile dict
        workout_inputs: dict with keys matching build_workout_prompt kwargs
                        (workout_days, workout_duration, workout_location,
                         experience_level, equipment, primary_goal,
                         focus_areas, injuries)

    Returns:
        Parsed workout plan dict or raises RuntimeError on failure.
    """
    prompt = build_workout_prompt(
        name=profile.get("name", "User"),
        age=int(profile.get("age", 25)),
        gender=profile.get("gender", "Male"),
        weight_kg=float(profile.get("weight_kg", 70.0)),
        height_cm=float(profile.get("height_cm", 170.0)),
        fitness_goal=profile.get("fitness_goal", "Maintenance"),
        activity_level=profile.get("activity_level", "Moderately Active"),
        **workout_inputs,
    )
    return generate_workout_plan(prompt)


# ---------------------------------------------------------------------------
# Utility constants
# ---------------------------------------------------------------------------

DAY_ICONS = {
    "day_1": ("📅", "#6c63ff"),
    "day_2": ("📅", "#00d4ff"),
    "day_3": ("📅", "#34d399"),
    "day_4": ("📅", "#fbbf24"),
    "day_5": ("📅", "#ff6584"),
    "day_6": ("📅", "#a78bfa"),
    "day_7": ("📅", "#f97316"),
}

WORKOUT_SECTION_ICONS = {
    "warmup":       "🔥",
    "main_workout": "💪",
    "cooldown":     "🧘",
}
