import pytest

from sftoken import SFToken
from sftoken import SFTokenKind
from clause_formatter import SelectClause


class TestSelectClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            SelectClause(tokens=[])

        with pytest.raises(ValueError):
            SelectClause(tokens=None)


    def test_render_zero_expressions(self):
        clause = SelectClause(tokens=[SFToken(SFTokenKind.WORD, "select")])

        expected = "select"
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

        expected = (
            "select foo\n"
            "     , bar\n"
            "     , baz"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual


    def test_render_simple_expressions_crappy_indentation(self):
        #select
        #    foo,
        #    bar,
        #    baz
        clause = SelectClause(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "baz"),
        ])

        expected = (
            "select foo\n"
            "     , bar\n"
            "     , baz"
        )
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

        expected = (
            "select distinct\n"
            "       foo\n"
            "     , bar\n"
            "     , baz"
        )
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

        expected = (
            "select distinct on(foo)\n"
            "       foo\n"
            "     , bar\n"
            "     , baz"
        )
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


    def test_custom_spacing(self):
        #select foo
        #     ,   l7
        #     ,  l30
        #     , l182
        clause = SelectClause(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "     "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "l7"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "     "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "l30"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "     "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "l182"),
        ])

        expected = (
            "select foo\n"
            "     ,   l7\n"
            "     ,  l30\n"
            "     , l182"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual


    def test_multiple_expressions_per_line(self):
        #select
        #    foo, bar,
        #    l7, l28, l91,
        #    stuff
        clause = SelectClause(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),            
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "l7"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "l28"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "l91"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "stuff"),
        ])

        expected = (
            "select foo\n"
            "     , bar\n"
            "     , l7\n"
            "     , l28\n"
            "     , l91\n"
            "     , stuff"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual
