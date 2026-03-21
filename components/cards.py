"""
Insight & Recommendation cards for the dark glassmorphism theme.

Each card renders as a styled markdown block with frosted glass effect.
"""

import streamlit as st


def render_insight_card(text: str) -> None:
    """Render a glass-effect insight card with a cyan/purple accent."""
    st.markdown(
        f"""
        <div style="
            background: rgba(110, 72, 255, 0.06);
            border: 1px solid rgba(110, 72, 255, 0.15);
            border-left: 4px solid #6e48ff;
            border-radius: 12px;
            padding: 20px 22px;
            margin: 12px 0;
            backdrop-filter: blur(10px);
            animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        ">
            <p style="
                margin: 0 0 8px 0;
                font-size: 0.7rem;
                font-weight: 700;
                color: #a78bfa;
                text-transform: uppercase;
                letter-spacing: 0.1em;
            ">💡 What the data shows</p>
            <p style="
                margin: 0;
                color: #c8d6e5;
                font-size: 0.9rem;
                line-height: 1.6;
            ">{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendation_card(text: str) -> None:
    """Render a glass-effect recommendation card with an amber accent."""
    st.markdown(
        f"""
        <div style="
            background: rgba(245, 158, 11, 0.06);
            border: 1px solid rgba(245, 158, 11, 0.15);
            border-left: 4px solid #f59e0b;
            border-radius: 12px;
            padding: 20px 22px;
            margin: 12px 0;
            backdrop-filter: blur(10px);
            animation: slideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        ">
            <p style="
                margin: 0 0 8px 0;
                font-size: 0.7rem;
                font-weight: 700;
                color: #fbbf24;
                text-transform: uppercase;
                letter-spacing: 0.1em;
            ">⚡ What this means for your business</p>
            <p style="
                margin: 0;
                color: #c8d6e5;
                font-size: 0.9rem;
                line-height: 1.6;
            ">{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
