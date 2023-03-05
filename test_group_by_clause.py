import pytest

import cf_flags
from cftoken import CFToken
from cftoken import CFTokenKind
from clause_formatter import GroupByClause


# pytest magic
def setup_module():
    cf_flags.reset_to_defaults()


class TestGroupByClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            GroupByClause(tokens=[])

        with pytest.raises(ValueError):
            GroupByClause(tokens=None)


    def test_render_zero_expressions(self):
        clause = GroupByClause(tokens=[CFToken(CFTokenKind.WORD, "group by")])

        expected = " group by"
        actual = clause.render(indent=0)

        assert expected == actual


    def test_render_single_expression(self):
        # "group by foo"
        clause = GroupByClause(tokens=[
            CFToken(CFTokenKind.WORD, "group by"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
        ])

        expected = (
            " group by foo"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_simple_expressions(self):
        # "group by foo, bar, baz"
        clause = GroupByClause(tokens=[
            CFToken(CFTokenKind.WORD, "group by"),
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
            " group by foo\n"
            "        , bar\n"
            "        , baz"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual
