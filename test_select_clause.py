import pytest

import cf_flags
from cftoken import CFToken
from cftoken import CFTokenKind
from cftoken import Symbols
from cftoken import Whitespace
from clause_formatter import SelectClause
from clause_formatter import CompoundStatement


# pytest magic
def setup_module():
    cf_flags.reset_to_defaults()


@pytest.fixture
def mode__default():
    cf_flags.FORMAT_MODE = cf_flags.FormatMode.DEFAULT


@pytest.fixture
def mode__trim_leading_whitespace():
    cf_flags.FORMAT_MODE = cf_flags.FormatMode.TRIM_LEADING_WHITESPACE


@pytest.fixture
def mode__compact_expressions():
    cf_flags.FORMAT_MODE = cf_flags.FormatMode.COMPACT_EXPRESSIONS


def test_creation_fails_on_empty_input():
    with pytest.raises(ValueError):
        SelectClause(tokens=[])

    with pytest.raises(ValueError):
        SelectClause(tokens=None)


def test_render_zero_expressions():
    clause = SelectClause(tokens=[CFToken(CFTokenKind.WORD, "select")])

    expected = "select"
    actual = clause.render(indent=0)

    assert expected == actual


def test_render_simple_expressions_no_qualifier():
    # "select foo, bar, baz"
    clause = SelectClause(tokens=[
        CFToken(CFTokenKind.WORD, "select"),
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
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "bar"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.LINE_COMMENT, "--LINE COMMENT\n"),
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "baz"),
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


def test_render_simple_expressions_line_comment_no_qualifier2():
    #select foo
    #     , bar
    #--LINE COMMENT
    #     , baz
    clause = SelectClause(tokens=[
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "bar"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.LINE_COMMENT, "--LINE COMMENT\n"),
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "baz"),
    ])

    expected = (
        "select foo\n"
        "     , bar\n"
        "--LINE COMMENT\n"
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
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "bar"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.BLOCK_COMMENT, "/* BLOCK\n        COMMENT */"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "baz"),
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
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "bar"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.BLOCK_COMMENT, "/* BLOCK\n   COMMENT */"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "baz"),
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


def test_render_simple_expressions_block_comment_no_qualifier3():
    #select foo
    #     , bar /* BLOCK
    #              COMMENT */
    #     , baz
    clause = SelectClause(tokens=[
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "bar"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.BLOCK_COMMENT, "/* BLOCK\n              COMMENT */"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "baz"),
    ])

    expected = (
        "select foo\n"
        "     , bar /* BLOCK\n"
        "              COMMENT */\n"
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
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "coalesce"),
        CFToken(CFTokenKind.SYMBOL, "("),
        CFToken(CFTokenKind.WORD, "bar"),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "0"),
        CFToken(CFTokenKind.SYMBOL, ")"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "case"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "when"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "active"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "            "),
        CFToken(CFTokenKind.WORD, "then"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "1"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "            "),
        CFToken(CFTokenKind.WORD, "else"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "0"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "             "),
        CFToken(CFTokenKind.WORD, "end"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "as"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "ACTIVE_INT"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "lag"),
        CFToken(CFTokenKind.SYMBOL, "("),
        CFToken(CFTokenKind.WORD, "blergh"),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.WORD, "1"),
        CFToken(CFTokenKind.SYMBOL, ")"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "over"),
        CFToken(CFTokenKind.SYMBOL, "("),
        CFToken(CFTokenKind.WORD, "partition"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "by"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "foo"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "order"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "by"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "bar"),
        CFToken(CFTokenKind.SYMBOL, ")"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "as"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "PREV_BLERGH"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.SYMBOL, "("),
        CFToken(CFTokenKind.SPACES, "   "),
        CFToken(CFTokenKind.WORD, "beep"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.SYMBOL, ">"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "0"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "        "),
        CFToken(CFTokenKind.WORD, "or"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "boop"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.SYMBOL, ">"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "0"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "       "),
        CFToken(CFTokenKind.SYMBOL, ")"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "as"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "BEEP_BOOP"),
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
        CFToken(CFTokenKind.WORD, "select"),
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
        cf_flags.reset_to_defaults()

    #select
    #    foo,
    #    bar,
    #    baz
    @pytest.fixture
    def tokens(self):
        return [
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "baz"),
        ]

    # this is kind of a silly test in that this behavior is not particularly _desirable_,
    # but it is what you get from this input in this mode
    def test_default(self, tokens, mode__default):
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

    def test_trim_leading_whitespace(self, tokens, mode__trim_leading_whitespace):
        clause = SelectClause(tokens)
        expected = (
            "select foo\n"
            "     , bar\n"
            "     , baz"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual

    def test_compact_expressions(self, tokens, mode__compact_expressions):
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
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "bar"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "baz"),
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
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "distinct"),
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
        "select distinct\n"
        "       foo\n"
        "     , bar\n"
        "     , baz"
    )
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_simple_expressions_distinct_qualifier_indented():
    # "select distinct foo, bar, baz"
    clause = SelectClause(tokens=[
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "distinct"),
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
            "select distinct\n"
        "           foo\n"
        "         , bar\n"
        "         , baz"
    )
    actual = clause.render(indent=4)

    print(actual)
    assert expected == actual


