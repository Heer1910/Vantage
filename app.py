"""
AI Business Analyst Agent — main Streamlit application.

Upload any CSV, ask natural language questions, and receive
chart-backed insights and ROI-framed recommendations powered
by Claude (Anthropic).
"""

import os
import sys
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from components.uploader import render_sidebar
from components.chat import render_conversation
from components.charts import render_chart
from components.cards import render_insight_card, render_recommendation_card
from engine.prompt_builder import build_system_prompt, build_chip_prompt
from engine.claude_client import ask_claude, generate_suggested_questions
from engine.executor import execute_code
from config.theme import PRIMARY, ACCENT, TEXT_SECONDARY, BACKGROUND

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Vantage",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS — Colorful Pastel Dashboard ────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap');

    /* ── Base ── */
    .stApp {
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #f8f7fc;
        color: #2d2d2d;
    }

    /* ── Hide Streamlit defaults ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2rem; }

    /* ── Sidebar — soft lavender ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f0eef5 0%, #ede8f5 100%) !important;
        border-right: 1px solid #e0daea;
    }
    section[data-testid="stSidebar"] * {
        color: #4a4556 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5 {
        color: #2d2d2d !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #ddd8e8;
    }

    /* ── Sidebar dataframe ── */
    section[data-testid="stSidebar"] [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e0daea;
    }

    /* ── Buttons — pastel pill style ── */
    .stButton > button {
        background: #ffffff !important;
        border: 1px solid #e0daea !important;
        border-radius: 12px !important;
        color: #4a4556 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 10px 16px !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        background: #ede8f5 !important;
        border-color: #c4b8de !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(123, 94, 167, 0.1);
    }

    /* ── Form submit — gradient button ── */
    .stForm [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #7b5ea7 0%, #e8889e 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 12px 24px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 15px rgba(123, 94, 167, 0.2);
    }
    .stForm [data-testid="stFormSubmitButton"] > button:hover {
        box-shadow: 0 6px 20px rgba(123, 94, 167, 0.3) !important;
        transform: translateY(-1px);
    }

    /* ── Text input ── */
    .stTextInput > div > div > input {
        background: #ffffff !important;
        border: 1px solid #e0daea !important;
        border-radius: 12px !important;
        color: #2d2d2d !important;
        padding: 14px 16px !important;
        font-size: 0.9rem !important;
        transition: border-color 0.2s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: #b8a9d4 !important;
        box-shadow: 0 0 0 3px rgba(123, 94, 167, 0.1) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #b5b0be !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: #ffffff;
        border-radius: 12px;
        border: 2px dashed #d8d2e4;
        padding: 8px;
    }
    [data-testid="stFileUploader"] button {
        background: #ede8f5 !important;
        border: 1px solid #d8d2e4 !important;
        color: #7b5ea7 !important;
    }

    /* ── Selectbox ── */
    .stSelectbox > div > div {
        background: #ffffff !important;
        border: 1px solid #e0daea !important;
        border-radius: 10px !important;
        color: #2d2d2d !important;
    }

    /* ── Plotly chart container ── */
    .stPlotlyChart {
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e6e2f0;
        padding: 12px;
        min-height: 460px;
        overflow: visible;
        box-shadow: 0 2px 8px rgba(123, 94, 167, 0.06);
    }
    .stPlotlyChart > div {
        min-height: 450px;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: #d8d2e4;
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: #c4b8de; }

    /* ── Spinner ── */
    .stSpinner > div { color: #7b5ea7 !important; }

    /* ── Divider ── */
    hr { border-color: #e6e2f0 !important; }

    /* ── Metric — pastel card style ── */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #ede8f5 0%, #e4eef8 100%);
        border-radius: 14px;
        padding: 18px;
        border: none;
    }
    div[data-testid="stMetric"] label { color: #7b5ea7 !important; font-weight: 500 !important; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #2d2d2d !important; font-weight: 700 !important; }

    /* ── Form border fix ── */
    [data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Session State Init ────────────────────────────────────────
def _init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "df": None,
        "dataset_name": None,
        "conversation_history": [],
        "suggested_questions": [],
        "data_changed": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_init_session_state()


# ── Sidebar ───────────────────────────────────────────────────
render_sidebar()


# ── Generate Suggested Questions on Data Change ───────────────
def _refresh_suggestions():
    """Generate new question chips when the dataset changes."""
    if st.session_state.get("data_changed") and st.session_state.get("df") is not None:
        st.session_state.data_changed = False
        try:
            chip_prompt = build_chip_prompt(
                st.session_state.df,
                st.session_state.dataset_name or "Dataset",
            )
            questions = generate_suggested_questions(chip_prompt)
            st.session_state.suggested_questions = questions
        except Exception:
            st.session_state.suggested_questions = [
                "What are the top 5 items by total value?",
                "Show me trends over time",
                "Which category has the highest average?",
                "Are there any outliers in the data?",
                "Break down the data by the main grouping column",
            ]
        st.session_state.conversation_history = []


_refresh_suggestions()


# ── Main Area ─────────────────────────────────────────────────
def _render_welcome():
    """Render colorful pastel onboarding page."""
    st.markdown(
        """
        <div style="
            padding: 50px 20px 40px;
            max-width: 680px;
            margin: 0 auto;
            text-align: center;
        ">
            <div style="
                width: 60px; height: 60px;
                border-radius: 16px;
                background: linear-gradient(135deg, #7b5ea7, #e8889e);
                display: inline-flex; align-items: center; justify-content: center;
                font-size: 1.5rem;
                color: white;
                margin-bottom: 20px;
                box-shadow: 0 6px 20px rgba(123, 94, 167, 0.25);
            ">◈</div>
            <h1 style="
                font-family: 'DM Serif Display', Georgia, serif;
                color: #2d2d2d;
                font-size: 2.8rem;
                font-weight: 400;
                margin: 0 0 12px 0;
                line-height: 1.15;
            ">Vantage</h1>
            <p style="
                color: #6b6578;
                font-size: 1rem;
                margin-bottom: 40px;
                line-height: 1.7;
                max-width: 440px;
                margin-left: auto;
                margin-right: auto;
            ">
                Drop a CSV, ask in plain English, get charts
                and business recommendations back.
            </p>
            <div style="
                display: flex;
                justify-content: center;
                gap: 16px;
                margin-bottom: 44px;
            ">
                <div style="
                    background: linear-gradient(135deg, #ede8f5, #e4eef8);
                    border-radius: 16px;
                    padding: 24px 20px;
                    width: 160px;
                    text-align: center;
                ">
                    <div style="font-size: 1.4rem; margin-bottom: 8px;">📁</div>
                    <p style="font-weight: 600; color: #7b5ea7; margin: 0; font-size: 0.9rem;">Upload</p>
                    <p style="color: #8a8494; font-size: 0.75rem; margin: 4px 0 0;">CSV or demo data</p>
                </div>
                <div style="
                    background: linear-gradient(135deg, #fce8e0, #f8e4ec);
                    border-radius: 16px;
                    padding: 24px 20px;
                    width: 160px;
                    text-align: center;
                ">
                    <div style="font-size: 1.4rem; margin-bottom: 8px;">💬</div>
                    <p style="font-weight: 600; color: #e8889e; margin: 0; font-size: 0.9rem;">Ask</p>
                    <p style="color: #8a8494; font-size: 0.75rem; margin: 4px 0 0;">Any business question</p>
                </div>
                <div style="
                    background: linear-gradient(135deg, #e3f3ee, #e4eef8);
                    border-radius: 16px;
                    padding: 24px 20px;
                    width: 160px;
                    text-align: center;
                ">
                    <div style="font-size: 1.4rem; margin-bottom: 8px;">📊</div>
                    <p style="font-weight: 600; color: #5cb8a5; margin: 0; font-size: 0.9rem;">Insights</p>
                    <p style="color: #8a8494; font-size: 0.75rem; margin: 4px 0 0;">Charts + actions</p>
                </div>
            </div>
            <p style="
                color: #b5b0be;
                font-size: 0.85rem;
            ">
                ← Pick a demo dataset in the sidebar to try it out
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_question_chips():
    """Render clickable suggested question chips."""
    questions = st.session_state.get("suggested_questions", [])
    if not questions:
        return

    st.markdown(
        f"<p style='font-size: 0.8rem; color: {TEXT_SECONDARY}; margin-bottom: 4px; "
        f"font-weight: 500;'>Suggested questions</p>",
        unsafe_allow_html=True,
    )

    cols = st.columns(min(len(questions), 3))
    for i, q in enumerate(questions):
        with cols[i % 3]:
            if st.button(q, key=f"chip_{i}", use_container_width=True):
                st.session_state.chip_question = q
                st.rerun()


def _process_question(question: str):
    """Run the full pipeline: prompt → Claude → execute → render."""
    timestamp = datetime.now().strftime("%I:%M %p")

    entry = {
        "question": question,
        "response": None,
        "result": None,
        "timestamp": timestamp,
        "error": None,
    }

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_key_here":
        entry["error"] = (
            "API key not configured. Add your Anthropic API key to the .env file: "
            "<br><code>ANTHROPIC_API_KEY=sk-ant-...</code>"
        )
        st.session_state.conversation_history.append(entry)
        return

    try:
        system_prompt = build_system_prompt(
            st.session_state.df,
            st.session_state.dataset_name or "Dataset",
        )

        with st.spinner("Analyzing your data…"):
            response = ask_claude(system_prompt, question)

        if isinstance(response, list):
            entry["response"] = {"dashboard": True, "panels": response}
            entry["result"] = "dashboard"
            st.session_state.conversation_history.append(entry)
            return

        code = response.get("analysis_code", "")
        if code:
            success, result = execute_code(code, st.session_state.df)
            if success:
                entry["response"] = response
                entry["result"] = result
            else:
                entry["error"] = str(result)
        else:
            entry["error"] = "No analysis code was generated. Try a different question."

    except ValueError as e:
        entry["error"] = str(e)
    except Exception as e:
        entry["error"] = f"Error: {type(e).__name__} — {e}"

    st.session_state.conversation_history.append(entry)


# ── Main Render ───────────────────────────────────────────────
if st.session_state.get("df") is None:
    _render_welcome()
else:
    # Header — gradient accent badge
    name = st.session_state.get("dataset_name", "Dataset")
    df = st.session_state.df
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #ede8f5 0%, #e4eef8 50%, #e3f3ee 100%);
            border: none;
            border-radius: 14px;
            padding: 18px 22px;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            gap: 14px;
        ">
            <div style="
                width: 42px; height: 42px;
                border-radius: 12px;
                background: linear-gradient(135deg, #7b5ea7, #e8889e);
                display: flex; align-items: center; justify-content: center;
                font-size: 1.1rem;
                color: white;
                font-weight: 600;
                box-shadow: 0 3px 10px rgba(123, 94, 167, 0.2);
            ">◈</div>
            <div>
                <h2 style="
                    font-family: 'DM Sans', sans-serif;
                    color: #2d2d2d;
                    margin: 0;
                    font-size: 1.15rem;
                    font-weight: 600;
                ">{name}</h2>
                <p style="color: #8a8494; font-size: 0.78rem; margin: 2px 0 0;">
                    {len(df):,} rows · {len(df.columns)} columns
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.conversation_history:
        render_conversation(st.session_state.conversation_history)
        st.markdown("---")

    _render_question_chips()

    with st.form("question_form", clear_on_submit=True):
        question = st.text_input(
            "Ask a question about your data",
            placeholder="e.g., Which product category has the highest revenue?",
            max_chars=500,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Analyze", use_container_width=True)

    chip_q = st.session_state.pop("chip_question", None)
    if chip_q:
        _process_question(chip_q)
        st.rerun()

    if submitted and question:
        _process_question(question)
        st.rerun()
