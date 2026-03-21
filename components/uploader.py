"""
Sidebar uploader component — file upload, demo dataset picker,
data preview table, and schema summary panel.
"""

import os
import streamlit as st
import pandas as pd


DEMO_DATASETS = {
    "— Select a demo dataset —": None,
    "🛒 Retail Sales Sample": "data/retail_sample.csv",
    "📞 Telecom Churn Sample": "data/churn_sample.csv",
}


def _render_schema_summary(df: pd.DataFrame) -> None:
    """Display column-level schema info: dtype, nulls, unique counts."""
    st.markdown("##### 📋 Schema Summary")
    summary_data = []
    for col in df.columns:
        summary_data.append({
            "Column": col,
            "Type": str(df[col].dtype),
            "Nulls": int(df[col].isnull().sum()),
            "Unique": int(df[col].nunique()),
        })
    st.dataframe(
        pd.DataFrame(summary_data),
        use_container_width=True,
        hide_index=True,
        height=min(250, 35 * len(summary_data) + 38),
    )


def _load_demo_dataset(path: str) -> pd.DataFrame | None:
    """Load a demo CSV from the data/ directory."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, path)
    if os.path.exists(full_path):
        return pd.read_csv(full_path)
    return None


def render_sidebar() -> None:
    """
    Render the full sidebar: file uploader, demo selector,
    data preview, and schema summary.

    Updates st.session_state with:
      - df: the active DataFrame
      - dataset_name: name of the loaded source
      - data_changed: flag indicating the dataset was just changed
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; padding: 0.5rem 0 1rem;">
                <span style="
                    font-size: 1.8rem;
                    filter: drop-shadow(0 0 12px rgba(110, 72, 255, 0.4));
                    color: #a78bfa !important;
                    font-family: 'Segoe UI Symbol', 'Noto Sans Symbols', sans-serif;
                ">&#x25C8;</span>
                <h2 style="
                    margin: 8px 0 0;
                    font-family: 'Playfair Display', Georgia, serif;
                    color: #ffffff !important;
                    font-size: 1.4rem;
                    font-weight: 700;
                ">
                    Vantage
                </h2>
                <p style="color: rgba(200,214,229,0.5) !important; font-size: 0.8rem; margin-top: 0.25rem;">
                    Upload data · Ask questions · Get insights
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ── File Upload ───────────────────────────────────────
        st.markdown("##### 📁 Upload Your Data")
        uploaded_file = st.file_uploader(
            "Drag and drop a CSV file",
            type=["csv"],
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                name = uploaded_file.name
                if (
                    st.session_state.get("dataset_name") != name
                    or st.session_state.get("df") is None
                ):
                    st.session_state.df = df
                    st.session_state.dataset_name = name
                    st.session_state.data_changed = True
            except Exception:
                st.error("⚠️ Could not parse this file. Please upload a valid CSV.")
                return

        # ── Demo Dataset Picker ───────────────────────────────
        st.markdown("##### 🗂️ Or Try a Demo Dataset")
        demo_choice = st.selectbox(
            "Select a demo dataset",
            options=list(DEMO_DATASETS.keys()),
            label_visibility="collapsed",
        )

        if DEMO_DATASETS.get(demo_choice) and uploaded_file is None:
            path = DEMO_DATASETS[demo_choice]
            name = demo_choice
            if (
                st.session_state.get("dataset_name") != name
                or st.session_state.get("df") is None
            ):
                df = _load_demo_dataset(path)
                if df is not None:
                    st.session_state.df = df
                    st.session_state.dataset_name = name
                    st.session_state.data_changed = True

        # ── Data Preview ──────────────────────────────────────
        if st.session_state.get("df") is not None:
            df = st.session_state.df
            name = st.session_state.get("dataset_name", "Dataset")

            st.markdown("---")
            st.markdown(f"##### 📊 {name}")
            st.caption(f"{len(df):,} rows · {len(df.columns)} columns")
            st.dataframe(
                df.head(5),
                use_container_width=True,
                hide_index=True,
            )

            _render_schema_summary(df)
