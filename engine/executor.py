"""
Safe code execution sandbox for Claude-generated pandas analysis.

Runs exec() in a controlled namespace with pandas, numpy, and
datetime available. Uses threading for timeout (compatible with
Streamlit's threaded execution model).
"""

import threading
import logging
from typing import Any

import pandas as pd
import numpy as np
import datetime

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 10


def execute_code(code_string: str, df: pd.DataFrame) -> tuple[bool, Any]:
    """
    Execute Claude-generated Python code against the user's DataFrame.

    The code runs in a controlled namespace with access to:
      - df: the user's pandas DataFrame (copy)
      - pd: pandas
      - np: numpy
      - datetime: datetime module

    The executed code MUST assign its output to a variable called `result`.

    Returns:
        (True, result) on success — result is a DataFrame, Series, or scalar.
        (False, error_message) on failure.
    """
    # Build execution namespace
    local_ns = {
        "df": df.copy(),
        "pd": pd,
        "np": np,
        "datetime": datetime,
        "result": None,
    }

    error_holder = [None]
    completed = threading.Event()

    def _run():
        try:
            exec(code_string, {"__builtins__": __builtins__}, local_ns)
        except Exception as e:
            error_holder[0] = e
        finally:
            completed.set()

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
    finished = completed.wait(timeout=TIMEOUT_SECONDS)

    if not finished:
        return False, "The analysis took too long to run. Try a simpler question."

    if error_holder[0] is not None:
        err = error_holder[0]
        logger.warning("Code execution failed: %s: %s", type(err).__name__, err)
        return False, f"Code execution error: {type(err).__name__}: {err}"

    result = local_ns.get("result")
    if result is None:
        return False, "Analysis code did not produce a result. Try rephrasing your question."

    return True, result
