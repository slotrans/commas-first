import pytest

from cftoken import CFTokenKind, CFToken


def test_word_equality():
    assert CFToken(CFTokenKind.WORD, "foo") == CFToken(CFTokenKind.WORD, "foo")
    assert CFToken(CFTokenKind.WORD, "foo") == CFToken(CFTokenKind.WORD, "FOO")


def test_literal_equality():
    assert CFToken(CFTokenKind.LITERAL, "foo") == CFToken(CFTokenKind.LITERAL, "foo")
    assert CFToken(CFTokenKind.LITERAL, "foo") != CFToken(CFTokenKind.LITERAL, "FOO")


def test_line_comment_equality():
    assert CFToken(CFTokenKind.LINE_COMMENT, "--foo\n") == CFToken(CFTokenKind.LINE_COMMENT, "--foo\n")
    assert CFToken(CFTokenKind.LINE_COMMENT, "--foo\n") != CFToken(CFTokenKind.LINE_COMMENT, "--FOO\n")


def test_block_comment_equality():
    assert CFToken(CFTokenKind.BLOCK_COMMENT, "/* foo */") == CFToken(CFTokenKind.BLOCK_COMMENT, "/* foo */")
    assert CFToken(CFTokenKind.BLOCK_COMMENT, "/* foo */") != CFToken(CFTokenKind.BLOCK_COMMENT, "/* FOO */")


def test_spaces_equality():
    assert CFToken(CFTokenKind.SPACES, " ") == CFToken(CFTokenKind.SPACES, " ")
    assert CFToken(CFTokenKind.SPACES, " ") != CFToken(CFTokenKind.SPACES, "  ")


def test_newline_equality():
    assert CFToken(CFTokenKind.NEWLINE, "\n") == CFToken(CFTokenKind.NEWLINE, "\n")


def test_newline_validation():
    with pytest.raises(ValueError):
        CFToken(CFTokenKind.NEWLINE, "foo")

    with pytest.raises(ValueError):
        CFToken(CFTokenKind.NEWLINE, "\r\n")


def test_spaces_validation():
    with pytest.raises(ValueError):
        CFToken(CFTokenKind.SPACES, "foo")

    with pytest.raises(ValueError):
        CFToken(CFTokenKind.SPACES, "  x  ")

    with pytest.raises(ValueError):
        CFToken(CFTokenKind.SPACES, "\n")

    with pytest.raises(ValueError):
        CFToken(CFTokenKind.SPACES, "\t")

    with pytest.raises(ValueError):
        CFToken(CFTokenKind.SPACES, "")
