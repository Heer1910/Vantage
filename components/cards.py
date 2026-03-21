"""
Insight & Recommendation cards — colorful pastel fills.

Each card renders with a soft pastel background and subtle accent border.
"""

import streamlit as st


def render_insight_card(text: str) -> None:
    """Render an insight card with soft lavender-sky gradient fill."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #ede8f5, #e4eef8);
            border-left: 3px solid #7b5ea7;
            border-radius: 12px;
            padding: 16px 18px;
            margin: 10px 0;
        ">
            <p style="
                margin: 0 0 6px 0;
                font-size: 0.72rem;
                font-weight: 600;
                color: #7b5ea7;
                letter-spacing: 0.04em;
            ">What the data shows</p>
            <p style="
                margin: 0;
                color: #3d3852;
                font-size: 0.88rem;
                line-height: 1.6;
            ">{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendation_card(text: str) -> None:
    """Render a recommendation card with soft peach-pink gradient fill."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #fce8e0, #f8e4ec);
            border-left: 3px solid #e8889e;
            border-radius: 12px;
            padding: 16px 18px;
            margin: 10px 0;
        ">
            <p style="
                margin: 0 0 6px 0;
                font-size: 0.72rem;
                font-weight: 600;
                color: #e8889e;
                letter-spacing: 0.04em;
            ">Business recommendation</p>
            <p style="
                margin: 0;
                color: #3d3852;
                font-size: 0.88rem;
                line-height: 1.6;
            ">{text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
