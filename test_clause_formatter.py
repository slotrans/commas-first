import pytest

from sftoken import SFToken
from sftoken import SFTokenKind
from clause_formatter import trim_trailing_whitespace


class TestTrimTrailingWhitespace:
    def test_empty(self):
        expected = []
        actual = trim_trailing_whitespace([])
        assert expected == actual


    def test_no_whitespace(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
        ]

        expected = tokens
        actual = trim_trailing_whitespace(tokens)

        assert expected == actual


    def test_one_spaces_token(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
            SFToken(SFTokenKind.SPACES, " "),
        ]

        expected = tokens[0:3]
        actual = trim_trailing_whitespace(tokens)

        assert expected == actual


    def test_one_newline_token(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
        ]

        expected = tokens[0:3]
        actual = trim_trailing_whitespace(tokens)

        assert expected == actual


    def test_multiple(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.NEWLINE, "\n"),
        ]

        expected = tokens[0:3]
        actual = trim_trailing_whitespace(tokens)

        assert expected == actual
