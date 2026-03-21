# AI Business Analyst Agent 🤖📊

A conversational AI tool that lets any business user upload data and get chart-backed insights and ROI-framed recommendations in plain English — built with Claude API and Streamlit.

**[▶ Live Demo](https://heer-analyst-agent.streamlit.app)** · **[Portfolio](https://heer1910.github.io)**

---

## What It Does

Upload any CSV → ask questions in plain English → get:

- **Interactive Plotly charts** auto-generated from your data
- **Insight narratives** explaining what the data shows
- **Business recommendations** framed in terms of cost, revenue, risk, or opportunity

The AI handles the entire pipeline: understanding your question, writing analysis code, executing it against your dataset, choosing the right chart type, and translating the results into actionable business language.

---

## Architecture

```
User Question
     ↓
prompt_builder.py   →  Injects dataset schema + sample rows into system prompt
     ↓
claude_client.py    →  Sends to Claude API (claude-sonnet-4-20250514, temp=0)
     ↓
executor.py         →  Safely executes generated pandas code in sandbox
     ↓
charts.py + cards.py →  Renders Plotly chart + Insight & Recommendation cards
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| App Framework | Streamlit |
| AI / LLM | Anthropic Claude API (claude-sonnet-4-20250514) |
| Data Processing | pandas |
| Visualization | Plotly Express |
| Deployment | Streamlit Community Cloud |

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Heer1910/ai-analyst-agent.git
cd ai-analyst-agent
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set API Key

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 3. Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`. Select a demo dataset or upload your own CSV to get started.

---

## File Structure

```
ai-analyst-agent/
├── app.py                      # Main Streamlit entry point
├── components/
│   ├── uploader.py             # CSV upload + schema detection
│   ├── chat.py                 # Conversation history rendering
│   ├── charts.py               # Plotly chart builder + brand theming
│   └── cards.py                # Insight & Recommendation cards
├── engine/
│   ├── claude_client.py        # Claude API wrapper + retry logic
│   ├── prompt_builder.py       # Dynamic system prompt constructor
│   └── executor.py             # Safe Python code execution sandbox
├── config/
│   └── theme.py                # Brand colors + Plotly template
├── data/
│   ├── retail_sample.csv       # Demo: 1,000 rows of retail sales
│   └── churn_sample.csv        # Demo: 500 rows of telecom churn
├── .streamlit/config.toml      # Streamlit theme config
├── .env.example                # API key template
├── requirements.txt            # Pinned dependencies
└── README.md
```

---

## Demo Datasets

| Dataset | Rows | Source Inspiration |
|---------|------|--------------------|
| Retail Sales Sample | 1,000 | [M5 Demand Forecasting](https://github.com/Heer1910/m5-demand-forecasting) |
| Telecom Churn Sample | 500 | [Telco Churn Prediction](https://github.com/Heer1910/telco-churn-prediction) |

---

## Deployment (Streamlit Cloud)

1. Push to public GitHub repo under `Heer1910`
2. Connect at [share.streamlit.io](https://share.streamlit.io) → select `app.py`
3. Add `ANTHROPIC_API_KEY` under Settings → Secrets
4. App goes live at `heer-analyst-agent.streamlit.app`

---

## Related Projects

- [M5 Demand Forecasting](https://github.com/Heer1910/m5-demand-forecasting) — source of the retail demo dataset and $2.7M ROI methodology
- [Retail KPI Dashboard](https://github.com/Heer1910/retail-kpi-dashboard) — star schema and BigQuery pipeline
- [Telco Churn Prediction](https://github.com/Heer1910/telco-churn-prediction) — source of the churn demo dataset

---

**Heer Patel** · [heerpatel7016@gmail.com](mailto:heerpatel7016@gmail.com) · [heer1910.github.io](https://heer1910.github.io)
