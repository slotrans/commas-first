import pytest

import cf_flags
from cftoken import CFToken
from cftoken import CFTokenKind
from cftoken import Symbols
from cftoken import Whitespace
from clause_formatter import CompoundStatement


# pytest magic
def setup_module():
    cf_flags.reset_to_defaults()


class TestCompoundStatement:
    #def test_?_on_empty_input(self):  what should exact behavior be for empty input?

    def test_bare_select(self):
        # select 1
        statement = CompoundStatement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
        ])

        expected = (
            "select 1"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_union_all(self):
        # select 1 union all select 2
        statement = CompoundStatement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "union all"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
        ])

        expected = (
            "select 1\n"
            "union all\n"
            "select 2"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_except(self):
        # select 1 except select 2
        statement = CompoundStatement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "except"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
        ])

        expected = (
            "select 1\n"
            "except\n"
            "select 2"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_intersect(self):
        # select 1 union all select 2
        statement = CompoundStatement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "intersect"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
        ])

        expected = (
            "select 1\n"
            "intersect\n"
            "select 2"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_from_where_union_all(self):
        # select foo from table1 where 1=1 union all select foo from table2 where 1=1
        statement = CompoundStatement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "table1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "union all"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "table2"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
        ])

        expected = (
            "select foo\n"
            "  from table1\n"
            " where 1=1\n"
            "union all\n"
            "select foo\n"
            "  from table2\n"
            " where 1=1"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_basic_cte(self):
        # with foo as (select 1) select 2
        statement = CompoundStatement(tokens=[
            CFToken(CFTokenKind.WORD, "with"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
        ])

        expected = (
            "with foo as\n"
            "(\n"
            "    select 1\n"
            ")\n"
            "select 2"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_cte_with_set_op(self):
        # with foo as (select 1 union select 2) select 3
        statement = CompoundStatement(tokens=[
            CFToken(CFTokenKind.WORD, "with"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "union"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "3"),
        ])

        expected = (
            "with foo as\n"
            "(\n"
            "    select 1\n"
            "    union\n"
            "    select 2\n"
            ")\n"
            "select 3"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    @pytest.mark.skip("this is valid but rare, I don't know how it should be laid out...")
    def test_parenthesized_queries_with_set_op(self):
        # (select foo from table1) union (select foo from table2)
        statement = CompoundStatement(tokens=[
            Symbols.LEFT_PAREN,
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "table1"),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "union"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "table2"),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            # this is what we produce, but I dunno if it's desirable enough to enshrine in a test...
            "(select foo\n"
            "from table1)\n"
            "union\n"
            "(select foo\n"
            "  from table2)\n"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual
