"""Command-line interface for ptoolkit (installed as ``ptk``)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from . import __version__, files, security, text


def _read_text(source: Optional[str]) -> str:
    """Read from a file path, or from stdin when *source* is None or '-'."""
    if source in (None, "-"):
        return sys.stdin.read()
    return Path(source).read_text(encoding="utf-8")


def _cmd_slug(args: argparse.Namespace) -> int:
    print(text.slugify(args.text, sep=args.sep, max_length=args.max_length))
    return 0


def _cmd_wc(args: argparse.Namespace) -> int:
    counts = text.word_count(_read_text(args.file))
    for key in ("lines", "words", "chars"):
        print(f"{key}: {counts[key]}")
    return 0


def _cmd_readtime(args: argparse.Namespace) -> int:
    minutes = text.reading_time(_read_text(args.file), wpm=args.wpm)
    print(f"{minutes} min read")
    return 0


def _cmd_emails(args: argparse.Namespace) -> int:
    for email in text.extract_emails(_read_text(args.file), unique=not args.all):
        print(email)
    return 0


def _cmd_hash(args: argparse.Namespace) -> int:
    for path in args.files:
        print(f"{files.hash_file(path, algo=args.algo)}  {path}")
    return 0


def _cmd_dupes(args: argparse.Namespace) -> int:
    groups = files.find_duplicates(args.directory)
    if not groups:
        print("No duplicates found.")
        return 0
    for index, group in enumerate(groups):
        if index:
            print()
        for path in group:
            print(path)
    return 0


def _cmd_du(args: argparse.Namespace) -> int:
    total = files.dir_size(args.path)
    print(f"{files.human_size(total)} ({total} bytes)")
    return 0


def _cmd_passgen(args: argparse.Namespace) -> int:
    for _ in range(args.count):
        print(
            security.generate_password(
                length=args.length,
                digits=not args.no_digits,
                symbols=not args.no_symbols,
            )
        )
    return 0


def _cmd_strength(args: argparse.Namespace) -> int:
    result = security.password_strength(args.password)
    print(f"{result.label} ({result.score}/4)")
    for tip in result.suggestions:
        print(f"- {tip}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ptk", description="Personal toolkit: text, file and password utilities."
    )
    parser.add_argument("--version", action="version", version=f"ptk {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    p = sub.add_parser("slug", help="turn text into a URL-friendly slug")
    p.add_argument("text")
    p.add_argument("--sep", default="-", help="separator (default: -)")
    p.add_argument("--max-length", type=int, default=None)
    p.set_defaults(func=_cmd_slug)

    p = sub.add_parser("wc", help="count lines, words and characters")
    p.add_argument("file", nargs="?", help="file path, or '-' / omitted for stdin")
    p.set_defaults(func=_cmd_wc)

    p = sub.add_parser("readtime", help="estimate reading time")
    p.add_argument("file", nargs="?", help="file path, or '-' / omitted for stdin")
    p.add_argument("--wpm", type=int, default=200, help="words per minute")
    p.set_defaults(func=_cmd_readtime)

    p = sub.add_parser("emails", help="extract email addresses")
    p.add_argument("file", nargs="?", help="file path, or '-' / omitted for stdin")
    p.add_argument("--all", action="store_true", help="keep duplicates")
    p.set_defaults(func=_cmd_emails)

    p = sub.add_parser("hash", help="print file checksums")
    p.add_argument("files", nargs="+")
    p.add_argument("--algo", default="sha256", help="hash algorithm (default: sha256)")
    p.set_defaults(func=_cmd_hash)

    p = sub.add_parser("dupes", help="find duplicate files in a directory")
    p.add_argument("directory")
    p.set_defaults(func=_cmd_dupes)

    p = sub.add_parser("du", help="show size of a file or directory")
    p.add_argument("path")
    p.set_defaults(func=_cmd_du)

    p = sub.add_parser("passgen", help="generate random passwords")
    p.add_argument("--length", type=int, default=16)
    p.add_argument("--count", type=int, default=1)
    p.add_argument("--no-digits", action="store_true")
    p.add_argument("--no-symbols", action="store_true")
    p.set_defaults(func=_cmd_passgen)

    p = sub.add_parser("strength", help="rate a password")
    p.add_argument("password")
    p.set_defaults(func=_cmd_strength)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    try:
        return args.func(args)
    except (OSError, ValueError) as exc:
        print(f"ptk: error: {exc}", file=sys.stderr)
        return 1
