import pytest

import sf_flags
from sftoken import SFToken
from sftoken import SFTokenKind
from clause_formatter import GroupByClause
from clause_formatter import RenderingContext


# pytest magic
def setup_module():
    sf_flags.reset_to_defaults()


class TestGroupByClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            GroupByClause(tokens=[])

        with pytest.raises(ValueError):
            GroupByClause(tokens=None)


    def test_render_zero_expressions(self):
        clause = GroupByClause(tokens=[SFToken(SFTokenKind.WORD, "group by")])

        expected = " group by"
        actual = clause.render(RenderingContext(indent=0))

        assert expected == actual


    def test_render_single_expression(self):
        # "group by foo"
        clause = GroupByClause(tokens=[
            SFToken(SFTokenKind.WORD, "group by"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
        ])

        expected = (
            " group by foo"
        )
        actual = clause.render(RenderingContext(indent=0))

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
            " group by foo\n"
            "        , bar\n"
            "        , baz"
        )
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual
