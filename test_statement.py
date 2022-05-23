import pytest

from sftoken import SFToken
from sftoken import SFTokenKind
from clause_formatter import ClauseScope
from clause_formatter import Statement


class TestStatement:
    #def test_?_on_empty_input(self):  what should exact behavior be for empty input?

    def test_bare_select(self):
        statement = Statement(tokens=[SFToken(SFTokenKind.WORD, "select")])

        expected = "select"
        actual = statement.render()

        print(actual)
        assert expected == actual


    def test_select_1(self):
        statement = Statement(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "1"),
        ])

        expected = "select 1"
        actual = statement.render()

        print(actual)
        assert expected == actual


    def test_select_only_simple(self):
        # select  foo,  bar,  baz
        statement = Statement(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "baz"),
        ])

        expected = (
            "select foo\n"
            "     , bar\n"
            "     , baz"
        )
        actual = statement.render()

        print(actual)
        assert expected == actual


    def test_select_from_simple(self):
        # select  foo,  bar,  baz  from  table1  join  table2  on(table1.id = table2.table1_id)
        statement = Statement(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "baz"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "table1"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "join"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "table2"),
            SFToken(SFTokenKind.SPACES, "  "),
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
        actual = statement.render()

        print(actual)
        assert expected == actual


    def test_select_from_where_simple(self):
        # select  foo  from  table1  where 1=1  and  bar > baz
        statement = Statement(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "table1"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, "  "),
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
        actual = statement.render()

        print(actual)
        assert expected == actual


    def test_select_from_where_group_by_simple(self):
        # select  foo,  count(1)  from  table1  where 1=1  group by  foo
        statement = Statement(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "count"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, ")"),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "table1"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "group by"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "foo"),
        ])

        expected = (
            "select foo\n"
            "     , count(1)\n"
            "  from table1\n"
            " where 1=1\n"
            " group by foo"
        )
        actual = statement.render()

        print(actual)
        assert expected == actual


    def test_select_from_where_order_by_simple(self):
        # select  foo  from  table1  where 1=1  order by  foo
        statement = Statement(tokens=[
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "table1"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "order by"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "foo"),
        ])

        expected = (
            "select foo\n"
            "  from table1\n"
            " where 1=1\n"
            " order by foo"
        )
        actual = statement.render()

        print(actual)
        assert expected == actual


    def test_select_where_from_raises_error(self):
        with pytest.raises(ValueError):
            # select  foo  where 1=1  from table1
            statement = Statement(tokens=[
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, "  "),
                SFToken(SFTokenKind.WORD, "foo"),
                SFToken(SFTokenKind.SPACES, "  "),
                SFToken(SFTokenKind.WORD, "where"),
                SFToken(SFTokenKind.WORD, "1"),
                SFToken(SFTokenKind.SYMBOL, "="),
                SFToken(SFTokenKind.WORD, "1"),
                SFToken(SFTokenKind.SPACES, "  "),
                SFToken(SFTokenKind.WORD, "from"),
                SFToken(SFTokenKind.SPACES, "  "),
                SFToken(SFTokenKind.WORD, "table1"),
            ])

