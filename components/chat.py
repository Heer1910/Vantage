"""
Chat / conversation history renderer — dark glassmorphism theme.

Renders a scrollable thread showing user questions and AI responses
(charts + insight cards + recommendation cards) with timestamps.
"""

from datetime import datetime
import streamlit as st

from components.charts import render_chart
from components.cards import render_insight_card, render_recommendation_card


def render_conversation(history: list[dict]) -> None:
    """
    Render the full conversation history.

    Each entry in history is a dict with:
      - question: str
      - response: dict (analysis result from Claude) or dashboard dict
      - result: Any (executed code result — DataFrame/Series/scalar or "dashboard")
      - timestamp: str
      - error: str | None
    """
    for entry in history:
        _render_user_message(entry["question"], entry.get("timestamp", ""))
        if entry.get("error"):
            _render_error(entry["error"])
        elif entry.get("response"):
            response = entry["response"]
            # Dashboard mode
            if isinstance(response, dict) and response.get("dashboard"):
                from components.charts import render_dashboard
                from engine.executor import execute_code
                import streamlit as _st
                df = _st.session_state.get("df")
                if df is not None:
                    render_dashboard(response["panels"], df, execute_code)
            else:
                _render_ai_response(response, entry.get("result"))


def _render_user_message(question: str, timestamp: str) -> None:
    """Render a right-aligned user question bubble with glass effect."""
    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: flex-end;
            margin: 16px 0 8px 0;
        ">
            <div style="
                background: linear-gradient(135deg, #6e48ff, #8b5cf6);
                color: #FFFFFF;
                border-radius: 16px 16px 4px 16px;
                padding: 14px 20px;
                max-width: 75%;
                font-size: 0.95rem;
                line-height: 1.5;
                box-shadow: 0 4px 20px rgba(110, 72, 255, 0.25);
            ">
                {question}
            </div>
        </div>
        <div style="text-align: right; margin-bottom: 4px;">
            <span style="font-size: 0.7rem; color: rgba(200, 214, 229, 0.4);">
                {timestamp}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_ai_response(response: dict, result) -> None:
    """Render chart + insight + recommendation cards."""
    chart_spec = response.get("chart_spec", {})
    insight = response.get("insight_narrative", "")
    recommendation = response.get("business_recommendation", "")

    # Render chart (handles its own fallbacks)
    if chart_spec and result is not None:
        render_chart(chart_spec, result)

    # Render cards
    if insight:
        render_insight_card(insight)
    if recommendation:
        render_recommendation_card(recommendation)


def _render_error(error_msg: str) -> None:
    """Render a glass-effect error message."""
    st.markdown(
        f"""
        <div style="
            background: rgba(239, 68, 68, 0.08);
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-left: 4px solid #ef4444;
            border-radius: 12px;
            padding: 16px 20px;
            margin: 8px 0;
            backdrop-filter: blur(10px);
        ">
            <p style="
                margin: 0 0 6px 0;
                font-size: 0.7rem;
                font-weight: 700;
                color: #f87171;
                text-transform: uppercase;
                letter-spacing: 0.1em;
            ">⚠️ Analysis Error</p>
            <p style="
                margin: 0;
                color: #fca5a5;
                font-size: 0.9rem;
                line-height: 1.5;
            ">{error_msg}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
