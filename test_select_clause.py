import pytest

import sf_flags
from sftoken import SFToken
from sftoken import SFTokenKind
from sftoken import Symbols
from sftoken import Whitespace
from clause_formatter import SelectClause
from clause_formatter import CompoundStatement


# pytest magic
def setup_module():
    sf_flags.reset_to_defaults()


@pytest.fixture
def trim_leading_whitespace_off():
    sf_flags.TRIM_LEADING_WHITESPACE = False


@pytest.fixture
def trim_leading_whitespace_on():
    sf_flags.TRIM_LEADING_WHITESPACE = True



def test_creation_fails_on_empty_input():
    with pytest.raises(ValueError):
        SelectClause(tokens=[])

    with pytest.raises(ValueError):
        SelectClause(tokens=None)


def test_render_zero_expressions():
    clause = SelectClause(tokens=[SFToken(SFTokenKind.WORD, "select")])

    expected = "select"
    actual = clause.render(indent=0)

    assert expected == actual


def test_render_simple_expressions_no_qualifier():
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
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_simple_expressions_line_comment_no_qualifier():
    #select foo
    #     , bar
    #     --LINE COMMENT
    #     , baz
    clause = SelectClause(tokens=[
        SFToken(SFTokenKind.WORD, "select"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "bar"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.LINE_COMMENT, "--LINE COMMENT\n"),
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "baz"),
    ])

    expected = (
        "select foo\n"
        "     , bar\n"
        "     --LINE COMMENT\n"
        "     , baz"
    )
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_simple_expressions_block_comment_no_qualifier():
    #select foo
    #     , bar
    #     /* BLOCK
    #        COMMENT */
    #     , baz
    clause = SelectClause(tokens=[
        SFToken(SFTokenKind.WORD, "select"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "bar"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.BLOCK_COMMENT, "/* BLOCK\n        COMMENT */"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "baz"),
    ])

    expected = (
        "select foo\n"
        "     , bar\n"
        "     /* BLOCK\n"
        "        COMMENT */\n"
        "     , baz"
    )
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_simple_expressions_block_comment_no_qualifier2():
    #select foo
    #     , bar
    #/* BLOCK
    #   COMMENT */
    #     , baz
    clause = SelectClause(tokens=[
        SFToken(SFTokenKind.WORD, "select"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "bar"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.BLOCK_COMMENT, "/* BLOCK\n   COMMENT */"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "baz"),
    ])

    expected = (
        "select foo\n"
        "     , bar\n"
        "/* BLOCK\n"
        "   COMMENT */\n"
        "     , baz"
    )
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_complex_expressions_no_qualifier():
    #select foo
    #     , coalesce(bar, 0)
    #     , case when active
    #            then 1
    #            else 0
    #             end as ACTIVE_INT
    #     , lag(blergh,1) over(partition by foo order by bar) as PREV_BLERGH
    #     , (   beep > 0
    #        or boop > 0
    #       ) as BEEP_BOOP
    clause = SelectClause(tokens=[
        SFToken(SFTokenKind.WORD, "select"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "coalesce"),
        SFToken(SFTokenKind.SYMBOL, "("),
        SFToken(SFTokenKind.WORD, "bar"),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "0"),
        SFToken(SFTokenKind.SYMBOL, ")"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "case"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "when"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "active"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "            "),
        SFToken(SFTokenKind.WORD, "then"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "1"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "            "),
        SFToken(SFTokenKind.WORD, "else"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "0"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "             "),
        SFToken(SFTokenKind.WORD, "end"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "as"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "ACTIVE_INT"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "lag"),
        SFToken(SFTokenKind.SYMBOL, "("),
        SFToken(SFTokenKind.WORD, "blergh"),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.WORD, "1"),
        SFToken(SFTokenKind.SYMBOL, ")"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "over"),
        SFToken(SFTokenKind.SYMBOL, "("),
        SFToken(SFTokenKind.WORD, "partition"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "by"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "foo"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "order"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "by"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "bar"),
        SFToken(SFTokenKind.SYMBOL, ")"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "as"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "PREV_BLERGH"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.SYMBOL, "("),
        SFToken(SFTokenKind.SPACES, "   "),
        SFToken(SFTokenKind.WORD, "beep"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.SYMBOL, ">"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "0"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "        "),
        SFToken(SFTokenKind.WORD, "or"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "boop"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.SYMBOL, ">"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "0"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "       "),
        SFToken(SFTokenKind.SYMBOL, ")"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "as"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "BEEP_BOOP"),
    ])

    expected = (
        "select foo\n"
        "     , coalesce(bar, 0)\n"
        "     , case when active\n"
        "            then 1\n"
        "            else 0\n"
        "             end as ACTIVE_INT\n"
        "     , lag(blergh,1) over(partition by foo order by bar) as PREV_BLERGH\n"
        "     , (   beep > 0\n"
        "        or boop > 0\n"
        "       ) as BEEP_BOOP"
    )
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_simple_expressions_no_qualifier_indented():
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
        ####
            "select foo\n"
        "         , bar\n"
        "         , baz"
    )
    actual = clause.render(indent=4)

    print(actual)
    assert expected == actual


class TestRenderSimpleExpressionsCrappyIndentation():
    @classmethod
    def teardown_class(cls):
        sf_flags.reset_to_defaults()

    #select
    #    foo,
    #    bar,
    #    baz
    @pytest.fixture
    def tokens(self):
        return [
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "baz"),
        ]

    # this is kind of a silly test in that this behavior is not particularly _desirable_,
    # but it is what you get from this input in this mode
    def test_trim_leading_off(self, tokens, trim_leading_whitespace_off):
        clause = SelectClause(tokens)
        expected = (
            "select \n"
            "       foo\n"
            "     , \n"
            "       bar\n"
            "     , \n"
            "       baz"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual

    def test_trim_leading_on(self, tokens, trim_leading_whitespace_on):
        clause = SelectClause(tokens)
        expected = (
            "select foo\n"
            "     , bar\n"
            "     , baz"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


def test_render_simple_expressions_no_indentation():
    #select foo
    #, bar
    #, baz
    clause = SelectClause(tokens=[
        SFToken(SFTokenKind.WORD, "select"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "bar"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "baz"),
    ])

    expected = (
        "select foo\n"
        "     , bar\n"
        "     , baz"
    )
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_simple_expressions_distinct_qualifier():
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
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_simple_expressions_distinct_qualifier_preformatted():
    # select distinct
    #        foo
    #      , bar
    #      , baz
    clause = SelectClause(tokens=[
        SFToken(SFTokenKind.WORD, "select"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "distinct"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "       "),
        SFToken(SFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "bar"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
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
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_simple_expressions_distinct_qualifier_preformatted_leading_spaces():
    # select distinct
    #          z
    #      ,  yz
    #      , xyz
    clause = SelectClause(tokens=[
        SFToken(SFTokenKind.WORD, "select"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "distinct"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "         "),
        SFToken(SFTokenKind.WORD, "z"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, "  "),
        SFToken(SFTokenKind.WORD, "yz"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "xyz"),
    ])

    expected = (
        "select distinct\n"
        "         z\n"
        "     ,  yz\n"
        "     , xyz"
    )
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_simple_expressions_all_qualifier():
    # "select all foo, bar, baz"
    clause = SelectClause(tokens=[
        SFToken(SFTokenKind.WORD, "select"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "all"),
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
        "select all\n"
        "       foo\n"
        "     , bar\n"
        "     , baz"
    )
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_simple_expressions_distinct_on_qualifier():
    # "select distinct on(foo) foo, bar, baz"
    clause = SelectClause(tokens=[
        SFToken(SFTokenKind.WORD, "select"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "distinct on"),
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
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_qualifier_only():
    # "select distinct"
    clause = SelectClause(tokens=[
        SFToken(SFTokenKind.WORD, "select"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "distinct"),
    ])

    expected = "select distinct"
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_qualifier_only2():
    # "select all"
    clause = SelectClause(tokens=[
        SFToken(SFTokenKind.WORD, "select"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "all"),
    ])

    expected = "select all"
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


class TestCustomSpacing:
    @classmethod
    def teardown_class(cls):
        sf_flags.reset_to_defaults()

    #select foo
    #     ,   l7
    #     ,  l30
    #     , l182
    @pytest.fixture
    def tokens(self):
        return [
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "     "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, "   "),
            SFToken(SFTokenKind.WORD, "l7"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "     "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "l30"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "     "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "l182"),
        ]

    def test_trim_leading_off(self, tokens, trim_leading_whitespace_off):
        clause = SelectClause(tokens)
        expected = (
            "select foo\n"
            "     ,   l7\n"
            "     ,  l30\n"
            "     , l182"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual

    def test_trim_leading_on(self, tokens, trim_leading_whitespace_on):
        clause = SelectClause(tokens)
        expected = (
            "select foo\n"
            "     , l7\n"
            "     , l30\n"
            "     , l182"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


def test_hand_formatted_case():
    #select foo
    #     , case when bar
    #            then 1
    #            when baz
    #            then 2
    #            else 3
    #             end as BLERGH
    #     , stuff
    clause = SelectClause(tokens=[
        SFToken(SFTokenKind.WORD, "select"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "foo"),
        SFToken(SFTokenKind.NEWLINE, "\n"),
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "case"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "when"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "bar"),
        SFToken(SFTokenKind.NEWLINE, "\n"),
        SFToken(SFTokenKind.SPACES, "            "),
        SFToken(SFTokenKind.WORD, "then"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "1"),
        SFToken(SFTokenKind.NEWLINE, "\n"),
        SFToken(SFTokenKind.SPACES, "            "),
        SFToken(SFTokenKind.WORD, "when"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "baz"),
        SFToken(SFTokenKind.NEWLINE, "\n"),
        SFToken(SFTokenKind.SPACES, "            "),
        SFToken(SFTokenKind.WORD, "then"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "2"),
        SFToken(SFTokenKind.NEWLINE, "\n"),
        SFToken(SFTokenKind.SPACES, "            "),
        SFToken(SFTokenKind.WORD, "else"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "3"),
        SFToken(SFTokenKind.NEWLINE, "\n"),
        SFToken(SFTokenKind.SPACES, "             "),
        SFToken(SFTokenKind.WORD, "end"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "as"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "BLERGH"),
        SFToken(SFTokenKind.NEWLINE, "\n"),
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.SYMBOL, ","),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "stuff"),
    ])

    expected = (
        "select foo\n"
        "     , case when bar\n"
        "            then 1\n"
        "            when baz\n"
        "            then 2\n"
        "            else 3\n"
        "             end as BLERGH\n"
        "     , stuff"
    )
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


class TestPoorlyFormattedCase():
    @classmethod
    def teardown_class(cls):
        sf_flags.reset_to_defaults()

    #select foo
    #     , case when bar
    #then 1
    #when baz
    #then 2
    #else 3
    #end as BLERGH
    #     , stuff
    @pytest.fixture
    def tokens(self):
        return [
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "     "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "case"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "when"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.WORD, "then"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "1"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.WORD, "when"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.WORD, "then"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "2"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.WORD, "else"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "3"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.WORD, "end"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "as"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "BLERGH"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "     "),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "stuff"),
        ]

    def test_trim_leading_off(self, tokens, trim_leading_whitespace_off):
        clause = SelectClause(tokens)
        expected = (
            "select foo\n"
            "     , case when bar\n"
            "       then 1\n"
            "       when baz\n"
            "       then 2\n"
            "       else 3\n"
            "       end as BLERGH\n"
            "     , stuff"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual

    def test_trim_leading_on(self, tokens, trim_leading_whitespace_on):
        clause = SelectClause(tokens)
        expected = (
            "select foo\n"
            "     , case when bar\n"
            "       then 1\n"
            "       when baz\n"
            "       then 2\n"
            "       else 3\n"
            "       end as BLERGH\n"
            "     , stuff"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


class TestMultipleExpressionsPerLine():
    @classmethod
    def teardown_class(cls):
        sf_flags.reset_to_defaults()

    #select
    #    foo, bar,
    #    l7, l28, l91,
    #    stuff
    @pytest.fixture
    def tokens(self):
        return [
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "bar"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "l7"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "l28"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "l91"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.NEWLINE, "\n"),
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "stuff"),
        ]

    # again this result is not exactly desirable but nevertheless it's what you get
    # not sure if the trailing spaces should be considered acceptable
    def test_trim_leading_off(self, tokens, trim_leading_whitespace_off):
        clause = SelectClause(tokens)
        expected = (
            "select \n"
            "       foo\n"
            "     , bar\n"
            "     , \n"
            "       l7\n"
            "     , l28\n"
            "     , l91\n"
            "     , \n"
            "       stuff"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual

    def test_trim_leading_on(self, tokens, trim_leading_whitespace_on):
        clause = SelectClause(tokens)
        expected = (
            "select foo\n"
            "     , bar\n"
            "     , l7\n"
            "     , l28\n"
            "     , l91\n"
            "     , stuff"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


class TestRenderScalarSubquery():
    @classmethod
    def teardown_class(cls):
        sf_flags.reset_to_defaults()

    # "select foo, (select count(1) from bar where 1=1), baz"
    @pytest.fixture
    def tokens(self):
        return [
            SFToken(SFTokenKind.WORD, "select"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                SFToken(SFTokenKind.WORD, "select"),
                SFToken(SFTokenKind.SPACES, " "),
                SFToken(SFTokenKind.WORD, "count"),
                Symbols.LEFT_PAREN,
                SFToken(SFTokenKind.WORD, "1"),
                Symbols.RIGHT_PAREN,
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
            SFToken(SFTokenKind.SYMBOL, ","),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "baz"),
        ]

    # off and on should be identical
    def test_trim_leading_off(self, tokens, trim_leading_whitespace_off):
        clause = SelectClause(tokens)
        expected = (
            "select foo\n"
            "     , (select count(1)\n"
            "          from bar\n"
            "         where 1=1\n"
            "       )\n"
            "     , baz"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual

    # off and on should be identical
    def test_trim_leading_on(self, tokens, trim_leading_whitespace_on):
        clause = SelectClause(tokens)
        expected = (
            "select foo\n"
            "     , (select count(1)\n"
            "          from bar\n"
            "         where 1=1\n"
            "       )\n"
            "     , baz"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual
