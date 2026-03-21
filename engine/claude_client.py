"""
Claude API client — handles prompt dispatch, response parsing, retries.

Wraps the Anthropic Python SDK to send structured requests and validate
that responses conform to the expected JSON schema.
"""

import json
import os
import time
import logging

import anthropic

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1500
TEMPERATURE = 0
TIMEOUT = 30
RETRY_STATUS = 529
RETRY_DELAY = 2

REQUIRED_FIELDS = {"analysis_code", "chart_spec", "insight_narrative", "business_recommendation"}


def _get_client() -> anthropic.Anthropic:
    """Instantiate the Anthropic client from env var or Streamlit secrets."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    # Fallback: check Streamlit secrets (used on Streamlit Community Cloud)
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:
            pass
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is not set. "
            "Add it to your .env file or Streamlit Secrets."
        )
    return anthropic.Anthropic(api_key=api_key, timeout=TIMEOUT)


def _parse_response(raw_text: str) -> dict | list:
    """
    Parse Claude's response text into a validated dictionary or list.
    Strips markdown fences if Claude accidentally includes them.
    Returns a dict for single responses, or a list for dashboard responses.
    """
    text = raw_text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    parsed = json.loads(text)

    # Dashboard mode: array of panel objects
    if isinstance(parsed, list):
        for i, panel in enumerate(parsed):
            missing = REQUIRED_FIELDS - set(panel.keys())
            if missing:
                raise ValueError(f"Dashboard panel {i} missing fields: {missing}")
        return parsed

    # Single response mode
    missing = REQUIRED_FIELDS - set(parsed.keys())
    if missing:
        raise ValueError(f"Response missing required fields: {missing}")

    return parsed


def ask_claude(system_prompt: str, user_question: str) -> dict:
    """
    Send a question to Claude with the dataset-aware system prompt.

    Returns a dict with keys: analysis_code, chart_spec,
    insight_narrative, business_recommendation.

    Retries once on 529 (overload) with a 2-second delay.
    """
    client = _get_client()

    for attempt in range(2):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                system=system_prompt,
                messages=[{"role": "user", "content": user_question}],
            )
            raw_text = response.content[0].text
            return _parse_response(raw_text)

        except anthropic.APIStatusError as e:
            if e.status_code == RETRY_STATUS and attempt == 0:
                logger.warning("Claude API overloaded (529), retrying in %ds…", RETRY_DELAY)
                time.sleep(RETRY_DELAY)
                continue
            raise

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Claude returned invalid JSON: {e}. "
                "Try rephrasing your question."
            ) from e

    raise RuntimeError("Claude API request failed after retries.")


def generate_suggested_questions(system_prompt: str) -> list[str]:
    """
    Lightweight Claude call to generate suggested question chips.
    Returns a list of 4–6 question strings.
    """
    client = _get_client()

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=500,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": "Generate suggested questions."}],
        )
        raw_text = response.content[0].text.strip()

        # Strip markdown fences if present
        if raw_text.startswith("```"):
            lines = raw_text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            raw_text = "\n".join(lines)

        questions = json.loads(raw_text)
        if isinstance(questions, list):
            return [str(q) for q in questions[:6]]
        return []

    except Exception as e:
        logger.warning("Failed to generate suggested questions: %s", e)
        return [
            "What are the top 5 items by total value?",
            "Show me trends over time",
            "Which category has the highest average?",
            "Are there any outliers in the data?",
            "Break down the data by the main grouping column",
        ]
