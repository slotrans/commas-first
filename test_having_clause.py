import pytest

import cf_flags
from cftoken import CFToken, Keywords, Symbols
from cftoken import CFTokenKind
from clause_formatter import HavingClause


# pytest magic
def setup_module():
    cf_flags.reset_to_defaults()


def test_creation_fails_on_empty_input():
    with pytest.raises(ValueError):
        HavingClause(tokens=[])

    with pytest.raises(ValueError):
        HavingClause(tokens=None)


def test_render_zero_expressions():
    clause = HavingClause(tokens=[CFToken(CFTokenKind.WORD, "having")])

    expected = "having"
    actual = clause.render(indent=0)

    assert expected == actual


def test_render_single_expression():
    # "having foo"
    clause = HavingClause(tokens=[
        CFToken(CFTokenKind.WORD, "having"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "foo"),
    ])

    expected = (
        "having foo"
    )
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_single_expression_realistic():
    # "having count(1) > 1"
    clause = HavingClause(tokens=[
        CFToken(CFTokenKind.WORD, "having"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "count"),
        Symbols.LEFT_PAREN,
        CFToken(CFTokenKind.WORD, "1"),
        Symbols.RIGHT_PAREN,
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.SYMBOL, ">"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "1"),
    ])

    expected = (
        "having count(1) > 1"
    )
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_two_expressions_ANDed():
    # "having foo > 1 and bar > 2"
    clause = HavingClause(tokens=[
        CFToken(CFTokenKind.WORD, "having"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "foo"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.SYMBOL, ">"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "1"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "and"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "bar"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.SYMBOL, ">"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "2"),
    ])

    expected = (
        "having foo > 1\n"
        "   and bar > 2"
    )
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual


def test_render_two_expressions_ORed():
    # "having foo > 1 and bar > 2"
    clause = HavingClause(tokens=[
        CFToken(CFTokenKind.WORD, "having"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "foo"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.SYMBOL, ">"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "1"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "or"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "bar"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.SYMBOL, ">"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "2"),
    ])

    expected = (
        "having foo > 1\n"
        "    or bar > 2"
    )
    actual = clause.render(indent=0)

    print(actual)
    assert expected == actual
