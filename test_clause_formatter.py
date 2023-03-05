import pytest

import cf_flags
from cftoken import (
    CFToken,
    CFTokenKind,
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
    cf_flags.reset_to_defaults()


class TestTrimTrailingWhitespace:
    def test_empty(self):
        expected = []
        actual = trim_trailing_whitespace([])
        assert expected == actual


    def test_no_whitespace(self):
        tokens = [
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "y"),
        ]

        expected = tokens
        actual = trim_trailing_whitespace(tokens)

        assert expected == actual


    def test_one_spaces_token(self):
        tokens = [
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "y"),
            CFToken(CFTokenKind.SPACES, " "),
        ]

        expected = tokens[0:3]
        actual = trim_trailing_whitespace(tokens)

        assert expected == actual


    def test_one_newline_token(self):
        tokens = [
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "y"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
        ]

        expected = tokens[0:3]
        actual = trim_trailing_whitespace(tokens)

        assert expected == actual


    def test_multiple(self):
        tokens = [
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "y"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.NEWLINE, "\n"),
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
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "y"),
        ]

        expected = tokens
        actual = trim_leading_whitespace(tokens)

        assert expected == actual


    def test_one_spaces_token(self):
        tokens = [
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "y"),
        ]

        expected = tokens[1:]
        actual = trim_leading_whitespace(tokens)

        assert expected == actual


    def test_one_newline_token(self):
        tokens = [
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "y"),
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
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "y"),
        ]

        expected = tokens
        actual = trim_one_leading_space(tokens)

        assert expected == actual


    def test_one_spaces_token(self):
        tokens = [
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "y"),
        ]

        expected = tokens[1:]
        actual = trim_one_leading_space(tokens)

        assert expected == actual


    def test_many_spaces_token(self):
        for i in range(2, 10): # enough examples to prove the point
            token_with_i_spaces = CFToken(CFTokenKind.SPACES, " "*i)
            tokens = [
                token_with_i_spaces,
                CFToken(CFTokenKind.WORD, "x"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "y"),
            ]

            one_space_shorter = CFToken(CFTokenKind.SPACES, " "*(i-1))
            expected = [one_space_shorter] + tokens[1:]
            actual = trim_one_leading_space(tokens)

            assert expected == actual


    def test_one_newline_token(self):
        tokens = [
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "y"),
        ]

        expected = tokens
        actual = trim_one_leading_space(tokens)

        assert expected == actual


    def test_mixed_whitespace_starting_with_newline(self):
        tokens = [
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "y"),
        ]

        expected = tokens
        actual = trim_one_leading_space(tokens)

        assert expected == actual


    def test_mixed_whitespace_starting_with_one_space(self):
        tokens = [
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "y"),
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
            get_paren_block([CFToken(CFTokenKind.WORD, "foo")])


    def test_incomplete_block(self):
        tokens = [
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
        ]

        actual = get_paren_block(tokens)

        assert actual is None


    def test_select_block(self):
        # (select foo from bar) extra tokens
        tokens = [
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SYMBOL, ")"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "extra"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "tokens"),
        ]

        expected = tokens[0:9]
        actual = get_paren_block(tokens)

        assert expected == actual


    def test_select_block_with_function_call(self):
        # (select coalesce(foo, -1) from bar) extra tokens
        tokens = [
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "coalesce"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "-1"),
            CFToken(CFTokenKind.SYMBOL, ")"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SYMBOL, ")"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "extra"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "tokens"),
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
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "b"),
        ]

        expected = [
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_only_spaces(self):
        tokens = [
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "b"),
        ]

        expected = [
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_only_newline(self):
        tokens = [
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.WORD, "b"),
        ]

        expected = [
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_spaces_then_newline(self):
        tokens = [
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.WORD, "b"),
        ]

        expected = [
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_newline_then_spaces(self):
        tokens = [
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "b"),
        ]

        expected = [
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_spaces_around_newline(self):
        tokens = [
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "b"),
        ]

        expected = [
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_newlines_around_spaces(self):
        tokens = [
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.WORD, "b"),
        ]

        expected = [
            CFToken(CFTokenKind.WORD, "a"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "b"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_left_paren_then_space(self):
        tokens = [
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.SPACES, " "),
        ]

        expected = [
            CFToken(CFTokenKind.SYMBOL, "("),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_space_then_right_paren(self):
        tokens = [
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ]

        expected = [
            CFToken(CFTokenKind.SYMBOL, ")"),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    def test_space_then_comma(self):
        tokens = [
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ","),
        ]

        expected = [
            CFToken(CFTokenKind.SYMBOL, ","),
        ]
        actual = make_compact(tokens)
        assert expected == actual


    # this isn't great, but make_compact() is about removing whitespace, not adding it...
    def test_packed_list(self):
        # (1,2,3)
        tokens = [
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.WORD, "3"),
            CFToken(CFTokenKind.SYMBOL, ")")
        ]

        # (1,2,3)
        expected = [
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.WORD, "3"),
            CFToken(CFTokenKind.SYMBOL, ")")
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual


    def test_spaces_in_list(self):
        # ( 1 , 2 )
        tokens = [
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ")")
        ]

        # (1, 2)
        expected = [
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SYMBOL, ")")
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual


    def test_spaces_around_list(self):
        # ` ( 1 , 2 ) `
        tokens = [
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ")"),
            CFToken(CFTokenKind.SPACES, " "),
        ]

        # (1, 2)
        expected = [
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SYMBOL, ")"),
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
            CFToken(CFTokenKind.WORD, "case"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "when"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ">"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "then"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "1"),
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "else"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.WORD, "end"),
        ]

        # case when foo > 0 then 1 else 0 end
        expected = [
            CFToken(CFTokenKind.WORD, "case"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "when"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ">"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "then"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "else"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "end"),
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
            CFToken(CFTokenKind.WORD, "join"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "bar"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "on"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.id"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.foo_id"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.active"),
        ]

        # join bar on foo.id = bar.foo_id and bar.active
        expected = [
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.id"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.foo_id"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.active"),
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
            CFToken(CFTokenKind.WORD, "coalesce"),
            CFToken(CFTokenKind.SYMBOL, "("),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SYMBOL, ","),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SYMBOL, ","),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SYMBOL, ")"),
        ]

        # coalesce(foo, bar, 0)
        expected = [
            CFToken(CFTokenKind.WORD, "coalesce"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            CFToken(CFTokenKind.SYMBOL, ")"),
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
            CFToken(CFTokenKind.WORD, "coalesce"),
            CFToken(CFTokenKind.SYMBOL, "("),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ","),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ","),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ]

        # coalesce(foo, bar, 0)
        expected = [
            CFToken(CFTokenKind.WORD, "coalesce"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            CFToken(CFTokenKind.SYMBOL, ")"),
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
            CFToken(CFTokenKind.SYMBOL, "("),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.WORD, "case"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "when"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ">"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "then"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "1"),
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "else"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.WORD, "end"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SYMBOL, ")"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "+"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.WORD, "round"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ]

        # (case when foo > 0 then 1 else 0 end) + round(baz, 2)
        expected = [
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "case"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "when"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ">"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "then"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "else"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "end"),
            CFToken(CFTokenKind.SYMBOL, ")"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "+"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "round"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "baz"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual


    def test_function_call_with_space(self):
        # max ( foo )
        tokens = [
            CFToken(CFTokenKind.WORD, "max"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ]

        # max(foo)
        expected = [
            CFToken(CFTokenKind.WORD, "max"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual


    def test_in_list_special_case(self):
        # foo in ( 1 , 2 , 3 )
        tokens = [
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "in"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "3"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ")")
        ]

        # foo in (1, 2, 3)
        expected = [
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "in"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "3"),
            CFToken(CFTokenKind.SYMBOL, ")")
        ]
        actual = make_compact(tokens)
        for t in actual:
            print(t)
        assert expected == actual
