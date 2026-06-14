# pages/diet_planner.py
"""
Diet Planner page — Phase 2.
Generates a fully personalised AI-powered diet plan using Google Gemini.
Reads base profile from session_state and accepts additional diet-specific inputs.
"""

from __future__ import annotations

import streamlit as st

from utils.session_manager import init_session_state, get_profile, is_profile_complete
from utils.styles import section_header, styled_divider
from utils.diet_generator import (
    get_personalized_diet_plan,
    MEAL_ORDER,
    GROCERY_CATEGORY_ICONS,
)
from utils.calculations import calculate_daily_calories, calculate_bmr, calculate_protein


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DIET_TYPES = ["Non-Vegetarian", "Vegetarian", "Vegan"]
BUDGET_OPTIONS = ["Low (budget-friendly)", "Medium (moderate spend)", "High (premium / organic)"]
WEIGHT_GOALS = ["Weight Loss", "Maintenance", "Weight Gain"]

CUISINE_OPTIONS = [
    "Any",
    "Indian",
    "Mediterranean",
    "East Asian",
    "American",
    "Mexican",
    "Middle Eastern",
    "European",
    "Japanese",
    "Italian",
]

ALLERGY_SUGGESTIONS = [
    "Nuts", "Peanuts", "Gluten", "Dairy", "Eggs", "Shellfish",
    "Soy", "Fish", "Sesame", "Sulfites",
]


# ---------------------------------------------------------------------------
# CSS specific to the Diet Planner (injected once per page render)
# ---------------------------------------------------------------------------

