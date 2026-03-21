"""
Brand theme — color palette and Plotly template for dark glassmorphism theme.
"""

import plotly.graph_objects as go

# ── Color Palette ─────────────────────────────────────────────
PRIMARY = "#ffffff"           # Main text color
ACCENT = "#6e48ff"            # Purple accent
ACCENT_LIGHT = "#a78bfa"      # Light purple
ACCENT_AMBER = "#f59e0b"      # Amber for recommendations
BACKGROUND = "#0d1b2a"        # Deep navy
CARD_BG = "rgba(255,255,255,0.04)"
TEXT_SECONDARY = "rgba(200, 214, 229, 0.6)"

# Chart color sequence
CHART_COLORS = [
    "#6e48ff", "#a78bfa", "#818cf8", "#6366f1",
    "#f59e0b", "#fbbf24", "#34d399", "#2dd4bf",
    "#f472b6", "#fb923c",
]

# ── Plotly Dark Template ──────────────────────────────────────
brand_template = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, -apple-system, sans-serif", color="#c8d6e5", size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        title=dict(
            font=dict(size=18, color="#ffffff", family="Inter, sans-serif"),
            x=0,
            xanchor="left",
        ),
        colorway=CHART_COLORS,
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(255,255,255,0.08)",
            tickfont=dict(color="#8b9dc3"),
            title_font=dict(color="#8b9dc3"),
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(255,255,255,0.08)",
            tickfont=dict(color="#8b9dc3"),
            title_font=dict(color="#8b9dc3"),
            zeroline=False,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c8d6e5"),
            borderwidth=0,
        ),
        margin=dict(l=50, r=20, t=50, b=50),
        hoverlabel=dict(
            bgcolor="#1b2838",
            font_color="#ffffff",
            bordercolor="rgba(110, 72, 255, 0.3)",
        ),
    )
)
