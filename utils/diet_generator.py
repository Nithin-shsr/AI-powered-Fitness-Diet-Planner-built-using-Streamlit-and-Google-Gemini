# utils/diet_generator.py
"""
Reusable helper functions for AI-powered diet plan generation.
Uses Google Gemini API to generate personalised meal plans based on
user profile and diet preferences.
"""

from __future__ import annotations

import os
import json
import logging
import re
import textwrap
from typing import Any

import google.generativeai as genai

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# TODO: Migrate google.generativeai to google.genai package in the future
# once it can be done safely without breaking existing functionality.


# ---------------------------------------------------------------------------
# Gemini client initialisation
# ---------------------------------------------------------------------------

def _get_gemini_client() -> genai.GenerativeModel:
    """Initialise and return a Gemini GenerativeModel instance."""

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "GOOGLE_API_KEY is not set. Please add it to your .env file."
        )

    genai.configure(api_key=api_key)

    preferred_models = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ]

    for model_name in preferred_models:
        try:
            return genai.GenerativeModel(model_name)
        except Exception:
            continue

    raise RuntimeError(
        "Unable to initialize any supported Gemini model."
    )


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def build_diet_prompt(
    *,
    # Profile fields
    name: str,
    age: int,
    gender: str,
    weight_kg: float,
    height_cm: float,
    fitness_goal: str,
    # Diet-planner-specific inputs
    meals_per_day: int,
    diet_type: str,          # Vegetarian | Non-Vegetarian | Vegan
    dietary_restrictions: str,
    food_allergies: str,
    daily_calorie_target: int,
    protein_target_g: int,
    budget_preference: str,
    preferred_cuisine: str,
    weight_goal: str,        # Weight Loss | Maintenance | Weight Gain
) -> str:
    """
    Build a structured prompt for Gemini to generate a full-day diet plan.
    Returns a plain string prompt.
    """
    allergy_note = food_allergies.strip() or "None"
    restriction_note = dietary_restrictions.strip() or "None"

    prompt = textwrap.dedent(f"""
    You are an expert certified nutritionist and dietitian. Generate a completely
    personalised, science-backed daily diet plan for the following person:

    === USER PROFILE ===
    Name                : {name}
    Age                 : {age} years
    Gender              : {gender}
    Weight              : {weight_kg} kg
    Height              : {height_cm} cm
    Overall Fitness Goal: {fitness_goal}

    === DIET PREFERENCES ===
    Diet Type           : {diet_type}
    Dietary Restrictions: {restriction_note}
    Food Allergies      : {allergy_note}
    Daily Calorie Target: {daily_calorie_target} kcal
    Protein Target      : {protein_target_g} g/day
    Budget Preference   : {budget_preference}
    Preferred Cuisine   : {preferred_cuisine}
    Weight Goal         : {weight_goal}
    Meals Per Day       : {meals_per_day}

    === OUTPUT FORMAT (STRICT JSON) ===
    Return ONLY a valid JSON object — no markdown fences, no explanations.
    The JSON must follow this exact schema:

    {{
      "plan_summary": "Brief overview of the plan rationale (max 80 words)",
      "meals": {{
        "breakfast": {{
          "items": ["item 1", "item 2"],
          "calories": 450,
          "protein_g": 30,
          "explanation": "Short reason (max 20 words)"
        }},
        "morning_snack": {{
          "items": ["item 1"],
          "calories": 150,
          "protein_g": 8,
          "explanation": "Short reason (max 20 words)"
        }},
        "lunch": {{
          "items": ["item 1", "item 2", "item 3"],
          "calories": 600,
          "protein_g": 40,
          "explanation": "Short reason (max 20 words)"
        }},
        "evening_snack": {{
          "items": ["item 1"],
          "calories": 100,
          "protein_g": 5,
          "explanation": "Short reason (max 20 words)"
        }},
        "dinner": {{
          "items": ["item 1", "item 2"],
          "calories": 500,
          "protein_g": 35,
          "explanation": "Short reason (max 20 words)"
        }}
      }},
      "daily_totals": {{
        "total_calories": 1800,
        "total_protein_g": 118,
        "calorie_vs_target": "18 kcal under target",
        "protein_vs_target": "3 g above target"
      }},
      "grocery_list": {{
        "proteins": ["item1", "item2", "item3", "item4", "item5"],
        "vegetables": ["item1", "item2", "item3", "item4", "item5"],
        "fruits": ["item1", "item2", "item3", "item4", "item5"],
        "grains": ["item1", "item2", "item3", "item4", "item5"],
        "dairy_or_alternatives": ["item1", "item2", "item3", "item4", "item5"],
        "pantry": ["item1", "item2", "item3", "item4", "item5"]
      }},
      "nutrition_tips": [
        "Tip 1 specific to this user",
        "Tip 2",
        "Tip 3"
      ]
    }}

    Rules:
    - All calorie and protein numbers must be realistic integers.
    - Respect ALL allergies and dietary restrictions strictly.
    - Keep budget in mind — prefer affordable, whole foods for "Low" budget.
    - Cuisine preference should influence food choices where possible.
    - If meals_per_day < 5, set calories/protein to 0 and items to [] for
      morning_snack and/or evening_snack as appropriate.
    - Each meal "explanation" must be UNDER 20 words.
    - "plan_summary" must be UNDER 80 words.
    - Each grocery category must have AT MOST 5 items.
    - Include exactly 3 nutrition tips.
    - Keep food item descriptions short (under 8 words each).
    - Return valid JSON only. Do not truncate. Do not use markdown.
    - Output ONLY the JSON. Do not wrap it in triple backticks or any prose.
    """)
    return prompt.strip()


