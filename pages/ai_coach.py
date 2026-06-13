# pages/ai_coach.py
"""
AI Coach page — Phase 5.
Personalized fitness and nutrition assistant powered by Gemini.
Uses pure plain text and strictly blocks HTML.
"""

import streamlit as st
from utils.session_manager import init_session_state
from utils.coach_generator import get_ai_coach_response

def render() -> None:
    init_session_state()

    # Initialize chat history
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    # Page Header (Strictly no HTML)
    st.title("🤖 AI Fitness Coach")
    st.write("Ask questions about your workouts, nutrition, recovery, and fitness goals.")
    
    # Clear chat button
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.button("Clear Chat"):
            st.session_state.ai_chat_history = []
            st.rerun()
            
    st.divider()

    # Render Chat History
    for msg in st.session_state.ai_chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
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
                    st.error("Google API key is missing. Please configure it in your environment.")
                except ValueError:
                    # HTML detection error or empty response
                    st.error("AI Coach returned an invalid format. Please try asking again.")
                except Exception as e:
                    # Generic API / Network error
                    err_str = str(e).lower()
                    if "429" in err_str or "quota" in err_str:
                        st.error("AI Coach is currently busy (rate limit reached). Please wait a moment and try again.")
                    else:
                        st.error("Unable to reach AI Coach right now. Please try again in a moment.")

