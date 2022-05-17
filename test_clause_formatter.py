import pytest

from sftoken import SFToken
from sftoken import SFTokenKind
from clause_formatter import trim_trailing_whitespace
from clause_formatter import SelectClause
from clause_formatter import FromClause
from clause_formatter import WhereClause
from clause_formatter import GroupByClause
from clause_formatter import OrderByClause
from clause_formatter import LimitOffsetClause


class TestTrimTrailingWhitespace:
    def test_empty(self):
        expected = []
        actual = trim_trailing_whitespace([])
        assert expected == actual


    def test_no_whitespace(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
        ]

        expected = tokens
        actual = trim_trailing_whitespace(tokens)

        assert expected == actual


    def test_one_spaces_token(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
            SFToken(SFTokenKind.SPACES, " "),
        ]

        expected = tokens[0:3]
        actual = trim_trailing_whitespace(tokens)

        assert expected == actual


    def test_one_newline_token(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
        ]

        expected = tokens[0:3]
        actual = trim_trailing_whitespace(tokens)

        assert expected == actual


    def test_multiple(self):
        tokens = [
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "y"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.NEWLINE, "\n"),
        ]

        expected = tokens[0:3]
        actual = trim_trailing_whitespace(tokens)

        assert expected == actual


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


class TestFromClause:
    # should we allow a FromClause to hold an empty list of tokens?
    # it's certainly possible for the FROM clause to be omitted, but should that be represented as
    # a missing (null/None) FromClause, or a FromClause that _contains_ nothing?

    def test_render_single_identifier(self):
        # "from foo"
        clause = FromClause(tokens=[
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
        ])

        expected = "  from foo"
        actual = clause.render()

        print(actual)
        assert expected == actual


    def test_render_single_function_call(self):
        # "from generate_series(0, 9)"
        clause = FromClause(tokens=[
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "generate_series"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "0"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "9"),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ])

        expected = "  from generate_series(0, 9)"
        actual = clause.render()

        print(actual)
        assert expected == actual


    def test_render_sql92_identifier_list(self):
        # "from foo, bar, baz"
        clause = FromClause(tokens=[
            SFToken(SFTokenKind.WORD, "from"),
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
            "  from foo\n"
            "     , bar\n"
            "     , baz"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual


    def test_render_sql99_one_simple_join_on(self):
        # "from foo join bar on(foo.x = bar.x)"
        clause = FromClause(tokens=[
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "join"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "on"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "foo.x"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.x"),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            "  from foo\n"
            "  join bar on(foo.x = bar.x)"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual


    def test_render_sql99_one_simple_join_using(self):
        # "from foo join bar using(x)"
        clause = FromClause(tokens=[
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "join"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "using"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            "  from foo\n"
            "  join bar using(x)"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual


    def test_render_sql99_one_complex_join_one_line(self):
        #from foo
        #join bar on(foo.x = bar.x and foo.y = bar.y)
        clause = FromClause(tokens=[
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.WORD, "join"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "on"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "foo.x"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.x"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.y"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.y"),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            "  from foo\n"
            "  join bar on(foo.x = bar.x and foo.y = bar.y)"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual


    def test_render_sql99_one_complex_join_already_formatted(self):
        #  from foo
        #  join bar on(    foo.x = bar.x 
        #              and foo.y = bar.y
        #             )
        clause = FromClause(tokens=[
            #SFToken(SFTokenKind.SPACES, "  "), # those leading spaces are there, but won't be passed into the construction of a WhereClause
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "join"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "on"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "foo.x"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.x"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "              "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.y"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.y"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "             "),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            "  from foo\n"
            "  join bar on(    foo.x = bar.x\n"
            "              and foo.y = bar.y\n"
            "             )"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual


class TestWhereClause:
    # same question as for the FROM clause, do we allow it to be empty?

    def test_render_one_equals_one(self):
        # "where 1=1"
        clause = WhereClause(tokens=[
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
        ])

        expected = " where 1=1"
        actual = clause.render()

        print(actual)
        assert expected == actual


    def test_render_two_expressions_ANDed(self):
        # "where foo.abc = bar.abc and foo.xyz = bar.xyz"
        clause = WhereClause(tokens=[
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.abc"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.abc"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.xyz"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.xyz"),
        ])

        expected = (
            " where foo.abc = bar.abc\n"
            "   and foo.xyz = bar.xyz"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual


    def test_render_complex_preformatted(self):
        # where 1=1
        #   and (   something
        #        or another_thing
        #       )
        clause = WhereClause(tokens=[
            #SFToken(SFTokenKind.SPACES, " "), # that leading space is there, but won't be passed into the construction of a WhereClause
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "something"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "        "),
            SFToken(SFTokenKind.WORD, "or"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "another_thing"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "       "),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            " where 1=1\n"
            "   and (   something\n"
            "        or another_thing\n"
            "       )"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual


class TestGroupByClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            GroupByClause(tokens=[])

        with pytest.raises(ValueError):
            GroupByClause(tokens=None)


    def test_render_zero_expressions(self):
        clause = GroupByClause(tokens=[SFToken(SFTokenKind.WORD, "group by")])

        expected = "group by"
        actual = clause.render()

        assert expected == actual


    def test_render_single_expression(self):
        # "group by foo"
        clause = GroupByClause(tokens=[
            SFToken(SFTokenKind.WORD, "group by"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
        ])

        expected = (
            "group by foo"
        )
        actual = clause.render()

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
            "group by foo\n"
            "       , bar\n"
            "       , baz"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual    


class TestOrderByClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            OrderByClause(tokens=[])

        with pytest.raises(ValueError):
            OrderByClause(tokens=None)


    def test_render_zero_expressions(self):
        clause = OrderByClause(tokens=[SFToken(SFTokenKind.WORD, "order by")])

        expected = "order by"
        actual = clause.render()

        assert expected == actual


    def test_render_single_expression(self):
        # "order by foo"
        clause = OrderByClause(tokens=[
            SFToken(SFTokenKind.WORD, "order by"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
        ])

        expected = (
            "order by foo"
        )
        actual = clause.render()

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
            "order by foo\n"
            "       , bar\n"
            "       , baz"
        )
        actual = clause.render()

        print(actual)
        assert expected == actual


class TestLimitOffsetClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            LimitOffsetClause(tokens=[])

        with pytest.raises(ValueError):
            LimitOffsetClause(tokens=None)


    def test_render_limit_zero_expressions(self):
        clause = LimitOffsetClause(tokens=[SFToken(SFTokenKind.WORD, "limit")])

        expected = " limit"
        actual = clause.render()

        assert expected == actual


    def test_render_offset_zero_expressions(self):
        clause = LimitOffsetClause(tokens=[SFToken(SFTokenKind.WORD, "offset")])

        expected = "offset"
        actual = clause.render()

        assert expected == actual


    def test_render_limit_with_number(self):
        clause = LimitOffsetClause(tokens=[
            SFToken(SFTokenKind.WORD, "limit"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "5"),
        ])

        expected = " limit 5"
        actual = clause.render()

        assert expected == actual


    def test_render_offset_with_number(self):
        clause = LimitOffsetClause(tokens=[
            SFToken(SFTokenKind.WORD, "offset"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "5"),
        ])

        expected = "offset 5"
        actual = clause.render()

        assert expected == actual


    def test_render_limit_offset_with_numbers(self):
        clause = LimitOffsetClause(tokens=[
            SFToken(SFTokenKind.WORD, "limit"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "offset"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
        ])

        expected = (
            " limit 1\n"
            "offset 2"
        )
        actual = clause.render()

        assert expected == actual


    def test_render_offset_limit_with_numbers(self):
        clause = LimitOffsetClause(tokens=[
            SFToken(SFTokenKind.WORD, "offset"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "limit"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
        ])

        expected = (
            "offset 2\n"
            " limit 1"
        )
        actual = clause.render()

        assert expected == actual


    def test_render_limit_offset_with_extra_garbage(self):
        # limit foo bar baz offset 2 + 3
        clause = LimitOffsetClause(tokens=[
            SFToken(SFTokenKind.WORD, "limit"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "offset"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "+"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "3"),
        ])

        expected = (
            " limit foo bar baz\n"
            "offset 2 + 3"
        )
        actual = clause.render()

        assert expected == actual