DIET_PAGE_CSS = """
<style>
/* ── Meal card ──────────────────────────────────────────────── */
.meal-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    padding: 1.6rem;
    margin-bottom: 1.2rem;
    transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
    position: relative;
    overflow: hidden;
}
.meal-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    border-radius: 4px 0 0 4px;
}
.meal-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 40px var(--shadow);
    border-color: var(--border);
}
.meal-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}
.meal-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
}
.meal-badge-row {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    align-items: center;
}
.meal-stat {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: var(--glass-bg);
    border: 1px solid var(--card-border);
    border-radius: 50px;
    padding: 0.25rem 0.75rem;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-secondary);
}
.meal-items {
    list-style: none;
    padding: 0;
    margin: 0.8rem 0;
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
}
.meal-item-tag {
    background: var(--glass-bg);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    padding: 0.3rem 0.7rem;
    font-size: 0.85rem;
    color: var(--text-primary);
    transition: border-color 0.2s;
}
.meal-item-tag:hover {
    border-color: var(--accent-1);
}
.meal-explanation {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.65;
    margin-top: 0.6rem;
    padding-top: 0.6rem;
    border-top: 1px solid var(--card-border);
}

/* ── Summary card ───────────────────────────────────────────── */
.summary-card {
    background: var(--metric-bg);
    border: 1px solid var(--metric-border);
    border-radius: 18px;
    padding: 1.4rem;
    text-align: center;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.summary-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 32px var(--shadow);
}
.summary-icon  { font-size: 2.2rem; margin-bottom: 0.4rem; }
.summary-label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
                 letter-spacing: 0.08em; color: var(--text-secondary); margin-bottom: 0.25rem; }
.summary-value { font-size: 1.9rem; font-weight: 800; font-family: 'Outfit', sans-serif;
                 background: var(--gradient); -webkit-background-clip: text;
                 -webkit-text-fill-color: transparent; background-clip: text; }
.summary-note  { font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.15rem; }

/* ── Grocery category ───────────────────────────────────────── */
.grocery-section {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.9rem;
    transition: border-color 0.25s;
}
.grocery-section:hover { border-color: var(--border); }
.grocery-cat-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.7rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.grocery-items {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
}
.grocery-chip {
    background: var(--glass-bg);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    padding: 0.22rem 0.7rem;
    font-size: 0.82rem;
    color: var(--text-primary);
    transition: all 0.2s;
}
.grocery-chip:hover {
    background: rgba(var(--accent-1-rgb), 0.12);
    border-color: var(--accent-1);
    color: var(--accent-1);
}

/* ── Tip card ───────────────────────────────────────────────── */
.tip-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
    font-size: 0.88rem;
    color: var(--text-secondary);
    line-height: 1.65;
    display: flex;
    gap: 0.6rem;
    align-items: flex-start;
}
.tip-number {
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
    font-family: 'Outfit', sans-serif;
    font-size: 1rem;
    flex-shrink: 0;
    margin-top: 0.05rem;
}

/* ── Plan summary banner ────────────────────────────────────── */
.plan-summary-banner {
    background: var(--metric-bg);
    border: 1px solid var(--metric-border);
    border-radius: 18px;
    padding: 1.3rem 1.7rem;
    margin-bottom: 1.6rem;
    font-size: 0.92rem;
    color: var(--text-secondary);
    line-height: 1.7;
}
.plan-summary-banner strong { color: var(--text-primary); }

/* ── Guard box ──────────────────────────────────────────────── */
.guard-box {
    text-align: center;
    padding: 3rem 1.5rem;
    background: var(--guard-bg);
    border: 1px dashed var(--guard-border);
    border-radius: 20px;
    margin-top: 1rem;
}
.guard-icon { font-size: 3.5rem; margin-bottom: 0.8rem; }
.guard-title { font-size: 1.3rem; font-weight: 700; color: var(--text-primary);
               margin-bottom: 0.5rem; }
.guard-desc { color: var(--text-secondary); font-size: 0.9rem;
              max-width: 420px; margin: 0 auto 1.5rem; line-height: 1.6; }

/* ── Form section ───────────────────────────────────────────── */
.form-section {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    padding: 1.6rem;
    margin-bottom: 1.2rem;
}

/* ── Loading shimmer ────────────────────────────────────────── */
@keyframes shimmer {
    0%   { background-position: -1000px 0; }
    100% { background-position:  1000px 0; }
}
.shimmer-line {
    height: 18px;
    border-radius: 8px;
    background: linear-gradient(90deg,
        var(--glass-bg) 25%,
        rgba(var(--accent-1-rgb), 0.1) 50%,
        var(--glass-bg) 75%
    );
    background-size: 1000px 100%;
    animation: shimmer 1.6s infinite linear;
    margin-bottom: 0.8rem;
}
.shimmer-line.short  { width: 55%; }
.shimmer-line.medium { width: 75%; }
.shimmer-line.full   { width: 100%; }
</style>
"""


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def _meal_card_html(
    meal_key: str,
    meal_label: str,
    accent: str,
    meal_data: dict,
    skipped: bool = False,
) -> str:
    """Render a meal card as HTML."""
    if skipped or not meal_data.get("items"):
        return f"""
        <div class="meal-card" style="opacity:0.5; border-left: 4px solid {accent};">
            <div class="meal-card-header">
                <div class="meal-title">{meal_label}</div>
                <span style="font-size:0.78rem;color:var(--text-muted);
                      background:var(--glass-bg);border:1px solid var(--card-border);
                      border-radius:50px;padding:0.2rem 0.7rem;">Skipped</span>
            </div>
            <div style="color:var(--text-muted);font-size:0.85rem;">
                Not included in your {meal_data.get('_meals_per_day',5)}-meal plan.
            </div>
        </div>
        """

    cal  = meal_data.get("calories", 0)
    prot = meal_data.get("protein_g", 0)
    expl = meal_data.get("explanation", "")
    items = meal_data.get("items", [])

    items_html = "".join(f'<span class="meal-item-tag">🔸 {i}</span>' for i in items)

    return f"""
    <div class="meal-card" style="border-left: 4px solid {accent};">
        <div class="meal-card-header">
            <div class="meal-title">{meal_label}</div>
            <div class="meal-badge-row">
                <span class="meal-stat">🔥 {cal} kcal</span>
                <span class="meal-stat">💪 {prot}g protein</span>
            </div>
        </div>
        <div class="meal-items">{items_html}</div>
        <div class="meal-explanation">💡 {expl}</div>
    </div>
    """


