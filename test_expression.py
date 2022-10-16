import pytest

from sftoken import SFToken
from sftoken import SFTokenKind
from sftoken import Symbols
from sftoken import Whitespace
from clause_formatter import Expression
from clause_formatter import RenderingContext


class SameEitherWay:
    def actual_test(self, trim_leading_whitespace):
        raise NotImplementedError

    def test_trim_leading_off(self):
        self.actual_test(trim_leading_whitespace=False)

    def test_trim_leading_on(self):
        self.actual_test(trim_leading_whitespace=True)


class TestEmpty(SameEitherWay):
    def actual_test(self, trim_leading_whitespace):
        actual = Expression([]).render(RenderingContext(indent=0, trim_leading_whitespace=trim_leading_whitespace))
        expected = ""
        assert expected == actual


class TestLiterals(SameEitherWay):
    def actual_test(self, trim_leading_whitespace):
        literals = [
            SFToken(SFTokenKind.LITERAL, "'foo'"),
            SFToken(SFTokenKind.WORD, "42"),
            SFToken(SFTokenKind.WORD, "3.14"),
            SFToken(SFTokenKind.WORD, "true"),
            SFToken(SFTokenKind.WORD, "null"),
        ]
        for lit in literals:
            actual = Expression([lit]).render(RenderingContext(indent=0, trim_leading_whitespace=trim_leading_whitespace))
            expected = lit.value
            assert expected == actual


class TestBasicCompoundExpressions(SameEitherWay):
    def actual_test(self, trim_leading_whitespace):
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
            actual = expr.render(RenderingContext(indent=0, trim_leading_whitespace=trim_leading_whitespace))
            expected = "".join([t.value for t in tseq])
            assert expected == actual


class TestCaseWithNewlines(SameEitherWay):
    def actual_test(self, trim_leading_whitespace):
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
        actual = expr.render(RenderingContext(indent=0, trim_leading_whitespace=trim_leading_whitespace))
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


class TestExpressionWhitespaceTrimmingTrivial:
    @pytest.fixture
    def tokens(self):
        return [
            SFToken(SFTokenKind.SPACES, "  "),
            SFToken(SFTokenKind.WORD, "sysdate"),
            SFToken(SFTokenKind.SPACES, " "),
        ]

    def test_trim_leading_off(self, tokens):
        actual = Expression(tokens).render(RenderingContext(indent=0, trim_leading_whitespace=False))
        expected = " sysdate"
        assert expected == actual

    def test_trim_leading_on(self, tokens):
        actual = Expression(tokens).render(RenderingContext(indent=0, trim_leading_whitespace=True))
        expected = "sysdate"
        assert expected == actual


class TestExpressionWhitespaceTrimmingTrailingComma:
    @pytest.fixture
    def tokens(self):
        return [
            Whitespace.NEWLINE,
            SFToken(SFTokenKind.SPACES, "    "),
            SFToken(SFTokenKind.WORD, "foo"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "as"),
            SFToken(SFTokenKind.SPACES, " "),
            SFToken(SFTokenKind.WORD, "BAR"),
        ]

    def test_trim_leading_off(self, tokens):
        actual = Expression(tokens).render(RenderingContext(indent=0, trim_leading_whitespace=False))
        expected = "\n    foo as BAR"
        assert expected == actual

    def test_trim_leading_on(self, tokens):
        actual = Expression(tokens).render(RenderingContext(indent=0, trim_leading_whitespace=True))
        expected = "foo as BAR"
        assert expected == actual
