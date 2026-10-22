import hashlib

import pytest

from ptoolkit.files import dir_size, find_duplicates, hash_file, human_size


class TestHumanSize:
    @pytest.mark.parametrize(
        "value, expected",
        [
            (0, "0 B"),
            (512, "512 B"),
            (1024, "1.0 KB"),
            (1536, "1.5 KB"),
            (1024**2, "1.0 MB"),
            (1024**3, "1.0 GB"),
            (1024**5 * 3, "3.0 PB"),
            (1024**6, "1024.0 PB"),
        ],
    )
    def test_formats(self, value, expected):
        assert human_size(value) == expected

    def test_negative(self):
        with pytest.raises(ValueError):
            human_size(-1)


class TestHashFile:
    def test_sha256(self, tmp_path):
        f = tmp_path / "a.txt"
        f.write_bytes(b"hello")
        assert hash_file(f) == hashlib.sha256(b"hello").hexdigest()

    def test_other_algo_and_small_chunks(self, tmp_path):
        f = tmp_path / "a.txt"
        f.write_bytes(b"hello world")
        assert hash_file(f, algo="md5", chunk_size=3) == hashlib.md5(b"hello world").hexdigest()

    def test_bad_algo(self, tmp_path):
        f = tmp_path / "a.txt"
        f.write_bytes(b"x")
        with pytest.raises(ValueError, match="unsupported"):
            hash_file(f, algo="nope")

    def test_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            hash_file(tmp_path / "missing")


class TestFindDuplicates:
    def test_finds_groups(self, tmp_path):
        (tmp_path / "sub").mkdir()
        (tmp_path / "a.txt").write_text("same")
        (tmp_path / "sub" / "b.txt").write_text("same")
        (tmp_path / "c.txt").write_text("diff")      # same size, different content
        (tmp_path / "d.txt").write_text("unique!")   # unique size
        groups = find_duplicates(tmp_path)
        assert groups == [[tmp_path / "a.txt", tmp_path / "sub" / "b.txt"]]

    def test_no_duplicates(self, tmp_path):
        (tmp_path / "a").write_text("1")
        (tmp_path / "b").write_text("2")
        assert find_duplicates(tmp_path) == []

    def test_not_a_directory(self, tmp_path):
        f = tmp_path / "f"
        f.write_text("x")
        with pytest.raises(NotADirectoryError):
            find_duplicates(f)


class TestDirSize:
    def test_directory(self, tmp_path):
        (tmp_path / "sub").mkdir()
        (tmp_path / "a").write_bytes(b"12345")
        (tmp_path / "sub" / "b").write_bytes(b"123")
        assert dir_size(tmp_path) == 8

    def test_single_file(self, tmp_path):
        f = tmp_path / "a"
        f.write_bytes(b"1234")
        assert dir_size(f) == 4

    def test_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            dir_size(tmp_path / "nope")

    def test_symlinks_ignored(self, tmp_path):
        target = tmp_path / "real"
        target.write_bytes(b"1234")
        link = tmp_path / "link"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):  # pragma: no cover
            pytest.skip("symlinks unsupported")
        assert dir_size(tmp_path) == 4
        assert find_duplicates(tmp_path) == []
