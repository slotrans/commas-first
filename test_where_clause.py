import pytest

import sf_flags
from sftoken import SFToken
from sftoken import SFTokenKind
from sftoken import Whitespace
from clause_formatter import WhereClause
from clause_formatter import CompoundStatement
from clause_formatter import RenderingContext


# pytest magic
def setup_module():
    sf_flags.reset_to_defaults()


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
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_one_equals_one_indented(self):
        # "where 1=1"
        clause = WhereClause(tokens=[
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
        ])

        # first line, so indent has no effect
        expected = " where 1=1"
        actual = clause.render(RenderingContext(indent=4))

        print(actual)
        assert expected == actual


    def test_render_one_equals_one_alt(self):
        # "where 1 = 1"
        # Not my preference, but if this is how it's written it's how we should render it
        clause = WhereClause(tokens=[
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
        ])

        expected = " where 1 = 1"
        actual = clause.render(RenderingContext(indent=0))

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
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_two_expressions_ANDed_poorly_formatted(self):
        #where foo.abc = bar.abc
        #and foo.xyz = bar.xyz"
        clause = WhereClause(tokens=[
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.abc"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.abc"),
            Whitespace.NEWLINE,
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
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_two_expressions_ANDed_indented(self):
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
            ####
                " where foo.abc = bar.abc\n"
            "       and foo.xyz = bar.xyz"
        )
        actual = clause.render(RenderingContext(indent=4))

        print(actual)
        assert expected == actual


    def test_render_custom_spacing(self):
        # where 1=1
        #   and   foo.a =   bar.a
        #   and  foo.ab =  bar.ab
        #   and foo.abc = bar.abc
        clause = WhereClause(tokens=[
            #SFToken(SFTokenKind.SPACES, " "), # that leading space is there, but won't be passed into the construction of a WhereClause
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "foo.a"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "bar.a"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "foo.ab"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "bar.ab"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.abc"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.abc"),
        ])

        expected = (
            " where 1=1\n"
            "   and   foo.a =   bar.a\n"
            "   and  foo.ab =  bar.ab\n"
            "   and foo.abc = bar.abc"
        )
        actual = clause.render(RenderingContext(indent=0))

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
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "something"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "        "),
            SFToken(SFTokenKind.WORD, "or"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "another_thing"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "       "),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            " where 1=1\n"
            "   and (   something\n"
            "        or another_thing\n"
            "       )"
        )
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_subquery(self):
        # where 1=1
        #   and foo_id in (select id from foo where 1=1)
        clause = WhereClause(tokens=[
            #SFToken(SFTokenKind.SPACES, " "), # that leading space is there, but won't be passed into the construction of a WhereClause
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo_id"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "in"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "("),
            CompoundStatement([
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "id"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "from"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "foo"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "where"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "1"),
                SFToken(SFTokenKind.SYMBOL, "="),
                SFToken(SFTokenKind.WORD, "1"),
            ]),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            " where 1=1\n"
            "   and foo_id in (select id\n"
            "                    from foo\n"
            "                   where 1=1\n"
            "                 )"
        )
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_multiple_expressions_with_line_comment1(self):
        # where foo.abc = bar.abc
        #   and foo.xyz = bar.xyz
        #   --comment
        #   and foo.qrs = bar.qrs
        clause = WhereClause(tokens=[
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.abc"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.abc"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.xyz"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.xyz"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.LINE_COMMENT, "--comment1\n"),
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.qrs"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.qrs"),
        ])

        expected = (
            " where foo.abc = bar.abc\n"
            "   and foo.xyz = bar.xyz\n"
            "   --comment1\n"
            "   and foo.qrs = bar.qrs"
        )
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_multiple_expressions_with_line_comment2(self):
        # where foo.abc = bar.abc
        #   and foo.xyz = bar.xyz --comment2
        #   and foo.qrs = bar.qrs
        clause = WhereClause(tokens=[
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.abc"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.abc"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.xyz"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.xyz"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.LINE_COMMENT, "--comment2\n"),
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.qrs"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.qrs"),
        ])

        expected = (
            " where foo.abc = bar.abc\n"
            "   and foo.xyz = bar.xyz --comment2\n"
            "   and foo.qrs = bar.qrs"
        )
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_multiple_expressions_with_line_comment3(self):
        # where foo.abc = bar.abc
        #   and foo.xyz = bar.xyz
        #--comment3
        #   and foo.qrs = bar.qrs
        clause = WhereClause(tokens=[
            SFToken(SFTokenKind.WORD, "where"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.abc"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.abc"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.xyz"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.xyz"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.LINE_COMMENT, "--comment3\n"),
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "and"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo.qrs"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar.qrs"),
        ])

        expected = (
            " where foo.abc = bar.abc\n"
            "   and foo.xyz = bar.xyz\n"
            "--comment3\n"
            "   and foo.qrs = bar.qrs"
        )
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual
