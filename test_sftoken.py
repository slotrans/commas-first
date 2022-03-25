import pytest

from sftoken import SFTokenKind, SFToken


def test_word_equality():
    assert SFToken(SFTokenKind.WORD, "foo") == SFToken(SFTokenKind.WORD, "foo")
    assert SFToken(SFTokenKind.WORD, "foo") == SFToken(SFTokenKind.WORD, "FOO")


def test_literal_equality():
    assert SFToken(SFTokenKind.LITERAL, "foo") == SFToken(SFTokenKind.LITERAL, "foo")
    assert SFToken(SFTokenKind.LITERAL, "foo") != SFToken(SFTokenKind.LITERAL, "FOO")


def test_line_comment_equality():
    assert SFToken(SFTokenKind.LINE_COMMENT, "--foo\n") == SFToken(SFTokenKind.LINE_COMMENT, "--foo\n")
    assert SFToken(SFTokenKind.LINE_COMMENT, "--foo\n") != SFToken(SFTokenKind.LINE_COMMENT, "--FOO\n")


def test_block_comment_equality():
    assert SFToken(SFTokenKind.BLOCK_COMMENT, "/* foo */") == SFToken(SFTokenKind.BLOCK_COMMENT, "/* foo */")
    assert SFToken(SFTokenKind.BLOCK_COMMENT, "/* foo */") != SFToken(SFTokenKind.BLOCK_COMMENT, "/* FOO */")


def test_spaces_equality():
    assert SFToken(SFTokenKind.SPACES, " ") == SFToken(SFTokenKind.SPACES, " ")
    assert SFToken(SFTokenKind.SPACES, " ") != SFToken(SFTokenKind.SPACES, "  ")


def test_newline_equality():
    assert SFToken(SFTokenKind.NEWLINE, "\n") == SFToken(SFTokenKind.NEWLINE, "\n")


def test_newline_validation():
    with pytest.raises(ValueError):
        SFToken(SFTokenKind.NEWLINE, "foo")

    with pytest.raises(ValueError):
        SFToken(SFTokenKind.NEWLINE, "\r\n")


def test_spaces_validation():
    with pytest.raises(ValueError):
        SFToken(SFTokenKind.SPACES, "foo")

    with pytest.raises(ValueError):
        SFToken(SFTokenKind.SPACES, "  x  ")

    with pytest.raises(ValueError):
        SFToken(SFTokenKind.SPACES, "\n")

    with pytest.raises(ValueError):
        SFToken(SFTokenKind.SPACES, "\t")
