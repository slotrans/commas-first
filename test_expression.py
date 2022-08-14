import pytest

import sf_flags
from sftoken import SFToken
from sftoken import SFTokenKind
from sftoken import Symbols
from sftoken import Whitespace
from clause_formatter import Expression


# pytest magic
def setup_module():
    sf_flags.reset_to_defaults()


def test_empty():
    tokens = []
    expr = Expression(tokens)
    actual = expr.render(indent=0)
    expected = ""
    assert expected == actual


def test_literals():
    literals = [
        SFToken(SFTokenKind.LITERAL, "'foo'"),
        SFToken(SFTokenKind.WORD, "42"),
        SFToken(SFTokenKind.WORD, "3.14"),
        SFToken(SFTokenKind.WORD, "true"),
        SFToken(SFTokenKind.WORD, "null"),
    ]
    for lit in literals:
        expr = Expression([lit])
        actual = expr.render(indent=0)
        expected = lit.value
        assert expected == actual


def test_basic_compound_expressions():
    token_sequences = [
        #a + b
        [SFToken(SFTokenKind.WORD, "a"), Whitespace.ONE_SPACE, SFToken(SFTokenKind.SYMBOL, "+"), Whitespace.ONE_SPACE, SFToken(SFTokenKind.WORD, "b")],
        #(1 + 2)
        [Symbols.LEFT_PAREN, SFToken(SFTokenKind.WORD, "1"), Whitespace.ONE_SPACE, SFToken(SFTokenKind.SYMBOL, "+"), Whitespace.ONE_SPACE, SFToken(SFTokenKind.WORD, "2"), Symbols.RIGHT_PAREN],
        #trunc(foo)
        [],
        #round(foo, 0)
        [],
        #
    ]
    for tseq in token_sequences:
        expr = Expression(tseq)
        actual = expr.render(indent=0)
        expected = "".join([t.value for t in tseq])
        assert expected == actual


def test_case_with_newlines():
    #case when foo = 0
    #     then 'zero'
    #     when foo = 1
    #     then 'one'
    #     else 'more'
    #      end as HOW_MANY
    expr = Expression([
        SFToken(SFTokenKind.WORD, "case"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "when"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "foo"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.SYMBOL, "="),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "0"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.WORD, "then"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.LITERAL, "'zero'"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.WORD, "when"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "foo"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.SYMBOL, "="),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "1"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.WORD, "then"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.LITERAL, "'one'"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "     "),
        SFToken(SFTokenKind.WORD, "else"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.LITERAL, "'more'"),
        Whitespace.NEWLINE,
        SFToken(SFTokenKind.SPACES, "      "),
        SFToken(SFTokenKind.WORD, "end"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "as"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "HOW_MANY"),
    ])
    actual = expr.render(indent=0)
    expected = (
        "case when foo = 0\n"
        "     then 'zero'\n"
        "     when foo = 1\n"
        "     then 'one'\n"
        "     else 'more'\n"
        "      end as HOW_MANY"
    )
    print(actual)
    assert expected == actual


@pytest.fixture
def trim_leading_whitespace_off():
    sf_flags.TRIM_LEADING_WHITESPACE = False

@pytest.fixture
def trim_leading_whitespace_on():
    sf_flags.TRIM_LEADING_WHITESPACE = True

class TestExpressionWhitespaceTrimming:
    @pytest.fixture
    def tokens(self):
        return [
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "sysdate"),
            SFToken(SFTokenKind.SPACES, " "),            
        ]

    def test_trim_leading_off(self, tokens, trim_leading_whitespace_off):
        actual = Expression(tokens).render(indent=0)
        expected = " sysdate"
        assert expected == actual

    def test_trim_leading_on(self, tokens, trim_leading_whitespace_on):
        actual = Expression(tokens).render(indent=0)
        expected = "sysdate"
        assert expected == actual


# TODO: convert the inputs into pytest fixtures, or just simple values, so that we can re-use them as inputs for all flag cases
# maybe each of these functions needs to be a class? and then the input can sit in the class and each flag case can be a method?
