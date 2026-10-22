"""File helpers: hashing, duplicate detection, directory size."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from pathlib import Path
from typing import List, Union

PathLike = Union[str, Path]

_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]


def human_size(num_bytes: int) -> str:
    """Format a byte count, e.g. ``1536`` -> ``"1.5 KB"``."""
    if num_bytes < 0:
        raise ValueError("num_bytes must be >= 0")
    size = float(num_bytes)
    for unit in _UNITS:
        if size < 1024 or unit == _UNITS[-1]:
            if unit == "B":
                return f"{int(size)} B"
            return f"{size:.1f} {unit}"
        size /= 1024
    raise AssertionError("unreachable")  # pragma: no cover


def hash_file(path: PathLike, algo: str = "sha256", chunk_size: int = 65536) -> str:
    """Return the hex digest of a file, read in chunks."""
    try:
        digest = hashlib.new(algo)
    except ValueError as exc:
        raise ValueError(f"unsupported hash algorithm: {algo}") from exc
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_duplicates(root: PathLike) -> List[List[Path]]:
    """Group files under *root* that have identical content.

    Files are grouped by size first so only potential matches are hashed.
    Returns a list of groups (each with 2+ paths), sorted for stable output.
    """
    root_path = Path(root)
    if not root_path.is_dir():
        raise NotADirectoryError(f"not a directory: {root}")

    by_size = defaultdict(list)
    for path in sorted(root_path.rglob("*")):
        if path.is_file() and not path.is_symlink():
            by_size[path.stat().st_size].append(path)

    groups: List[List[Path]] = []
    for paths in by_size.values():
        if len(paths) < 2:
            continue
        by_hash = defaultdict(list)
        for path in paths:
            by_hash[hash_file(path)].append(path)
        groups.extend(sorted(p) for p in by_hash.values() if len(p) > 1)
    return sorted(groups)


def dir_size(path: PathLike) -> int:
    """Total size in bytes of a file, or of all files under a directory."""
    target = Path(path)
    if not target.exists():
        raise FileNotFoundError(f"no such path: {path}")
    if target.is_file():
        return target.stat().st_size
    return sum(
        p.stat().st_size
        for p in target.rglob("*")
        if p.is_file() and not p.is_symlink()
    )
