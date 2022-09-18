import pytest

import sf_flags
from sftoken import SFToken
from sftoken import SFTokenKind
from clause_formatter import OrderByClause


# pytest magic
def setup_module():
    sf_flags.reset_to_defaults()


class TestOrderByClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            OrderByClause(tokens=[])

        with pytest.raises(ValueError):
            OrderByClause(tokens=None)


    def test_render_zero_expressions(self):
        clause = OrderByClause(tokens=[SFToken(SFTokenKind.WORD, "order by")])

        expected = " order by"
        actual = clause.render(indent=0)

        assert expected == actual


    def test_render_single_expression(self):
        # "order by foo"
        clause = OrderByClause(tokens=[
            SFToken(SFTokenKind.WORD, "order by"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
        ])

        expected = (
            " order by foo"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_simple_expressions(self):
        # "order by foo, bar, baz"
        clause = OrderByClause(tokens=[
            SFToken(SFTokenKind.WORD, "order by"),
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
            " order by foo\n"
            "        , bar\n"
            "        , baz"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual
