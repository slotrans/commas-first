import pytest

import sf_flags
from sftoken import (
    SFToken,
    SFTokenKind,
)
from clause_formatter import (
    trim_trailing_whitespace,
    trim_leading_whitespace,
    trim_one_leading_space,
    get_paren_block,
)


# pytest magic
def setup_module():
    sf_flags.reset_to_defaults()


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


class TestTrimLeadingWhitespace:
    def test_empty(self):
        expected = []
        actual = trim_leading_whitespace([])
        assert expected == actual


    def test_no_whitespace(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
        ]

        expected = tokens
        actual = trim_leading_whitespace(tokens)

        assert expected == actual


    def test_one_spaces_token(self):
        tokens = [
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
        ]

        expected = tokens[1:]
        actual = trim_leading_whitespace(tokens)

        assert expected == actual


    def test_one_newline_token(self):
        tokens = [
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
        ]

        expected = tokens[1:]
        actual = trim_leading_whitespace(tokens)

        assert expected == actual


class TestTrimOneLeadingSpace:
    def test_empty(self):
        expected = []
        actual = trim_one_leading_space([])
        assert expected == actual


    def test_no_whitespace(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
        ]

        expected = tokens
        actual = trim_one_leading_space(tokens)

        assert expected == actual


    def test_one_spaces_token(self):
        tokens = [
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
        ]

        expected = tokens[1:]
        actual = trim_one_leading_space(tokens)

        assert expected == actual


    def test_many_spaces_token(self):
        for i in range(2, 10): # enough examples to prove the point
            token_with_i_spaces = SFToken(SFTokenKind.SPACES, " "*i)
            tokens = [
                token_with_i_spaces,
                SFToken(SFTokenKind.WORD, "x"),
                SFToken(SFTokenKind.SYMBOL, "="),
                SFToken(SFTokenKind.WORD, "y"),
            ]

            one_space_shorter = SFToken(SFTokenKind.SPACES, " "*(i-1))
            expected = [one_space_shorter] + tokens[1:]
            actual = trim_one_leading_space(tokens)

            assert expected == actual


    def test_one_newline_token(self):
        tokens = [
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
        ]

        expected = tokens
        actual = trim_one_leading_space(tokens)

        assert expected == actual


    def test_mixed_whitespace_starting_with_newline(self):
        tokens = [
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
        ]

        expected = tokens
        actual = trim_one_leading_space(tokens)

        assert expected == actual


    def test_mixed_whitespace_starting_with_one_space(self):
        tokens = [
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
        ]

        expected = tokens[1:]
        actual = trim_one_leading_space(tokens)

        assert expected == actual


class TestGetParenBlock:
    def test_empty(self):
        with pytest.raises(ValueError):
            get_paren_block([])


    def test_inappropriate_input(self):
        with pytest.raises(ValueError):
            get_paren_block([SFToken(SFTokenKind.WORD, "foo")])


    def test_incomplete_block(self):
        tokens = [
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
        ]

        actual = get_paren_block(tokens)

        assert actual is None


    def test_select_block(self):
        # (select foo from bar) extra tokens
        tokens = [
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ")"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "extra"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "tokens"),
        ]

        expected = tokens[0:9]
        actual = get_paren_block(tokens)

        assert expected == actual


    def test_select_block_with_function_call(self):
        # (select coalesce(foo, -1) from bar) extra tokens
        tokens = [
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "coalesce"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "-1"),
            SFToken(SFTokenKind.SYMBOL, ")"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ")"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "extra"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "tokens"),
        ]

        expected = tokens[0:15]
        actual = get_paren_block(tokens)

        assert expected == actual
