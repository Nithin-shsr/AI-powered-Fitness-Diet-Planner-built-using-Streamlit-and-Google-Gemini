# utils/styles.py
"""
Theming & CSS helpers for AI Fitness Planner.

Architecture:
  - DARK_VARS / LIGHT_VARS  → CSS custom-property (:root) blocks
  - GLOBAL_CSS              → All rules use var(--token) – no hardcoded colours
  - apply_global_styles(theme) → injects the right var block + GLOBAL_CSS
  - Component helpers        → return HTML strings that rely on the CSS classes
"""

import streamlit as st


# ===========================================================================
# CSS CUSTOM PROPERTIES — Dark Theme
# ===========================================================================

DARK_VARS = """:root {
  /* Backgrounds */
  --bg-primary:   #0a0a0f;
  --bg-secondary: #12121a;
  --bg-card:      #1a1a2e;

  /* Accent colours */
  --accent-1:     #6c63ff;
  --accent-1-rgb: 108, 99, 255;
  --accent-2:     #00d4ff;
  --accent-2-rgb: 0, 212, 255;
  --accent-3:     #ff6584;

  /* Semantic colours */
  --success: #34d399;
  --warning: #fbbf24;
  --danger:  #f87171;
  --info:    #60a5fa;

  /* Text */
  --text-primary:   #e2e8f0;
  --text-secondary: #94a3b8;
  --text-muted:     #4a5568;

  /* Borders & surfaces */
  --border:       rgba(108, 99, 255, 0.25);
  --card-bg:      rgba(255, 255, 255, 0.035);
  --card-border:  rgba(108, 99, 255, 0.18);
  --glass-bg:     rgba(255, 255, 255, 0.04);
  --input-bg:     rgba(255, 255, 255, 0.05);
  --input-border: rgba(108, 99, 255, 0.25);
  --progress-track: rgba(255, 255, 255, 0.08);

  /* Sidebar */
  --sidebar-bg-start: #12121a;
  --sidebar-bg-end:   #0d0d1a;
  --sidebar-border:   rgba(108, 99, 255, 0.2);
  --divider-line:     rgba(108, 99, 255, 0.15);

  /* Stat strip */
  --stat-bg:     rgba(255, 255, 255, 0.03);
  --stat-border: rgba(108, 99, 255, 0.15);

  /* Shadows */
  --shadow:       rgba(108, 99, 255, 0.15);
  --shadow-hover: rgba(108, 99, 255, 0.5);

  /* Misc elements */
  --coming-soon-color:  #2d3748;
  --footer-color:       #2d3748;
  --section-border:     rgba(108, 99, 255, 0.3);
  --divider-gradient:   rgba(108, 99, 255, 0.4);

  /* Badge tints */
  --badge-success-bg:     rgba(52, 211, 153, 0.15);
  --badge-success-border: rgba(52, 211, 153, 0.35);
  --badge-warning-bg:     rgba(251, 191, 36, 0.15);
  --badge-warning-border: rgba(251, 191, 36, 0.35);
  --badge-danger-bg:      rgba(248, 113, 113, 0.15);
  --badge-danger-border:  rgba(248, 113, 113, 0.35);
  --badge-info-bg:        rgba(96, 165, 250, 0.15);
  --badge-info-border:    rgba(96, 165, 250, 0.35);

  /* Hero / page-specific */
  --hero-badge-bg:     linear-gradient(135deg, rgba(108,99,255,0.15), rgba(0,212,255,0.08));
  --hero-badge-border: rgba(108, 99, 255, 0.3);
  --gradient:          linear-gradient(135deg, #6c63ff, #00d4ff);
  --gradient-full:     linear-gradient(135deg, #6c63ff 0%, #00d4ff 50%, #ff6584 100%);
  --metric-bg:         linear-gradient(135deg, rgba(108,99,255,0.12) 0%, rgba(0,212,255,0.06) 100%);
  --metric-border:     rgba(108, 99, 255, 0.3);
  --welcome-bg:        linear-gradient(135deg, rgba(108,99,255,0.12), rgba(0,212,255,0.06));
  --welcome-border:    rgba(108, 99, 255, 0.25);
  --detail-bg:         rgba(255, 255, 255, 0.03);
  --detail-border:     rgba(108, 99, 255, 0.2);
  --hydration-bg:      rgba(0, 212, 255, 0.06);
  --hydration-border:  rgba(0, 212, 255, 0.25);
  --hydration-value:   #00d4ff;
  --bmr-bg:            rgba(108, 99, 255, 0.06);
  --bmr-border:        rgba(108, 99, 255, 0.25);
  --bmr-value:         #6c63ff;
  --guard-bg:          rgba(255, 255, 255, 0.03);
  --guard-border:      rgba(108, 99, 255, 0.3);
  --coming-soon-bg:    rgba(255, 255, 255, 0.02);
  --coming-soon-border:rgba(108, 99, 255, 0.2);
  --soon-badge-bg:     rgba(108, 99, 255, 0.15);
  --soon-badge-border: rgba(108, 99, 255, 0.3);
  --soon-badge-color:  #6c63ff;
  --profile-active-bg:     rgba(52, 211, 153, 0.08);
  --profile-active-border: rgba(52, 211, 153, 0.25);
  --profile-active-title:  #34d399;
  --profile-inactive-bg:     rgba(251, 191, 36, 0.08);
  --profile-inactive-border: rgba(251, 191, 36, 0.25);
  --profile-inactive-title:  #fbbf24;

  /* Scrollbar */
  --scrollbar-bg:    #12121a;
  --scrollbar-thumb: #6c63ff;
  --scrollbar-hover: #00d4ff;

  /* Sidebar nav active/hover states */
  --nav-hover-bg:       rgba(108, 99, 255, 0.12);
  --nav-hover-border:   rgba(108, 99, 255, 0.4);
  --nav-active-bg:      rgba(108, 99, 255, 0.22);
  --nav-active-border:  rgba(108, 99, 255, 0.65);
  --nav-active-color:   #c4c0ff;
}"""


# ===========================================================================
# CSS CUSTOM PROPERTIES — Light Theme
# ===========================================================================

LIGHT_VARS = """:root {
  /* Backgrounds */
  --bg-primary:   #f8fafc;
  --bg-secondary: #f1f5f9;
  --bg-card:      #ffffff;

  /* Accent colours */
  --accent-1:     #3b82f6;
  --accent-1-rgb: 59, 130, 246;
  --accent-2:     #06b6d4;
  --accent-2-rgb: 6, 182, 212;
  --accent-3:     #ec4899;

  /* Semantic colours */
  --success: #10b981;
  --warning: #f59e0b;
  --danger:  #ef4444;
  --info:    #3b82f6;

  /* Text */
  --text-primary:   #0f172a;
  --text-secondary: #475569;
  --text-muted: #64748b;

  /* Borders & surfaces */
  --border:       rgba(59, 130, 246, 0.25);
  --card-bg:      #ffffff;
  --card-border:  rgba(59, 130, 246, 0.2);
  --glass-bg:     rgba(255, 255, 255, 0.85);
  --input-bg:     #ffffff;
  --input-border: rgba(59, 130, 246, 0.3);
  --progress-track: rgba(0, 0, 0, 0.07);

  /* Sidebar */
  --sidebar-bg-start: #f8fafc;
  --sidebar-bg-end:   #eef2ff;
  --sidebar-border:   rgba(59, 130, 246, 0.18);
  --divider-line:     rgba(59, 130, 246, 0.12);

  /* Stat strip */
  --stat-bg:     rgba(59, 130, 246, 0.05);
  --stat-border: rgba(59, 130, 246, 0.15);

  /* Shadows */
  --shadow:       rgba(59, 130, 246, 0.1);
  --shadow-hover: rgba(59, 130, 246, 0.35);

  /* Misc elements */
  --coming-soon-color: #64748b;
  --footer-color: #64748b;
  --section-border:     rgba(59, 130, 246, 0.25);
  --divider-gradient:   rgba(59, 130, 246, 0.35);

  /* Badge tints */
  --badge-success-bg:     rgba(16, 185, 129, 0.12);
  --badge-success-border: rgba(16, 185, 129, 0.35);
  --badge-warning-bg:     rgba(245, 158, 11, 0.12);
  --badge-warning-border: rgba(245, 158, 11, 0.35);
  --badge-danger-bg:      rgba(239, 68, 68, 0.12);
  --badge-danger-border:  rgba(239, 68, 68, 0.35);
  --badge-info-bg:        rgba(59, 130, 246, 0.12);
  --badge-info-border:    rgba(59, 130, 246, 0.35);

  /* Hero / page-specific */
  --hero-badge-bg:     linear-gradient(135deg, rgba(59,130,246,0.1), rgba(6,182,212,0.06));
  --hero-badge-border: rgba(59, 130, 246, 0.3);
  --gradient:          linear-gradient(135deg, #3b82f6, #06b6d4);
  --gradient-full:     linear-gradient(135deg, #3b82f6 0%, #06b6d4 50%, #ec4899 100%);
  --metric-bg:         linear-gradient(135deg, rgba(59,130,246,0.08) 0%, rgba(6,182,212,0.05) 100%);
  --metric-border:     rgba(59, 130, 246, 0.25);
  --welcome-bg:        linear-gradient(135deg, rgba(59,130,246,0.08), rgba(6,182,212,0.05));
  --welcome-border:    rgba(59, 130, 246, 0.2);
  --detail-bg:         #ffffff;
  --detail-border:     rgba(59, 130, 246, 0.15);
  --hydration-bg:      rgba(6, 182, 212, 0.06);
  --hydration-border:  rgba(6, 182, 212, 0.25);
  --hydration-value:   #0891b2;
  --bmr-bg:            rgba(59, 130, 246, 0.06);
  --bmr-border:        rgba(59, 130, 246, 0.25);
  --bmr-value:         #2563eb;
  --guard-bg:          rgba(59, 130, 246, 0.04);
  --guard-border:      rgba(59, 130, 246, 0.25);
  --coming-soon-bg:    rgba(59, 130, 246, 0.02);
  --coming-soon-border:rgba(59, 130, 246, 0.2);
  --soon-badge-bg:     rgba(59, 130, 246, 0.1);
  --soon-badge-border: rgba(59, 130, 246, 0.3);
  --soon-badge-color:  #3b82f6;
  --profile-active-bg:     rgba(16, 185, 129, 0.08);
  --profile-active-border: rgba(16, 185, 129, 0.25);
  --profile-active-title:  #059669;
  --profile-inactive-bg:     rgba(245, 158, 11, 0.08);
  --profile-inactive-border: rgba(245, 158, 11, 0.25);
  --profile-inactive-title:  #d97706;

  /* Scrollbar */
  --scrollbar-bg:    #f1f5f9;
  --scrollbar-thumb: #3b82f6;
  --scrollbar-hover: #06b6d4;

  /* Sidebar nav active/hover states */
  --nav-hover-bg:       rgba(59, 130, 246, 0.1);
  --nav-hover-border:   rgba(59, 130, 246, 0.4);
  --nav-active-bg:      rgba(59, 130, 246, 0.16);
  --nav-active-border:  rgba(59, 130, 246, 0.6);
  --nav-active-color:   #1d4ed8;
}"""


