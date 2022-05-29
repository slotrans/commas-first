import pytest

from sftoken import SFToken
from sftoken import SFTokenKind
from clause_formatter import GroupByClause


class TestGroupByClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            GroupByClause(tokens=[])

        with pytest.raises(ValueError):
            GroupByClause(tokens=None)


    def test_render_zero_expressions(self):
        clause = GroupByClause(tokens=[SFToken(SFTokenKind.WORD, "group by")])

        expected = "group by"
        actual = clause.render()

        assert expected == actual


    def test_render_single_expression(self):
        # "group by foo"
        clause = GroupByClause(tokens=[
            SFToken(SFTokenKind.WORD, "group by"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
        ])

        expected = (
            "group by foo"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual 


    def test_render_simple_expressions(self):
        # "group by foo, bar, baz"
        clause = GroupByClause(tokens=[
            SFToken(SFTokenKind.WORD, "group by"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
        ])

        expected = (
            "group by foo\n"
            "       , bar\n"
            "       , baz"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual    