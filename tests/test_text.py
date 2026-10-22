import pytest

from ptoolkit.text import extract_emails, reading_time, slugify, word_count


class TestSlugify:
    def test_basic(self):
        assert slugify("Hello, World!") == "hello-world"

    def test_accents_stripped(self):
        assert slugify("Café Münster") == "cafe-munster"

    def test_collapses_separators(self):
        assert slugify("  a   --  b  ") == "a-b"

    def test_custom_separator(self):
        assert slugify("Hello World", sep="_") == "hello_world"

    def test_max_length(self):
        assert slugify("hello world again", max_length=8) == "hello-wo"

    def test_max_length_trims_trailing_separator(self):
        assert slugify("hello world", max_length=6) == "hello"

    def test_empty_and_symbols_only(self):
        assert slugify("") == ""
        assert slugify("!!!") == ""

    def test_empty_sep_rejected(self):
        with pytest.raises(ValueError):
            slugify("x", sep="")

    def test_bad_max_length(self):
        with pytest.raises(ValueError):
            slugify("x", max_length=0)


class TestWordCount:
    def test_counts(self):
        assert word_count("one two\nthree") == {"lines": 2, "words": 3, "chars": 13}

    def test_empty(self):
        assert word_count("") == {"lines": 0, "words": 0, "chars": 0}


class TestReadingTime:
    def test_empty_is_zero(self):
        assert reading_time("") == 0

    def test_short_text_is_one_minute(self):
        assert reading_time("just a few words") == 1

    def test_rounds_up(self):
        assert reading_time("word " * 401) == 3

    def test_custom_wpm(self):
        assert reading_time("word " * 100, wpm=50) == 2

    def test_bad_wpm(self):
        with pytest.raises(ValueError):
            reading_time("x", wpm=0)


class TestExtractEmails:
    TEXT = "Mail a@x.com, B@Y.org; again A@X.com and c.d+e@sub.domain.io."

    def test_unique_case_insensitive(self):
        assert extract_emails(self.TEXT) == ["a@x.com", "B@Y.org", "c.d+e@sub.domain.io"]

    def test_keep_duplicates(self):
        assert len(extract_emails(self.TEXT, unique=False)) == 4

    def test_none_found(self):
        assert extract_emails("no emails here") == []
