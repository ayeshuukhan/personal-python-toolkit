import string

import pytest

from ptoolkit.security import SYMBOLS, generate_password, password_strength


class TestGeneratePassword:
    def test_default_length_and_classes(self):
        for _ in range(50):
            pw = generate_password()
            assert len(pw) == 16
            assert any(c in string.ascii_lowercase for c in pw)
            assert any(c in string.ascii_uppercase for c in pw)
            assert any(c in string.digits for c in pw)
            assert any(c in SYMBOLS for c in pw)

    def test_options_disable_classes(self):
        pw = generate_password(length=30, digits=False, symbols=False, uppercase=False)
        assert pw.islower() and pw.isalpha()

    def test_minimum_length_boundary(self):
        assert len(generate_password(length=4)) == 4

    def test_too_short(self):
        with pytest.raises(ValueError):
            generate_password(length=3)

    def test_passwords_differ(self):
        assert generate_password(32) != generate_password(32)


class TestPasswordStrength:
    @pytest.mark.parametrize("pw", ["password", "PASSWORD", "123456", "aaaaaaaaaaaa"])
    def test_common_or_repeated_is_zero(self, pw):
        result = password_strength(pw)
        assert result.score == 0
        assert result.label == "very weak"
        assert any("common" in s for s in result.suggestions)

    def test_empty_password(self):
        assert password_strength("").score == 0

    def test_weak(self):
        assert password_strength("abcdefgh").score == 1

    def test_fair(self):
        assert password_strength("abcdefghijkl").score == 2

    def test_strong(self):
        result = password_strength("Abcdefgh1234")
        assert result.score == 3
        assert result.label == "strong"

    def test_very_strong(self):
        result = password_strength("Abcdefgh1234!xyz")
        assert result.score == 4
        assert result.suggestions == []

    def test_suggestions_for_short_simple(self):
        tips = password_strength("abc").suggestions
        assert any("12 characters" in t for t in tips)
        assert any("mix" in t for t in tips)