def _summary_card_html(icon: str, label: str, value: str, note: str = "") -> str:
    return f"""
    <div class="summary-card">
        <div class="summary-icon">{icon}</div>
        <div class="summary-label">{label}</div>
        <div class="summary-value">{value}</div>
        <div class="summary-note">{note}</div>
    </div>
    """


def _grocery_section_html(category: str, items: list[str]) -> str:
    icon = GROCERY_CATEGORY_ICONS.get(category, "🛒")
    title = category.replace("_", " ").replace("or", "/").title()
    chips = "".join(f'<span class="grocery-chip">{item}</span>' for item in items)
    return f"""
    <div class="grocery-section">
        <div class="grocery-cat-title">{icon} {title}</div>
        <div class="grocery-items">{chips}</div>
    </div>
    """


def _tip_html(index: int, tip: str) -> str:
    return f"""
    <div class="tip-card">
        <span class="tip-number">{index}.</span>
        <span>{tip}</span>
    </div>
    """


def _loading_shimmer() -> str:
    return """
    <div style="padding: 1rem 0;">
        <div class="shimmer-line full"></div>
        <div class="shimmer-line medium"></div>
        <div class="shimmer-line short"></div>
        <div class="shimmer-line full" style="margin-top:1rem;"></div>
        <div class="shimmer-line medium"></div>
        <div class="shimmer-line short"></div>
        <div class="shimmer-line full" style="margin-top:1rem;"></div>
        <div class="shimmer-line medium"></div>
    </div>
    """


# ---------------------------------------------------------------------------
# Defaults derived from profile
# ---------------------------------------------------------------------------

def _get_profile_defaults(profile: dict) -> dict:
    """Pre-fill diet planner defaults from existing profile fields."""
    weight   = float(profile.get("weight_kg", 70.0))
    height   = float(profile.get("height_cm", 170.0))
    age      = int(profile.get("age", 25))
    gender   = profile.get("gender", "Male")
    activity = profile.get("activity_level", "Moderately Active")
    goal     = profile.get("fitness_goal", "Maintenance")

    from utils.calculations import calculate_bmr, calculate_daily_calories, calculate_protein
    bmr       = calculate_bmr(weight, height, age, gender)
    rec_cals  = calculate_daily_calories(bmr, activity, goal)
    prot_min, prot_max = calculate_protein(weight, goal)

    # Map fitness_goal → weight_goal
    if "Loss" in goal:
        weight_goal_default = "Weight Loss"
    elif "Gain" in goal or "Muscle" in goal:
        weight_goal_default = "Weight Gain"
    else:
        weight_goal_default = "Maintenance"

    # Map diet_preference → diet_type
    diet_pref = profile.get("diet_preference", "No Restriction")
    if "Vegan" in diet_pref:
        diet_type_default = "Vegan"
    elif "Vegetarian" in diet_pref:
        diet_type_default = "Vegetarian"
    else:
        diet_type_default = "Non-Vegetarian"

    cuisine = profile.get("preferred_cuisine", "Any")

    return {
        "rec_cals": rec_cals,
        "prot_min": prot_min,
        "prot_max": prot_max,
        "weight_goal_default": weight_goal_default,
        "diet_type_default": diet_type_default,
        "cuisine_default": cuisine,
    }


# ---------------------------------------------------------------------------
# Input form section
# ---------------------------------------------------------------------------

