import pytest

from sftoken import SFToken
from sftoken import SFTokenKind
from clause_formatter import FromClause


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
        actual = clause.render(indent=0)

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
        actual = clause.render(indent=0)

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
        actual = clause.render(indent=0)

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
        actual = clause.render(indent=0)

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
        actual = clause.render(indent=0)

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
        actual = clause.render(indent=0)

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
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual
