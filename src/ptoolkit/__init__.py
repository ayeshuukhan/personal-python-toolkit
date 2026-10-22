"""ptoolkit: a small personal toolkit of text, file and security helpers."""

__version__ = "0.1.0"

from .files import dir_size, find_duplicates, hash_file, human_size
from .security import StrengthResult, generate_password, password_strength
from .text import extract_emails, reading_time, slugify, word_count

__all__ = [
    "__version__",
    "slugify",
    "word_count",
    "reading_time",
    "extract_emails",
    "human_size",
    "hash_file",
    "find_duplicates",
    "dir_size",
    "generate_password",
    "password_strength",
    "StrengthResult",
]
