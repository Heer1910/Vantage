"""
Brand theme — vibrant pastel palette with gradient accents.
"""

import plotly.graph_objects as go

# ── Color Palette ─────────────────────────────────────────────
PRIMARY = "#2d2d2d"              # Charcoal — main text
ACCENT = "#7b5ea7"               # Muted purple — primary accent
ACCENT_LIGHT = "#b8a9d4"         # Light lavender
ACCENT_PINK = "#e8889e"          # Soft coral-pink
ACCENT_AMBER = "#e8a859"         # Warm amber
BACKGROUND = "#f8f7fc"           # Very light lavender-white
SIDEBAR_BG = "#f0eef5"           # Soft lavender sidebar
CARD_BG = "#ffffff"              # White card base
BORDER = "#e6e2f0"               # Lavender-grey border
TEXT_SECONDARY = "#8a8494"       # Muted purple-grey

# Pastel card fills
CARD_LAVENDER = "#ede8f5"
CARD_MINT = "#e3f3ee"
CARD_PEACH = "#fce8e0"
CARD_PINK = "#f8e4ec"
CARD_SKY = "#e4eef8"

# Chart color sequence — vibrant pastels
CHART_COLORS = [
    "#7b5ea7",  # purple
    "#e8889e",  # coral pink
    "#5cb8a5",  # teal
    "#e8a859",  # amber
    "#6aa3d4",  # sky blue
    "#c97bb5",  # mauve
    "#8bc587",  # sage
    "#d4856a",  # terracotta
    "#9b8ec4",  # soft violet
    "#e5c06e",  # gold
]

# ── Plotly Template ───────────────────────────────────────────
brand_template = go.layout.Template(
    layout=go.Layout(
        font=dict(family="'DM Sans', -apple-system, sans-serif", color="#4a4556", size=13),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#faf9fe",
        title=dict(
            font=dict(size=16, color="#2d2d2d", family="'DM Sans', sans-serif"),
            x=0,
            xanchor="left",
        ),
        colorway=CHART_COLORS,
        xaxis=dict(
            showgrid=True,
            gridcolor="#edeaf2",
            linecolor="#ddd8e8",
            tickfont=dict(color="#8a8494"),
            title_font=dict(color="#5a5566"),
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#edeaf2",
            linecolor="#ddd8e8",
            tickfont=dict(color="#8a8494"),
            title_font=dict(color="#5a5566"),
            zeroline=False,
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0)",
            font=dict(color="#5a5566"),
            borderwidth=0,
        ),
        margin=dict(l=50, r=20, t=50, b=50),
        hoverlabel=dict(
            bgcolor="#2d2d2d",
            font_color="#ffffff",
            bordercolor="#7b5ea7",
        ),
    )
)
