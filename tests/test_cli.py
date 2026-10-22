import io
import runpy
import shutil
import subprocess
import sys

import pytest

import ptoolkit
from ptoolkit.cli import main


def run(capsys, *argv):
    code = main(list(argv))
    out = capsys.readouterr()
    return code, out.out, out.err


def test_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert ptoolkit.__version__ in capsys.readouterr().out


def test_no_command_prints_help(capsys):
    code, out, _ = run(capsys)
    assert code == 0
    assert "usage: ptk" in out


def test_slug(capsys):
    code, out, _ = run(capsys, "slug", "Hello World!", "--sep", "_", "--max-length", "8")
    assert (code, out.strip()) == (0, "hello_wo")


def test_slug_error(capsys):
    code, _, err = run(capsys, "slug", "x", "--max-length", "0")
    assert code == 1
    assert "error" in err


def test_wc_file(capsys, tmp_path):
    f = tmp_path / "t.txt"
    f.write_text("one two\nthree\n")
    code, out, _ = run(capsys, "wc", str(f))
    assert code == 0
    assert "lines: 2" in out and "words: 3" in out


def test_wc_stdin(capsys, monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO("a b c"))
    code, out, _ = run(capsys, "wc", "-")
    assert code == 0 and "words: 3" in out


def test_wc_missing_file(capsys, tmp_path):
    code, out, err = run(capsys, "wc", str(tmp_path / "nope.txt"))
    assert code == 1 and out == "" and "error" in err


def test_readtime(capsys, monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO("word " * 450))
    code, out, _ = run(capsys, "readtime", "--wpm", "100")
    assert (code, out.strip()) == (0, "5 min read")


def test_emails_unique_and_all(capsys, tmp_path):
    f = tmp_path / "m.txt"
    f.write_text("a@x.com a@x.com b@y.org")
    _, out, _ = run(capsys, "emails", str(f))
    assert out.split() == ["a@x.com", "b@y.org"]
    _, out, _ = run(capsys, "emails", str(f), "--all")
    assert len(out.split()) == 3


def test_hash(capsys, tmp_path):
    f = tmp_path / "h.txt"
    f.write_bytes(b"hello")
    code, out, _ = run(capsys, "hash", str(f), "--algo", "md5")
    assert code == 0
    assert out.startswith("5d41402abc4b2a76b9719d911017c592")


def test_hash_bad_algo(capsys, tmp_path):
    f = tmp_path / "h.txt"
    f.write_bytes(b"x")
    code, _, err = run(capsys, "hash", str(f), "--algo", "nope")
    assert code == 1 and "unsupported" in err


def test_dupes_found_and_none(capsys, tmp_path):
    (tmp_path / "a").write_text("x")
    (tmp_path / "b").write_text("x")
    (tmp_path / "c").write_text("y")
    code, out, _ = run(capsys, "dupes", str(tmp_path))
    assert code == 0 and "a" in out and "b" in out and "c\n" not in out

    (tmp_path / "b").unlink()
    _, out, _ = run(capsys, "dupes", str(tmp_path))
    assert "No duplicates found." in out


def test_dupes_multiple_groups_separated(capsys, tmp_path):
    for name, body in [("a1", "1"), ("a2", "1"), ("b1", "22"), ("b2", "22")]:
        (tmp_path / name).write_text(body)
    _, out, _ = run(capsys, "dupes", str(tmp_path))
    assert "\n\n" in out


def test_dupes_not_a_dir(capsys, tmp_path):
    f = tmp_path / "f"
    f.write_text("x")
    code, _, err = run(capsys, "dupes", str(f))
    assert code == 1 and "not a directory" in err


def test_du(capsys, tmp_path):
    (tmp_path / "a").write_bytes(b"x" * 2048)
    code, out, _ = run(capsys, "du", str(tmp_path))
    assert (code, out.strip()) == (0, "2.0 KB (2048 bytes)")


def test_passgen(capsys):
    code, out, _ = run(capsys, "passgen", "--length", "20", "--count", "3", "--no-symbols")
    lines = out.split()
    assert code == 0 and len(lines) == 3
    assert all(len(p) == 20 and p.isalnum() for p in lines)


def test_passgen_no_digits(capsys):
    _, out, _ = run(capsys, "passgen", "--no-digits", "--length", "30")
    assert not any(c.isdigit() for c in out.strip())


def test_passgen_too_short(capsys):
    code, _, err = run(capsys, "passgen", "--length", "2")
    assert code == 1 and "length" in err


def test_strength(capsys):
    code, out, _ = run(capsys, "strength", "password")
    assert code == 0
    assert "very weak (0/4)" in out and "- " in out


def test_python_dash_m(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["ptoolkit", "slug", "Hi There"])
    sys.modules.pop("ptoolkit.__main__", None)
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("ptoolkit", run_name="__main__")
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == "hi-there"


def test_installed_console_script(tmp_path):
    exe = shutil.which("ptk")
    if exe is None:
        pytest.skip("ptk not on PATH (package not installed)")
    result = subprocess.run(
        [exe, "slug", "Works Anywhere"], cwd=tmp_path, capture_output=True, text=True
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "works-anywhere"