def test_render_simple_expressions_distinct_qualifier_preformatted():
    # select distinct
    #        foo
    #      , bar
    #      , baz
    clause = SelectClause(tokens=[
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "distinct"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "       "),
        CFToken(CFTokenKind.WORD, "foo"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "bar"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "baz"),
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
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "distinct"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "         "),
        CFToken(CFTokenKind.WORD, "z"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, "  "),
        CFToken(CFTokenKind.WORD, "yz"),
        Whitespace.NEWLINE,
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "xyz"),
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
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "all"),
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
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "distinct on"),
        CFToken(CFTokenKind.SYMBOL, "("),
        CFToken(CFTokenKind.WORD, "foo"),
        CFToken(CFTokenKind.SYMBOL, ")"),
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
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "distinct"),
    ])

    expected = "select distinct"
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_qualifier_only2():
    # "select all"
    clause = SelectClause(tokens=[
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "all"),
    ])

    expected = "select all"
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


class TestCustomSpacing:
    @classmethod
    def teardown_class(cls):
        cf_flags.reset_to_defaults()

    #select foo
    #     ,   l7
    #     ,  l30
    #     , l182
    @pytest.fixture
    def tokens(self):
        return [
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "     "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, "   "),
            CFToken(CFTokenKind.WORD, "l7"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "     "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "l30"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "     "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "l182"),
        ]

    def test_default(self, tokens, mode__default):
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

    def test_trim_leading_whitespace(self, tokens, mode__trim_leading_whitespace):
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

    def test_compact_expressions(self, tokens, mode__compact_expressions):
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
        CFToken(CFTokenKind.WORD, "select"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "foo"),
        CFToken(CFTokenKind.NEWLINE, "\n"),
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "case"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "when"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "bar"),
        CFToken(CFTokenKind.NEWLINE, "\n"),
        CFToken(CFTokenKind.SPACES, "            "),
        CFToken(CFTokenKind.WORD, "then"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "1"),
        CFToken(CFTokenKind.NEWLINE, "\n"),
        CFToken(CFTokenKind.SPACES, "            "),
        CFToken(CFTokenKind.WORD, "when"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "baz"),
        CFToken(CFTokenKind.NEWLINE, "\n"),
        CFToken(CFTokenKind.SPACES, "            "),
        CFToken(CFTokenKind.WORD, "then"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "2"),
        CFToken(CFTokenKind.NEWLINE, "\n"),
        CFToken(CFTokenKind.SPACES, "            "),
        CFToken(CFTokenKind.WORD, "else"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "3"),
        CFToken(CFTokenKind.NEWLINE, "\n"),
        CFToken(CFTokenKind.SPACES, "             "),
        CFToken(CFTokenKind.WORD, "end"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "as"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "BLERGH"),
        CFToken(CFTokenKind.NEWLINE, "\n"),
        CFToken(CFTokenKind.SPACES, "     "),
        CFToken(CFTokenKind.SYMBOL, ","),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "stuff"),
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
        cf_flags.reset_to_defaults()

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
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "     "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "case"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "when"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.WORD, "then"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.WORD, "when"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.WORD, "then"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "2"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.WORD, "else"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "3"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.WORD, "end"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "BLERGH"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "     "),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "stuff"),
        ]

    def test_default(self, tokens, mode__default):
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

    def test_trim_leading_whitespace(self, tokens, mode__trim_leading_whitespace):
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

    def test_compact_expressions(self, tokens, mode__compact_expressions):
        clause = SelectClause(tokens)
        expected = (
            "select foo\n"
            "     , case when bar then 1 when baz then 2 else 3 end as BLERGH\n"
            "     , stuff"
        )
        actual = clause.render(indent=0)

        print(actual)
        assert expected == actual


class TestMultipleExpressionsPerLine():
    @classmethod
    def teardown_class(cls):
        cf_flags.reset_to_defaults()

    #select
    #    foo, bar,
    #    l7, l28, l91,
    #    stuff
    @pytest.fixture
    def tokens(self):
        return [
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "bar"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "l7"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "l28"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "l91"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.NEWLINE, "\n"),
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "stuff"),
        ]

    # again this result is not exactly desirable but nevertheless it's what you get
    # not sure if the trailing spaces should be considered acceptable
    def test_default(self, tokens, mode__default):
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

    def test_trim_leading_whitespace(self, tokens, mode__trim_leading_whitespace):
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

    def test_compact_expressions(self, tokens, mode__compact_expressions):
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
        cf_flags.reset_to_defaults()

    # "select foo, (select count(1) from bar where 1=1), baz"
    @pytest.fixture
    def tokens(self):
        return [
            CFToken(CFTokenKind.WORD, "select"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            Symbols.LEFT_PAREN,
            CompoundStatement([
                CFToken(CFTokenKind.WORD, "select"),
                CFToken(CFTokenKind.SPACES, " "),
                CFToken(CFTokenKind.WORD, "count"),
                Symbols.LEFT_PAREN,
                CFToken(CFTokenKind.WORD, "1"),
                Symbols.RIGHT_PAREN,
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
            CFToken(CFTokenKind.SYMBOL, ","),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "baz"),
        ]

    # formatting mode doesn't affect this one

    def test_default(self, tokens, mode__default):
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

    def test_trim_leading_whitespace(self, tokens, mode__trim_leading_whitespace):
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

    def test_compact_expressions(self, tokens, mode__compact_expressions):
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