def _render_input_form(profile: dict) -> dict | None:
    """
    Render the diet preferences form and return a diet_inputs dict on submit,
    or None if not yet submitted.
    """
    defaults = _get_profile_defaults(profile)

    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    section_header("⚙️ Diet Preferences")

    col1, col2, col3 = st.columns(3)

    with col1:
        meals_per_day = st.selectbox(
            "🍽️ Meals per Day",
            options=[3, 4, 5],
            index=2,
            key="dp_meals_per_day",
            help="3 = main meals only · 4 = + 1 snack · 5 = all meals + 2 snacks",
        )

    with col2:
        diet_type_idx = DIET_TYPES.index(defaults["diet_type_default"]) \
            if defaults["diet_type_default"] in DIET_TYPES else 0
        diet_type = st.selectbox(
            "🌿 Diet Type",
            options=DIET_TYPES,
            index=diet_type_idx,
            key="dp_diet_type",
        )

    with col3:
        wg_idx = WEIGHT_GOALS.index(defaults["weight_goal_default"]) \
            if defaults["weight_goal_default"] in WEIGHT_GOALS else 1
        weight_goal = st.selectbox(
            "🎯 Weight Goal",
            options=WEIGHT_GOALS,
            index=wg_idx,
            key="dp_weight_goal",
        )

    col4, col5 = st.columns(2)

    with col4:
        daily_calorie_target = st.number_input(
            "🔥 Daily Calorie Target (kcal)",
            min_value=800,
            max_value=5000,
            value=int(defaults["rec_cals"]),
            step=50,
            key="dp_calories",
            help=f"Recommended for your profile: {defaults['rec_cals']} kcal",
        )

    with col5:
        protein_target_g = st.number_input(
            "💪 Protein Target (g/day)",
            min_value=30,
            max_value=300,
            value=int(defaults["prot_min"]),
            step=5,
            key="dp_protein",
            help=f"Recommended range: {defaults['prot_min']}–{defaults['prot_max']} g",
        )

    col6, col7 = st.columns(2)

    with col6:
        cuisine_idx = CUISINE_OPTIONS.index(defaults["cuisine_default"]) \
            if defaults["cuisine_default"] in CUISINE_OPTIONS else 0
        preferred_cuisine = st.selectbox(
            "🌍 Preferred Cuisine",
            options=CUISINE_OPTIONS,
            index=cuisine_idx,
            key="dp_cuisine",
        )

    with col7:
        budget_preference = st.selectbox(
            "💰 Budget Preference",
            options=BUDGET_OPTIONS,
            index=1,
            key="dp_budget",
        )

    food_allergies = st.text_input(
        "⚠️ Food Allergies",
        placeholder="e.g. Nuts, Shellfish, Gluten — leave blank if none",
        key="dp_allergies",
        help="Separate multiple allergies with commas.",
    )

    dietary_restrictions = st.text_input(
        "🚫 Additional Dietary Restrictions",
        placeholder="e.g. No spicy food, No processed sugar — leave blank if none",
        key="dp_restrictions",
    )

    st.markdown('</div>', unsafe_allow_html=True)

    col_l, col_btn, col_r = st.columns([1, 2, 1])
    with col_btn:
        generate_clicked = st.button(
            "✨  Generate My Diet Plan",
            use_container_width=True,
            key="dp_generate_btn",
            type="primary",
        )

    if generate_clicked:
        return {
            "meals_per_day": int(meals_per_day),
            "diet_type": diet_type,
            "dietary_restrictions": dietary_restrictions,
            "food_allergies": food_allergies,
            "daily_calorie_target": int(daily_calorie_target),
            "protein_target_g": int(protein_target_g),
            "budget_preference": budget_preference,
            "preferred_cuisine": preferred_cuisine,
            "weight_goal": weight_goal,
        }

    return None


# ---------------------------------------------------------------------------
# Plan display
# ---------------------------------------------------------------------------

