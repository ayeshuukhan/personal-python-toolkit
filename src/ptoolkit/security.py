"""Security helpers: password generation and strength estimation."""

from __future__ import annotations

import re
import secrets
import string
from dataclasses import dataclass, field
from typing import List

SYMBOLS = "!@#$%^&*()-_=+[]{}"

_COMMON = {
    "password", "password1", "123456", "12345678", "123456789", "qwerty",
    "qwerty123", "abc123", "letmein", "iloveyou", "admin", "welcome", "111111",
}

_LABELS = ["very weak", "weak", "fair", "strong", "very strong"]


def generate_password(
    length: int = 16,
    digits: bool = True,
    symbols: bool = True,
    uppercase: bool = True,
) -> str:
    """Generate a random password using :mod:`secrets`.

    Guarantees at least one character from every enabled character class.
    """
    pools = [string.ascii_lowercase]
    if uppercase:
        pools.append(string.ascii_uppercase)
    if digits:
        pools.append(string.digits)
    if symbols:
        pools.append(SYMBOLS)
    if length < len(pools):
        raise ValueError(f"length must be >= {len(pools)} for the chosen options")

    chars = [secrets.choice(pool) for pool in pools]
    alphabet = "".join(pools)
    chars += [secrets.choice(alphabet) for _ in range(length - len(chars))]
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


@dataclass
class StrengthResult:
    score: int  # 0 (very weak) .. 4 (very strong)
    label: str
    suggestions: List[str] = field(default_factory=list)


def password_strength(password: str) -> StrengthResult:
    """Rate a password from 0 to 4 with improvement suggestions."""
    classes = sum(
        bool(re.search(pattern, password))
        for pattern in (r"[a-z]", r"[A-Z]", r"\d", r"[^A-Za-z0-9]")
    )
    suggestions: List[str] = []

    if password.lower() in _COMMON or (password and re.fullmatch(r"(.)\1*", password)):
        score = 0
        suggestions.append("avoid common or repeated-character passwords")
    else:
        score = 0
        score += len(password) >= 8
        score += len(password) >= 12
        score += classes >= 3
        score += len(password) >= 16 and classes >= 3

    if len(password) < 12:
        suggestions.append("use at least 12 characters")
    if classes < 3:
        suggestions.append("mix upper/lower case, digits and symbols")

    return StrengthResult(score=score, label=_LABELS[score], suggestions=suggestions)
