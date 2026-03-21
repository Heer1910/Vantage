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
    page_icon="▷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS — Premium Dark Glassmorphism ───────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');

    /* ── Animated gradient background ── */
    .stApp {
        font-family: 'Inter', -apple-system, sans-serif;
        background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 25%, #1b2838 50%, #0d1b2a 75%, #0a0a1a 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        color: #e0e6ed;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ── Hide Streamlit defaults ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 2rem; }

    /* ── Glassmorphism sidebar ── */
    section[data-testid="stSidebar"] {
        background: rgba(13, 27, 42, 0.85) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    section[data-testid="stSidebar"] * {
        color: #c8d6e5 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5 {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08);
    }

    /* ── Sidebar table/dataframe styling ── */
    section[data-testid="stSidebar"] [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.06);
    }

    /* ── Button chips ── */
    .stButton > button {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #c8d6e5 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        padding: 10px 18px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px);
        letter-spacing: 0.01em;
    }
    .stButton > button:hover {
        background: rgba(110, 72, 255, 0.15) !important;
        border-color: rgba(110, 72, 255, 0.4) !important;
        color: #ffffff !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(110, 72, 255, 0.2);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* ── Form submit button ── */
    .stForm [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #6e48ff 0%, #8b5cf6 50%, #a78bfa 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 12px 24px !important;
        letter-spacing: 0.02em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(110, 72, 255, 0.3);
    }
    .stForm [data-testid="stFormSubmitButton"] > button:hover {
        box-shadow: 0 8px 30px rgba(110, 72, 255, 0.5) !important;
        transform: translateY(-2px);
    }

    /* ── Text input ── */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e0e6ed !important;
        padding: 14px 18px !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(110, 72, 255, 0.5) !important;
        box-shadow: 0 0 0 3px rgba(110, 72, 255, 0.1), 0 0 20px rgba(110, 72, 255, 0.1) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: rgba(200, 214, 229, 0.4) !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        border: 1px dashed rgba(255,255,255,0.1);
        padding: 8px;
    }
    [data-testid="stFileUploader"] button {
        background: rgba(110, 72, 255, 0.15) !important;
        border: 1px solid rgba(110, 72, 255, 0.3) !important;
        color: #a78bfa !important;
    }

    /* ── Selectbox ── */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        color: #c8d6e5 !important;
    }

    /* ── Plotly chart container ── */
    .stPlotlyChart {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        padding: 12px;
        animation: slideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        min-height: 460px;
        overflow: visible;
    }
    .stPlotlyChart > div {
        min-height: 450px;
    }

    /* ── Animations ── */
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(110, 72, 255, 0.1); }
        50% { box-shadow: 0 0 40px rgba(110, 72, 255, 0.2); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-6px); }
    }
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(110, 72, 255, 0.3);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(110, 72, 255, 0.5); }

    /* ── Spinner ── */
    .stSpinner > div { color: #a78bfa !important; }

    /* ── Divider ── */
    hr { border-color: rgba(255,255,255,0.06) !important; }

    /* ── Metric ── */
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 16px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    div[data-testid="stMetric"] label { color: #8b9dc3 !important; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #ffffff !important; }

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
            # Fallback suggestions
            st.session_state.suggested_questions = [
                "What are the top 5 items by total value?",
                "Show me trends over time",
                "Which category has the highest average?",
                "Are there any outliers in the data?",
                "Break down the data by the main grouping column",
            ]
        # Clear conversation on dataset change
        st.session_state.conversation_history = []


_refresh_suggestions()


# ── Main Area ─────────────────────────────────────────────────
def _render_welcome():
    """Render the premium onboarding empty state."""
    st.markdown(
        """
        <div style="
            text-align: center;
            padding: 80px 20px 40px;
            max-width: 700px;
            margin: 0 auto;
        ">
            <div style="
                font-size: 3rem;
                margin-bottom: 20px;
                animation: float 3s ease-in-out infinite;
                filter: drop-shadow(0 0 20px rgba(110, 72, 255, 0.3));
                color: #a78bfa !important;
                font-family: 'Segoe UI Symbol', 'Noto Sans Symbols', sans-serif;
            ">&#x25C8;</div>
            <h1 style="
                font-family: 'Playfair Display', Georgia, serif;
                color: #ffffff !important;
                font-size: 3.2rem;
                font-weight: 700;
                margin-bottom: 12px;
                letter-spacing: -0.02em;
            ">Vantage</h1>
            <p style="
                color: rgba(200, 214, 229, 0.7);
                font-size: 1.1rem;
                margin-bottom: 50px;
                line-height: 1.7;
                max-width: 500px;
                margin-left: auto;
                margin-right: auto;
            ">
                Upload any dataset and get chart-backed insights with
                plain-English business recommendations — powered by <span style="color: #a78bfa;">Claude AI</span>.
                <br><span style="font-size: 0.85rem; color: rgba(200,214,229,0.4);">Supports dashboards, 12+ chart types, and actionable insights.</span>
            </p>
            <div style="
                display: flex;
                justify-content: center;
                gap: 24px;
                margin-bottom: 50px;
            ">
                <div style="
                    background: rgba(255,255,255,0.03);
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 16px;
                    padding: 28px 24px;
                    width: 180px;
                    transition: all 0.3s ease;
                    backdrop-filter: blur(10px);
                " onmouseover="this.style.background='rgba(110,72,255,0.08)';this.style.borderColor='rgba(110,72,255,0.2)';this.style.transform='translateY(-4px)'"
                   onmouseout="this.style.background='rgba(255,255,255,0.03)';this.style.borderColor='rgba(255,255,255,0.08)';this.style.transform='translateY(0)'">
                    <div style="font-size: 2rem; margin-bottom: 12px;">📁</div>
                    <p style="font-weight: 600; color: #ffffff; margin: 0; font-size: 1rem;">Upload</p>
                    <p style="color: rgba(200,214,229,0.5); font-size: 0.8rem; margin: 6px 0 0;">
                        Drop a CSV or pick a demo
                    </p>
                </div>
                <div style="
                    background: rgba(255,255,255,0.03);
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 16px;
                    padding: 28px 24px;
                    width: 180px;
                    transition: all 0.3s ease;
                    backdrop-filter: blur(10px);
                " onmouseover="this.style.background='rgba(110,72,255,0.08)';this.style.borderColor='rgba(110,72,255,0.2)';this.style.transform='translateY(-4px)'"
                   onmouseout="this.style.background='rgba(255,255,255,0.03)';this.style.borderColor='rgba(255,255,255,0.08)';this.style.transform='translateY(0)'">
                    <div style="font-size: 2rem; margin-bottom: 12px;">💬</div>
                    <p style="font-weight: 600; color: #ffffff; margin: 0; font-size: 1rem;">Ask</p>
                    <p style="color: rgba(200,214,229,0.5); font-size: 0.8rem; margin: 6px 0 0;">
                        Type any business question
                    </p>
                </div>
                <div style="
                    background: rgba(255,255,255,0.03);
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 16px;
                    padding: 28px 24px;
                    width: 180px;
                    transition: all 0.3s ease;
                    backdrop-filter: blur(10px);
                " onmouseover="this.style.background='rgba(110,72,255,0.08)';this.style.borderColor='rgba(110,72,255,0.2)';this.style.transform='translateY(-4px)'"
                   onmouseout="this.style.background='rgba(255,255,255,0.03)';this.style.borderColor='rgba(255,255,255,0.08)';this.style.transform='translateY(0)'">
                    <div style="font-size: 2rem; margin-bottom: 12px;">📈</div>
                    <p style="font-weight: 600; color: #ffffff; margin: 0; font-size: 1rem;">Decide</p>
                    <p style="color: rgba(200,214,229,0.5); font-size: 0.8rem; margin: 6px 0 0;">
                        Get charts + recommendations
                    </p>
                </div>
            </div>
            <p style="
                color: rgba(200,214,229,0.4);
                font-size: 0.85rem;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            ">
                <span style="animation: float 2s ease-in-out infinite;">👈</span>
                Select a demo dataset in the sidebar to get started
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
        f"<p style='font-size: 0.85rem; color: {TEXT_SECONDARY}; margin-bottom: 4px;'>"
        "💡 Suggested questions</p>",
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

    # Check API key before making a call
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_key_here":
        entry["error"] = (
            "🔑 API key not configured. Add your Anthropic API key to the .env file: "
            "<br><code>ANTHROPIC_API_KEY=sk-ant-...</code>"
        )
        st.session_state.conversation_history.append(entry)
        return

    try:
        # 1. Build prompt
        system_prompt = build_system_prompt(
            st.session_state.df,
            st.session_state.dataset_name or "Dataset",
        )

        # 2. Call Claude
        with st.spinner("✦ Analyzing your data…"):
            response = ask_claude(system_prompt, question)

        # 3. Check if dashboard (array of panels)
        if isinstance(response, list):
            entry["response"] = {"dashboard": True, "panels": response}
            entry["result"] = "dashboard"
            st.session_state.conversation_history.append(entry)
            return

        # 4. Execute generated code
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
    # Header — prominent dataset title badge
    name = st.session_state.get("dataset_name", "Dataset")
    df = st.session_state.df
    st.markdown(
        f"""
        <div style="
            background: rgba(110, 72, 255, 0.08);
            border: 1px solid rgba(110, 72, 255, 0.2);
            border-radius: 14px;
            padding: 18px 24px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 16px;
            backdrop-filter: blur(10px);
        ">
            <div style="
                font-size: 1.6rem;
                filter: drop-shadow(0 0 8px rgba(110, 72, 255, 0.3));
                color: #a78bfa !important;
                font-family: 'Segoe UI Symbol', 'Noto Sans Symbols', sans-serif;
            ">&#x25C8;</div>
            <div>
                <h2 style="
                    font-family: 'Playfair Display', Georgia, serif;
                    color: #ffffff;
                    margin: 0;
                    font-size: 1.5rem;
                    font-weight: 700;
                ">{name}</h2>
                <p style="color: rgba(200,214,229,0.5); font-size: 0.8rem; margin: 4px 0 0;">
                    {len(df):,} rows · {len(df.columns)} columns · Ask anything in plain English
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Conversation history
    if st.session_state.conversation_history:
        render_conversation(st.session_state.conversation_history)
        st.markdown("---")

    # Suggested question chips
    _render_question_chips()

    # Question input — wrapped in a form to prevent rerun loops
    with st.form("question_form", clear_on_submit=True):
        question = st.text_input(
            "Ask a question about your data",
            placeholder="e.g., Which product category has the highest revenue?",
            max_chars=500,
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("🔍 Analyze", use_container_width=True)

    # Handle chip click (outside the form)
    chip_q = st.session_state.pop("chip_question", None)
    if chip_q:
        _process_question(chip_q)
        st.rerun()

    # Handle form submission
    if submitted and question:
        _process_question(question)
        st.rerun()
