import pytest

import cf_flags
from cftoken import CFToken
from cftoken import CFTokenKind
from cftoken import Whitespace
from cftoken import Symbols
from clause_formatter import WithClause
from clause_formatter import CompoundStatement


# pytest magic
def setup_module():
    cf_flags.reset_to_defaults()


class TestWithClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            WithClause(tokens=[])

        with pytest.raises(ValueError):
            WithClause(tokens=None)


    def test_render_single_simple_cte(self):
        # "with foo as (select 1)"
        clause = WithClause(tokens=[
            CFToken(CFTokenKind.WORD, "with"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "with foo as\n"
            "(\n"
            "    select 1\n"
            ")"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_two_simple_ctes(self):
        # "with foo as (select 1), bar as (select 2)"
        clause = WithClause(tokens=[
            CFToken(CFTokenKind.WORD, "with"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "2"),
            ]),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "with foo as\n"
            "(\n"
            "    select 1\n"
            ")\n"
            ", bar as\n"
            "(\n"
            "    select 2\n"
            ")"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_cte_with_column_list(self):
        # "with foo(x, y) as (select 1, 2)"
        clause = WithClause(tokens=[
            CFToken(CFTokenKind.WORD, "with"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            Symbols.LEFT_PAREN,
            CFToken(CFTokenKind.WORD, "x"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "y"),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
                CFToken(CFTokenKind.SYMBOL, ","),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "2"),
            ]),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "with foo(x, y) as\n"
            "(\n"
            "    select 1\n"
            "         , 2\n"
            ")"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_materialized_cte(self):
        # "with foo as materialized (select 1)"
        clause = WithClause(tokens=[
            CFToken(CFTokenKind.WORD, "with"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "materialized"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "with foo as materialized\n"
            "(\n"
            "    select 1\n"
            ")"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_cte_with_trailing_junk(self):
        # "with foo as (select 1) blorp"
        clause = WithClause(tokens=[
            CFToken(CFTokenKind.WORD, "with"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "blorp"),
        ])

        expected = (
            "with foo as\n"
            "(\n"
            "    select 1\n"
            ") blorp"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_recursive_cte_with_search_clause(self):
        # This example is straight from the PG docs

        #with recursive search_tree(id, link, data) as (
        #    select t.id, t.link, t.data
        #    from tree t
        #  union all
        #    select t.id, t.link, t.data
        #    from tree t, search_tree st
        #    where t.id = st.link
        #) search depth first by id set ordercol
        clause = WithClause(tokens=[
            CFToken(CFTokenKind.WORD, "with"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "recursive"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "search_tree"),
            Symbols.LEFT_PAREN,
            CFToken(CFTokenKind.WORD, "id"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "link"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "data"),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "t.id"),
                CFToken(CFTokenKind.SYMBOL, ","),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "t.link"),
                CFToken(CFTokenKind.SYMBOL, ","),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "t.data"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "    "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "tree"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "t"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "  "),
                CFToken(CFTokenKind.WORD, "union all"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "    "),
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "t.id"),
                CFToken(CFTokenKind.SYMBOL, ","),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "t.link"),
                CFToken(CFTokenKind.SYMBOL, ","),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "t.data"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "    "),
                CFToken(CFTokenKind.WORD, "from"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "tree"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "t"),
                CFToken(CFTokenKind.SYMBOL, ","),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "search_tree"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "st"),
                Whitespace.NEWLINE,
                CFToken(CFTokenKind.SPACES, "    "),
                CFToken(CFTokenKind.WORD, "where"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "t.id"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.SYMBOL, "="),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "st.link"),
            ]),
            Symbols.RIGHT_PAREN,
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "search"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "depth"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "first"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "by"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "id"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "set"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "ordercol"),
        ])

        expected = (
            "with recursive search_tree(id, link, data) as\n"
            "(\n"
            "    select t.id\n"
            "         , t.link\n"
            "         , t.data\n"
            "      from tree t\n"
            "    union all\n"
            "    select t.id\n"
            "         , t.link\n"
            "         , t.data\n"
            "      from tree t\n"
            "         , search_tree st\n"
            "     where t.id = st.link\n"
            ") search depth first by id set ordercol"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_render_single_simple_cte_with_line_comment(self):
        #with foo as
        #--comment
        #(
        #    select 1
        #)
        clause = WithClause(tokens=[
            CFToken(CFTokenKind.WORD, "with"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.LINE_COMMENT, "--comment\n"),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
        ])

        expected = (
            "with foo as\n"
            "--comment\n"
            "(\n"
            "    select 1\n"
            ")"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


    def test_single_cte_full_query(self):
        # with cte1 as (select 1 from bar where 1=1)
        clause = WithClause(tokens=[
            CFToken(CFTokenKind.WORD, 'with'),
            CFToken(CFTokenKind.SPACES, ' '),
            CFToken(CFTokenKind.WORD, 'cte1'),
            CFToken(CFTokenKind.SPACES, ' '),
            CFToken(CFTokenKind.WORD, 'as'),
            CFToken(CFTokenKind.SPACES, ' '),
            CFToken(CFTokenKind.SYMBOL, '('),
            CompoundStatement([
                CFToken(CFTokenKind.WORD, 'select'),
                CFToken(CFTokenKind.SPACES, ' '),
                CFToken(CFTokenKind.LITERAL, '1'),
                CFToken(CFTokenKind.SPACES, ' '),
                CFToken(CFTokenKind.WORD, 'from'),
                CFToken(CFTokenKind.SPACES, ' '),
                CFToken(CFTokenKind.WORD, 'bar'),
                CFToken(CFTokenKind.SPACES, ' '),
                CFToken(CFTokenKind.WORD, 'where'),
                CFToken(CFTokenKind.SPACES, ' '),
                CFToken(CFTokenKind.LITERAL, '1'),
                CFToken(CFTokenKind.SYMBOL, '='),
                CFToken(CFTokenKind.LITERAL, '1'),
            ]),
            CFToken(CFTokenKind.SYMBOL, ')'),
        ])

        expected = (
            "with cte1 as\n"
            "(\n"
            "    select 1\n"
            "      from bar\n"
            "     where 1=1\n"
            ")"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual
