import textwrap

import pytest

from sftoken import SFToken, SFTokenKind
from clause_formatter import SelectClause


class TestSelectClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            SelectClause(tokens=[])

        with pytest.raises(ValueError):
            SelectClause(tokens=None)


    def test_render_zero_expressions(self):
        clause = SelectClause(tokens=[SFToken(SFTokenKind.WORD, "select")])

        expected = "select\n"
        actual = clause.render()

        assert expected == actual


    def test_render_simple_expressions_no_qualifier(self):
        # "select foo, bar, baz"
        clause = SelectClause(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
        ])

        expected = textwrap.dedent("""\
            select foo
                 , bar
                 , baz""")
        actual = clause.render()

        print(actual)
        assert expected == actual


    def test_render_simple_expressions_distinct_qualifier(self):
        # "select distinct foo, bar, baz"
        clause = SelectClause(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "distinct"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
        ])

        expected = textwrap.dedent("""\
            select distinct
                   foo
                 , bar
                 , baz""")
        actual = clause.render()

        print(actual)
        assert expected == actual


    def test_render_simple_expressions_distinct_on_qualifier(self):
        # "select distinct on(foo) foo, bar, baz"
        clause = SelectClause(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "distinct"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "on"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ")"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
        ])

        expected = textwrap.dedent("""\
            select distinct on(foo)
                   foo
                 , bar
                 , baz""")
        actual = clause.render()

        print(actual)
        assert expected == actual


    def test_render_qualifier_only(self):
        # "select distinct"
        clause = SelectClause(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "distinct"),
        ])

        expected = "select distinct\n"
        actual = clause.render()

        assert expected == actual
