# pages/dashboard.py
"""
Dashboard page – displays calculated health & fitness metrics.
Reads profile data from session state and uses utils/calculations.py.
"""

import streamlit as st

from utils.session_manager import init_session_state, get_profile, is_profile_complete
from utils.calculations import (
    calculate_bmi,
    bmi_category,
    calculate_bmr,
    calculate_daily_calories,
    calculate_protein,
    calculate_water_intake,
    estimate_goal_weeks,
)
from utils.styles import (
    metric_card_html,
    section_header,
    styled_divider,
    badge_html,
    glass_card,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _progress_ring(value: float, max_val: float, colour: str, label: str) -> str:
    """Return HTML for a simple linear progress bar with label."""
    pct = min(100, round(value / max_val * 100))
    return f"""
    <div style="margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;margin-bottom:0.35rem;">
            <span style="font-size:0.82rem;color:#94a3b8;">{label}</span>
            <span style="font-size:0.82rem;font-weight:600;color:{colour};">{pct}%</span>
        </div>
        <div style="height:8px;background:rgba(255,255,255,0.08);border-radius:50px;overflow:hidden;">
            <div style="
                width:{pct}%;
                height:100%;
                background:linear-gradient(90deg,{colour}aa,{colour});
                border-radius:50px;
                transition:width 0.6s ease;
            "></div>
        </div>
    </div>
    """


def _bmi_gauge(bmi: float) -> str:
    """
    Return HTML for a horizontal BMI gauge strip.
    Ranges: <18.5 (blue) | 18.5–25 (green) | 25–30 (amber) | >30 (red)
    """
    # Clamp display position 10-40 → 0-100%
    clamped = max(10, min(40, bmi))
    pos = (clamped - 10) / 30 * 100

    _, colour = bmi_category(bmi)

    return f"""
    <div style="margin:1rem 0;">
        <div style="position:relative;height:14px;border-radius:50px;overflow:hidden;
                    background:linear-gradient(90deg,#60a5fa 0%,#34d399 30%,#fbbf24 60%,#f87171 100%);">
            <div style="
                position:absolute;
                left:calc({pos}% - 8px);
                top:-3px;
                width:20px;
                height:20px;
                background:{colour};
                border-radius:50%;
                border:3px solid #0a0a0f;
                box-shadow:0 0 10px {colour}88;
                transition:left 0.6s ease;
            "></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:0.4rem;">
            <span style="font-size:0.7rem;color:#60a5fa;">Underweight<br/>&lt;18.5</span>
            <span style="font-size:0.7rem;color:#34d399;">Normal<br/>18.5–25</span>
            <span style="font-size:0.7rem;color:#fbbf24;">Overweight<br/>25–30</span>
            <span style="font-size:0.7rem;color:#f87171;">Obese<br/>&gt;30</span>
        </div>
    </div>
    """


# ---------------------------------------------------------------------------
# Page renderer
# ---------------------------------------------------------------------------

def render() -> None:
    """Render the Dashboard page."""
    init_session_state()

    # ── Page header ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="padding: 1.5rem 0 0.5rem;">
            <h1 style="
                font-family:'Outfit',sans-serif;
                font-size:2rem;
                font-weight:800;
                background:linear-gradient(135deg,#6c63ff,#00d4ff);
                -webkit-background-clip:text;
                -webkit-text-fill-color:transparent;
                background-clip:text;
                margin-bottom:0.3rem;
            ">📊 Health Dashboard</h1>
            <p style="color:#94a3b8;font-size:0.95rem;">
                Your personalised health metrics — calculated from your profile.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    styled_divider()

    # ── Guard: require profile ─────────────────────────────────────────────
    if not is_profile_complete():
        st.markdown(
            """
            <div style="
                text-align:center;
                padding:3rem 1rem;
                background:rgba(255,255,255,0.03);
                border:1px dashed rgba(108,99,255,0.3);
                border-radius:20px;
                margin-top:1rem;
            ">
                <div style="font-size:3rem;margin-bottom:1rem;">🔒</div>
                <h3 style="color:#e2e8f0;margin-bottom:0.5rem;">Profile Required</h3>
                <p style="color:#94a3b8;max-width:400px;margin:0 auto 1.5rem;">
                    Please complete your profile first so we can calculate your personalised metrics.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_l, col_btn, col_r = st.columns([2, 1, 2])
        with col_btn:
            if st.button("👤  Go to Profile", use_container_width=True, key="dash_goto_profile"):
                st.session_state.current_page = "Profile"
                st.rerun()
        return

    # ── Compute metrics ────────────────────────────────────────────────────
    profile = get_profile()

    weight   = profile["weight_kg"]
    height   = profile["height_cm"]
    age      = profile["age"]
    gender   = profile["gender"]
    activity = profile["activity_level"]
    goal     = profile["fitness_goal"]
    target   = profile["target_weight_kg"]

    bmi          = calculate_bmi(weight, height)
    bmi_cat, bmi_colour = bmi_category(bmi)
    bmr          = calculate_bmr(weight, height, age, gender)
    daily_cals   = calculate_daily_calories(bmr, activity, goal)
    protein_min, protein_max = calculate_protein(weight, goal)
    water_litres = calculate_water_intake(weight)
    weeks        = estimate_goal_weeks(weight, target, goal)

    # ── Welcome banner ─────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background:linear-gradient(135deg,rgba(108,99,255,0.12),rgba(0,212,255,0.06));
            border:1px solid rgba(108,99,255,0.25);
            border-radius:18px;
            padding:1.4rem 1.8rem;
            margin-bottom:1.5rem;
            display:flex;
            align-items:center;
            gap:1rem;
        ">
            <div style="font-size:2.5rem;">👋</div>
            <div>
                <div style="font-size:1.2rem;font-weight:700;color:#e2e8f0;">
                    Hello, {profile['name']}!
                </div>
                <div style="color:#94a3b8;font-size:0.9rem;margin-top:0.2rem;">
                    Goal: <strong style="color:#6c63ff;">{goal}</strong> ·
                    Activity: <strong style="color:#00d4ff;">{activity}</strong> ·
                    Diet: <strong style="color:#ff6584;">{profile['diet_preference']}</strong>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Main metric cards row ──────────────────────────────────────────────
    section_header("🔢 Key Health Metrics")

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.markdown(
            metric_card_html("⚖️", "BMI", str(bmi), bmi_cat),
            unsafe_allow_html=True,
        )

    with m2:
        st.markdown(
            metric_card_html("🔥", "BMR", f"{int(bmr):,}", "kcal / day"),
            unsafe_allow_html=True,
        )

    with m3:
        st.markdown(
            metric_card_html("🍽️", "Daily Calories", f"{daily_cals:,}", "kcal target"),
            unsafe_allow_html=True,
        )

    with m4:
        st.markdown(
            metric_card_html("💪", "Protein", f"{protein_min}–{protein_max}", "g / day"),
            unsafe_allow_html=True,
        )

    with m5:
        st.markdown(
            metric_card_html("💧", "Water", str(water_litres), "litres / day"),
            unsafe_allow_html=True,
        )

    styled_divider()

    # ── Two-column detail area ─────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1], gap="large")

    # LEFT — BMI detail
    with col_left:
        section_header("⚖️ BMI Analysis")

        badge_variant = (
            "success" if bmi_cat == "Normal Weight"
            else "info" if bmi_cat == "Underweight"
            else "warning" if bmi_cat == "Overweight"
            else "danger"
        )

        st.markdown(
            f"""
            <div style="
                background:rgba(255,255,255,0.03);
                border:1px solid rgba(108,99,255,0.2);
                border-radius:16px;
                padding:1.5rem;
            ">
                <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.8rem;">
                    <span style="font-size:2.5rem;font-family:'Outfit',sans-serif;font-weight:800;
                                 color:{bmi_colour};">{bmi}</span>
                    {badge_html(bmi_cat, badge_variant)}
                </div>
                {_bmi_gauge(bmi)}
                <div style="margin-top:1rem;font-size:0.88rem;color:#94a3b8;line-height:1.7;">
                    <strong style="color:#e2e8f0;">Height:</strong> {height} cm &nbsp;|&nbsp;
                    <strong style="color:#e2e8f0;">Weight:</strong> {weight} kg<br/>
                    <strong style="color:#e2e8f0;">Target:</strong> {target} kg
                    {"&nbsp;|&nbsp;<strong style='color:#e2e8f0;'>ETA:</strong> ~" + str(weeks) + " weeks" if weeks else ""}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # RIGHT — Calorie & macro breakdown
    with col_right:
        section_header("🍽️ Calorie & Macro Breakdown")

        total_macros = daily_cals

        # Macro distribution (approximate split by goal)
        if "Muscle" in goal:
            carb_pct, fat_pct = 0.45, 0.25
        elif "Weight Loss" in goal:
            carb_pct, fat_pct = 0.35, 0.30
        else:
            carb_pct, fat_pct = 0.50, 0.25

        protein_cals = protein_min * 4
        carb_cals    = round(total_macros * carb_pct)
        fat_cals     = round(total_macros * fat_pct)
        carb_g       = carb_cals // 4
        fat_g        = fat_cals // 9

        st.markdown(
            f"""
            <div style="
                background:rgba(255,255,255,0.03);
                border:1px solid rgba(108,99,255,0.2);
                border-radius:16px;
                padding:1.5rem;
            ">
                <div style="font-size:0.9rem;color:#94a3b8;margin-bottom:1rem;">
                    Daily target: <strong style="color:#e2e8f0;font-size:1.1rem;">{daily_cals:,} kcal</strong>
                    &nbsp;({goal})
                </div>

                {_progress_ring(protein_min * 4, total_macros, "#6c63ff",
                  f"🥩 Protein  {protein_min}–{protein_max} g  ({protein_min*4} kcal)")}
                {_progress_ring(carb_cals, total_macros, "#00d4ff",
                  f"🍞 Carbs  ~{carb_g} g  ({carb_cals} kcal)")}
                {_progress_ring(fat_cals, total_macros, "#ff6584",
                  f"🥑 Fats  ~{fat_g} g  ({fat_cals} kcal)")}

                <div style="font-size:0.75rem;color:#4a5568;margin-top:0.5rem;">
                    * Macro split is approximate and goal-adjusted.
                    Adjust under guidance of a nutritionist.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    styled_divider()

    # ── Hydration & BMR detail ─────────────────────────────────────────────
    col_h, col_b = st.columns(2, gap="large")

    with col_h:
        section_header("💧 Daily Hydration Goal")
        glasses = round(water_litres / 0.25)  # 1 glass ≈ 250 ml

        st.markdown(
            f"""
            <div style="
                background:rgba(0,212,255,0.06);
                border:1px solid rgba(0,212,255,0.25);
                border-radius:16px;
                padding:1.4rem;
                text-align:center;
            ">
                <div style="font-size:3rem;">💧</div>
                <div style="font-size:2.5rem;font-weight:800;font-family:'Outfit',sans-serif;
                             color:#00d4ff;margin:0.3rem 0;">{water_litres} L</div>
                <div style="color:#94a3b8;font-size:0.88rem;">
                    ≈ <strong style="color:#e2e8f0;">{glasses} glasses</strong> of water per day
                </div>
                <div style="margin-top:1rem;font-size:0.8rem;color:#4a5568;">
                    Based on 35 ml / kg body-weight (EFSA guideline)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_b:
        section_header("🔥 Basal Metabolic Rate")
        st.markdown(
            f"""
            <div style="
                background:rgba(108,99,255,0.06);
                border:1px solid rgba(108,99,255,0.25);
                border-radius:16px;
                padding:1.4rem;
                text-align:center;
            ">
                <div style="font-size:3rem;">🔥</div>
                <div style="font-size:2.5rem;font-weight:800;font-family:'Outfit',sans-serif;
                             color:#6c63ff;margin:0.3rem 0;">{int(bmr):,}</div>
                <div style="color:#94a3b8;font-size:0.88rem;">kcal burned at complete rest per day</div>
                <div style="margin-top:1rem;font-size:0.8rem;color:#4a5568;">
                    Mifflin-St Jeor formula · TDEE = {daily_cals:,} kcal
                    (× {1.2 if activity == "Sedentary" else 1.375 if activity == "Lightly Active" else 1.55 if activity == "Moderately Active" else 1.725 if activity == "Very Active" else 1.9} activity multiplier)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    styled_divider()

    # ── Methodology note ───────────────────────────────────────────────────
    with st.expander("ℹ️  How are these values calculated?"):
        st.markdown(
            """
            | Metric | Formula / Standard |
            |--------|-------------------|
            | **BMI** | Weight (kg) ÷ Height² (m) — WHO classification |
            | **BMR** | Mifflin-St Jeor equation (1990) |
            | **Daily Calories (TDEE)** | BMR × Activity Multiplier ± Goal Delta |
            | **Protein** | 1.6–2.2 g/kg body-weight — ISSN recommendation |
            | **Water** | 35 ml × body-weight (kg) — EFSA guideline |

            > These are evidence-based estimates. For medical or clinical decisions,
            > always consult a registered dietitian or healthcare professional.
            """
        )