# ===========================================================================
# GLOBAL CSS — uses only var(--token), zero hardcoded colours
# ===========================================================================

GLOBAL_CSS = """
/* ── Google Font ──────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;800&display=swap');

/* ── Reset & Base ─────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Fix Material Icons showing as raw text due to font-family overrides */
.material-icons,
.material-icons-outlined,
.material-symbols-outlined,
.material-symbols-rounded,
[class^="material-symbols-"],
[class^="material-icons-"] {
    font-family: 'Material Symbols Outlined', 'Material Symbols Rounded', 'Material Icons' !important;
}

/* ── Hide Streamlit chrome ───────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--sidebar-bg-start) 0%, var(--sidebar-bg-end) 100%) !important;
    border-right: 1px solid var(--sidebar-border) !important;
}

[data-testid="stSidebar"] *:not(.material-icons):not(.material-icons-outlined):not(.material-symbols-outlined):not(.material-symbols-rounded) {
    font-family: 'Inter', sans-serif !important;
}

/* ── Sidebar nav radio ───────────────────────────────────── */
[data-testid="stSidebar"] .stRadio > div {
    gap: 0.5rem;
    display: flex;
    flex-direction: column;
}

/* Hide the actual radio dot */
[data-testid="stSidebar"] .stRadio input[type="radio"] {
    display: none !important;
}

[data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    padding: 0.7rem 1.2rem !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
    border: 1px solid transparent !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    margin-bottom: 0 !important;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background: var(--nav-hover-bg) !important;
    border-color: var(--nav-hover-border) !important;
    color: var(--text-primary) !important;
}

/* Active / selected nav item */
[data-testid="stSidebar"] .stRadio label:has(input[type="radio"]:checked) {
    background: var(--nav-active-bg) !important;
    border-color: var(--nav-active-border) !important;
    color: var(--nav-active-color) !important;
    font-weight: 700 !important;
}

/* ── Glass card ──────────────────────────────────────────── */
.glass-card {
    background: var(--glass-bg);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    padding: 1.8rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    margin-bottom: 1rem;
}

.glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 40px var(--shadow);
    border-color: var(--border);
}

/* ── Metric card ─────────────────────────────────────────── */
.metric-card {
    background: var(--metric-bg);
    border: 1px solid var(--metric-border);
    border-radius: 18px;
    padding: 1.5rem 1.2rem;
    text-align: center;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 30px var(--shadow);
}

.metric-icon  { font-size: 2rem; margin-bottom: 0.5rem; }
.metric-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
    margin-bottom: 0.3rem;
}
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    font-family: 'Outfit', sans-serif;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.metric-unit { font-size: 0.82rem; color: var(--text-secondary); margin-top: 0.15rem; }

/* ── Feature card ────────────────────────────────────────── */
.feature-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 18px;
    padding: 1.6rem;
    text-align: center;
    height: 100%;
    transition: all 0.3s ease, transform 0.1s ease;
    box-shadow: 0 2px 8px var(--shadow);
    cursor: pointer;
}

.feature-card:hover {
    background: var(--glass-bg);
    border-color: var(--border);
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 16px 35px var(--shadow);
}

.feature-card:active {
    transform: translateY(0px) scale(0.98);
    box-shadow: 0 4px 15px var(--shadow);
}

.feature-icon  { font-size: 2.5rem; margin-bottom: 0.8rem; display: block; pointer-events: none; }
.feature-title { font-size: 1.05rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem; pointer-events: none; }
.feature-desc  { font-size: 0.88rem; color: var(--text-secondary); line-height: 1.6; pointer-events: none; }

/* ── Section header ──────────────────────────────────────── */
.section-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1.2rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid var(--section-border);
}

/* ── Status badges ───────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 50px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}
.badge-success { background: var(--badge-success-bg); color: var(--success); border: 1px solid var(--badge-success-border); }
.badge-warning { background: var(--badge-warning-bg); color: var(--warning); border: 1px solid var(--badge-warning-border); }
.badge-danger  { background: var(--badge-danger-bg);  color: var(--danger);  border: 1px solid var(--badge-danger-border); }
.badge-info    { background: var(--badge-info-bg);    color: var(--info);    border: 1px solid var(--badge-info-border); }

/* ── Styled divider ──────────────────────────────────────── */
.styled-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--divider-gradient), transparent);
    margin: 1.5rem 0;
    border: none;
}

/* ── Streamlit button ────────────────────────────────────── */
.stButton > button {
    background: var(--gradient) !important;
    border: none !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.8rem !important;
    letter-spacing: 0.03em !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 15px var(--shadow) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px var(--shadow-hover) !important;
    opacity: 0.95 !important;
}

/* ── Streamlit inputs ────────────────────────────────────── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: var(--input-bg) !important;
    border: 1px solid var(--input-border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--accent-1) !important;
    box-shadow: 0 0 0 3px rgba(var(--accent-1-rgb), 0.15) !important;
}

.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--input-bg) !important;
    border: 1px solid var(--input-border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Slider & progress bar ───────────────────────────────── */
.stSlider > div > div > div > div,
.stProgress > div > div > div > div {
    background: var(--gradient) !important;
}

/* ── Expander ────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] summary {
    color: var(--text-primary) !important;
}

/* ── Info / success / error boxes ───────────────────────── */
.stAlert {
    background: var(--card-bg) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}

/* ── Caption / small text ────────────────────────────────── */
.stCaption, small { color: var(--text-secondary) !important; }

/* ── Toggle (theme switch) ───────────────────────────────── */
[data-testid="stToggle"] label { color: var(--text-secondary) !important; }

/* ── Scrollbar ───────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--scrollbar-bg); }
::-webkit-scrollbar-thumb { background: var(--scrollbar-thumb); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--scrollbar-hover); }

/* ── Markdown text colour ────────────────────────────────── */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] td,
[data-testid="stMarkdownContainer"] th {
    color: var(--text-primary) !important;
}

/* ── Selectbox / dropdown text (fixes white-on-white in light mode) ── */
[data-baseweb="select"] span,
[data-baseweb="select"] div[class*="placeholder"],
[data-baseweb="menu"] li,
[data-baseweb="menu"] [role="option"],
.stSelectbox label,
.stMultiSelect label,
.stNumberInput label,
.stTextInput label,
.stSlider label {
    color: var(--text-primary) !important;
}

/* Selectbox dropdown background */
[data-baseweb="popover"],
[data-baseweb="menu"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--card-border) !important;
}

/* ── Form labels & widget text ───────────────────────────── */
.stRadio label p,
.stCheckbox label p,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
    color: var(--text-primary) !important;
}

/* ── Expander header text ───────────────────────────────── */
[data-testid="stExpander"] summary p {
    color: var(--text-primary) !important;
}

/* ── st.success / st.error / st.info / st.warning ────────── */
[data-testid="stNotification"] p,
[data-testid="stNotification"] span {
    color: inherit !important;
}

/* ── Prevent horizontal overflow ─────────────────────────── */
[data-testid="stAppViewContainer"] {
    overflow-x: hidden !important;
}

/* ── Caption text ─────────────────────────────────────────── */
[data-testid="stCaptionContainer"] p {
    color: var(--text-muted) !important;
}

/* ── Chat messages ────────────────────────────────────────── */
[data-testid="stChatMessage"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 14px !important;
    margin-bottom: 0.75rem !important;
}
[data-testid="stChatMessage"] p {
    color: var(--text-primary) !important;
}

/* ── Chat input ───────────────────────────────────────────── */
[data-testid="stChatInput"] textarea {
    background: var(--input-bg) !important;
    border: 1px solid var(--input-border) !important;
    color: var(--text-primary) !important;
    border-radius: 12px !important;
}

/* ── View Transitions (Theme Radial Reveal) ───────────────── */
::view-transition-old(root),
::view-transition-new(root) {
  animation: none;
  mix-blend-mode: normal;
}

::view-transition-old(root) {
  z-index: 1;
}

::view-transition-new(root) {
  z-index: 9999;
  clip-path: circle(0px at var(--theme-x, 50%) var(--theme-y, 50%));
  animation: theme-reveal 0.8s ease-out forwards;
}

@keyframes theme-reveal {
  to {
    clip-path: circle(150% at var(--theme-x, 50%) var(--theme-y, 50%));
  }
}

/* ── Navigation Hub ──────────────────────────────────────── */
.nav-hub {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-top: 2rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

/* For Streamlit buttons inside the nav hub */
.nav-hub-btn-container {
    flex: 1 1 0;
    min-width: 150px;
    max-width: 200px;
}

/* Removed overlay hacks */

/* ── Floating Real Streamlit Buttons ────────────────────── */
.floating-theme-btn {
    position: fixed !important;
    top: 15px !important;
    right: 20px !important;
    z-index: 999999 !important;
}

.floating-theme-btn button {
    background: var(--glass-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 50% !important;
    width: 48px !important;
    height: 48px !important;
    font-size: 1.2rem !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px var(--shadow) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    color: var(--text-primary) !important;
    padding: 0 !important;
}

.floating-theme-btn button:hover {
    transform: scale(1.1) !important;
    box-shadow: 0 8px 20px var(--shadow-hover) !important;
}

.floating-theme-btn button p {
    margin: 0 !important;
    padding: 0 !important;
}

.floating-home-btn {
    position: fixed !important;
    top: 15px !important;
    left: 20px !important;
    z-index: 999999 !important;
}

.floating-home-btn button {
    background: var(--glass-bg) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 50px !important;
    padding: 0.5rem 1.2rem !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    box-shadow: 0 4px 15px var(--shadow) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    color: var(--text-primary) !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.4rem !important;
    height: auto !important;
}

.floating-home-btn button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 8px 20px var(--shadow-hover) !important;
}

.floating-home-btn button p {
    margin: 0 !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ── Responsive: tablet (≤ 1024px) ───────────────────────── */
@media (max-width: 1024px) {
    /* Reduce padding on main content */
    [data-testid="stMain"] .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}

/* ── Responsive: mobile (≤ 768px) ────────────────────────── */
@media (max-width: 768px) {
    /* Prevent horizontal scroll on all levels */
    html, body { overflow-x: hidden !important; }

    /* Reduce main padding */
    [data-testid="stMain"] .block-container {
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
        padding-top: 1rem !important;
    }

    /* Glass / metric / feature cards — full width on mobile */
    .glass-card, .metric-card, .feature-card,
    .meal-card, .day-card, .summary-card, .wo-summary-card {
        margin-left: 0 !important;
        margin-right: 0 !important;
    }

    /* Stack Nav Hub on mobile */
    .nav-hub {
        flex-direction: column;
        align-items: stretch;
    }
    .nav-hub-btn-container {
        max-width: 100%;
    }

    /* Reduce hero heading */
    h1 { font-size: clamp(1.6rem, 5vw, 2.5rem) !important; }

    /* Make tables horizontally scrollable */
    .wo-table {
        display: block;
        overflow-x: auto;
        white-space: nowrap;
    }

    /* Section headers font size */
    .section-header { font-size: 1.2rem !important; }
}
"""


# ===========================================================================
# Public API
# ===========================================================================

def apply_global_styles(theme: str = "Light") -> None:
    """
    Inject CSS custom properties + global styles into the Streamlit app.
    Call once at the top of app.py, after reading the theme from session state.

    Args:
        theme: "Light" (default) or "Dark"
    """
    vars_block = DARK_VARS if theme == "Dark" else LIGHT_VARS
    st.markdown(
        f"<style>{vars_block}\n{GLOBAL_CSS}</style>",
        unsafe_allow_html=True,
    )


def get_theme_from_state() -> str:
    """Return the current theme from session state (defaults to 'Light')."""
    return st.session_state.get("theme", "Light")


# ---------------------------------------------------------------------------
# HTML component helpers — all colours via CSS vars
# ---------------------------------------------------------------------------

def metric_card_html(icon: str, label: str, value: str, unit: str = "") -> str:
    """Return HTML for a styled metric card (colours from CSS vars)."""
    return f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-unit">{unit}</div>
    </div>
    """


def feature_card_html(icon: str, title: str, description: str, page: str = None) -> str:
    """Return HTML for a feature highlight card. If page is provided, makes it clickable via clickNavHub."""
    onclick_attr = f""" onclick="if(window.parent.clickNavHub) window.parent.clickNavHub('{page}')" """ if page else ""
    return f"""
    <div class="feature-card"{onclick_attr}>
        <span class="feature-icon">{icon}</span>
        <div class="feature-title">{title}</div>
        <div class="feature-desc">{description}</div>
    </div>
    """


def badge_html(text: str, variant: str = "info") -> str:
    """Return an HTML badge. variant: 'success' | 'warning' | 'danger' | 'info'."""
    return f'<span class="badge badge-{variant}">{text}</span>'


def section_header(title: str) -> None:
    """Render a styled section header."""
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def styled_divider() -> None:
    """Render a gradient divider."""
    st.markdown('<hr class="styled-divider" />', unsafe_allow_html=True)


def glass_card(content_html: str) -> None:
    """Wrap content in a glass-morphism card."""
    st.markdown(f'<div class="glass-card">{content_html}</div>', unsafe_allow_html=True)
