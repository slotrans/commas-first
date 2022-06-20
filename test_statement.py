import pytest

from sftoken import SFToken
from sftoken import SFTokenKind
from sftoken import Symbols
from sftoken import Whitespace
from clause_formatter import ClauseScope
from clause_formatter import Statement


class TestStatement:
    #def test_?_on_empty_input(self):  what should exact behavior be for empty input?

    def test_bare_select(self):
        statement = Statement(tokens=[SFToken(SFTokenKind.WORD, "select")])

        expected = "select"
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_bare_select_indented(self):
        statement = Statement(tokens=[SFToken(SFTokenKind.WORD, "select")])

        # remember the first line is not indented, so the indent has no effect here
        expected = "select"
        actual = statement.render(indent=4)

        print(actual)
        assert expected == actual


    def test_select_1(self):
        statement = Statement(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
        ])

        expected = "select 1"
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_only_simple(self):
        # select foo, bar, baz
        statement = Statement(tokens=[
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
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual


    def test_select_only_simple_indented(self):
        # select foo, bar, baz
        statement = Statement(tokens=[
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
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "table1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "join"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "table2"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "on"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "table1.id"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "table2.table1_id"),
            SFToken(SFTokenKind.SYMBOL, ")"),
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
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "table1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ">"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
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
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "table1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, ">"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
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
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "count"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, ")"),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "table1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "group by"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
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
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "table1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "order by"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
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
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "table1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "order by"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "limit"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "9"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "offset"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "0"),
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
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "foo"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "where"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "1"),
                SFToken(SFTokenKind.SYMBOL, "="),
                SFToken(SFTokenKind.WORD, "1"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "from"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "table1"),
            ])


    def test_inline_view(self):
        #select x.foo
        #  from (select foo
        #          from bar
        #         where 1=1
        #       ) x
        # where 1=1
        statement = Statement(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "x.foo"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "          "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "         "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "       "),
            SFToken(SFTokenKind.SYMBOL, ")"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
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
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "     "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "          "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "         "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "       "),
            Symbols.RIGHT_PAREN,
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "as"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "SCALAR_SUBQUERY"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
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
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "     "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "id"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "in"),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar_id"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "                "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "               "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "             "),
            Symbols.RIGHT_PAREN,
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "as"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "INLIST_SUBQUERY"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
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


    def test_subquery_in_where(self):
        #select foo
        #  from bar
        # where 1=1
        #   and id in (select bar_id
        #                from bar_baz_map
        #               where 1=1
        #             )
        statement = Statement(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "id"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "in"),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar_id"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "                "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar_baz_map"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "               "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "             "),
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


    def test_select_union_all(self):
        # select foo from table1 union all select foo from table2
        statement = Statement(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "table1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "union all"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "table2"),
        ])

        expected = (
            "select foo\n"
            "  from table1\n"
            "union all\n"
            "select foo\n"
            "  from table2\n"
        )
        actual = statement.render(indent=0)

        print(actual)
        assert expected == actual
