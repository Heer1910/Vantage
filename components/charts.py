"""
Chart renderer — routes chart_spec to the correct Plotly chart type
and applies the dark glassmorphism theme. Supports 12 chart types
and multi-chart dashboard layouts.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config.theme import brand_template, CHART_COLORS

SUPPORTED_TYPES = {
    "bar", "line", "scatter", "pie", "area",
    "histogram", "heatmap", "treemap", "donut",
    "box", "funnel", "sunburst",
}


def _safe_get(spec: dict, key: str, default=None):
    """Safely extract a key from chart_spec."""
    val = spec.get(key, default)
    if val == "null" or val == "None":
        return None
    return val


def render_chart(chart_spec: dict, result) -> None:
    """
    Render a Plotly chart based on chart_spec and
    the computed result (DataFrame, Series, or scalar).
    """
    if result is None:
        st.info("No data to chart.")
        return

    chart_type = _safe_get(chart_spec, "type", "bar").lower()
    title = _safe_get(chart_spec, "title", "Analysis Result")
    x_col = _safe_get(chart_spec, "x_col")
    y_col = _safe_get(chart_spec, "y_col")
    color_col = _safe_get(chart_spec, "color_col")

    # Ensure unsupported types fall back to bar
    if chart_type not in SUPPORTED_TYPES:
        chart_type = "bar"

    # Convert Series or scalar to DataFrame for charting
    if isinstance(result, pd.Series):
        df = result.reset_index()
        df.columns = ["index", "value"]
        if not x_col:
            x_col = "index"
        if not y_col:
            y_col = "value"
    elif isinstance(result, pd.DataFrame):
        df = result.copy()
    else:
        # Scalar result — display as metric
        st.metric(label=title, value=str(result))
        return

    if df.empty:
        st.info("The analysis returned no data to chart.")
        return

    # Auto-detect columns if not specified
    if not x_col and len(df.columns) >= 1:
        x_col = df.columns[0]
    if not y_col and len(df.columns) >= 2:
        y_col = df.columns[1]

    try:
        fig = _build_figure(chart_type, df, x_col, y_col, color_col, title, chart_spec)
        fig.update_layout(template=brand_template, height=450)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        # Fallback: try a basic bar chart
        try:
            fig = px.bar(df, x=x_col, y=y_col, title=title,
                        color_discrete_sequence=CHART_COLORS)
            fig.update_layout(template=brand_template, height=450)
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.markdown(f"**{title}**")
            st.dataframe(df, use_container_width=True, hide_index=True)


def render_dashboard(panels: list[dict], df: pd.DataFrame, execute_fn) -> None:
    """
    Render a multi-chart dashboard from a list of analysis panels.
    Each panel has: analysis_code, chart_spec, insight_narrative, business_recommendation.
    """
    from components.cards import render_insight_card, render_recommendation_card

    st.markdown("""
        <div style="
            text-align: center;
            margin: 10px 0 20px;
            padding: 12px;
            background: rgba(110, 72, 255, 0.08);
            border: 1px solid rgba(110, 72, 255, 0.2);
            border-radius: 12px;
        ">
            <span style="font-size: 1.2rem;">📊</span>
            <span style="color: #a78bfa; font-weight: 600; font-size: 0.95rem; margin-left: 8px;">
                Dashboard View
            </span>
        </div>
    """, unsafe_allow_html=True)

    # Render charts in a 2-column grid
    for i in range(0, len(panels), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(panels):
                break
            panel = panels[idx]
            with col:
                code = panel.get("analysis_code", "")
                if code:
                    success, result = execute_fn(code, df)
                    if success:
                        chart_spec = panel.get("chart_spec", {})
                        if chart_spec and result is not None:
                            render_chart(chart_spec, result)
                        insight = panel.get("insight_narrative", "")
                        if insight:
                            render_insight_card(insight)
                    else:
                        st.error(f"Panel error: {result}")


def _build_figure(
    chart_type: str,
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str | None,
    title: str,
    spec: dict = None,
):
    """Build the appropriate Plotly figure based on chart type."""
    spec = spec or {}
    base_kwargs = dict(
        data_frame=df,
        title=title,
        color_discrete_sequence=CHART_COLORS,
    )

    # ── Pie / Donut ──
    if chart_type in ("pie", "donut"):
        names = _safe_get(spec, "labels_col") or x_col
        values = _safe_get(spec, "values_col") or y_col
        fig = px.pie(df, names=names, values=values, title=title,
                     color_discrete_sequence=CHART_COLORS)
        if chart_type == "donut":
            fig.update_traces(hole=0.45)
        return fig

    # ── Histogram ──
    if chart_type == "histogram":
        kwargs = {**base_kwargs, "x": x_col}
        if color_col and color_col in df.columns:
            kwargs["color"] = color_col
        return px.histogram(**kwargs)

    # ── Box ──
    if chart_type == "box":
        kwargs = {**base_kwargs}
        if x_col and x_col in df.columns:
            kwargs["x"] = x_col
        if y_col and y_col in df.columns:
            kwargs["y"] = y_col
        if color_col and color_col in df.columns:
            kwargs["color"] = color_col
        return px.box(**kwargs)

    # ── Area ──
    if chart_type == "area":
        kwargs = {**base_kwargs, "x": x_col, "y": y_col}
        if color_col and color_col in df.columns:
            kwargs["color"] = color_col
        return px.area(**kwargs)

    # ── Heatmap ──
    if chart_type == "heatmap":
        # Try to create a pivot-style heatmap
        try:
            numeric_df = df.select_dtypes(include="number")
            if len(numeric_df.columns) >= 2:
                corr = numeric_df.corr()
                fig = px.imshow(corr, text_auto=".2f", title=title,
                               color_continuous_scale=["#0d1b2a", "#6e48ff", "#a78bfa", "#f59e0b"])
                return fig
        except Exception:
            pass
        fig = px.imshow(df.select_dtypes(include="number"), title=title,
                       color_continuous_scale=["#0d1b2a", "#6e48ff", "#a78bfa"])
        return fig

    # ── Treemap ──
    if chart_type == "treemap":
        path_col = _safe_get(spec, "labels_col") or x_col
        values_col = _safe_get(spec, "values_col") or y_col
        return px.treemap(df, path=[path_col], values=values_col, title=title,
                         color_discrete_sequence=CHART_COLORS)

    # ── Sunburst ──
    if chart_type == "sunburst":
        path_col = _safe_get(spec, "labels_col") or x_col
        values_col = _safe_get(spec, "values_col") or y_col
        return px.sunburst(df, path=[path_col], values=values_col, title=title,
                          color_discrete_sequence=CHART_COLORS)

    # ── Funnel ──
    if chart_type == "funnel":
        return px.funnel(df, x=y_col, y=x_col, title=title,
                        color_discrete_sequence=CHART_COLORS)

    # ── Standard: bar, line, scatter ──
    kwargs = {**base_kwargs, "x": x_col, "y": y_col}
    if color_col and color_col in df.columns:
        kwargs["color"] = color_col

    if chart_type == "line":
        return px.line(**kwargs)
    elif chart_type == "scatter":
        return px.scatter(**kwargs)
    else:
        return px.bar(**kwargs)
