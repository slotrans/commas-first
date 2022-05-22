import pytest

from sftoken import SFToken
from sftoken import SFTokenKind
from clause_formatter import WhereClause


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
