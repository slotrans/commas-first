import pytest

import sf_flags
from sftoken import SFToken
from sftoken import SFTokenKind
from sftoken import Whitespace
from sftoken import Symbols
from clause_formatter import WithClause
from clause_formatter import CompoundStatement


# pytest magic
def setup_module():
    sf_flags.reset_to_defaults()


class TestWithClause:
    def test_creation_fails_on_empty_input(self):
        with pytest.raises(ValueError):
            WithClause(tokens=[])

        with pytest.raises(ValueError):
            WithClause(tokens=None)


    def test_render_single_simple_cte(self):
        # "with foo as (select 1)"
        clause = WithClause(tokens=[
            SFToken(SFTokenKind.WORD, "with"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "as"),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "1"),
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
            SFToken(SFTokenKind.WORD, "with"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "as"),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "as"),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "2"),
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
            SFToken(SFTokenKind.WORD, "with"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            Symbols.LEFT_PAREN,
            SFToken(SFTokenKind.WORD, "x"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "y"),
            Symbols.RIGHT_PAREN,            
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "as"),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "1"),
                SFToken(SFTokenKind.SYMBOL, ","),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "2"),
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
            SFToken(SFTokenKind.WORD, "with"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "as"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "materialized"),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "1"),
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
            SFToken(SFTokenKind.WORD, "with"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "as"),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "1"),
            ]),
            Symbols.RIGHT_PAREN,
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "blorp"),
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
            SFToken(SFTokenKind.WORD, "with"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "recursive"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "search_tree"),
            Symbols.LEFT_PAREN,
            SFToken(SFTokenKind.WORD, "id"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "link"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "data"),
            Symbols.RIGHT_PAREN,
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "as"),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "t.id"),
                SFToken(SFTokenKind.SYMBOL, ","),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "t.link"),
                SFToken(SFTokenKind.SYMBOL, ","),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "t.data"),
                Whitespace.NEWLINE,
                SFToken(SFTokenKind.SPACES, "    "),
                SFToken(SFTokenKind.WORD, "from"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "tree"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "t"),
                Whitespace.NEWLINE,
                SFToken(SFTokenKind.SPACES, "  "),
                SFToken(SFTokenKind.WORD, "union all"),
                Whitespace.NEWLINE,
                SFToken(SFTokenKind.SPACES, "    "),
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "t.id"),
                SFToken(SFTokenKind.SYMBOL, ","),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "t.link"),
                SFToken(SFTokenKind.SYMBOL, ","),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "t.data"),
                Whitespace.NEWLINE,
                SFToken(SFTokenKind.SPACES, "    "),
                SFToken(SFTokenKind.WORD, "from"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "tree"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "t"),
                SFToken(SFTokenKind.SYMBOL, ","),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "search_tree"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "st"),
                Whitespace.NEWLINE,
                SFToken(SFTokenKind.SPACES, "    "),
                SFToken(SFTokenKind.WORD, "where"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "t.id"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.SYMBOL, "="),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "st.link"),
            ]),
            Symbols.RIGHT_PAREN,
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "search"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "depth"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "first"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "by"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "id"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "set"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "ordercol"),
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
            SFToken(SFTokenKind.WORD, "with"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "as"),
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.LINE_COMMENT, "--comment\n"),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "1"),
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
            SFToken(SFTokenKind.WORD, 'with'),
            SFToken(SFTokenKind.SPACES, ' '),
            SFToken(SFTokenKind.WORD, 'cte1'),
            SFToken(SFTokenKind.SPACES, ' '),
            SFToken(SFTokenKind.WORD, 'as'),
            SFToken(SFTokenKind.SPACES, ' '),
            SFToken(SFTokenKind.SYMBOL, '('),
            CompoundStatement([
                SFToken(SFTokenKind.WORD, 'select'),
                SFToken(SFTokenKind.SPACES, ' '),
                SFToken(SFTokenKind.LITERAL, '1'),
                SFToken(SFTokenKind.SPACES, ' '),
                SFToken(SFTokenKind.WORD, 'from'),
                SFToken(SFTokenKind.SPACES, ' '),
                SFToken(SFTokenKind.WORD, 'bar'),
                SFToken(SFTokenKind.SPACES, ' '),
                SFToken(SFTokenKind.WORD, 'where'),
                SFToken(SFTokenKind.SPACES, ' '),
                SFToken(SFTokenKind.LITERAL, '1'),
                SFToken(SFTokenKind.SYMBOL, '='),
                SFToken(SFTokenKind.LITERAL, '1'),
            ]),
            SFToken(SFTokenKind.SYMBOL, ')'),
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
