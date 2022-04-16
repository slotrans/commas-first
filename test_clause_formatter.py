import pytest

from sftoken import SFToken, SFTokenKind
from clause_formatter import trim_trailing_whitespace
from clause_formatter import SelectClause, FromClause, WhereClause


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
        #from foo
        #join bar on(    foo.x = bar.x 
        #            and foo.y = bar.y
        #           )
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
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "foo.x"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.x"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "            "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.y"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.y"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "           "),
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
