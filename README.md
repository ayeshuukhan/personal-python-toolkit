# ptoolkit

A small, dependency-free personal toolkit with text, file and password utilities,
usable both as a Python library and as a command-line tool (`ptk`).

## Features

| Area     | Functions                                             | CLI command            |
|----------|-------------------------------------------------------|------------------------|
| Text     | `slugify`, `word_count`, `reading_time`, `extract_emails` | `slug`, `wc`, `readtime`, `emails` |
| Files    | `hash_file`, `find_duplicates`, `dir_size`, `human_size`  | `hash`, `dupes`, `du`  |
| Security | `generate_password`, `password_strength`              | `passgen`, `strength`  |

## Installation

Python 3.9+ required. From the project root:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"            # editable install + test tools
```

Plain editable install (no test tools): `pip install -e .`

Once the virtualenv is active, `ptk` works from **any directory**:

```bash
cd ~ && ptk --version
```

## CLI usage

```bash
ptk slug "Hello, Wörld!"                 # hello-world
ptk slug "Long title here" --max-length 8 --sep _
ptk wc notes.txt                         # lines / words / chars
cat notes.txt | ptk readtime --wpm 180   # reads stdin when no file given
ptk emails contacts.txt                  # unique emails (use --all to keep dupes)
ptk hash a.iso b.iso --algo sha256
ptk dupes ~/Downloads                    # groups of identical files
ptk du ~/Downloads                       # 1.4 GB (1503238553 bytes)
ptk passgen --length 24 --count 3
ptk strength "Tr0ub4dor&3"
```

Errors go to stderr and the exit code is `1`; success is `0`.
`python -m ptoolkit ...` works too.

## Library usage

```python
from ptoolkit import slugify, generate_password, find_duplicates

slugify("Café au lait")        # 'cafe-au-lait'
generate_password(20)          # random, uses `secrets`
find_duplicates("~/Pictures")  # [[Path(...), Path(...)], ...]
```

## Testing & coverage

```bash
pytest                         # runs tests + coverage (configured in pyproject.toml)
```

Reports produced on every run:

- terminal summary with missing lines
- `htmlcov/index.html` (open in a browser)
- `coverage.xml` (for CI tools)

The suite fails if total coverage drops below **95%**.
A snapshot of the latest report is saved in `coverage.txt`.

## Project layout

```
ptoolkit/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/ptoolkit/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── files.py
│   ├── security.py
│   └── text.py
└── tests/
    ├── test_cli.py
    ├── test_files.py
    ├── test_security.py
    └── test_text.py
```

## License

MIT
