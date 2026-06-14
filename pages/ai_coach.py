# pages/ai_coach.py
"""
AI Coach page — Phase 5.
Personalized fitness and nutrition assistant powered by Gemini.
Uses pure plain text and strictly blocks HTML.
"""

import streamlit as st
from utils.session_manager import init_session_state
from utils.coach_generator import get_ai_coach_response

# Page-specific UI CSS (no logic changes)
COACH_CSS = """
<style>
/* ── Suggestion chips ──────────────────────────────────────── */
.suggestion-chip {
    display: inline-block;
    background: var(--glass-bg);
    border: 1px solid var(--card-border);
    border-radius: 50px;
    padding: 0.35rem 0.9rem;
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin: 0.2rem;
    transition: all 0.2s ease;
}
.suggestion-chip:hover {
    background: rgba(var(--accent-1-rgb), 0.12);
    border-color: var(--accent-1);
    color: var(--accent-1);
}
</style>
"""


def render() -> None:
    init_session_state()

    # Inject UI-only styles
    st.markdown(COACH_CSS, unsafe_allow_html=True)

    # Initialize chat history
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    # ── Page header + Clear button ─────────────────────────────────────────
    header_col, btn_col = st.columns([7, 1])
    with header_col:
        st.markdown(
            """
            <div style="padding: 1.2rem 0 0.2rem;">
                <h1 style="
                    font-family:'Outfit',sans-serif;
                    font-size:2rem;
                    font-weight:800;
                    background:var(--gradient);
                    -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;
                    background-clip:text;
                    margin-bottom:0.2rem;
                ">🤖 AI Fitness Coach</h1>
                <p style="color:var(--text-secondary);font-size:0.92rem;margin:0;">
                    Ask questions about your workouts, nutrition, recovery, and fitness goals.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with btn_col:
        st.markdown("<div style='padding-top:1.8rem;'>", unsafe_allow_html=True)
        if st.button("🗑️ Clear", key="coach_clear_btn", help="Clear chat history"):
            st.session_state.ai_chat_history = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<hr style='border:none;border-top:1px solid var(--divider-line);margin:0 0 1rem;'/>",
        unsafe_allow_html=True,
    )

    # ── Empty state ────────────────────────────────────────────────────────
    if not st.session_state.ai_chat_history:
        st.markdown(
            """
            <div style="
                text-align:center;
                padding:3rem 1rem 2.5rem;
                background:var(--card-bg);
                border:1px dashed var(--card-border);
                border-radius:20px;
                margin-bottom:1.5rem;
            ">
                <div style="font-size:3.5rem;margin-bottom:0.8rem;">💬</div>
                <div style="
                    font-size:1.15rem;
                    font-weight:700;
                    color:var(--text-primary);
                    margin-bottom:0.6rem;
                    font-family:'Outfit',sans-serif;
                ">Your AI Coach is ready!</div>
                <div style="color:var(--text-secondary);font-size:0.9rem;max-width:480px;
                            margin:0 auto;line-height:1.7;">
                    Ask me anything about fitness, nutrition, recovery, or your personalised plans.
                    I have full context of your profile, diet plan, and workout programme.
                </div>
                <div style="
                    display:flex;
                    gap:0.4rem;
                    flex-wrap:wrap;
                    justify-content:center;
                    margin-top:1.5rem;
                    max-width:560px;
                    margin-left:auto;
                    margin-right:auto;
                ">
                    <span class="suggestion-chip">💡 How can I stay motivated?</span>
                    <span class="suggestion-chip">🥗 Pre-workout nutrition tips?</span>
                    <span class="suggestion-chip">💧 Daily water intake guidance?</span>
                    <span class="suggestion-chip">💪 Build muscle while losing fat?</span>
                    <span class="suggestion-chip">😴 Sleep &amp; recovery tips?</span>
                    <span class="suggestion-chip">📈 Progressive overload guide?</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Render chat history ────────────────────────────────────────────────
    for msg in st.session_state.ai_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Chat input ─────────────────────────────────────────────────────────
    if user_input := st.chat_input("Ask your coach a question..."):
        # Append user message
        st.session_state.ai_chat_history.append({"role": "user", "content": user_input})

        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        # Build context
        profile = st.session_state.get("profile")
        diet_plan = st.session_state.get("diet_plan_result")
        workout_plan = st.session_state.get("workout_plan_result")
        history = st.session_state.ai_chat_history[:-1]

        with st.chat_message("assistant"):
            with st.spinner("Coach is thinking..."):
                try:
                    response_text = get_ai_coach_response(
                        user_query=user_input,
                        profile=profile,
                        diet_plan=diet_plan,
                        workout_plan=workout_plan,
                        chat_history=history
                    )

                    # Store to history
                    st.session_state.ai_chat_history.append({
                        "role": "assistant",
                        "content": response_text
                    })

                    # Render response
                    st.markdown(response_text)

                except EnvironmentError:
                    st.error("🔑 Google API key is missing. Please configure it in your `.env` file.")
                except ValueError:
                    # HTML detection error or empty response
                    st.error("⚠️ AI Coach returned an invalid format. Please try asking again.")
                except Exception as e:
                    # Generic API / Network error
                    err_str = str(e).lower()
                    if "429" in err_str or "quota" in err_str:
                        st.error("⏳ AI Coach is currently busy (rate limit reached). Please wait a moment and try again.")
                    else:
                        st.error("🔌 Unable to reach AI Coach right now. Please try again in a moment.")
