# utils/session_manager.py
"""
Session state management helpers for AI Fitness Planner.
Initializes and manages all Streamlit session state variables.
"""

import streamlit as st


# ---------------------------------------------------------------------------
# Default profile skeleton
# ---------------------------------------------------------------------------

DEFAULT_PROFILE = {
    "name": "",
    "age": 25,
    "gender": "Male",
    "height_cm": 170.0,
    "weight_kg": 70.0,
    "target_weight_kg": 65.0,
    "activity_level": "Moderately Active",
    "fitness_goal": "Weight Loss",
    "diet_preference": "No Restriction",
    "preferred_cuisine": "Any",
    "workout_time": "Morning",
    "available_equipment": [],
}


# ---------------------------------------------------------------------------
# Initializers
# ---------------------------------------------------------------------------

def init_session_state() -> None:
    """Initialize all session state variables with safe defaults."""
    if "profile_saved" not in st.session_state:
        st.session_state.profile_saved = False

    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    if "profile" not in st.session_state:
        st.session_state.profile = DEFAULT_PROFILE.copy()

    if "theme" not in st.session_state:
        st.session_state.theme = "Light"   # Light is the default


def get_profile() -> dict:
    """Return the current user profile from session state."""
    init_session_state()
    return st.session_state.profile


def update_profile(key: str, value) -> None:
    """Update a single field in the profile."""
    init_session_state()
    st.session_state.profile[key] = value


def save_profile(profile_data: dict) -> None:
    """Persist a full profile dict to session state and mark as saved."""
    init_session_state()
    st.session_state.profile = profile_data
    st.session_state.profile_saved = True


def is_profile_complete() -> bool:
    """Return True if the minimum required profile fields are filled in."""
    profile = get_profile()
    required = ["name", "age", "height_cm", "weight_kg"]
    return all(profile.get(field) for field in required)


def reset_profile() -> None:
    """Reset the profile to default values."""
    st.session_state.profile = DEFAULT_PROFILE.copy()
    st.session_state.profile_saved = False


# ---------------------------------------------------------------------------
# Theme helpers
# ---------------------------------------------------------------------------

def get_theme() -> str:
    """Return the active theme ('Light' or 'Dark')."""
    init_session_state()
    return st.session_state.get("theme", "Light")


def set_theme(theme: str) -> None:
    """Set the active theme. theme must be 'Light' or 'Dark'."""
    if theme in ("Light", "Dark"):
        st.session_state.theme = theme
