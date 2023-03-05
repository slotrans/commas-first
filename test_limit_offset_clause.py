import pytest

import cf_flags
from cftoken import CFToken
from cftoken import CFTokenKind
from clause_formatter import LimitOffsetClause


# pytest magic
def setup_module():
    cf_flags.reset_to_defaults()


class TestLimitOffsetClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            LimitOffsetClause(tokens=[])

        with pytest.raises(ValueError):
            LimitOffsetClause(tokens=None)


    def test_render_limit_zero_expressions(self):
        clause = LimitOffsetClause(tokens=[CFToken(CFTokenKind.WORD, "limit")])

        expected = " limit"
        actual = clause.render(indent=0)

        assert expected == actual


    def test_render_offset_zero_expressions(self):
        clause = LimitOffsetClause(tokens=[CFToken(CFTokenKind.WORD, "offset")])

        expected = "offset"
        actual = clause.render(indent=0)

        assert expected == actual


    def test_render_limit_with_number(self):
        clause = LimitOffsetClause(tokens=[
            CFToken(CFTokenKind.WORD, "limit"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "5"),
        ])

        expected = " limit 5"
        actual = clause.render(indent=0)

        assert expected == actual


    def test_render_offset_with_number(self):
        clause = LimitOffsetClause(tokens=[
            CFToken(CFTokenKind.WORD, "offset"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "5"),
        ])

        expected = "offset 5"
        actual = clause.render(indent=0)

        assert expected == actual


    def test_render_limit_offset_with_numbers(self):
        clause = LimitOffsetClause(tokens=[
            CFToken(CFTokenKind.WORD, "limit"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "offset"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
        ])

        expected = (
            " limit 1\n"
            "offset 2"
        )
        actual = clause.render(indent=0)

        assert expected == actual


    def test_render_offset_limit_with_numbers(self):
        clause = LimitOffsetClause(tokens=[
            CFToken(CFTokenKind.WORD, "offset"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "limit"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
        ])

        expected = (
            "offset 2\n"
            " limit 1"
        )
        actual = clause.render(indent=0)

        assert expected == actual


    def test_render_limit_offset_with_extra_garbage(self):
        # limit foo bar baz offset 2 + 3
        clause = LimitOffsetClause(tokens=[
            CFToken(CFTokenKind.WORD, "limit"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "offset"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "+"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "3"),
        ])

        expected = (
            " limit foo bar baz\n"
            "offset 2 + 3"
        )
        actual = clause.render(indent=0)

        assert expected == actual


    def test_render_limit_offset_with_trailing_line_comments(self):
        # limit 1 --one
        #offset 2 --two
        clause = LimitOffsetClause(tokens=[
            CFToken(CFTokenKind.WORD, "limit"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.LINE_COMMENT, "--one\n"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "offset"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.LINE_COMMENT, "--two\n"),
        ])

        expected = (
            " limit 1 --one\n"
            "offset 2 --two"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_limit_offset_with_trailing_block_comments(self):
        # limit 1 /* one */
        #offset 2 /* two */
        clause = LimitOffsetClause(tokens=[
            CFToken(CFTokenKind.WORD, "limit"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.BLOCK_COMMENT, "/* one */"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "offset"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.BLOCK_COMMENT, "/* two */"),
        ])

        expected = (
            " limit 1 /* one */\n"
            "offset 2 /* two */"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual    