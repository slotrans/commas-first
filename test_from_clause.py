import pytest

import cf_flags
from cftoken import CFToken
from cftoken import CFTokenKind
from cftoken import Symbols
from cftoken import Whitespace
from clause_formatter import FromClause
from clause_formatter import CompoundStatement


# pytest magic
def setup_module():
    cf_flags.reset_to_defaults()


class TestFromClause:
    # should we allow a FromClause to hold an empty list of tokens?
    # it's certainly possible for the FROM clause to be omitted, but should that be represented as
    # a missing (null/None) FromClause, or a FromClause that _contains_ nothing?

    def test_render_single_identifier(self):
        # "from foo"
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
        ])

        expected = "  from foo"
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_single_function_call(self):
        # "from generate_series(0, 9)"
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "generate_series"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "0"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "9"),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ])

        expected = "  from generate_series(0, 9)"
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_sql92_identifier_list(self):
        # "from foo, bar, baz"
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
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
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "foo.x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.x"),
            CFToken(CFTokenKind.SYMBOL, ")"),
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
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "using"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, ")"),
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
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "foo.x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.y"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.y"),
            CFToken(CFTokenKind.SYMBOL, ")"),
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
            #CFToken(CFTokenKind.SPACES, "  "), # those leading spaces are there, but won't be passed into the construction of a WhereClause
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "foo.x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.x"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "              "),
            CFToken(CFTokenKind.WORD, "and"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo.y"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.y"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "             "),
            CFToken(CFTokenKind.SYMBOL, ")"),
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


    def test_render_sql99_one_simple_join_on_with_line_comment1(self):
        #  from foo
        #  --comment1
        #  join bar on(foo.x = bar.x)
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.LINE_COMMENT, "--comment1\n"),
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "foo.x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.x"),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            "  from foo\n"
            "  --comment1\n"
            "  join bar on(foo.x = bar.x)"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_sql99_one_simple_join_on_with_line_comment2(self):
        #  from foo --comment2
        #  join bar on(foo.x = bar.x)
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.LINE_COMMENT, "--comment2\n"),
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "foo.x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.x"),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            "  from foo --comment2\n"
            "  join bar on(foo.x = bar.x)"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_sql99_two_simple_join_on_with_line_comment3(self):
        #  from foo
        #  join bar on(foo.x = bar.x) --comment3
        #  join baz on(bar.y = baz.y)
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "foo.x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.x"),
            CFToken(CFTokenKind.SYMBOL, ")"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.LINE_COMMENT, "--comment3\n"),
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "bar.y"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz.y"),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            "  from foo\n"
            "  join bar on(foo.x = bar.x) --comment3\n"
            "  join baz on(bar.y = baz.y)"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_inline_view(self):
        # "from (select foo from bar where 1=1) x"
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "foo"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "bar"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "x"),
        ])

        expected = (
            "  from (select foo\n"
            "          from bar\n"
            "         where 1=1\n"
            "       ) x"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_inline_view_with_join1(self):
        # "from (select foo from bar where 1=1) x join baz on(true)"
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "foo"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "bar"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            Symbols.LEFT_PAREN,
            CFToken(CFTokenKind.WORD, "true"),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "  from (select foo\n"
            "          from bar\n"
            "         where 1=1\n"
            "       ) x\n"
            "  join baz on(true)"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_inline_view_with_join2(self):
        # "from baz join (select foo from bar where 1=1) x on(true)"
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "foo"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "bar"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            Symbols.LEFT_PAREN,
            CFToken(CFTokenKind.WORD, "true"),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "  from baz\n"
            "  join (select foo\n"
            "          from bar\n"
            "         where 1=1\n"
            "       ) x on(true)"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_inline_view_with_left_join(self):
        # "from baz left join (select foo from bar where 1=1) x on(true)"
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "left join"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "foo"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "bar"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            Symbols.LEFT_PAREN,
            CFToken(CFTokenKind.WORD, "true"),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "  from baz\n"
            "  left join (select foo\n"
            "               from bar\n"
            "              where 1=1\n"
            "            ) x on(true)"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_inline_view_with_left_outer_join(self):
        # "from baz left outer join (select foo from bar where 1=1) x on(true)"
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "left outer join"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "foo"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "bar"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            Symbols.LEFT_PAREN,
            CFToken(CFTokenKind.WORD, "true"),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "  from baz\n"
            "  left outer join (select foo\n"
            "                     from bar\n"
            "                    where 1=1\n"
            "                  ) x on(true)"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_inline_view_with_full_join(self):
        # "from baz full join (select foo from bar where 1=1) x on(true)"
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "full join"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "foo"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "bar"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            Symbols.LEFT_PAREN,
            CFToken(CFTokenKind.WORD, "true"),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "  from baz\n"
            "  full join (select foo\n"
            "               from bar\n"
            "              where 1=1\n"
            "            ) x on(true)"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_inline_view_with_full_outer_join(self):
        # "from baz full join (select foo from bar where 1=1) x on(true)"
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "full outer join"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "foo"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "bar"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            Symbols.LEFT_PAREN,
            CFToken(CFTokenKind.WORD, "true"),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "  from baz\n"
            "  full outer join (select foo\n"
            "                     from bar\n"
            "                    where 1=1\n"
            "                  ) x on(true)"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    # arguably we should just discard "inner"...
    def test_render_inner_join(self):
        # "from foo inner join bar on(foo.x = bar.x)"
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "inner join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "foo.x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.x"),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            "  from foo\n"
            "  inner join bar on(foo.x = bar.x)"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual        


    def test_render_join_with_dbt_templating(self):
        # "from foo join {{ ref('__bar') }} bar on(foo.x = bar.x) join baz on(bar.y = baz.y)"
        clause = FromClause(tokens=[
            CFToken(CFTokenKind.WORD, "from"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "{{"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "ref"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.LITERAL, "'__bar'"),
            CFToken(CFTokenKind.SYMBOL, ")"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "}}"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "foo.x"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar.x"),
            CFToken(CFTokenKind.SYMBOL, ")"),
            CFToken(CFTokenKind.WORD, "join"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "on"),
            CFToken(CFTokenKind.SYMBOL, "("),
            CFToken(CFTokenKind.WORD, "bar.y"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz.y"),
            CFToken(CFTokenKind.SYMBOL, ")"),
        ])

        expected = (
            "  from foo\n"
            "  join {{ ref('__bar') }} bar on(foo.x = bar.x)\n"
            "  join baz on(bar.y = baz.y)"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual