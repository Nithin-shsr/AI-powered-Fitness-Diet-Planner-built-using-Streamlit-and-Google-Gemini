# pages/workout_planner.py
"""
Workout Planner page — Phase 3.
Generates a fully personalised AI-powered workout plan using Google Gemini.
Reads base profile from session_state and accepts additional workout-specific inputs.
"""

from __future__ import annotations

import streamlit as st

from utils.session_manager import init_session_state, get_profile, is_profile_complete
from utils.styles import section_header, styled_divider
from utils.workout_generator import (
    get_personalized_workout_plan,
    DAY_ICONS,
    WORKOUT_SECTION_ICONS,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORKOUT_DAYS_OPTIONS = [3, 4, 5, 6, 7]
DURATION_OPTIONS = [30, 45, 60, 90]
LOCATION_OPTIONS = ["Home", "Gym"]
EXPERIENCE_OPTIONS = ["Beginner", "Intermediate", "Advanced"]
EQUIPMENT_OPTIONS = ["Bodyweight Only", "Dumbbells", "Resistance Bands", "Full Gym"]
PRIMARY_GOAL_OPTIONS = [
    "Fat Loss",
    "Muscle Gain",
    "Strength",
    "Endurance",
    "General Fitness",
]
FOCUS_AREA_OPTIONS = ["Chest", "Back", "Legs", "Shoulders", "Arms", "Core"]


# ---------------------------------------------------------------------------
# CSS specific to the Workout Planner (injected once per page render)
# ---------------------------------------------------------------------------

WORKOUT_PAGE_CSS = """
<style>
/* ── Day card ──────────────────────────────────────────────── */
.day-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    padding: 1.6rem;
    margin-bottom: 1.2rem;
    transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
    position: relative;
    overflow: hidden;
}
.day-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    border-radius: 4px 0 0 4px;
}
.day-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 40px var(--shadow);
    border-color: var(--border);
}
.day-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}
.day-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-primary);
}
.day-badge-row {
    display: flex;
    gap: 0.6rem;
    flex-wrap: wrap;
    align-items: center;
}
.day-stat {
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

/* ── Section label inside day card ─────────────────────────── */
.wo-section-label {
    font-size: 0.82rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
    margin: 1rem 0 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

/* ── Exercise list items ───────────────────────────────────── */
.wo-item-tag {
    background: var(--glass-bg);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    padding: 0.3rem 0.7rem;
    font-size: 0.85rem;
    color: var(--text-primary);
    transition: border-color 0.2s;
    display: inline-block;
    margin: 0.15rem 0.2rem;
}
.wo-item-tag:hover {
    border-color: var(--accent-1);
}

/* ── Exercise table ────────────────────────────────────────── */
.wo-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 0.5rem 0;
    font-size: 0.85rem;
}
.wo-table thead th {
    background: var(--glass-bg);
    color: var(--text-secondary);
    font-weight: 700;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 0.55rem 0.8rem;
    text-align: left;
    border-bottom: 1px solid var(--card-border);
}
.wo-table thead th:first-child { border-radius: 10px 0 0 0; }
.wo-table thead th:last-child  { border-radius: 0 10px 0 0; }
.wo-table tbody td {
    padding: 0.55rem 0.8rem;
    color: var(--text-primary);
    border-bottom: 1px solid var(--card-border);
}
.wo-table tbody tr:last-child td { border-bottom: none; }
.wo-table tbody tr:hover td {
    background: rgba(var(--accent-1-rgb), 0.04);
}

/* ── Summary card ───────────────────────────────────────────── */
.wo-summary-card {
    background: var(--metric-bg);
    border: 1px solid var(--metric-border);
    border-radius: 18px;
    padding: 1.4rem;
    text-align: center;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.wo-summary-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 32px var(--shadow);
}
.wo-summary-icon  { font-size: 2.2rem; margin-bottom: 0.4rem; }
.wo-summary-label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
                    letter-spacing: 0.08em; color: var(--text-secondary); margin-bottom: 0.25rem; }
.wo-summary-value { font-size: 1.9rem; font-weight: 800; font-family: 'Outfit', sans-serif;
                    background: var(--gradient); -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent; background-clip: text; }
.wo-summary-note  { font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.15rem; }

/* ── Tip card ───────────────────────────────────────────────── */
.wo-tip-card {
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
.wo-tip-number {
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
.wo-plan-summary-banner {
    background: var(--metric-bg);
    border: 1px solid var(--metric-border);
    border-radius: 18px;
    padding: 1.3rem 1.7rem;
    margin-bottom: 1.6rem;
    font-size: 0.92rem;
    color: var(--text-secondary);
    line-height: 1.7;
}
.wo-plan-summary-banner strong { color: var(--text-primary); }

/* ── Progression advice banner ──────────────────────────────── */
.wo-progression-banner {
    background: var(--badge-success-bg);
    border: 1px solid var(--badge-success-border);
    border-radius: 18px;
    padding: 1.3rem 1.7rem;
    margin-bottom: 1rem;
    font-size: 0.92rem;
    color: var(--text-secondary);
    line-height: 1.7;
}
.wo-progression-banner strong { color: var(--text-primary); }

/* ── Guard box ──────────────────────────────────────────────── */
.wo-guard-box {
    text-align: center;
    padding: 3rem 1.5rem;
    background: var(--guard-bg);
    border: 1px dashed var(--guard-border);
    border-radius: 20px;
    margin-top: 1rem;
}
.wo-guard-icon  { font-size: 3.5rem; margin-bottom: 0.8rem; }
.wo-guard-title { font-size: 1.3rem; font-weight: 700; color: var(--text-primary);
                  margin-bottom: 0.5rem; }
.wo-guard-desc  { color: var(--text-secondary); font-size: 0.9rem;
                  max-width: 420px; margin: 0 auto 1.5rem; line-height: 1.6; }

/* ── Form section ───────────────────────────────────────────── */
.wo-form-section {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    padding: 1.6rem;
    margin-bottom: 1.2rem;
}

/* ── Loading shimmer ────────────────────────────────────────── */
@keyframes wo-shimmer {
    0%   { background-position: -1000px 0; }
    100% { background-position:  1000px 0; }
}
.wo-shimmer-line {
    height: 18px;
    border-radius: 8px;
    background: linear-gradient(90deg,
        var(--glass-bg) 25%,
        rgba(var(--accent-1-rgb), 0.1) 50%,
        var(--glass-bg) 75%
    );
    background-size: 1000px 100%;
    animation: wo-shimmer 1.6s infinite linear;
    margin-bottom: 0.8rem;
}
.wo-shimmer-line.short  { width: 55%; }
.wo-shimmer-line.medium { width: 75%; }
.wo-shimmer-line.full   { width: 100%; }
</style>
"""


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def _day_card_html(
    day_key: str,
    day_data: dict,
    accent: str,
) -> str:
    """Render a workout day card as HTML."""
    title = day_data.get("title", day_key.replace("_", " ").title())
    target = day_data.get("target_muscles", "—")
    duration = day_data.get("duration_minutes", 60)

    # Warmup items
    warmup = day_data.get("warmup", [])
    warmup_html = "".join(
        f'<span class="wo-item-tag">🔸 {item}</span>' for item in warmup
    ) if warmup else '<span class="wo-item-tag" style="opacity:0.5;">None</span>'

    # Main workout table
    main = day_data.get("main_workout", [])
    rows_html = ""
    for ex in main:
        rows_html += f"""
        <tr>
            <td style="font-weight:600;">{ex.get("exercise", "—")}</td>
            <td>{ex.get("sets", "—")}</td>
            <td>{ex.get("reps", "—")}</td>
            <td>{ex.get("rest_seconds", "—")}s</td>
        </tr>"""

    # Cooldown items
    cooldown = day_data.get("cooldown", [])
    cooldown_html = "".join(
        f'<span class="wo-item-tag">🔹 {item}</span>' for item in cooldown
    ) if cooldown else '<span class="wo-item-tag" style="opacity:0.5;">None</span>'

    return f"""<div class="day-card" style="border-left: 4px solid {accent};">
    <div class="day-card-header">
        <div class="day-title">{title}</div>
        <div class="day-badge-row">
            <span class="day-stat">🎯 {target}</span>
            <span class="day-stat">⏱️ {duration} min</span>
        </div>
    </div>

    <div class="wo-section-label">{WORKOUT_SECTION_ICONS['warmup']} Warm-up</div>
    <div style="display:flex;flex-wrap:wrap;gap:0.3rem;">{warmup_html}</div>

    <div class="wo-section-label">{WORKOUT_SECTION_ICONS['main_workout']} Main Workout</div>
    <table class="wo-table">
        <thead>
            <tr>
                <th>Exercise</th>
                <th>Sets</th>
                <th>Reps</th>
                <th>Rest</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>

    <div class="wo-section-label">{WORKOUT_SECTION_ICONS['cooldown']} Cool-down</div>
    <div style="display:flex;flex-wrap:wrap;gap:0.3rem;">{cooldown_html}</div>
</div>"""



def _summary_card_html(icon: str, label: str, value: str, note: str = "") -> str:
    return f"""<div class="wo-summary-card">
    <div class="wo-summary-icon">{icon}</div>
    <div class="wo-summary-label">{label}</div>
    <div class="wo-summary-value">{value}</div>
    <div class="wo-summary-note">{note}</div>
</div>"""



def _tip_html(index: int, tip: str) -> str:
    return f"""<div class="wo-tip-card">
    <span class="wo-tip-number">{index}.</span>
    <span>{tip}</span>
</div>"""



def _loading_shimmer() -> str:
    return """<div style="padding: 1rem 0;">
    <div class="wo-shimmer-line full"></div>
    <div class="wo-shimmer-line medium"></div>
    <div class="wo-shimmer-line short"></div>
    <div class="wo-shimmer-line full" style="margin-top:1rem;"></div>
    <div class="wo-shimmer-line medium"></div>
    <div class="wo-shimmer-line short"></div>
    <div class="wo-shimmer-line full" style="margin-top:1rem;"></div>
    <div class="wo-shimmer-line medium"></div>
</div>"""



# ---------------------------------------------------------------------------
# Defaults derived from profile
# ---------------------------------------------------------------------------

def _get_profile_defaults(profile: dict) -> dict:
    """Pre-fill workout planner defaults from existing profile fields."""
    goal = profile.get("fitness_goal", "Maintenance")

    # Map fitness_goal → primary_goal
    if "Weight Loss" in goal:
        primary_default = "Fat Loss"
    elif "Muscle" in goal:
        primary_default = "Muscle Gain"
    else:
        primary_default = "General Fitness"

    # Map available_equipment → equipment option
    equip_list = profile.get("available_equipment", [])
    if isinstance(equip_list, str):
        equip_list = [equip_list] if equip_list else []

    if "Full Gym Access" in equip_list:
        equip_default = "Full Gym"
    elif "Dumbbells" in equip_list:
        equip_default = "Dumbbells"
    elif "Resistance Bands" in equip_list:
        equip_default = "Resistance Bands"
    else:
        equip_default = "Bodyweight Only"

    return {
        "primary_default": primary_default,
        "equip_default": equip_default,
    }


# ---------------------------------------------------------------------------
# Input form section
# ---------------------------------------------------------------------------

def _render_input_form(profile: dict) -> dict | None:
    """
    Render the workout preferences form and return a workout_inputs dict
    on submit, or None if not yet submitted.
    """
    defaults = _get_profile_defaults(profile)

    st.html('<div class="wo-form-section">')
    section_header("⚙️ Workout Preferences")

    col1, col2, col3 = st.columns(3)

    with col1:
        workout_days = st.selectbox(
            "📅 Workout Days / Week",
            options=WORKOUT_DAYS_OPTIONS,
            index=2,  # default 5
            key="wp_days",
            help="How many days per week you want to work out.",
        )

    with col2:
        workout_duration = st.selectbox(
            "⏱️ Session Duration (min)",
            options=DURATION_OPTIONS,
            index=2,  # default 60
            key="wp_duration",
        )

    with col3:
        workout_location = st.selectbox(
            "📍 Workout Location",
            options=LOCATION_OPTIONS,
            index=1,  # default Gym
            key="wp_location",
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        experience_level = st.selectbox(
            "🏋️ Experience Level",
            options=EXPERIENCE_OPTIONS,
            index=0,  # default Beginner
            key="wp_experience",
        )

    with col5:
        equip_idx = EQUIPMENT_OPTIONS.index(defaults["equip_default"]) \
            if defaults["equip_default"] in EQUIPMENT_OPTIONS else 0
        equipment = st.selectbox(
            "🔧 Equipment Available",
            options=EQUIPMENT_OPTIONS,
            index=equip_idx,
            key="wp_equipment",
        )

    with col6:
        goal_idx = PRIMARY_GOAL_OPTIONS.index(defaults["primary_default"]) \
            if defaults["primary_default"] in PRIMARY_GOAL_OPTIONS else 4
        primary_goal = st.selectbox(
            "🎯 Primary Goal",
            options=PRIMARY_GOAL_OPTIONS,
            index=goal_idx,
            key="wp_goal",
        )

    focus_areas = st.multiselect(
        "💪 Focus Areas",
        options=FOCUS_AREA_OPTIONS,
        default=FOCUS_AREA_OPTIONS,  # all selected by default
        key="wp_focus",
        help="Select the muscle groups you want to prioritise.",
    )

    injuries = st.text_input(
        "🩹 Injuries / Limitations",
        placeholder="e.g. Lower back pain, Shoulder impingement — leave blank if none",
        key="wp_injuries",
        help="Describe any injuries or physical limitations.",
    )

    st.html('</div>')

    col_l, col_btn, col_r = st.columns([1, 2, 1])
    with col_btn:
        generate_clicked = st.button(
            "✨  Generate My Workout Plan",
            use_container_width=True,
            key="wp_generate_btn",
            type="primary",
        )

    if generate_clicked:
        return {
            "workout_days": int(workout_days),
            "workout_duration": int(workout_duration),
            "workout_location": workout_location,
            "experience_level": experience_level,
            "equipment": equipment,
            "primary_goal": primary_goal,
            "focus_areas": focus_areas,
            "injuries": injuries,
        }

    return None


# ---------------------------------------------------------------------------
# Plan display
# ---------------------------------------------------------------------------

def _render_plan(plan: dict, workout_inputs: dict) -> None:
    """Render the full generated workout plan."""

    workout_days = workout_inputs.get("workout_days", 5)

    # ── Plan summary banner ────────────────────────────────────────────────
    summary_text = plan.get("plan_summary", "")
    if summary_text:
        st.html(
            f'<div class="wo-plan-summary-banner">📋 <strong>Plan Overview:</strong> {summary_text}</div>')

    # ── Quick stats cards ──────────────────────────────────────────────────
    section_header("📊 Workout Overview")

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(
            _summary_card_html("📅", "Days / Week", str(workout_days), "training days"),
            unsafe_allow_html=True,
        )
    with sc2:
        st.markdown(
            _summary_card_html("⏱️", "Session Duration",
                               f"{workout_inputs['workout_duration']}m", "per session"),
            unsafe_allow_html=True,
        )
    with sc3:
        st.markdown(
            _summary_card_html("🎯", "Primary Goal",
                               workout_inputs["primary_goal"], "focus"),
            unsafe_allow_html=True,
        )
    with sc4:
        st.markdown(
            _summary_card_html("🏋️", "Experience",
                               workout_inputs["experience_level"], "level"),
            unsafe_allow_html=True,
        )

    styled_divider()

    # ── Weekly schedule cards ──────────────────────────────────────────────
    section_header("🗓️ Your Weekly Schedule")

    schedule = plan.get("weekly_schedule", {})


    for i in range(1, workout_days + 1):
        day_key = f"day_{i}"
        day_data = schedule.get(day_key, {})
        _, accent = DAY_ICONS.get(day_key, ("📅", "#6c63ff"))
        st.html(
            _day_card_html(day_key, day_data, accent)
        )

    styled_divider()

    # ── Tips section ──────────────────────────────────────────────────────
    tips = plan.get("tips", [])
    if tips:
        section_header("💡 Personalised Workout Tips")
        for idx, tip in enumerate(tips, 1):
            st.markdown(_tip_html(idx, tip), unsafe_allow_html=True)

    styled_divider()

    # ── Progression advice ────────────────────────────────────────────────
    progression = plan.get("progression_advice", "")
    if progression:
        section_header("📈 Progression Advice")
        st.markdown(
            f'<div class="wo-progression-banner">🚀 <strong>How to Progress:</strong> {progression}</div>',
            unsafe_allow_html=True,
        )

    styled_divider()

    # ── Regenerate / reset button row ──────────────────────────────────────
    col_l, col_regen, col_clear, col_r = st.columns([1, 2, 2, 1])
    with col_regen:
        if st.button("🔄  Regenerate Plan", use_container_width=True, key="wp_regen"):
            st.session_state.pop("workout_plan_result", None)
            st.session_state.pop("workout_plan_inputs", None)
            st.rerun()
    with col_clear:
        if st.button("🗑️  Clear & Start Over", use_container_width=True, key="wp_clear"):
            st.session_state.pop("workout_plan_result", None)
            st.session_state.pop("workout_plan_inputs", None)
            st.rerun()

    # ── Disclaimer ─────────────────────────────────────────────────────────
    st.html(
        """
        <div style="
            text-align:center;
            font-size:0.75rem;
            color:var(--text-muted);
            margin-top:1rem;
            padding:0.8rem;
            border-top: 1px solid var(--divider-line);
        ">
            ⚕️ This AI-generated workout plan is for informational purposes only.
            Consult a certified fitness professional or physician before starting
            any new exercise programme, especially if you have pre-existing conditions.
        </div>
        """,
    )


# ---------------------------------------------------------------------------
# Page renderer (entry point)
# ---------------------------------------------------------------------------

def render() -> None:
    """Render the Workout Planner page."""
    init_session_state()

    # Inject page-specific CSS
    st.markdown(WORKOUT_PAGE_CSS, unsafe_allow_html=True)

    # ── Page header ─────────────────────────────────────────────────────────
    st.html(
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
            ">💪 AI Workout Planner</h1>
            <p style="color:var(--text-secondary);font-size:0.95rem;">
                Powered by Google Gemini · Get a fully personalised workout plan in seconds.
            </p>
        </div>
        """,
    )
    styled_divider()

    # ── Guard: profile required ─────────────────────────────────────────────
    if not is_profile_complete():
        st.html(
            """
            <div class="wo-guard-box">
                <div class="wo-guard-icon">🔒</div>
                <div class="wo-guard-title">Profile Required</div>
                <div class="wo-guard-desc">
                    Please complete your profile first so we can personalise
                    your workout plan with your body metrics and fitness goals.
                </div>
            </div>
            """,
        )
        col_l, col_btn, col_r = st.columns([2, 1, 2])
        with col_btn:
            if st.button("👤  Go to Profile", use_container_width=True, key="wo_goto_profile"):
                st.session_state.current_page = "Profile"
                st.rerun()
        return

    profile = get_profile()

    # ── Profile preview strip ───────────────────────────────────────────────
    st.html(
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
                    Activity: <strong style="color:var(--accent-2);">{profile.get('activity_level','—')}</strong>
                </div>
            </div>
        </div>
        """,
    )

    # ── Check if a plan is already stored in session state ──────────────────
    if "workout_plan_result" in st.session_state and "workout_plan_inputs" in st.session_state:
        stored_plan   = st.session_state["workout_plan_result"]
        stored_inputs = st.session_state["workout_plan_inputs"]

        st.success("✅ Your workout plan is ready! Scroll down to explore it.", icon="💪")
        st.html(
            "<p style='color:var(--text-secondary);font-size:0.85rem;margin-bottom:0.8rem;'>"
            "This plan is stored for this session. Click <strong>Regenerate</strong> for a fresh plan "
            "or adjust your preferences below and generate again.</p>"
        )

        # Show form again (collapsed via expander) for quick re-generation
        with st.expander("🔧 Adjust Preferences & Regenerate", expanded=False):
            new_inputs = _render_input_form(profile)
            if new_inputs:
                with st.spinner(""):
                    shimmer_placeholder = st.empty()
                    shimmer_placeholder.markdown(_loading_shimmer(), unsafe_allow_html=True)
                    try:
                        new_plan = get_personalized_workout_plan(profile, new_inputs)
                        shimmer_placeholder.empty()
                        st.session_state["workout_plan_result"] = new_plan
                        st.session_state["workout_plan_inputs"] = new_inputs
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
    workout_inputs = _render_input_form(profile)

    if workout_inputs is None:
        # Not yet submitted — show a teaser
        st.html(
            """
            <div style="
                text-align:center;
                padding:2.5rem 1rem;
                margin-top:0.5rem;
                background:var(--card-bg);
                border:1px dashed var(--card-border);
                border-radius:20px;
            ">
                <div style="font-size:3.5rem;margin-bottom:0.8rem;">💪</div>
                <div style="font-weight:700;font-size:1.1rem;color:var(--text-primary);
                            margin-bottom:0.5rem;">Ready to build your workout plan?</div>
                <div style="color:var(--text-secondary);font-size:0.9rem;max-width:420px;
                            margin:0 auto;line-height:1.65;">
                    Fill in your preferences above and click
                    <strong>Generate My Workout Plan</strong> to get a fully
                    personalised, AI-powered training programme with exercises and tips.
                </div>
            </div>
            """,
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
                Gemini is crafting your personalised workout plan…
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
        plan = get_personalized_workout_plan(profile, workout_inputs)
        # Store in session state so it persists during the session
        st.session_state["workout_plan_result"] = plan
        st.session_state["workout_plan_inputs"] = workout_inputs
        gen_placeholder.empty()
        shimmer_ph.empty()
        st.success("✅ Your personalised workout plan is ready!", icon="💪")
        _render_plan(plan, workout_inputs)

    except RuntimeError as exc:
        gen_placeholder.empty()
        shimmer_ph.empty()
        st.error("⚠️ Workout Plan Generation Failed")
        st.html(
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
        )
        col_l2, col_retry, col_r2 = st.columns([2, 1, 2])
        with col_retry:
            if st.button("🔁  Try Again", use_container_width=True, key="wp_retry"):
                st.rerun()
