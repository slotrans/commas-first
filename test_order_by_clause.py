import pytest

import cf_flags
from cftoken import CFToken
from cftoken import CFTokenKind
from clause_formatter import OrderByClause


# pytest magic
def setup_module():
    cf_flags.reset_to_defaults()


class TestOrderByClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            OrderByClause(tokens=[])

        with pytest.raises(ValueError):
            OrderByClause(tokens=None)


    def test_render_zero_expressions(self):
        clause = OrderByClause(tokens=[CFToken(CFTokenKind.WORD, "order by")])

        expected = " order by"
        actual = clause.render(indent=0)

        assert expected == actual


    def test_render_single_expression(self):
        # "order by foo"
        clause = OrderByClause(tokens=[
            CFToken(CFTokenKind.WORD, "order by"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
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
            CFToken(CFTokenKind.WORD, "order by"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
        ])

        expected = (
            " order by foo\n"
            "        , bar\n"
            "        , baz"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual
