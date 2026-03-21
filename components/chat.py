"""
Chat / conversation history renderer — colorful pastel theme.

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
    """Render a right-aligned user question bubble with gradient."""
    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: flex-end;
            margin: 14px 0 6px 0;
        ">
            <div style="
                background: linear-gradient(135deg, #7b5ea7, #9b7bc4);
                color: #ffffff;
                border-radius: 14px 14px 4px 14px;
                padding: 12px 16px;
                max-width: 75%;
                font-size: 0.9rem;
                line-height: 1.5;
                box-shadow: 0 3px 10px rgba(123, 94, 167, 0.15);
            ">
                {question}
            </div>
        </div>
        <div style="text-align: right; margin-bottom: 4px;">
            <span style="font-size: 0.7rem; color: #b5b0be;">
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

    if chart_spec and result is not None:
        render_chart(chart_spec, result)

    if insight:
        render_insight_card(insight)
    if recommendation:
        render_recommendation_card(recommendation)


def _render_error(error_msg: str) -> None:
    """Render a pastel error card."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #fce8e0, #fde8e0);
            border-left: 3px solid #d4856a;
            border-radius: 12px;
            padding: 14px 18px;
            margin: 8px 0;
        ">
            <p style="
                margin: 0 0 4px 0;
                font-size: 0.72rem;
                font-weight: 600;
                color: #d4856a;
                letter-spacing: 0.04em;
            ">Something went wrong</p>
            <p style="
                margin: 0;
                color: #5a4d48;
                font-size: 0.88rem;
                line-height: 1.5;
            ">{error_msg}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
