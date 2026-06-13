# pages/home.py
"""
Home page – hero section, feature cards, and call-to-action.
All inline colours use CSS custom properties (var(--token)) so the
Light / Dark theme toggle in the sidebar is reflected here automatically.
"""

import streamlit as st
from utils.styles import (
    feature_card_html,
    styled_divider,
)
from utils.session_manager import init_session_state


# ---------------------------------------------------------------------------
# Feature highlights data
# ---------------------------------------------------------------------------

FEATURES = [
    {
        "icon": "🤖",
        "title": "AI-Powered Plans",
        "desc": "Gemini AI generates fully personalised meal and workout plans tailored to your body and goals.",
    },
    {
        "icon": "📊",
        "title": "Smart Dashboard",
        "desc": "Track BMI, BMR, daily calories, protein targets, and hydration goals all in one place.",
    },
    {
        "icon": "🥗",
        "title": "Diet Planner",
        "desc": "Get weekly meal plans based on your dietary preferences, cuisine taste, and calorie budget.",
    },
    {
        "icon": "💪",
        "title": "Workout Planner",
        "desc": "Receive structured workout routines matched to your available equipment and fitness level.",
    },
    {
        "icon": "💬",
        "title": "AI Coach",
        "desc": "Chat with your personal AI fitness coach for real-time motivation, tips, and answers.",
    },
    {
        "icon": "📈",
        "title": "Progress Tracker",
        "desc": "Log weight, measurements, and workout data to visualise your transformation over time.",
    },
]


# ---------------------------------------------------------------------------
# Page renderer
# ---------------------------------------------------------------------------

def render() -> None:
    """Render the Home page."""
    init_session_state()

    # ── Hero ───────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center; padding: 3rem 1rem 1.5rem;">
            <div style="
                display: inline-block;
                background: var(--hero-badge-bg);
                border: 1px solid var(--hero-badge-border);
                border-radius: 50px;
                padding: 0.4rem 1.2rem;
                font-size: 0.8rem;
                font-weight: 600;
                color: var(--accent-1);
                letter-spacing: 0.12em;
                text-transform: uppercase;
                margin-bottom: 1.5rem;
            ">✦ Powered by Google Gemini AI</div>

            <h1 style="
                font-family: 'Outfit', sans-serif;
                font-size: clamp(2.4rem, 6vw, 4rem);
                font-weight: 800;
                line-height: 1.1;
                margin-bottom: 1rem;
                background: var(--gradient-full);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            ">
                AI Fitness &amp; Diet Planner
            </h1>

            <p style="
                font-size: 1.15rem;
                color: var(--text-secondary);
                max-width: 600px;
                margin: 0 auto 0.8rem;
                line-height: 1.75;
            ">
                Your intelligent companion for achieving peak fitness.
                Personalised plans, real-time insights, and AI coaching — all in one place.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Stats strip ────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        ("🔥", "Calories", "Tracked"),
        ("💪", "Workouts", "Planned"),
        ("🥗", "Meal Plans", "Generated"),
        ("📊", "Metrics", "Monitored"),
    ]
    for col, (icon, label, sub) in zip([c1, c2, c3, c4], stats):
        with col:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    padding:1.2rem 0.5rem;
                    background:var(--stat-bg);
                    border:1px solid var(--stat-border);
                    border-radius:14px;
                    margin-bottom:0.5rem;
                ">
                    <div style="font-size:1.8rem;">{icon}</div>
                    <div style="font-size:1rem;font-weight:700;color:var(--text-primary);margin-top:0.3rem;">{label}</div>
                    <div style="font-size:0.78rem;color:var(--text-secondary);">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    styled_divider()

    # ── Feature cards ──────────────────────────────────────────────────────
    st.markdown(
        """
        <h2 style="
            text-align:center;
            font-family:'Outfit',sans-serif;
            font-size:1.75rem;
            font-weight:700;
            color:var(--text-primary);
            margin-bottom:0.4rem;
        ">Everything You Need</h2>
        <p style="text-align:center;color:var(--text-secondary);margin-bottom:1.8rem;font-size:0.95rem;">
            A complete fitness ecosystem — from planning to tracking.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # 3 columns × 2 rows
    for row_start in range(0, len(FEATURES), 3):
        cols = st.columns(3)
        for col, feature in zip(cols, FEATURES[row_start : row_start + 3]):
            with col:
                st.markdown(
                    feature_card_html(
                        feature["icon"],
                        feature["title"],
                        feature["desc"],
                    ),
                    unsafe_allow_html=True,
                )

    styled_divider()

    # ── CTA ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="text-align:center;padding:1.5rem 0 0.5rem;">
            <p style="color:var(--text-secondary);font-size:0.95rem;margin-bottom:1.2rem;">
                Ready to transform your lifestyle? Start by setting up your profile.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_btn, col_r = st.columns([2, 1, 2])
    with col_btn:
        if st.button("🚀  Get Started", use_container_width=True, key="home_cta"):
            st.session_state.current_page = "Profile"
            st.rerun()

    # ── Footer note ────────────────────────────────────────────────────────
    st.markdown(
        """
        <p style="text-align:center;color:var(--text-muted);font-size:0.78rem;margin-top:3rem;">
            AI Fitness &amp; Diet Planner · IBM SkillsBuild Internship Project
        </p>
        """,
        unsafe_allow_html=True,
    )
