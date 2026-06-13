# app.py
"""
AI Fitness & Diet Planner — Main Application Entry Point
Run with:  streamlit run app.py
"""

import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables first
load_dotenv()

# ── Page config (must be the very first Streamlit call) ───────────────────
st.set_page_config(
    page_title="AI Fitness & Diet Planner",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local imports (after page config) ────────────────────────────────────
from utils.styles import apply_global_styles
from utils.session_manager import init_session_state, is_profile_complete, get_theme, set_theme

import pages.home         as home_page
import pages.profile      as profile_page
import pages.dashboard    as dashboard_page
import pages.diet_planner as diet_planner_page
import pages.workout_planner as workout_planner_page
import pages.ai_coach     as ai_coach_page


# ---------------------------------------------------------------------------
# Navigation configuration
# ---------------------------------------------------------------------------

NAV_ITEMS = {
    "🏠  Home":              "Home",
    "👤  Profile":           "Profile",
    "📊  Dashboard":         "Dashboard",
    "🥗  Diet Planner":      "Diet Planner",
    "💪  Workout Planner":   "Workout Planner",
    "🤖  AI Coach":          "AI Coach",
}


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def render_sidebar() -> None:
    """Build the sidebar navigation."""
    with st.sidebar:

        # Logo / brand
        st.markdown(
            """
            <div style="text-align:center;padding:1.5rem 0 1rem;">
                <div style="
                    width:60px;height:60px;
                    background:var(--gradient);
                    border-radius:16px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.8rem;
                    margin:0 auto 0.8rem;
                    box-shadow:0 8px 20px var(--shadow);
                ">💪</div>
                <div style="
                    font-family:'Outfit',sans-serif;
                    font-size:1.1rem;
                    font-weight:800;
                    background:var(--gradient);
                    -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;
                    background-clip:text;
                ">AI Fitness Planner</div>
                <div style="font-size:0.72rem;color:var(--text-muted);margin-top:0.2rem;">
                    Powered by Google Gemini
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr style='border:none;border-top:1px solid var(--divider-line);margin:0 0 1rem;'/>", unsafe_allow_html=True)

        # Active navigation
        st.markdown(
            "<p style='font-size:0.7rem;font-weight:700;text-transform:uppercase;"
            "letter-spacing:0.1em;color:var(--text-muted);padding:0 0.3rem;margin-bottom:0.5rem;'>"
            "Navigation</p>",
            unsafe_allow_html=True,
        )

        nav_labels = list(NAV_ITEMS.keys())
        nav_values = list(NAV_ITEMS.values())

        # Find current index
        current = st.session_state.get("current_page", "Home")
        try:
            current_idx = nav_values.index(current)
        except ValueError:
            current_idx = 0

        selected_label = st.radio(
            "nav",
            options=nav_labels,
            index=current_idx,
            label_visibility="collapsed",
            key="sidebar_nav",
        )
        st.session_state.current_page = NAV_ITEMS[selected_label]

        # Profile status
        st.markdown(
            "<hr style='border:none;border-top:1px solid var(--divider-line);margin:1rem 0 0.8rem;'/>",
            unsafe_allow_html=True,
        )

        profile_done = is_profile_complete()
        profile_name = st.session_state.profile.get("name", "")
        if profile_done and profile_name:
            st.markdown(
                f"""
                <div style="
                    background:var(--profile-active-bg);
                    border:1px solid var(--profile-active-border);
                    border-radius:12px;
                    padding:0.75rem 1rem;
                    font-size:0.82rem;
                ">
                    <div style="color:var(--profile-active-title);font-weight:600;margin-bottom:0.2rem;">✅ Profile Active</div>
                    <div style="color:var(--text-secondary);">{profile_name}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div style="
                    background:var(--profile-inactive-bg);
                    border:1px solid var(--profile-inactive-border);
                    border-radius:12px;
                    padding:0.75rem 1rem;
                    font-size:0.82rem;
                ">
                    <div style="color:var(--profile-inactive-title);font-weight:600;margin-bottom:0.2rem;">⚠️ No Profile</div>
                    <div style="color:var(--text-secondary);">Set up your profile to unlock all features.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Theme toggle ───────────────────────────────────────────────────────
        st.markdown(
            "<hr style='border:none;border-top:1px solid var(--divider-line);margin:1rem 0 0.8rem;'/>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='font-size:0.7rem;font-weight:700;text-transform:uppercase;"
            "letter-spacing:0.1em;color:var(--text-muted);padding:0 0.3rem;margin-bottom:0.5rem;'>"
            "Appearance</p>",
            unsafe_allow_html=True,
        )

        current_theme = get_theme()
        is_dark = st.toggle(
            "🌙 Dark Mode",
            value=(current_theme == "Dark"),
            key="theme_toggle",
            help="Switch between Light and Dark themes",
        )
        new_theme = "Dark" if is_dark else "Light"
        if new_theme != current_theme:
            set_theme(new_theme)
            st.rerun()

        # Version footer
        st.markdown(
            "<div style='text-align:center;font-size:0.7rem;color:var(--footer-color);margin-top:1.5rem;'>"
            "v3.0 · Phase 3</div>",
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # 1. Initialise session state first (so theme is available)
    init_session_state()

    # 2. Inject global styles with the active theme
    apply_global_styles(get_theme())

    # 3. Render sidebar (may update theme and trigger rerun)
    render_sidebar()

    # 4. Route to correct page
    page = st.session_state.current_page

    if page == "Home":
        home_page.render()
    elif page == "Profile":
        profile_page.render()
    elif page == "Dashboard":
        dashboard_page.render()
    elif page == "Diet Planner":
        diet_planner_page.render()
    elif page == "Workout Planner":
        workout_planner_page.render()
    elif page == "AI Coach":
        ai_coach_page.render()
    else:
        home_page.render()


if __name__ == "__main__":
    main()
