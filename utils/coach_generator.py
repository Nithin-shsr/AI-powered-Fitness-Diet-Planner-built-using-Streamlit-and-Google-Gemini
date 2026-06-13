# utils/coach_generator.py
"""
AI Coach generator module.
Handles interaction with Gemini for the AI Coach feature.
Enforces strict plain text responses and explicitly blocks HTML and JSON.
"""

from __future__ import annotations

import json
import logging
import re
import textwrap

import google.generativeai as genai
from utils.diet_generator import _get_gemini_client

logger = logging.getLogger(__name__)

# Pattern to detect forbidden HTML tags
HTML_TAGS_PATTERN = re.compile(r"<(div|span|table|tr|td|th|tbody|thead|style|html|body)\b", re.IGNORECASE)

def _validate_response_text(raw_text: str) -> None:
    """Check for forbidden HTML tags in the raw response text."""
    if HTML_TAGS_PATTERN.search(raw_text):
        raise ValueError("HTML detected in Gemini response")
    if not raw_text:
        raise ValueError("Empty response from Gemini")

def get_ai_coach_response(
    user_query: str,
    profile: dict | None = None,
    diet_plan: dict | None = None,
    workout_plan: dict | None = None,
    chat_history: list[dict] | None = None,
) -> str:
    """
    Build context, append user question, call Gemini, and return plain text.
    """
    model = _get_gemini_client()
    
    # 1-3. Build context
    context_sections = []

    if profile and profile.get("name"):
        context_sections.append(f"=== USER PROFILE ===\n{json.dumps(profile, indent=2)}")

    if diet_plan:
        context_sections.append(f"=== CURRENT DIET PLAN ===\n{json.dumps(diet_plan, indent=2)}")

    if workout_plan:
        context_sections.append(f"=== CURRENT WORKOUT PLAN ===\n{json.dumps(workout_plan, indent=2)}")

    history_str = ""
    if chat_history:
        # Keep recent context
        recent_history = chat_history[-6:] 
        history_lines = []
        for msg in recent_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            history_lines.append(f"{role.capitalize()}: {content}")
        history_str = "=== RECENT CONVERSATION HISTORY ===\n" + "\n".join(history_lines)

    context_str = "\n\n".join(context_sections)

    # 4. Append user question and rules
    prompt = textwrap.dedent(f"""
    You are an expert AI Fitness Coach.
    Answer the user's latest question using their profile, diet plan, and workout plan as context if provided.
    
    {context_str}

    {history_str}

    === USER'S LATEST QUESTION ===
    {user_query}

    === CRITICAL RESPONSE RULES ===
    Return ONLY plain text.

    Do NOT generate:
    - HTML
    - CSS
    - JavaScript
    - Markdown tables
    - XML
    - JSON
    - Code blocks

    Never use:
    <div>
    <span>
    <table>
    <style>

    Return only natural conversational text.
    """)

    generation_config = genai.types.GenerationConfig(
        temperature=0.7,
        max_output_tokens=1024,
    )

    # 5. Call Gemini
    try:
        response = model.generate_content(
            prompt.strip(),
            generation_config=generation_config,
        )
    except Exception as exc:
        raise RuntimeError(f"Gemini API error: {exc}") from exc

    raw_text = response.text.strip()
    
    # Safety Filter
    _validate_response_text(raw_text)
    
    # 6. Return plain text only
    return raw_text