def _render_plan(plan: dict, diet_inputs: dict) -> None:
    """Render the full generated diet plan."""

    meals_per_day = diet_inputs.get("meals_per_day", 5)

    # ── Plan summary banner ────────────────────────────────────────────────
    summary_text = plan.get("plan_summary", "")
    if summary_text:
        st.markdown(
            f'<div class="plan-summary-banner">📋 <strong>Plan Overview:</strong> {summary_text}</div>',
            unsafe_allow_html=True,
        )

    # ── Daily summary cards ────────────────────────────────────────────────
    section_header("📊 Daily Nutrition Summary")

    totals = plan.get("daily_totals", {})
    total_cal  = totals.get("total_calories", "—")
    total_prot = totals.get("total_protein_g", "—")
    cal_note   = totals.get("calorie_vs_target", "")
    prot_note  = totals.get("protein_vs_target", "")

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(
            _summary_card_html("🔥", "Total Calories", str(total_cal), "kcal today"),
            unsafe_allow_html=True,
        )
    with sc2:
        st.markdown(
            _summary_card_html("💪", "Total Protein", f"{total_prot}g", "daily protein"),
            unsafe_allow_html=True,
        )
    with sc3:
        st.markdown(
            _summary_card_html("🎯", "Calorie Goal", str(diet_inputs["daily_calorie_target"]), cal_note or "target"),
            unsafe_allow_html=True,
        )
    with sc4:
        st.markdown(
            _summary_card_html("🏆", "Protein Goal", f"{diet_inputs['protein_target_g']}g", prot_note or "target"),
            unsafe_allow_html=True,
        )

    # Status note
    if cal_note:
        st.markdown(
            f"""
            <div style="
                background: rgba(52,211,153,0.08);
                border: 1px solid rgba(52,211,153,0.25);
                border-radius: 12px;
                padding: 0.75rem 1.1rem;
                font-size: 0.85rem;
                color: var(--text-secondary);
                margin: 0.5rem 0 1rem;
                display: flex; gap: 0.6rem; align-items: center;
            ">
                ✅ <span><strong style="color:var(--text-primary)">Calorie:</strong> {cal_note}
                &nbsp;&nbsp;|&nbsp;&nbsp;
                <strong style="color:var(--text-primary)">Protein:</strong> {prot_note}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    styled_divider()

    # ── Meal cards ─────────────────────────────────────────────────────────
    section_header("🍽️ Your Meal Plan")

    meals_data = plan.get("meals", {})

    # Determine which snacks to skip based on meals_per_day
    skip_morning_snack  = meals_per_day < 4
    skip_evening_snack  = meals_per_day < 5

    for meal_key, meal_label, accent in MEAL_ORDER:
        meal_data = meals_data.get(meal_key, {})
        skipped = (
            (meal_key == "morning_snack" and skip_morning_snack) or
            (meal_key == "evening_snack" and skip_evening_snack)
        )
        st.markdown(
            _meal_card_html(meal_key, meal_label, accent, meal_data, skipped=skipped),
            unsafe_allow_html=True,
        )

    styled_divider()

    # ── Grocery list ───────────────────────────────────────────────────────
    section_header("🛒 Weekly Grocery Shopping List")
    st.markdown(
        "<p style='color:var(--text-secondary);font-size:0.88rem;margin-bottom:1rem;'>"
        "Based on your meal plan — shop once and prep for the week.</p>",
        unsafe_allow_html=True,
    )

    grocery = plan.get("grocery_list", {})
    gcol1, gcol2 = st.columns(2)

    grocery_items = list(grocery.items())
    half = (len(grocery_items) + 1) // 2

    with gcol1:
        for cat, items in grocery_items[:half]:
            if items:
                st.markdown(_grocery_section_html(cat, items), unsafe_allow_html=True)

    with gcol2:
        for cat, items in grocery_items[half:]:
            if items:
                st.markdown(_grocery_section_html(cat, items), unsafe_allow_html=True)

    styled_divider()

    # ── Nutrition tips ─────────────────────────────────────────────────────
    tips = plan.get("nutrition_tips", [])
    if tips:
        section_header("💡 Personalised Nutrition Tips")
        for idx, tip in enumerate(tips, 1):
            st.markdown(_tip_html(idx, tip), unsafe_allow_html=True)

    styled_divider()

    # ── Regenerate / reset button row ──────────────────────────────────────
    col_l, col_regen, col_clear, col_r = st.columns([1, 2, 2, 1])
    with col_regen:
        if st.button("🔄  Regenerate Plan", use_container_width=True, key="dp_regen"):
            # Clear stored plan to force a fresh generation
            st.session_state.pop("diet_plan_result", None)
            st.session_state.pop("diet_plan_inputs", None)
            st.rerun()
    with col_clear:
        if st.button("🗑️  Clear & Start Over", use_container_width=True, key="dp_clear"):
            st.session_state.pop("diet_plan_result", None)
            st.session_state.pop("diet_plan_inputs", None)
            st.rerun()

    # ── Disclaimer ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:0.75rem;
            color:var(--text-muted);
            margin-top:1rem;
            padding:0.8rem;
            border-top: 1px solid var(--divider-line);
        ">
            ⚕️ This AI-generated diet plan is for informational purposes only.
            Consult a registered dietitian or healthcare professional before making
            significant dietary changes.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Page renderer (entry point)
# ---------------------------------------------------------------------------

def render() -> None:
    """Render the Diet Planner page."""
    init_session_state()

    # Inject page-specific CSS
    st.markdown(DIET_PAGE_CSS, unsafe_allow_html=True)

    # ── Page header ─────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding: 1.5rem 0 0.5rem;">
            <h1 style="
                font-family:'Outfit',sans-serif;
                font-size:2rem;
                font-weight:800;
                background:var(--gradient);
                -webkit-background-clip:text;
                -webkit-text-fill-color:transparent;
                background-clip:text;
                margin-bottom:0.3rem;
            ">🥗 AI Diet Planner</h1>
            <p style="color:var(--text-secondary);font-size:0.95rem;">
                Powered by Google Gemini · Get a fully personalised meal plan in seconds.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    styled_divider()

    # ── Guard: profile required ─────────────────────────────────────────────
    if not is_profile_complete():
        st.markdown(
            """
            <div class="guard-box">
                <div class="guard-icon">🔒</div>
                <div class="guard-title">Profile Required</div>
                <div class="guard-desc">
                    Please complete your profile first so we can personalise
                    your diet plan with your body metrics and fitness goals.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_l, col_btn, col_r = st.columns([2, 1, 2])
        with col_btn:
            if st.button("👤  Go to Profile", use_container_width=True, key="diet_goto_profile"):
                st.session_state.current_page = "Profile"
                st.rerun()
        return

    profile = get_profile()

    # ── Profile preview strip ───────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background: var(--welcome-bg);
            border: 1px solid var(--welcome-border);
            border-radius: 14px;
            padding: 0.9rem 1.3rem;
            margin-bottom: 1.4rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            flex-wrap: wrap;
        ">
            <div style="font-size:1.8rem;">👤</div>
            <div>
                <div style="font-weight:700;color:var(--text-primary);font-size:0.95rem;">
                    {profile.get('name','User')}
                </div>
                <div style="color:var(--text-secondary);font-size:0.82rem;margin-top:0.15rem;">
                    {profile.get('age')} yrs · {profile.get('gender')} ·
                    {profile.get('weight_kg')} kg · {profile.get('height_cm')} cm ·
                    Goal: <strong style="color:var(--accent-1);">{profile.get('fitness_goal','—')}</strong> ·
                    Diet: <strong style="color:var(--accent-2);">{profile.get('diet_preference','—')}</strong>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Check if a plan is already stored in session state ──────────────────
    if "diet_plan_result" in st.session_state and "diet_plan_inputs" in st.session_state:
        stored_plan   = st.session_state["diet_plan_result"]
        stored_inputs = st.session_state["diet_plan_inputs"]

        st.success("✅ Your diet plan is ready! Scroll down to explore it.", icon="🥗")
        st.markdown(
            "<p style='color:var(--text-secondary);font-size:0.85rem;margin-bottom:0.8rem;'>"
            "This plan is stored for this session. Click <strong>Regenerate</strong> for a fresh plan "
            "or adjust your preferences below and generate again.</p>",
            unsafe_allow_html=True,
        )

        # Show form again (collapsed via expander) for quick re-generation
        with st.expander("🔧 Adjust Preferences & Regenerate", expanded=False):
            new_inputs = _render_input_form(profile)
            if new_inputs:
                # User clicked generate inside expander → regenerate
                with st.spinner(""):
                    shimmer_placeholder = st.empty()
                    shimmer_placeholder.markdown(_loading_shimmer(), unsafe_allow_html=True)
                    try:
                        new_plan = get_personalized_diet_plan(profile, new_inputs)
                        shimmer_placeholder.empty()
                        st.session_state["diet_plan_result"] = new_plan
                        st.session_state["diet_plan_inputs"] = new_inputs
                        st.rerun()
                    except RuntimeError as exc:
                        shimmer_placeholder.empty()
                        st.error(f"⚠️ Could not generate plan: {exc}")
                        st.info(
                            "Possible causes: invalid API key, network issue, or unexpected "
                            "model response. Please try again in a moment."
                        )

        styled_divider()
        _render_plan(stored_plan, stored_inputs)
        return

    # ── No plan yet → show input form ──────────────────────────────────────
    diet_inputs = _render_input_form(profile)

    if diet_inputs is None:
        # Not yet submitted — show a teaser
        st.markdown(
            """
            <div style="
                text-align:center;
                padding:2.5rem 1rem;
                margin-top:0.5rem;
                background:var(--card-bg);
                border:1px dashed var(--card-border);
                border-radius:20px;
            ">
                <div style="font-size:3.5rem;margin-bottom:0.8rem;">🥗</div>
                <div style="font-weight:700;font-size:1.1rem;color:var(--text-primary);
                            margin-bottom:0.5rem;">Ready to build your meal plan?</div>
                <div style="color:var(--text-secondary);font-size:0.9rem;max-width:420px;
                            margin:0 auto;line-height:1.65;">
                    Fill in your preferences above and click
                    <strong>Generate My Diet Plan</strong> to get a fully
                    personalised, AI-powered meal plan with grocery list and tips.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Generate plan ───────────────────────────────────────────────────────
    gen_placeholder = st.empty()
    gen_placeholder.markdown(
        """
        <div style="
            text-align:center;
            padding:1.5rem;
            background:linear-gradient(135deg,rgba(108,99,255,0.08),rgba(0,212,255,0.04));
            border:1px solid rgba(108,99,255,0.2);
            border-radius:16px;
            margin:1rem 0;
        ">
            <div style="font-size:2.5rem;margin-bottom:0.6rem;">🤖</div>
            <div style="font-weight:700;color:var(--text-primary);font-size:1rem;margin-bottom:0.3rem;">
                Gemini is crafting your personalised diet plan…
            </div>
            <div style="color:var(--text-secondary);font-size:0.85rem;">
                Analysing your profile, goals, and preferences — this usually takes 10–20 seconds.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    shimmer_ph = st.empty()
    shimmer_ph.markdown(_loading_shimmer(), unsafe_allow_html=True)

    try:
        plan = get_personalized_diet_plan(profile, diet_inputs)
        # Store in session state so it persists during the session
        st.session_state["diet_plan_result"] = plan
        st.session_state["diet_plan_inputs"] = diet_inputs
        gen_placeholder.empty()
        shimmer_ph.empty()
        st.success("✅ Your personalised diet plan is ready!", icon="🥗")
        _render_plan(plan, diet_inputs)

    except RuntimeError as exc:
        gen_placeholder.empty()
        shimmer_ph.empty()
        st.error("⚠️ Diet Plan Generation Failed")
        st.markdown(
            f"""
            <div style="
                background:rgba(248,113,113,0.06);
                border:1px solid rgba(248,113,113,0.25);
                border-radius:14px;
                padding:1rem 1.2rem;
                font-size:0.88rem;
                color:var(--text-secondary);
                line-height:1.65;
                margin-top:0.5rem;
            ">
                <strong style="color:var(--danger);">Error details:</strong><br/>
                {exc}<br/><br/>
                <strong>What you can try:</strong><br/>
                • Check that your <code>GOOGLE_API_KEY</code> in <code>.env</code> is valid<br/>
                • Ensure you have an active internet connection<br/>
                • Wait a moment and try generating again
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_l2, col_retry, col_r2 = st.columns([2, 1, 2])
        with col_retry:
            if st.button("🔁  Try Again", use_container_width=True, key="dp_retry"):
                st.rerun()
