import pytest

import sflexer
from sftoken import SFToken, SFTokenKind


def test_none():
    text = None
    expected = []
    actual = sflexer.lex(text)
    assert expected == actual


def test_empty():
    text = ""
    expected = []
    actual = sflexer.lex(text)
    assert expected == actual


def test_newline():
    text = "\n"
    expected = [SFToken(SFTokenKind.NEWLINE, "\n")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_spaces():
    for i in range(1, 10): # arbitrary
        i_spaces = " " * i
        expected = [SFToken(SFTokenKind.SPACES, i_spaces)]
        actual = sflexer.lex(i_spaces)
        assert expected == actual


def test_integer_literal():
    text = "1"
    expected = [SFToken(SFTokenKind.WORD, "1")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_decimal_literal():
    text = "3.14"
    expected = [SFToken(SFTokenKind.WORD, "3.14")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_scientific_literal():
    text = "1.23e4"
    expected = [SFToken(SFTokenKind.WORD, "1.23e4")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_word():
    text = "foo"
    expected = [SFToken(SFTokenKind.WORD, "foo")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_words_with_spaces():
    text = "foo bar baz"
    expected = [
        SFToken(SFTokenKind.WORD, "foo"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "bar"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "baz"),
    ]
    actual = sflexer.lex(text)
    assert expected == actual


def test_words_with_newlines():
    text = "foo\nbar\nbaz"
    expected = [
        SFToken(SFTokenKind.WORD, "foo"),
        SFToken(SFTokenKind.NEWLINE, "\n"),
        SFToken(SFTokenKind.WORD, "bar"),
        SFToken(SFTokenKind.NEWLINE, "\n"),
        SFToken(SFTokenKind.WORD, "baz"),
    ]
    actual = sflexer.lex(text)
    assert expected == actual


def test_single_quoted_literal():
    text = "'literal'"
    expected = [SFToken(SFTokenKind.LITERAL, "'literal'")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_single_quoted_literal_with_escaped_quote1():
    text = "'bob''s'"
    expected = [SFToken(SFTokenKind.LITERAL, "'bob''s'")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_single_quoted_literal_with_escaped_quote2():
    text = r"'bob\'s'"
    expected = [SFToken(SFTokenKind.LITERAL, r"'bob\'s'")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_single_quoted_literal_multiline():
    text = "'line one\nline two'"
    expected = [SFToken(SFTokenKind.LITERAL, "'line one\nline two'")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_double_quoted_identifier():
    text = '"identifier"'
    expected = [SFToken(SFTokenKind.LITERAL, '"identifier"')]
    actual = sflexer.lex(text)
    assert expected == actual


def test_double_quoted_identifier_with_escaped_quote1():
    text = '"this is a ""bad"" identifier"'
    expected = [SFToken(SFTokenKind.LITERAL, '"this is a ""bad"" identifier"')]
    actual = sflexer.lex(text)
    assert expected == actual


def test_double_quoted_identifier_with_escaped_quote2():
    text = r'"this is a \"bad\" identifier"'
    expected = [SFToken(SFTokenKind.LITERAL, r'"this is a \"bad\" identifier"')]
    actual = sflexer.lex(text)
    assert expected == actual


def test_backtick_quoted_identifier():
    text = "`identifier`"
    expected = [SFToken(SFTokenKind.LITERAL, "`identifier`")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_backtick_quoted_identifier_with_escaped_quote1():
    text = "`one ``two`` three`"
    expected = [SFToken(SFTokenKind.LITERAL, "`one ``two`` three`")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_backtick_quoted_identifier_with_escaped_quote2():
    text = r"`one \`two\` three`"
    expected = [SFToken(SFTokenKind.LITERAL, r"`one \`two\` three`")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_dotted_identifier():
    text = "foo.bar"
    expected = [SFToken(SFTokenKind.WORD, "foo"), SFToken(SFTokenKind.SYMBOL, "."), SFToken(SFTokenKind.WORD, "bar")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_line_comment(): # this one case is probably not sufficient
    text = "foo\n--hey\nbar"
    expected = [
        SFToken(SFTokenKind.WORD, "foo"),
        SFToken(SFTokenKind.NEWLINE, "\n"),
        SFToken(SFTokenKind.LINE_COMMENT, "--hey\n"),
        SFToken(SFTokenKind.WORD, "bar"),
    ]
    actual = sflexer.lex(text)
    assert expected == actual


def test_block_comment(): # this one case is probably not sufficient
    text = "foo/* hey */bar"
    expected = [
        SFToken(SFTokenKind.WORD, "foo"),
        SFToken(SFTokenKind.BLOCK_COMMENT, "/* hey */"),
        SFToken(SFTokenKind.WORD, "bar"),
    ]
    actual = sflexer.lex(text)
    assert expected == actual


def test_symbols():
    symbols = [
        "~",
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "&",
        "*",
        "(",
        ")",
        "-",
        "+",
        "=",
        "[",
        "]",
        "{",
        "}",
        "|",
        ",",
        "<",
        ">",
        "?",
        "/",
        ":",
        ";",
        ",",
        ".",
    ]

    for s in symbols:
        expected = [SFToken(SFTokenKind.SYMBOL, s)]
        actual = sflexer.lex(s)
        assert expected == actual
