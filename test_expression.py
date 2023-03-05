import pytest

import cf_flags
from cftoken import CFToken
from cftoken import CFTokenKind
from cftoken import Symbols
from cftoken import Whitespace
from clause_formatter import Expression


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


class SameAnyWay:
    @classmethod
    def teardown_class(cls):
        cf_flags.reset_to_defaults()

    def actual_test(self):
        raise NotImplementedError

    def test_default(self, mode__default):
        self.actual_test()

    def test_trim_leading_whitespace(self, mode__trim_leading_whitespace):
        self.actual_test()

    def test_compact_expressions(self, mode__compact_expressions):
        self.actual_test()


class TestEmpty(SameAnyWay):
    def actual_test(self):
        actual = Expression([]).render(indent=0)
        expected = ""
        assert expected == actual


class TestLiterals(SameAnyWay):
    def actual_test(self):
        literals = [
            CFToken(CFTokenKind.LITERAL, "'foo'"),
            CFToken(CFTokenKind.WORD, "42"),
            CFToken(CFTokenKind.WORD, "3.14"),
            CFToken(CFTokenKind.WORD, "true"),
            CFToken(CFTokenKind.WORD, "null"),
        ]
        for lit in literals:
            actual = Expression([lit]).render(indent=0)
            expected = lit.value
            assert expected == actual


class TestBasicCompoundExpressions(SameAnyWay):
    def actual_test(self):
        token_sequences = [
            #a + b
            [CFToken(CFTokenKind.WORD, "a"), Whitespace.ONE_SPACE, CFToken(CFTokenKind.SYMBOL, "+"), Whitespace.ONE_SPACE, CFToken(CFTokenKind.WORD, "b")],
            #(1 + 2)
            [Symbols.LEFT_PAREN, CFToken(CFTokenKind.WORD, "1"), Whitespace.ONE_SPACE, CFToken(CFTokenKind.SYMBOL, "+"), Whitespace.ONE_SPACE, CFToken(CFTokenKind.WORD, "2"), Symbols.RIGHT_PAREN],
            #trunc(foo)
            [CFToken(CFTokenKind.WORD, "trunc"), Symbols.LEFT_PAREN, CFToken(CFTokenKind.WORD, "foo"), Symbols.RIGHT_PAREN],
            #round(foo, 0)
            [CFToken(CFTokenKind.WORD, "round"), Symbols.LEFT_PAREN, CFToken(CFTokenKind.WORD, "foo"), Symbols.COMMA, CFToken(CFTokenKind.SPACES, " "), CFToken(CFTokenKind.WORD, "0"), Symbols.RIGHT_PAREN],
            #
        ]
        for tseq in token_sequences:
            expr = Expression(tseq)
            actual = expr.render(indent=0)
            expected = "".join([t.value for t in tseq])
            assert expected == actual


class TestCaseWithNewlines:
    @classmethod
    def teardown_class(cls):
        cf_flags.reset_to_defaults()

    @pytest.fixture
    def tokens(self):
        #case when foo = 0
        #     then 'zero'
        #     when foo = 1
        #     then 'one'
        #     else 'more'
        #      end as HOW_MANY
        return [
            CFToken(CFTokenKind.WORD, "case"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "when"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "0"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "     "),
            CFToken(CFTokenKind.WORD, "then"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.LITERAL, "'zero'"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "     "),
            CFToken(CFTokenKind.WORD, "when"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.SYMBOL, "="),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "1"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "     "),
            CFToken(CFTokenKind.WORD, "then"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.LITERAL, "'one'"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "     "),
            CFToken(CFTokenKind.WORD, "else"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.LITERAL, "'more'"),
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "      "),
            CFToken(CFTokenKind.WORD, "end"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "HOW_MANY"),
        ]

    def test_default(self, tokens, mode__default):
        actual = Expression(tokens).render(indent=0)
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

    def test_trim_leading_whitespace(self, tokens, mode__trim_leading_whitespace):
        actual = Expression(tokens).render(indent=0)
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

    def test_compact_expressions(self, tokens, mode__compact_expressions):
        actual = Expression(tokens).render(indent=0)
        expected = (
            "case when foo = 0 then 'zero' when foo = 1 then 'one' else 'more' end as HOW_MANY"
        )
        print(actual)
        assert expected == actual


class TestExpressionWhitespaceTrimmingTrivial:
    @classmethod
    def teardown_class(cls):
        cf_flags.reset_to_defaults()

    @pytest.fixture
    def tokens(self):
        return [
            CFToken(CFTokenKind.SPACES, "  "),
            CFToken(CFTokenKind.WORD, "sysdate"),
            CFToken(CFTokenKind.SPACES, " "),
        ]

    def test_default(self, tokens, mode__default):
        actual = Expression(tokens).render(indent=0)
        expected = " sysdate"
        assert expected == actual

    def test_trim_leading_whitespace(self, tokens, mode__trim_leading_whitespace):
        actual = Expression(tokens).render(indent=0)
        expected = "sysdate"
        assert expected == actual

    def test_compact_expressions(self, tokens, mode__compact_expressions):
        actual = Expression(tokens).render(indent=0)
        expected = "sysdate"
        assert expected == actual


class TestExpressionWhitespaceTrimmingTrailingComma:
    @classmethod
    def teardown_class(cls):
        cf_flags.reset_to_defaults()

    @pytest.fixture
    def tokens(self):
        return [
            Whitespace.NEWLINE,
            CFToken(CFTokenKind.SPACES, "    "),
            CFToken(CFTokenKind.WORD, "foo"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "as"),
            CFToken(CFTokenKind.SPACES, " "),
            CFToken(CFTokenKind.WORD, "BAR"),
        ]

    def test_default(self, tokens, mode__default):
        actual = Expression(tokens).render(indent=0)
        expected = "\n    foo as BAR"
        assert expected == actual

    def test_trim_leading_whitespace(self, tokens, mode__trim_leading_whitespace):
        actual = Expression(tokens).render(indent=0)
        expected = "foo as BAR"
        assert expected == actual

    def test_compact_expressions(self, tokens, mode__compact_expressions):
        actual = Expression(tokens).render(indent=0)
        expected = "foo as BAR"
        assert expected == actual
