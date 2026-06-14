# pages/profile.py
"""
Profile page – collects and persists user health & fitness data.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from utils.session_manager import init_session_state, save_profile, get_profile
from utils.styles import section_header, styled_divider, glass_card


# ---------------------------------------------------------------------------
# Constants / option lists
# ---------------------------------------------------------------------------

GENDERS         = ["Male", "Female", "Other / Prefer not to say"]
ACTIVITY_LEVELS = [
    "Sedentary",
    "Lightly Active",
    "Moderately Active",
    "Very Active",
    "Extra Active",
]
FITNESS_GOALS = [
    "Weight Loss",
    "Aggressive Weight Loss",
    "Maintenance",
    "Muscle Gain",
    "Aggressive Muscle Gain",
]
DIET_PREFS = [
    "No Restriction",
    "Vegetarian",
    "Vegan",
    "Pescatarian",
    "Keto",
    "Paleo",
    "Mediterranean",
    "Gluten-Free",
    "Dairy-Free",
]
CUISINES = [
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
WORKOUT_TIMES = ["Morning", "Afternoon", "Evening", "Late Night", "Flexible"]
EQUIPMENT_OPTIONS = [
    "No Equipment (Bodyweight only)",
    "Resistance Bands",
    "Dumbbells",
    "Barbell & Plates",
    "Pull-up Bar",
    "Bench",
    "Treadmill",
    "Stationary Bike",
    "Rowing Machine",
    "Full Gym Access",
]

DATA_FILE = Path(__file__).parent.parent / "data" / "user_data.csv"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _activity_description(level: str) -> str:
    descriptions = {
        "Sedentary": "Little or no exercise, desk job",
        "Lightly Active": "Light exercise 1–3 days/week",
        "Moderately Active": "Moderate exercise 3–5 days/week",
        "Very Active": "Hard exercise 6–7 days/week",
        "Extra Active": "Very hard exercise or physical job",
    }
    return descriptions.get(level, "")


def _save_to_csv(profile: dict) -> None:
    """Append or update user profile row in user_data.csv."""
    try:
        df = pd.DataFrame([profile])
        if DATA_FILE.exists():
            existing = pd.read_csv(DATA_FILE)
            # Remove old row with same name (case-insensitive) then append
            existing = existing[existing["name"].str.lower() != profile["name"].lower()]
            df = pd.concat([existing, df], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
    except Exception:
        pass  # silently skip CSV write errors


# ---------------------------------------------------------------------------
# Page renderer
# ---------------------------------------------------------------------------

def render() -> None:
    """Render the Profile page."""
    init_session_state()
    profile = get_profile()

    # ── Page header ────────────────────────────────────────────────────────
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
            ">👤 Your Profile</h1>
            <p style="color:var(--text-secondary);font-size:0.95rem;">
                Fill in your details so we can personalise your fitness journey.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    styled_divider()

    with st.form("profile_form", clear_on_submit=False):

        # ── Section 1 · Personal Info ──────────────────────────────────────
        section_header("🧑 Personal Information")
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Full Name",
                value=profile.get("name", ""),
                placeholder="e.g. Alex Johnson",
                key="inp_name",
            )
            age = st.number_input(
                "Age (years)",
                min_value=10,
                max_value=100,
                value=int(profile.get("age", 25)),
                step=1,
                key="inp_age",
            )

        with col2:
            gender = st.selectbox(
                "Gender",
                options=GENDERS,
                index=GENDERS.index(profile.get("gender", "Male")),
                key="inp_gender",
            )
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        styled_divider()

        # ── Section 2 · Body Metrics ───────────────────────────────────────
        section_header("📏 Body Metrics")
        col3, col4, col5 = st.columns(3)

        with col3:
            height_cm = st.number_input(
                "Height (cm)",
                min_value=100.0,
                max_value=250.0,
                value=float(profile.get("height_cm", 170.0)),
                step=0.5,
                format="%.1f",
                key="inp_height",
            )

        with col4:
            weight_kg = st.number_input(
                "Current Weight (kg)",
                min_value=20.0,
                max_value=300.0,
                value=float(profile.get("weight_kg", 70.0)),
                step=0.5,
                format="%.1f",
                key="inp_weight",
            )

        with col5:
            target_weight_kg = st.number_input(
                "Target Weight (kg)",
                min_value=20.0,
                max_value=300.0,
                value=float(profile.get("target_weight_kg", 65.0)),
                step=0.5,
                format="%.1f",
                key="inp_target_weight",
            )

        styled_divider()

        # ── Section 3 · Fitness Goals ──────────────────────────────────────
        section_header("🎯 Fitness Goals & Activity")
        col6, col7 = st.columns(2)

        with col6:
            activity_level = st.selectbox(
                "Activity Level",
                options=ACTIVITY_LEVELS,
                index=ACTIVITY_LEVELS.index(profile.get("activity_level", "Moderately Active")),
                key="inp_activity",
                help="How physically active are you on a typical week?",
            )
            st.caption(f"💡 {_activity_description(activity_level)}")

        with col7:
            fitness_goal = st.selectbox(
                "Primary Fitness Goal",
                options=FITNESS_GOALS,
                index=FITNESS_GOALS.index(profile.get("fitness_goal", "Weight Loss")),
                key="inp_goal",
            )

        styled_divider()

        # ── Section 4 · Diet Preferences ──────────────────────────────────
        section_header("🥗 Diet & Cuisine Preferences")
        col8, col9 = st.columns(2)

        with col8:
            diet_preference = st.selectbox(
                "Dietary Preference / Restriction",
                options=DIET_PREFS,
                index=DIET_PREFS.index(profile.get("diet_preference", "No Restriction")),
                key="inp_diet",
            )

        with col9:
            preferred_cuisine = st.selectbox(
                "Preferred Cuisine",
                options=CUISINES,
                index=CUISINES.index(profile.get("preferred_cuisine", "Any")),
                key="inp_cuisine",
            )

        styled_divider()

        # ── Section 5 · Workout Preferences ───────────────────────────────
        section_header("💪 Workout Preferences")
        col10, col11 = st.columns(2)

        with col10:
            workout_time = st.selectbox(
                "Preferred Workout Time",
                options=WORKOUT_TIMES,
                index=WORKOUT_TIMES.index(profile.get("workout_time", "Morning")),
                key="inp_wtime",
            )

        with col11:
            # Ensure default value is a list
            default_equip = profile.get("available_equipment", [])
            if isinstance(default_equip, str):
                default_equip = [default_equip] if default_equip else []

            available_equipment = st.multiselect(
                "Available Equipment",
                options=EQUIPMENT_OPTIONS,
                default=default_equip,
                key="inp_equip",
                help="Select all equipment you have access to.",
            )

        styled_divider()

        # ── Submit ─────────────────────────────────────────────────────────
        col_l, col_btn, col_r = st.columns([1, 2, 1])
        with col_btn:
            submitted = st.form_submit_button(
                "💾  Save Profile",
                use_container_width=True,
            )

    # ── Handle save ────────────────────────────────────────────────────────
    if submitted:
        if not name.strip():
            st.error("⚠️ Please enter your name before saving.")
        else:
            new_profile = {
                "name": name.strip(),
                "age": int(age),
                "gender": gender,
                "height_cm": float(height_cm),
                "weight_kg": float(weight_kg),
                "target_weight_kg": float(target_weight_kg),
                "activity_level": activity_level,
                "fitness_goal": fitness_goal,
                "diet_preference": diet_preference,
                "preferred_cuisine": preferred_cuisine,
                "workout_time": workout_time,
                "available_equipment": available_equipment,
            }
            save_profile(new_profile)
            _save_to_csv(new_profile)
            st.success("✅ Profile saved successfully!")
            st.markdown(
                "<p style='color:var(--text-secondary);font-size:0.9rem;margin-top:0.5rem;'>"
                "Head over to the <strong>Dashboard</strong> to view your personalised health metrics.</p>",
                unsafe_allow_html=True,
            )

            col_a, col_dash, col_b = st.columns([2, 1, 2])
            with col_dash:
                if st.button("📊  View Dashboard", use_container_width=True, key="goto_dash"):
                    st.session_state.current_page = "Dashboard"
                    st.rerun()

    # ── If profile already saved, show summary card ────────────────────────
    elif st.session_state.profile_saved and profile.get("name"):
        st.info(
            f"📌 Profile loaded for **{profile['name']}**. "
            "Edit any field above and click **Save Profile** to update."
        )
