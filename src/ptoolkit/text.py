"""Text helpers: slugs, counts, reading time and email extraction."""

from __future__ import annotations

import math
import re
import unicodedata
from typing import Dict, List, Optional

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def slugify(text: str, sep: str = "-", max_length: Optional[int] = None) -> str:
    """Turn arbitrary text into a URL-friendly slug.

    Accents are stripped ("Café" -> "cafe"), everything that is not a letter
    or digit becomes a single separator.
    """
    if not sep:
        raise ValueError("sep must not be empty")
    if max_length is not None and max_length < 1:
        raise ValueError("max_length must be >= 1")

    ascii_text = (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    )
    slug = re.sub(r"[^a-z0-9]+", lambda _m: sep, ascii_text.lower()).strip(sep)
    if max_length is not None:
        slug = slug[:max_length].strip(sep)
    return slug


def word_count(text: str) -> Dict[str, int]:
    """Return ``{"lines": ..., "words": ..., "chars": ...}`` for *text*."""
    return {
        "lines": len(text.splitlines()),
        "words": len(text.split()),
        "chars": len(text),
    }


def reading_time(text: str, wpm: int = 200) -> int:
    """Estimated reading time in whole minutes (0 for empty text, else >= 1)."""
    if wpm < 1:
        raise ValueError("wpm must be >= 1")
    words = len(text.split())
    if words == 0:
        return 0
    return max(1, math.ceil(words / wpm))


def extract_emails(text: str, unique: bool = True) -> List[str]:
    """Find email addresses in *text*, preserving order of appearance."""
    found = _EMAIL_RE.findall(text)
    if not unique:
        return found
    seen = set()
    result = []
    for email in found:
        key = email.lower()
        if key not in seen:
            seen.add(key)
            result.append(email)
    return result
