import pytest

import cf_flags
from cftoken import CFToken
from cftoken import CFTokenKind
from cftoken import Whitespace
from clause_formatter import WhereClause
from clause_formatter import CompoundStatement


# pytest magic
def setup_module():
    cf_flags.reset_to_defaults()


class TestWhereClause:
    # same question as for the FROM clause, do we allow it to be empty?

    def test_render_one_equals_one(self):
        # "where 1=1"
        clause = WhereClause(tokens=[
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
        ])

        expected = " where 1=1"
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_one_equals_one_indented(self):
        # "where 1=1"
        clause = WhereClause(tokens=[
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
        ])

        # first line, so indent has no effect
        expected = " where 1=1"
        actual = clause.render(indent=4)

        print(actual)
        assert expected == actual


    def test_render_one_equals_one_alt(self):
        # "where 1 = 1"
        # Not my preference, but if this is how it's written it's how we should render it
        clause = WhereClause(tokens=[
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
        ])

        expected = " where 1 = 1"
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_two_expressions_ANDed(self):
        # "where foo.abc = bar.abc and foo.xyz = bar.xyz"
        clause = WhereClause(tokens=[
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.abc"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.abc"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.xyz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.xyz"),
        ])

        expected = (
            " where foo.abc = bar.abc\n"
            "   and foo.xyz = bar.xyz"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_two_expressions_ANDed_poorly_formatted(self):
        #where foo.abc = bar.abc
        #and foo.xyz = bar.xyz"
        clause = WhereClause(tokens=[
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.abc"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.abc"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.xyz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.xyz"),
        ])

        expected = (
            " where foo.abc = bar.abc\n"
            "   and foo.xyz = bar.xyz"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_two_expressions_ANDed_indented(self):
        # "where foo.abc = bar.abc and foo.xyz = bar.xyz"
        clause = WhereClause(tokens=[
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.abc"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.abc"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.xyz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.xyz"),
        ])

        expected = (
            ####
                " where foo.abc = bar.abc\n"
            "       and foo.xyz = bar.xyz"
        )
        actual = clause.render(indent=4)

        print(actual)
        assert expected == actual


    def test_render_custom_spacing(self):
        # where 1=1
        #   and   foo.a =   bar.a
        #   and  foo.ab =  bar.ab
        #   and foo.abc = bar.abc
        clause = WhereClause(tokens=[
            #CFToken(CFTokenKind.SPACES, " "), # that leading space is there, but won't be passed into the construction of a WhereClause
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "foo.a"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "bar.a"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "foo.ab"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "bar.ab"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.abc"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.abc"),
        ])

        expected = (
            " where 1=1\n"
            "   and   foo.a =   bar.a\n"
            "   and  foo.ab =  bar.ab\n"
            "   and foo.abc = bar.abc"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_complex_preformatted(self):
        # where 1=1
        #   and (   something
        #        or another_thing
        #       )
        clause = WhereClause(tokens=[
            #CFToken(CFTokenKind.SPACES, " "), # that leading space is there, but won't be passed into the construction of a WhereClause
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "something"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "        "),
            CFToken(CFTokenKind.WORD, "or"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "another_thing"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "       "),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            " where 1=1\n"
            "   and (   something\n"
            "        or another_thing\n"
            "       )"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_subquery(self):
        # where 1=1
        #   and foo_id in (select id from foo where 1=1)
        clause = WhereClause(tokens=[
            #CFToken(CFTokenKind.SPACES, " "), # that leading space is there, but won't be passed into the construction of a WhereClause
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo_id"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "in"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "("),
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "id"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "foo"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            " where 1=1\n"
            "   and foo_id in (select id\n"
            "                    from foo\n"
            "                   where 1=1\n"
            "                 )"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_multiple_expressions_with_line_comment1(self):
        # where foo.abc = bar.abc
        #   and foo.xyz = bar.xyz
        #   --comment
        #   and foo.qrs = bar.qrs
        clause = WhereClause(tokens=[
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.abc"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.abc"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.xyz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.xyz"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.LINE_COMMENT, "--comment1\n"),
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.qrs"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.qrs"),
        ])

        expected = (
            " where foo.abc = bar.abc\n"
            "   and foo.xyz = bar.xyz\n"
            "   --comment1\n"
            "   and foo.qrs = bar.qrs"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_multiple_expressions_with_line_comment2(self):
        # where foo.abc = bar.abc
        #   and foo.xyz = bar.xyz --comment2
        #   and foo.qrs = bar.qrs
        clause = WhereClause(tokens=[
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.abc"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.abc"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.xyz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.xyz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.LINE_COMMENT, "--comment2\n"),
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.qrs"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.qrs"),
        ])

        expected = (
            " where foo.abc = bar.abc\n"
            "   and foo.xyz = bar.xyz --comment2\n"
            "   and foo.qrs = bar.qrs"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_multiple_expressions_with_line_comment3(self):
        # where foo.abc = bar.abc
        #   and foo.xyz = bar.xyz
        #--comment3
        #   and foo.qrs = bar.qrs
        clause = WhereClause(tokens=[
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.abc"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.abc"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.xyz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.xyz"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.LINE_COMMENT, "--comment3\n"),
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.qrs"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.qrs"),
        ])

        expected = (
            " where foo.abc = bar.abc\n"
            "   and foo.xyz = bar.xyz\n"
            "--comment3\n"
            "   and foo.qrs = bar.qrs"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_between(self):
        # where 1=1
        #   and foo between 0 and 9
        clause = WhereClause(tokens=[
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "between"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "9"),
        ])

        expected = (
            " where 1=1\n"
            "   and foo between 0 and 9"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_case(self):
        # where 1=1
        #   and case when foo > 0
        #             and bar > 0
        #            then true
        #            else false
        #             end
        clause = WhereClause(tokens=[
            CFToken(CFTokenKind.WORD, "where"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "case"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "when"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ">"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "             "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, ">"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "            "),
            CFToken(CFTokenKind.WORD, "then"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "true"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "            "),
            CFToken(CFTokenKind.WORD, "else"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "false"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "             "),
            CFToken(CFTokenKind.WORD, "end"),
        ])

        expected = (
            " where 1=1\n"
            "   and case when foo > 0\n"
            "             and bar > 0\n"
            "            then true\n"
            "            else false\n"
            "             end"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual
