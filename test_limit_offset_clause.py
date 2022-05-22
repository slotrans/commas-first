import pytest

from sftoken import SFToken
from sftoken import SFTokenKind
from clause_formatter import LimitOffsetClause


class TestLimitOffsetClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            LimitOffsetClause(tokens=[])

        with pytest.raises(ValueError):
            LimitOffsetClause(tokens=None)


    def test_render_limit_zero_expressions(self):
        clause = LimitOffsetClause(tokens=[SFToken(SFTokenKind.WORD, "limit")])

        expected = " limit"
        actual = clause.render()

        assert expected == actual


    def test_render_offset_zero_expressions(self):
        clause = LimitOffsetClause(tokens=[SFToken(SFTokenKind.WORD, "offset")])

        expected = "offset"
        actual = clause.render()

        assert expected == actual


    def test_render_limit_with_number(self):
        clause = LimitOffsetClause(tokens=[
            SFToken(SFTokenKind.WORD, "limit"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "5"),
        ])

        expected = " limit 5"
        actual = clause.render()

        assert expected == actual


    def test_render_offset_with_number(self):
        clause = LimitOffsetClause(tokens=[
            SFToken(SFTokenKind.WORD, "offset"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "5"),
        ])

        expected = "offset 5"
        actual = clause.render()

        assert expected == actual


    def test_render_limit_offset_with_numbers(self):
        clause = LimitOffsetClause(tokens=[
            SFToken(SFTokenKind.WORD, "limit"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "offset"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
        ])

        expected = (
            " limit 1\n"
            "offset 2"
        )
        actual = clause.render()

        assert expected == actual


    def test_render_offset_limit_with_numbers(self):
        clause = LimitOffsetClause(tokens=[
            SFToken(SFTokenKind.WORD, "offset"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "limit"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
        ])

        expected = (
            "offset 2\n"
            " limit 1"
        )
        actual = clause.render()

        assert expected == actual


    def test_render_limit_offset_with_extra_garbage(self):
        # limit foo bar baz offset 2 + 3
        clause = LimitOffsetClause(tokens=[
            SFToken(SFTokenKind.WORD, "limit"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "offset"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "+"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "3"),
        ])

        expected = (
            " limit foo bar baz\n"
            "offset 2 + 3"
        )
        actual = clause.render()

        assert expected == actual
