import random
import re
import time
from typing import Optional, Tuple


def human_delay(min_sec: float = 0.5, max_sec: float = 3.0) -> None:
    """Human-like delay using Gaussian distribution clamped to range."""
    mean = (min_sec + max_sec) / 2
    std = (max_sec - min_sec) / 4
    delay = max(min_sec, min(max_sec, random.gauss(mean, std)))
    time.sleep(delay)


def process_url(url: str) -> str:
    """Clean Google redirect URLs."""
    if url and url.startswith("/url?q="):
        return url.split("&sa=")[0].replace("/url?q=", "")
    return url


def extract_date_from_snippet(snippet: str) -> Tuple[Optional[str], str]:
    """Extract and remove dates from snippet text. Returns (date, cleaned_snippet)."""
    date_pattern = r"""
        ^\s*
        (
            \d{1,2}[-\/]\w{3,}[-\/]\d{2,4}
            |
            \w{3,}\s\d{1,2},\s\d{4}
            |
            \d{4}[-\/]\d{1,2}[-\/]\d{1,2}
        )
        \s*
        [-\u2013\u2014:]
        \s*
    """
    match = re.search(date_pattern, snippet, re.X | re.I | re.U)
    if not match:
        return (None, snippet.strip())
    cleaned = snippet[match.end():].strip()
    return (match.group(1), cleaned)
