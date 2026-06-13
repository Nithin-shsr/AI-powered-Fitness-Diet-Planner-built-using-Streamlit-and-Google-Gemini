# utils/calculations.py
"""
Health & fitness calculation helpers for AI Fitness Planner.

All formulas use internationally recognised standards:
  - BMI   : WHO classification
  - BMR   : Mifflin-St Jeor equation (1990) – more accurate than Harris-Benedict
  - TDEE  : Mifflin BMR × activity multiplier
  - Protein: 1.6–2.2 g / kg body-weight range (ISSN recommendation)
  - Water  : 35 ml / kg body-weight (European Food Safety Authority guideline)
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Activity-level multipliers (Mifflin-St Jeor TDEE)
# ---------------------------------------------------------------------------

ACTIVITY_MULTIPLIERS: dict[str, float] = {
    "Sedentary": 1.2,          # Little or no exercise
    "Lightly Active": 1.375,   # 1–3 days/week
    "Moderately Active": 1.55, # 3–5 days/week
    "Very Active": 1.725,      # 6–7 days/week
    "Extra Active": 1.9,       # Twice per day / physical job
}

# ---------------------------------------------------------------------------
# Goal-based calorie adjustments
# ---------------------------------------------------------------------------

GOAL_CALORIE_DELTA: dict[str, int] = {
    "Weight Loss": -500,
    "Aggressive Weight Loss": -750,
    "Maintenance": 0,
    "Muscle Gain": +300,
    "Aggressive Muscle Gain": +500,
}


# ---------------------------------------------------------------------------
# BMI
# ---------------------------------------------------------------------------

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Return BMI rounded to 1 decimal place."""
    if height_cm <= 0:
        return 0.0
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def bmi_category(bmi: float) -> tuple[str, str]:
    """Return (category_label, colour_hex) for a given BMI value."""
    if bmi < 18.5:
        return "Underweight", "#60a5fa"       # blue
    elif bmi < 25.0:
        return "Normal Weight", "#34d399"     # green
    elif bmi < 30.0:
        return "Overweight", "#fbbf24"        # amber
    else:
        return "Obese", "#f87171"             # red


# ---------------------------------------------------------------------------
# BMR  (Mifflin-St Jeor)
# ---------------------------------------------------------------------------

def calculate_bmr(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
) -> float:
    """
    Return Basal Metabolic Rate in kcal/day.

    Formula:
        Male   : 10·W + 6.25·H − 5·A + 5
        Female : 10·W + 6.25·H − 5·A − 161
    """
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    bmr = base + 5 if gender.lower() == "male" else base - 161
    return round(bmr, 0)


# ---------------------------------------------------------------------------
# TDEE / Daily Calories
# ---------------------------------------------------------------------------

def calculate_daily_calories(
    bmr: float,
    activity_level: str,
    fitness_goal: str = "Maintenance",
) -> int:
    """Return recommended daily calorie intake after applying goal delta."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    tdee = bmr * multiplier
    delta = GOAL_CALORIE_DELTA.get(fitness_goal, 0)
    return max(1200, round(tdee + delta))   # never below 1 200 kcal


# ---------------------------------------------------------------------------
# Macros
# ---------------------------------------------------------------------------

def calculate_protein(weight_kg: float, fitness_goal: str) -> tuple[int, int]:
    """
    Return (min_g, max_g) daily protein range.

    Higher end for muscle-gain goals; moderate for weight loss / maintenance.
    """
    if "Muscle" in fitness_goal:
        low, high = 1.8, 2.2
    elif "Weight Loss" in fitness_goal:
        low, high = 1.6, 2.0   # higher protein during deficit preserves muscle
    else:
        low, high = 1.4, 1.8

    return round(weight_kg * low), round(weight_kg * high)


# ---------------------------------------------------------------------------
# Hydration
# ---------------------------------------------------------------------------

def calculate_water_intake(weight_kg: float) -> float:
    """Return recommended daily water intake in litres (35 ml / kg)."""
    return round(weight_kg * 35 / 1000, 1)


# ---------------------------------------------------------------------------
# Weight-goal timeline estimate
# ---------------------------------------------------------------------------

def estimate_goal_weeks(
    current_weight: float,
    target_weight: float,
    fitness_goal: str,
) -> int | None:
    """
    Rough estimate of weeks to reach target weight.
    Assumes ~0.5 kg/week for weight loss, ~0.25 kg/week for muscle gain.
    Returns None for maintenance or if already at goal.
    """
    diff = abs(current_weight - target_weight)
    if diff < 0.5:
        return None
    rate = 0.5 if "Weight Loss" in fitness_goal else 0.25
    return round(diff / rate)
