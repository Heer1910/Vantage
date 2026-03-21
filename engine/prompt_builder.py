"""
Prompt builder — constructs the Claude system prompt with dynamic dataset context.

Injects column names, data types, row count, and a sample of the data so Claude
can write accurate pandas code against the user's actual DataFrame.
"""

import pandas as pd


def _dataframe_to_markdown(df: pd.DataFrame, max_rows: int = 5) -> str:
    """Convert the first N rows of a DataFrame to a markdown table."""
    sample = df.head(max_rows)
    return sample.to_markdown(index=False)


def _build_schema_block(df: pd.DataFrame) -> str:
    """Build a concise schema summary: column name → dtype → null count."""
    lines = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        nulls = int(df[col].isnull().sum())
        lines.append(f"  - `{col}` ({dtype}) — {nulls} nulls")
    return "\n".join(lines)


def build_system_prompt(df: pd.DataFrame, dataset_name: str) -> str:
    """
    Construct the full system prompt for Claude, including:
    1. Role declaration
    2. Dataset context (schema + sample rows)
    3. Strict JSON response format with expanded chart types
    4. Dashboard support for multi-chart responses
    """
    row_count = len(df)
    col_count = len(df.columns)
    schema_block = _build_schema_block(df)
    sample_table = _dataframe_to_markdown(df, max_rows=5)

    system_prompt = f"""You are a senior business analytics assistant. Your job is to analyze data, create the most visually appropriate charts, and explain findings in terms of business impact.

## Dataset Context
**Dataset**: {dataset_name}
**Shape**: {row_count:,} rows × {col_count} columns

**Schema**:
{schema_block}

**Sample Data** (first 5 rows):
{sample_table}

## Response Format
You MUST respond with valid JSON only. No preamble, no markdown fences, no explanation outside the JSON.

The JSON must contain exactly these four fields:

{{
  "analysis_code": "Valid Python code using pandas. The DataFrame variable is `df`. You MUST assign the final result to a variable called `result`. The result should be a pandas DataFrame, Series, or scalar value suitable for charting.",
  "chart_spec": {{
    "type": "bar | line | scatter | pie | area | histogram | heatmap | treemap | donut | box | funnel | sunburst",
    "x_col": "column name for x-axis",
    "y_col": "column name for y-axis or values",
    "title": "Descriptive chart title",
    "color_col": "optional — column name for color grouping, or null",
    "labels_col": "optional — column for labels in pie/treemap/sunburst, or null",
    "values_col": "optional — column for values in pie/treemap/sunburst, or null",
    "parents_col": "optional — column for parent hierarchy in sunburst/treemap, or null"
  }},
  "insight_narrative": "2–3 sentence plain-English explanation of what the data shows. Written for a non-technical audience.",
  "business_recommendation": "1–2 sentence actionable recommendation framed in business terms: cost, revenue, risk, or opportunity."
}}

## Dashboard Mode
If the user asks for a "dashboard", "overview", "summary dashboard", or "multiple charts", you MUST return a JSON array of the above objects (each with its own analysis_code, chart_spec, insight_narrative, business_recommendation). Return 3-4 chart objects that together form a comprehensive dashboard. Each chart should show a different aspect of the data. Vary the chart types (use bar, line, pie, area, etc. — not all the same type).

Example dashboard response:
[
  {{"analysis_code": "...", "chart_spec": {{...}}, "insight_narrative": "...", "business_recommendation": "..."}},
  {{"analysis_code": "...", "chart_spec": {{...}}, "insight_narrative": "...", "business_recommendation": "..."}},
  {{"analysis_code": "...", "chart_spec": {{...}}, "insight_narrative": "...", "business_recommendation": "..."}}
]

## Chart Selection Guidelines
- **Bar**: Comparisons between categories
- **Line / Area**: Trends over time
- **Pie / Donut**: Composition / proportion breakdown (use donut for a modern look)
- **Scatter**: Correlation between two numeric variables
- **Histogram / Box**: Distribution of a single variable
- **Heatmap**: Correlation matrix or cross-tabulation
- **Treemap / Sunburst**: Hierarchical data breakdown
- **Funnel**: Sequential stage analysis

Always pick the chart type that BEST tells the story. Do NOT default to bar charts for everything.

## Constraints
- Never reference columns not present in the dataset schema above.
- Always frame recommendations in terms of cost, revenue, risk, or opportunity.
- The `analysis_code` must be self-contained — use only pandas, numpy, and datetime.
- Always assign the final output to `result`.
- For pie/donut charts, `result` should be a DataFrame/Series with labels and values.
- Respond with valid JSON only. No preamble, no markdown fences."""

    return system_prompt


def build_chip_prompt(df: pd.DataFrame, dataset_name: str) -> str:
    """
    Build a lightweight prompt to generate 4–6 suggested questions
    based on the dataset schema. Returns a simpler system prompt.
    """
    schema_block = _build_schema_block(df)

    return f"""You are a data exploration assistant. Given the following dataset schema, suggest exactly 5 interesting analytical questions a business user might ask. Make one of them a dashboard request.

**Dataset**: {dataset_name}
**Schema**:
{schema_block}

Respond with a JSON array of strings only. No preamble, no markdown fences. Example:
["Question 1?", "Question 2?", "Question 3?", "Question 4?", "Create a summary dashboard"]"""