# ---------------------------------------------------------------------------
# JSON extraction helper
# ---------------------------------------------------------------------------

def _extract_json(raw_text: str) -> str:
    """
    Safely extract a JSON object from *raw_text* by locating the first '{'
    and the last '}', then returning only that substring.

    Falls back to returning the full text stripped if no braces are found.
    """
    first = raw_text.find("{")
    last = raw_text.rfind("}")
    if first != -1 and last != -1 and last > first:
        return raw_text[first : last + 1]
    return raw_text.strip()

def _clean_malformed_json(json_str: str) -> str:
    """
    Attempt to clean up common JSON formatting errors introduced by LLMs.
    """
    # Remove trailing commas before closing braces/brackets
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    # Strip any remaining markdown or HTML wrapper that might have bypassed previous steps
    json_str = json_str.replace("```json", "").replace("```", "")
    json_str = re.sub(r'<[^>]+>', '', json_str)
    return json_str.strip()


# ---------------------------------------------------------------------------
# Plan generator
# ---------------------------------------------------------------------------

def generate_diet_plan(prompt: str) -> dict[str, Any]:
    """
    Call Gemini with the given prompt and return the parsed diet plan dict.

    Returns a dict with keys: plan_summary, meals, daily_totals,
    grocery_list, nutrition_tips.

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
        logger.info("Diet plan request sent to Gemini.")
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
        )
        logger.info("Diet plan response received.")
    except Exception as exc:
        logger.error("API failure during diet plan generation: %s", exc)
        raise RuntimeError("Network or API failure. Please try again.") from exc

    raw_text = response.text.strip()
    
    # Strip any accidental markdown fences that the model may add
    raw_text = re.sub(r"^```(?:json)?", "", raw_text, flags=re.MULTILINE).strip()
    raw_text = re.sub(r"```$", "", raw_text, flags=re.MULTILINE).strip()

    # Extract the JSON object safely
    json_text = _extract_json(raw_text)

    try:
        plan = json.loads(json_text)
        return plan
    except json.JSONDecodeError as first_err:
        logger.warning("First JSON parse failed (%s). Attempting automatic cleanup...", first_err)
        cleaned_text = _clean_malformed_json(json_text)
        try:
            plan = json.loads(cleaned_text)
            logger.info("Automatic cleanup successful.")
            return plan
        except json.JSONDecodeError as cleanup_err:
            logger.error("JSON parsing failure after cleanup: %s", cleanup_err)
            logger.info("Retry triggered for diet plan.")

    # ── Retry: one additional call with an explicit instruction ────────────
    retry_prompt = (
        prompt
        + "\n\nIMPORTANT: Return valid JSON only. Do not truncate. "
        "Do not use markdown. Keep all text values short and concise."
    )

    try:
        logger.info("Retry diet plan request sent.")
        response = model.generate_content(
            retry_prompt,
            generation_config=generation_config,
        )
        logger.info("Retry diet plan response received.")
    except Exception as exc:
        logger.error("API failure on retry: %s", exc)
        raise RuntimeError("Failed to connect to the AI model on retry. Please try again.") from exc

    raw_text = response.text.strip()

    raw_text = re.sub(r"^```(?:json)?", "", raw_text, flags=re.MULTILINE).strip()
    raw_text = re.sub(r"```$", "", raw_text, flags=re.MULTILINE).strip()

    json_text = _extract_json(raw_text)

    try:
        plan = json.loads(json_text)
        return plan
    except json.JSONDecodeError as exc:
        logger.error("Final JSON parsing failure: %s", exc)
        raise RuntimeError(
            "The AI generated an invalid diet plan format. Please try generating again."
        ) from exc


# ---------------------------------------------------------------------------
# Convenience wrapper
# ---------------------------------------------------------------------------

def get_personalized_diet_plan(
    profile: dict,
    diet_inputs: dict,
) -> dict[str, Any]:
    """
    High-level helper that combines profile + diet inputs, builds the prompt,
    calls Gemini, and returns the parsed plan dict.

    Args:
        profile   : st.session_state.profile dict
        diet_inputs: dict with keys matching build_diet_prompt kwargs
                     (meals_per_day, diet_type, dietary_restrictions,
                      food_allergies, daily_calorie_target,
                      protein_target_g, budget_preference,
                      preferred_cuisine, weight_goal)

    Returns:
        Parsed diet plan dict or raises RuntimeError on failure.
    """
    prompt = build_diet_prompt(
        name=profile.get("name", "User"),
        age=int(profile.get("age", 25)),
        gender=profile.get("gender", "Male"),
        weight_kg=float(profile.get("weight_kg", 70.0)),
        height_cm=float(profile.get("height_cm", 170.0)),
        fitness_goal=profile.get("fitness_goal", "Maintenance"),
        **diet_inputs,
    )
    return generate_diet_plan(prompt)


# ---------------------------------------------------------------------------
# Utility: safe meal key list (ordered)
# ---------------------------------------------------------------------------

MEAL_ORDER = [
    ("breakfast",     "🌅 Breakfast",       "#6c63ff"),
    ("morning_snack", "🍎 Morning Snack",   "#00d4ff"),
    ("lunch",         "🍽️ Lunch",           "#34d399"),
    ("evening_snack", "🥜 Evening Snack",   "#fbbf24"),
    ("dinner",        "🌙 Dinner",          "#ff6584"),
]

GROCERY_CATEGORY_ICONS = {
    "proteins":             "🥩",
    "vegetables":           "🥦",
    "fruits":               "🍎",
    "grains":               "🌾",
    "dairy_or_alternatives":"🥛",
    "pantry":               "🫙",
}
