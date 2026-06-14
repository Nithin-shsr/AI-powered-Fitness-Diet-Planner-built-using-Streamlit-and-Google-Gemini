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
# Global UI Injection (Theme Toggle & Back to Home)
# ---------------------------------------------------------------------------

def handle_theme_toggle():
    """Callback for the real Streamlit theme button."""
    current = get_theme()
    set_theme("Light" if current == "Dark" else "Dark")

def handle_home_toggle():
    """Callback for the real Streamlit home button."""
    st.session_state.current_page = "Home"

def inject_global_ui() -> None:
    """Inject the true Streamlit widgets and convert them into floating UI via JS."""
    current_theme = get_theme()
    theme_icon = "☀️" if current_theme == "Dark" else "🌙"
    
    # 1. Render the TRUE visible widgets. No hidden divs.
    st.button(theme_icon, key="global_theme_btn", on_click=handle_theme_toggle)
    
    if st.session_state.current_page != "Home":
        st.button("🏠 Home", key="global_home_btn", on_click=handle_home_toggle)

    # 2. Inject JS to style them and attach View Transition
    st.html("""
        <script>
            // This script finds the real Streamlit buttons and adds classes to their containers
            // so CSS can float them. It also attaches the View Transition to the theme button.
            
            const initUI = () => {
                const doc = window.parent.document;
                const buttons = Array.from(doc.querySelectorAll('button p'));
                
                // --- Theme Button ---
                const themeP = buttons.find(b => b.textContent === '☀️' || b.textContent === '🌙');
                if (themeP) {
                    const themeBtn = themeP.closest('button');
                    const wrapper = themeBtn.closest('div[data-testid="stButton"]');
                    if (wrapper && !wrapper.classList.contains('floating-theme-btn')) {
                        wrapper.classList.add('floating-theme-btn');
                        
                        // Attach capture-phase listener for View Transition
                        themeBtn.addEventListener('click', (e) => {
                            // Update localStorage instantly to avoid flicker on next load
                            const isDarkNow = themeP.textContent === '☀️';
                            localStorage.setItem('ai_fitness_theme', isDarkNow ? 'Light' : 'Dark');
                            
                            if (doc.startViewTransition) {
                                doc.documentElement.style.setProperty('--theme-x', e.clientX + 'px');
                                doc.documentElement.style.setProperty('--theme-y', e.clientY + 'px');
                                
                                doc.startViewTransition(() => {
                                    return new Promise(resolve => {
                                        const observer = new MutationObserver(() => {
                                            setTimeout(() => { resolve(); observer.disconnect(); }, 50);
                                        });
                                        observer.observe(doc.body, { childList: true, subtree: true });
                                    });
                                });
                            }
                        }, true); // true = capture phase!
                    }
                }
                
                // --- Home Button ---
                const homeP = buttons.find(b => b.textContent.includes('🏠 Home'));
                if (homeP) {
                    const wrapper = homeP.closest('div[data-testid="stButton"]');
                    if (wrapper && !wrapper.classList.contains('floating-home-btn')) {
                        wrapper.classList.add('floating-home-btn');
                    }
                }
                
                // --- LocalStorage Sync ---
                const savedTheme = localStorage.getItem('ai_fitness_theme');
                if (savedTheme && themeP) {
                    const pythonThemeIsDark = themeP.textContent === '☀️';
                    const pythonThemeStr = pythonThemeIsDark ? 'Dark' : 'Light';
                    if (savedTheme !== pythonThemeStr) {
                        // Silent sync if out of sync on load
                        themeBtn.click();
                    }
                }
            };

            // Run once immediately, and also on load to catch DOM
            initUI();
            setTimeout(initUI, 100);
        </script>
    """)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # 1. Initialise session state first (so theme is available)
    init_session_state()

    # 2. Inject global styles with the active theme
    apply_global_styles(get_theme())

    # 3. Inject Floating UI
    inject_global_ui()

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
