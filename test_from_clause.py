import pytest

import sf_flags
from sftoken import SFToken
from sftoken import SFTokenKind
from sftoken import Symbols
from sftoken import Whitespace
from clause_formatter import FromClause
from clause_formatter import CompoundStatement
from clause_formatter import RenderingContext


# pytest magic
def setup_module():
    sf_flags.reset_to_defaults()


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
        actual = clause.render(RenderingContext(indent=0))

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
        actual = clause.render(RenderingContext(indent=0))

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
        actual = clause.render(RenderingContext(indent=0))

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
        actual = clause.render(RenderingContext(indent=0))

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
        actual = clause.render(RenderingContext(indent=0))

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
        actual = clause.render(RenderingContext(indent=0))

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
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_sql99_one_simple_join_on_with_line_comment1(self):
        #  from foo
        #  --comment1
        #  join bar on(foo.x = bar.x)
        clause = FromClause(tokens=[
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.LINE_COMMENT, "--comment1\n"),
            SFToken(SFTokenKind.SPACES, "  "),
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
            "  --comment1\n"
            "  join bar on(foo.x = bar.x)"
        )
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_sql99_one_simple_join_on_with_line_comment2(self):
        #  from foo --comment2
        #  join bar on(foo.x = bar.x)
        clause = FromClause(tokens=[
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.LINE_COMMENT, "--comment2\n"),
            SFToken(SFTokenKind.SPACES, "  "),
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
            "  from foo --comment2\n"
            "  join bar on(foo.x = bar.x)"
        )
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_sql99_two_simple_join_on_with_line_comment3(self):
        #  from foo
        #  join bar on(foo.x = bar.x) --comment3
        #  join baz on(bar.y = baz.y)
        clause = FromClause(tokens=[
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "  "),
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
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.LINE_COMMENT, "--comment3\n"),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "join"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "on"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "bar.y"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz.y"),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            "  from foo\n"
            "  join bar on(foo.x = bar.x) --comment3\n"
            "  join baz on(bar.y = baz.y)"
        )
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_inline_view(self):
        # "from (select foo from bar where 1=1) x"
        clause = FromClause(tokens=[
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "foo"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "from"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "bar"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "where"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "1"),
                SFToken(SFTokenKind.SYMBOL, "="),
                SFToken(SFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "x"),
        ])

        expected = (
            "  from (select foo\n"
            "          from bar\n"
            "         where 1=1\n"
            "       ) x"
        )
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_inline_view_with_join1(self):
        # "from (select foo from bar where 1=1) x join baz on(true)"
        clause = FromClause(tokens=[
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "foo"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "from"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "bar"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "where"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "1"),
                SFToken(SFTokenKind.SYMBOL, "="),
                SFToken(SFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "join"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "on"),
            Symbols.LEFT_PAREN,
            SFToken(SFTokenKind.WORD, "true"),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "  from (select foo\n"
            "          from bar\n"
            "         where 1=1\n"
            "       ) x\n"
            "  join baz on(true)"
        )
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_inline_view_with_join2(self):
        # "from baz join (select foo from bar where 1=1) x on(true)"
        clause = FromClause(tokens=[
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "join"),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "foo"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "from"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "bar"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "where"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "1"),
                SFToken(SFTokenKind.SYMBOL, "="),
                SFToken(SFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "on"),
            Symbols.LEFT_PAREN,
            SFToken(SFTokenKind.WORD, "true"),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "  from baz\n"
            "  join (select foo\n"
            "          from bar\n"
            "         where 1=1\n"
            "       ) x on(true)"
        )
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual


    def test_render_join_with_dbt_templating(self):
        # "from foo join {{ ref('__bar') }} bar on(foo.x = bar.x) join baz on(bar.y = baz.y)"
        clause = FromClause(tokens=[
            SFToken(SFTokenKind.WORD, "from"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "join"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "{{"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "ref"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.LITERAL, "'__bar'"),
            SFToken(SFTokenKind.SYMBOL, ")"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "}}"),
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
            SFToken(SFTokenKind.WORD, "join"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "on"),
            SFToken(SFTokenKind.SYMBOL, "("),
            SFToken(SFTokenKind.WORD, "bar.y"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.SYMBOL, "="),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz.y"),
            SFToken(SFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            "  from foo\n"
            "  join {{ ref('__bar') }} bar on(foo.x = bar.x)\n"
            "  join baz on(bar.y = baz.y)"
        )
        actual = clause.render(RenderingContext(indent=0))

        print(actual)
        assert expected == actual