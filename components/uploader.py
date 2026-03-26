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
    st.markdown("##### Schema")
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
    """
    with st.sidebar:
        # ── Branding icon (rendered as image to avoid CSS color override)
        _icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "icon_white.svg",
        )
        st.image(_icon_path, width=42)
        st.markdown(
            """
            <div style="text-align: center; margin-top: -8px; padding-bottom: 0.5rem;">
                <h2 style="
                    margin: 0;
                    font-family: 'DM Serif Display', Georgia, serif;
                    color: #2d2d2d !important;
                    font-size: 1.3rem;
                    font-weight: 400;
                ">Vantage</h2>
                <p style="color: #8a8494 !important; font-size: 0.75rem; margin-top: 0.25rem;">
                    Upload · Ask · Insights
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ── File Upload ───────────────────────────────────────
        st.markdown("##### Upload your data")
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
                st.error("Could not parse this file. Please upload a valid CSV.")
                return

        # ── Demo Dataset Picker ───────────────────────────────
        st.markdown("##### Or try a demo")
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
            st.markdown(f"##### {name}")
            st.caption(f"{len(df):,} rows · {len(df.columns)} columns")
            st.dataframe(
                df.head(5),
                use_container_width=True,
                hide_index=True,
            )

            _render_schema_summary(df)
