import pytest

import cf_flags
from cftoken import CFToken
from cftoken import CFTokenKind
from cftoken import Symbols
from cftoken import Whitespace
from clause_formatter import ClauseScope
from clause_formatter import Statement
from clause_formatter import CompoundStatement


# pytest magic
def setup_module():
    cf_flags.reset_to_defaults()


class TestStatement:
    #def test_?_on_empty_input(self):  what should exact behavior be for empty input?

    def test_bare_select(self):
        statement = Statement(tokens=[CFToken(CFTokenKind.WORD, "select")])

        expected = "select"
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_bare_select_indented(self):
        statement = Statement(tokens=[CFToken(CFTokenKind.WORD, "select")])

        # remember the first line is not indented, so the indent has no effect here
        expected = "select"
        actual = statement.render(indent=4)

        print(actual)
        assert expected == actual


    def test_select_1(self):
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
        ])

        expected = "select 1"
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_only_simple(self):
        # select foo, bar, baz
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
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
            "select foo\n"
            "     , bar\n"
            "     , baz"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_only_simple_indented(self):
        # select foo, bar, baz
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
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
            ####
                "select foo\n"
            "         , bar\n"
            "         , baz"
        )
        actual = statement.render(indent=4)

        print(actual)
        assert expected == actual


    def test_select_from_simple(self):
        # select foo, bar, baz from table1 join table2 on(table1.id = table2.table1_id)
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "table1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "table2"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "table1.id"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "table2.table1_id"),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            "select foo\n"
            "     , bar\n"
            "     , baz\n"
            "  from table1\n"
            "  join table2 on(table1.id = table2.table1_id)"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_from_where_simple(self):
        # select foo from table1 where 1=1 and bar > baz
        statement = Statement(tokens=[
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
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ">"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
        ])

        expected = (
            "select foo\n"
            "  from table1\n"
            " where 1=1\n"
            "   and bar > baz"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_from_where_simple_indented(self):
        # select foo from table1 where 1=1 and bar > baz
        statement = Statement(tokens=[
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
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ">"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
        ])

        expected = (
            ####
                "select foo\n"
            "      from table1\n"
            "     where 1=1\n"
            "       and bar > baz"
        )
        actual = statement.render(indent=4)

        print(actual)
        assert expected == actual


    def test_select_from_where_group_by_simple(self):
        # select foo, count(1) from table1 where 1=1 group by foo
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "count"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, ")"),
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
            CFToken(CFTokenKind.WORD, "group by"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
        ])

        expected = (
            "select foo\n"
            "     , count(1)\n"
            "  from table1\n"
            " where 1=1\n"
            " group by foo"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_from_where_order_by_simple(self):
        # select foo from table1 where 1=1 order by foo
        statement = Statement(tokens=[
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
            CFToken(CFTokenKind.WORD, "order by"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
        ])

        expected = (
            "select foo\n"
            "  from table1\n"
            " where 1=1\n"
            " order by foo"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_from_where_order_by_limit_offset_simple(self):
        # select foo from table1 where 1=1 order by foo limit 9 offset 0
        statement = Statement(tokens=[
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
            CFToken(CFTokenKind.WORD, "order by"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "limit"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "9"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "offset"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
        ])

        expected = (
            "select foo\n"
            "  from table1\n"
            " where 1=1\n"
            " order by foo\n"
            " limit 9\n"
            "offset 0"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_where_from_raises_error(self):
        with pytest.raises(ValueError):
            # select foo where 1=1 from table1
            statement = Statement(tokens=[
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "foo"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "table1"),
            ])


    def test_inline_view(self):
        #select x.foo
        #  from (select foo
        #          from bar
        #         where 1=1
        #       ) x
        # where 1=1
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "x.foo"),
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "foo"),
                CFToken(CFTokenKind.NEWLINE, "\n"),
                CFToken(CFTokenKind.SPACES, "          "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "bar"),
                CFToken(CFTokenKind.NEWLINE, "\n"),
                CFToken(CFTokenKind.SPACES, "         "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
        ])

        expected = (
            "select x.foo\n"
            "  from (select foo\n"
            "          from bar\n"
            "         where 1=1\n"
            "       ) x\n"
            " where 1=1"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_scalar_subquery(self):
        #select foo
        #     , (select 1
        #          from baz
        #         where 1=1
        #       ) as SCALAR_SUBQUERY
        #  from bar
        # where 1=1
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "     "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "          "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "baz"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "         "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "SCALAR_SUBQUERY"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
        ])

        expected = (
            "select foo\n"
            "     , (select 1\n"
            "          from baz\n"
            "         where 1=1\n"
            "       ) as SCALAR_SUBQUERY\n"
            "  from bar\n"
            " where 1=1"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_inlist_subquery(self):
        #select foo
        #     , id in (select bar_id
        #                from baz
        #               where 1=1
        #             ) as INLIST_SUBQUERY
        #  from bar
        # where 1=1
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "     "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "id"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "in"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "bar_id"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "                "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "baz"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "               "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "INLIST_SUBQUERY"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
        ])

        expected = (
            "select foo\n"
            "     , id in (select bar_id\n"
            "                from baz\n"
            "               where 1=1\n"
            "             ) as INLIST_SUBQUERY\n"
            "  from bar\n"
            " where 1=1"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_inlist_subquery_with_qualifier(self):
        #select foo
        #     , id in (select distinct
        #                     bar_id
        #                from baz
        #               where 1=1
        #             ) as INLIST_SUBQUERY
        #  from bar
        # where 1=1
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "     "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "id"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "in"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "distinct"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "                     "),
                CFToken(CFTokenKind.WORD, "bar_id"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "                "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "baz"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "               "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "INLIST_SUBQUERY"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
        ])

        expected = (
            "select foo\n"
            "     , id in (select distinct\n"
            "                     bar_id\n"
            "                from baz\n"
            "               where 1=1\n"
            "             ) as INLIST_SUBQUERY\n"
            "  from bar\n"
            " where 1=1"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_subquery_in_where(self):
        #select foo
        #  from bar
        # where 1=1
        #   and id in (select bar_id
        #                from bar_baz_map
        #               where 1=1
        #             )
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "id"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "in"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "bar_id"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "                "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "bar_baz_map"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "               "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "select foo\n"
            "  from bar\n"
            " where 1=1\n"
            "   and id in (select bar_id\n"
            "                from bar_baz_map\n"
            "               where 1=1\n"
            "             )"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_subquery_with_qualifier_in_where(self):
        #select foo
        #  from bar
        # where 1=1
        #   and id in (select distinct
        #                     bar_id
        #                from bar_baz_map
        #               where 1=1
        #             )
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "id"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "in"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "distinct"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "                     "),
                CFToken(CFTokenKind.WORD, "bar_id"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "                "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "bar_baz_map"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "               "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "select foo\n"
            "  from bar\n"
            " where 1=1\n"
            "   and id in (select distinct\n"
            "                     bar_id\n"
            "                from bar_baz_map\n"
            "               where 1=1\n"
            "             )"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_window_function_in_select(self):
        # "order by" appears inside a function call here, should not trigger a new scope

        #select foo
        #     , lead(foo, 1) over(order by event_datetime) as NEXT_FOO
        #  from bar
        # where 1=1
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "     "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "lead"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, ")"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "over"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "order by"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "event_datetime"),
            CFToken(CFTokenKind.SYMBOL, ")"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "NEXT_FOO"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
        ])

        expected = (
            "select foo\n"
            "     , lead(foo, 1) over(order by event_datetime) as NEXT_FOO\n"
            "  from bar\n"
            " where 1=1"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_substring_and_extract_in_where(self):
        # "from" appears inside function calls here, should not trigger a new scope

        #select 1
        #  from bar
        # where 1=1
        #   and substring(foo from 2 for 3) != 'xxx'
        #   and extract('year' from event_datetime) > 2000
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "substring"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "for"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "3"),
            CFToken(CFTokenKind.SYMBOL, ")"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "!="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.LITERAL, "'xxx'"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "extract"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.LITERAL, "'year'"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "event_datetime"),
            CFToken(CFTokenKind.SYMBOL, ")"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ">"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2000"),
        ])

        expected = (
            "select 1\n"
            "  from bar\n"
            " where 1=1\n"
            "   and substring(foo from 2 for 3) != 'xxx'\n"
            "   and extract('year' from event_datetime) > 2000"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_single_cte(self):
        # with cte1 as (select 1) select foo from table1
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "with"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "cte1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "table1"),
        ])

        expected = (
            "with cte1 as\n"
            "(\n"
            "    select 1\n"
            ")\n"
            "select foo\n"
            "  from table1"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_two_ctes(self):
        # with cte1 as (select 1), cte2 as (select 2) select foo from table1
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "with"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "cte1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            Symbols.COMMA,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "cte2"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "2"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "table1"),
        ])

        expected = (
            "with cte1 as\n"
            "(\n"
            "    select 1\n"
            ")\n"
            ", cte2 as\n"
            "(\n"
            "    select 2\n"
            ")\n"
            "select foo\n"
            "  from table1"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_nested_cte(self):
        # with cte1 as (with cte2 as (select 1)) select foo from table1
        statement = Statement(tokens=[
            CFToken(CFTokenKind.WORD, "with"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "cte1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "with"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "cte2"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "as"),
                Symbols.LEFT_PAREN,
                CompoundStatement([
                    CFToken(CFTokenKind.WORD, "select"),
                    CFToken(CFTokenKind.SPACES, " "),
                    CFToken(CFTokenKind.WORD, "1"),
                ]),
                Symbols.RIGHT_PAREN,
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "table1"),
        ])

        expected = (
            "with cte1 as\n"
            "(\n"
            "    with cte2 as\n"
            "    (\n"
            "        select 1\n"
            "    )\n"
            ")\n"
            "select foo\n"
            "  from table1"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_block_comment_before_select(self):
        # /* hey */ select foo, bar, baz
        statement = Statement(tokens=[
            CFToken(CFTokenKind.BLOCK_COMMENT, "/* hey */"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "select"),
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
            "/* hey */ \n" # preserving this space isn't ideal...
            "select foo\n"
            "     , bar\n"
            "     , baz"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_line_comment_before_select(self):
        # --hey
        # select foo, bar, baz
        statement = Statement(tokens=[
            CFToken(CFTokenKind.LINE_COMMENT, "--hey\n"),
            CFToken(CFTokenKind.WORD, "select"),
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
            "--hey\n"
            "select foo\n"
            "     , bar\n"
            "     , baz"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual
