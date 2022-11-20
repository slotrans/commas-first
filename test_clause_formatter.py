import pytest

import sf_flags
from sftoken import (
    SFToken,
    SFTokenKind,
    Whitespace,
)
from clause_formatter import (
    trim_trailing_whitespace,
    trim_leading_whitespace,
    trim_one_leading_space,
    get_paren_block,
    make_compact,
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


class TestMakeCompact:
    def test_empty(self):
        expected = []
        actual = make_compact([])
        assert expected == actual


    def test_one_space(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "b"),
        ]

        expected = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_only_spaces(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "b"),
        ]

        expected = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_only_newline(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.WORD, "b"),
        ]

        expected = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_spaces_then_newline(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.WORD, "b"),
        ]

        expected = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_newline_then_spaces(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "b"),
        ]

        expected = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_spaces_around_newline(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "b"),
        ]

        expected = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_newlines_around_spaces(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.WORD, "b"),
        ]

        expected = [
            SFToken(SFTokenKind.WORD, "a"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_left_paren_then_space(self):
        tokens = [
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.SPACES, " "),
        ]

        expected = [
            SFToken(SFTokenKind.SYMBOL, "("),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_space_then_right_paren(self):
        tokens = [
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ]

        expected = [
            SFToken(SFTokenKind.SYMBOL, ")"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_space_then_comma(self):
        tokens = [
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ","),
        ]

        expected = [
            SFToken(SFTokenKind.SYMBOL, ","),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    # this isn't great, but make_compact() is about removing whitespace, not adding it...
    def test_packed_list(self):
        # (1,2,3)
        tokens = [
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.WORD, "3"),
            SFToken(SFTokenKind.SYMBOL, ")")
        ]

        # (1,2,3)
        expected = [
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.WORD, "3"),
            SFToken(SFTokenKind.SYMBOL, ")")
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual


    def test_spaces_in_list(self):
        # ( 1 , 2 )
        tokens = [
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ")")
        ]

        # (1, 2)
        expected = [
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SYMBOL, ")")
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual


    def test_spaces_around_list(self):
        # ` ( 1 , 2 ) `
        tokens = [
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ")"),
            SFToken(SFTokenKind.SPACES, " "),
        ]

        # (1, 2)
        expected = [
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual


    def test_case_with_newlines(self):
        # case
        #   when foo > 0
        #     then 1
        #   else 0
        # end
        tokens = [
            SFToken(SFTokenKind.WORD, "case"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "when"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ">"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "then"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "1"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "else"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.WORD, "end"),
        ]

        # case when foo > 0 then 1 else 0 end
        expected = [
            SFToken(SFTokenKind.WORD, "case"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "when"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ">"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "0"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "then"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "else"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "0"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "end"),
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual


    def test_indented_join(self):
        # join
        #     bar
        #     on foo.id = bar.foo_id
        #     and bar.active
        tokens = [
            SFToken(SFTokenKind.WORD, "join"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "bar"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "on"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.id"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.foo_id"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.active"),
        ]

        # join bar on foo.id = bar.foo_id and bar.active
        expected = [
            SFToken(SFTokenKind.WORD, "join"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "on"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.id"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.foo_id"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.active"),
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual


    def test_multiline_function_call(self):
        # coalesce(
        #     foo,
        #     bar,
        #     0
        # )
        tokens = [
            SFToken(SFTokenKind.WORD, "coalesce"),
            SFToken(SFTokenKind.SYMBOL, "("),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SYMBOL, ")"),
        ]

        # coalesce(foo, bar, 0)
        expected = [
            SFToken(SFTokenKind.WORD, "coalesce"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "0"),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual


    def test_multiline_function_call_with_crazy_extra_spaces(self):
        # coalesce (
        #     foo ,
        #     bar ,
        #     0
        #  )
        tokens = [
            SFToken(SFTokenKind.WORD, "coalesce"),
            SFToken(SFTokenKind.SYMBOL, "("),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ","),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ","),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ]

        # coalesce(foo, bar, 0)
        expected = [
            SFToken(SFTokenKind.WORD, "coalesce"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "0"),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual


    def test_parenthesized_case_with_newlines_plus_function(self):
        # (
        # case
        #   when foo > 0
        #     then 1
        #   else 0
        # end
        # )
        #  +
        # round ( baz , 2 )
        tokens = [
            SFToken(SFTokenKind.SYMBOL, "("),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.WORD, "case"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "when"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ">"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "then"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "1"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "else"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.WORD, "end"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SYMBOL, ")"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "+"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.WORD, "round"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ]

        # (case when foo > 0 then 1 else 0 end) + round(baz, 2)
        expected = [
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "case"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "when"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ">"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "0"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "then"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "else"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "0"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "end"),
            SFToken(SFTokenKind.SYMBOL, ")"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "+"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "round"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "baz"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual


    def test_function_call_with_space(self):
        # max ( foo )
        tokens = [
            SFToken(SFTokenKind.WORD, "max"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ]

        # max(foo)
        expected = [
            SFToken(SFTokenKind.WORD, "max"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual


    def test_in_list_special_case(self):
        # foo in ( 1 , 2 , 3 )
        tokens = [
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "in"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "3"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ")")
        ]

        # foo in (1, 2, 3)
        expected = [
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "in"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "3"),
            SFToken(SFTokenKind.SYMBOL, ")")
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual
