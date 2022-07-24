import pytest

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

import retokenize
from sftoken import SFToken, SFTokenKind


lexer = get_lexer_by_name("postgres", stripall=True)


### FIRST PASS

def test_simple_string_literal():
    tokens = list(lexer.get_tokens("'String Literal'")) # [(Token.Literal.String.Single, "'"), (Token.Literal.String.Single, 'String Literal'), (Token.Literal.String.Single, "'")]
    actual_token, actual_consumed = retokenize.get_single_quoted_literal(tokens)
    expected_token = (Token.Literal.String.Single, "'String Literal'")
    expected_consumed = 3
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_string_literal_with_quotes():
    tokens = list(lexer.get_tokens("'Bob''s'")) # [(Token.Literal.String.Single, "'"), (Token.Literal.String.Single, 'bob'), (Token.Literal.String.Single, "''"), (Token.Literal.String.Single, 's'), (Token.Literal.String.Single, "'")]
    actual_token, actual_consumed = retokenize.get_single_quoted_literal(tokens)
    expected_token = (Token.Literal.String.Single, "'Bob''s'")
    expected_consumed = 5
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_broken_string_literal():
    tokens = list(lexer.get_tokens("'broken literal")) # [(Token.Literal.String.Single, "'"), (Token.Literal.String.Single, 'broken literal\n')]
    actual_token, actual_consumed = retokenize.get_single_quoted_literal(tokens)
    expected_token, expected_consumed = (None, None)
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_simple_dollar_quoted_literal():
    tokens = list(lexer.get_tokens("$$dollar literal$$")) # [(Token.Literal.String, '$'), (Token.Literal.String.Delimiter, ''), (Token.Literal.String, '$'), (Token.Literal.String, 'dollar literal'), (Token.Literal.String, '$'), (Token.Literal.String.Delimiter, ''), (Token.Literal.String, '$')]
    actual_token, actual_consumed = retokenize.get_dollar_quoted_literal(tokens)
    expected_token = (Token.Literal.String, "$$dollar literal$$")
    expected_consumed = 7
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_custom_dollar_quoted_literal():
    tokens = list(lexer.get_tokens("$body$dollar literal$body$")) # [(Token.Literal.String, '$'), (Token.Literal.String.Delimiter, 'body'), (Token.Literal.String, '$'), (Token.Literal.String, 'dollar literal'), (Token.Literal.String, '$'), (Token.Literal.String.Delimiter, 'body'), (Token.Literal.String, '$')]
    actual_token, actual_consumed = retokenize.get_dollar_quoted_literal(tokens)
    expected_token = (Token.Literal.String, "$body$dollar literal$body$")
    expected_consumed = 7
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_double_quoted_identifier():
    tokens = list(lexer.get_tokens('"IdEnTiFiEr"')) # [(Token.Literal.String.Name, '"'), (Token.Literal.String.Name, 'IdEnTiFiEr'), (Token.Literal.String.Name, '"')]
    actual_token, actual_consumed = retokenize.get_quoted_name(tokens)
    expected_token = (Token.Literal.String.Name, '"IdEnTiFiEr"')
    expected_consumed = 3
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_backtick_quoted_identifier():
    tokens = list(lexer.get_tokens('`IdEnTiFiEr`')) # [(Token.Operator, '`'), (Token.Name, 'IdEnTiFiEr'), (Token.Operator, '`')]
    actual_token, actual_consumed = retokenize.get_quoted_name(tokens)
    expected_token = (Token.Literal.String.Name, '`IdEnTiFiEr`')
    expected_consumed = 3
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_broken_double_quoted_identifier():
    tokens = list(lexer.get_tokens('"broken identifier')) # [(Token.Literal.String.Name, '"'), (Token.Literal.String.Name, 'broken identifier\n')]
    actual_token, actual_consumed = retokenize.get_quoted_name(tokens)
    expected_token, expected_consumed = (None, None)
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_broken_backtick_quoted_identifier():
    tokens = list(lexer.get_tokens('`broken identifier')) # [(Token.Operator, '`'), (Token.Name, 'broken'), (Token.Text.Whitespace, ' '), (Token.Keyword, 'identifier')]
    actual_token, actual_consumed = retokenize.get_quoted_name(tokens)
    expected_token, expected_consumed = (None, None)
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_block_comment():
    tokens = list(lexer.get_tokens('/* blergh */')) # [(Token.Comment.Multiline, '/*'), (Token.Comment.Multiline, ' blergh '), (Token.Comment.Multiline, '*/')]
    actual_token, actual_consumed = retokenize.get_block_comment(tokens)
    expected_token = (Token.Comment.Multiline, '/* blergh */')
    expected_consumed = 3
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_nested_block_comment():
    tokens = list(lexer.get_tokens('/* /* blergh */ */')) # [(Token.Comment.Multiline, '/*'), (Token.Comment.Multiline, ' '), (Token.Comment.Multiline, '/*'), (Token.Comment.Multiline, ' blergh '), (Token.Comment.Multiline, '*/'), (Token.Comment.Multiline, ' '), (Token.Comment.Multiline, '*/'), (Token.Text.Whitespace, '\n')]
    actual_token, actual_consumed = retokenize.get_block_comment(tokens)
    expected_token = (Token.Comment.Multiline, '/* /* blergh */ */')
    expected_consumed = 7
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_broken_block_comment():
    tokens = list(lexer.get_tokens('/* blergh')) # [(Token.Comment.Multiline, '/*'), (Token.Comment.Multiline, ' blergh ')]
    actual_token, actual_consumed = retokenize.get_block_comment(tokens)
    expected_token, expected_consumed = (None, None)
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_two_word_key_phrases():
    phrases = [
        'cross join',
        'distinct on',
        'left join',
        'right join',
        'group by',
        'order by',
        'partition by',
        'within group',
        'is false',
        'is null',
        'is true',
        'is unknown',
        'not between',
        'between symmetric',
        'union all',
        'union distinct',
        'except all',
        'except distinct',
        'intersect all',
        'intersect distinct',
    ]
    for phrase in phrases:
        tokens = list(lexer.get_tokens(phrase))
        actual_token, actual_consumed = retokenize.get_two_word_key_phrase(tokens)
        expected_token = (Token.Keyword, phrase)
        expected_consumed = 3 # 2 words plus 1 whitespace separator
        assert expected_token == actual_token
        assert expected_consumed == actual_consumed


def test_three_word_key_phrases():
    phrases = [
        'left outer join',
        'right outer join',
        'full outer join',
        'is not false',
        'is not null',
        'is not true',
        'is not unknown',
        'is distinct from',
        'not between symmetric',
        'at time zone',
    ]
    for phrase in phrases:
        tokens = list(lexer.get_tokens(phrase))
        actual_token, actual_consumed = retokenize.get_three_word_key_phrase(tokens)
        expected_token = (Token.Keyword, phrase)
        expected_consumed = 5 # 3 words plus 2 whitespace separators
        assert expected_token == actual_token
        assert expected_consumed == actual_consumed


def test_four_word_key_phrases():
    phrases = [
        'is not distinct from',
    ]
    for phrase in phrases:
        tokens = list(lexer.get_tokens(phrase))
        actual_token, actual_consumed = retokenize.get_four_word_key_phrase(tokens)
        expected_token = (Token.Keyword, phrase)
        expected_consumed = 7 # 4 words plus 3 whitespace separators
        assert expected_token == actual_token
        assert expected_consumed == actual_consumed


#TODO: whitespace tests


### SECOND PASS

def test_qualified_identifier_one_dot():
    tokens = retokenize.retokenize1(list(lexer.get_tokens("foo.bar"))) # [(Token.Name, 'foo'), (Token.Literal.Number.Float, '.'), (Token.Name, 'bar')]
    actual_token, actual_consumed = retokenize.get_qualified_identifier(tokens)
    expected_token = (Token.Name, "foo.bar")
    expected_consumed = 3
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_two_dots():
    tokens = retokenize.retokenize1(list(lexer.get_tokens("foo.bar.baz"))) # [(Token.Name, 'foo'), (Token.Literal.Number.Float, '.'), (Token.Name, 'bar'), (Token.Literal.Number.Float, '.'), (Token.Name, 'baz')]
    actual_token, actual_consumed = retokenize.get_qualified_identifier(tokens)
    expected_token = (Token.Name, "foo.bar.baz")
    expected_consumed = 5
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_three_dots():
    tokens = retokenize.retokenize1(list(lexer.get_tokens("foo.bar.baz.idk"))) # [(Token.Name, 'foo'), (Token.Literal.Number.Float, '.'), (Token.Name, 'bar'), (Token.Literal.Number.Float, '.'), (Token.Name, 'baz'), (Token.Literal.Number.Float, '.'), (Token.Name, 'idk')]
    actual_token, actual_consumed = retokenize.get_qualified_identifier(tokens)
    expected_token = (Token.Name, "foo.bar.baz.idk")
    expected_consumed = 7
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_with_quotes_one_dot():
    tokens = retokenize.retokenize1(list(lexer.get_tokens('"Alice"."Bob"'))) # [(Token.Name, '"Alice"'), (Token.Literal.Number.Float, '.'), (Token.Name, '"Bob"')]
    actual_token, actual_consumed = retokenize.get_qualified_identifier(tokens)
    expected_token = (Token.Name, '"Alice"."Bob"')
    expected_consumed = 3
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_with_quotes_two_dots():
    tokens = retokenize.retokenize1(list(lexer.get_tokens('"Alice"."Bob"."Cindy"'))) # [(Token.Name, '"Alice"'), (Token.Literal.Number.Float, '.'), (Token.Name, '"Bob"'), (Token.Literal.Number.Float, '.'), (Token.Name, '"Cindy"')]
    actual_token, actual_consumed = retokenize.get_qualified_identifier(tokens)
    expected_token = (Token.Name, '"Alice"."Bob"."Cindy"')
    expected_consumed = 5
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


### TRANSLATION

def test_translation_of_integer_literal():
    token = (Token.Literal.Number.Float, "42")
    actual = retokenize.pygments_token_to_sftoken(token)
    expected = SFToken(SFTokenKind.LITERAL, "42")
    assert expected == actual

def test_translation_of_ordinary_float_literal():
    token = (Token.Literal.Number.Float, "3.14")
    actual = retokenize.pygments_token_to_sftoken(token)
    expected = SFToken(SFTokenKind.LITERAL, "3.14")
    assert expected == actual

def test_translation_of_scientific_float_literal():
    token = (Token.Literal.Number.Float, "1e6")
    actual = retokenize.pygments_token_to_sftoken(token)
    expected = SFToken(SFTokenKind.LITERAL, "1e6")
    assert expected == actual

def test_translation_of_string_literal():
    token = (Token.Literal.String.Single, "'string literal'")
    actual = retokenize.pygments_token_to_sftoken(token)
    expected = SFToken(SFTokenKind.LITERAL, "'string literal'")
    assert expected == actual

def test_translation_of_unquoted_single_qualified_identifier():
    token = (Token.Name, "foo.bar")
    actual = retokenize.pygments_token_to_sftoken(token)
    expected = SFToken(SFTokenKind.WORD, "foo.bar")
    assert expected == actual

def test_translation_of_quoted_single_qualified_identifier():
    token = (Token.Name, '"foo"."bar"')
    actual = retokenize.pygments_token_to_sftoken(token)
    expected = SFToken(SFTokenKind.LITERAL, '"foo"."bar"')
    assert expected == actual

def test_translation_of_unquoted_double_qualified_identifier():
    token = (Token.Name, "foo.bar.baz")
    actual = retokenize.pygments_token_to_sftoken(token)
    expected = SFToken(SFTokenKind.WORD, "foo.bar.baz")
    assert expected == actual

def test_translation_of_quoted_double_qualified_identifier():
    token = (Token.Name, '"foo"."bar"."baz"')
    actual = retokenize.pygments_token_to_sftoken(token)
    expected = SFToken(SFTokenKind.LITERAL, '"foo"."bar"."baz"')
    assert expected == actual

def test_translation_of_operators():
    for token in [
        # these are sorted
        (Token.Operator, '!='),
        (Token.Operator, '!~'),
        (Token.Operator, '!~*'),
        (Token.Operator, '##'),
        (Token.Operator, '#-#'),
        (Token.Operator, '&&'),
        (Token.Operator, '&<'),
        (Token.Operator, '&<|'),
        (Token.Operator, '&>'),
        (Token.Operator, '*'),
        (Token.Operator, '+'),
        (Token.Operator, '-'),
        (Token.Operator, '/'),
        (Token.Operator, '::'),
        (Token.Operator, '<'),
        (Token.Operator, '<<'),
        (Token.Operator, '<<|'),
        (Token.Operator, '<='),
        (Token.Operator, '<@'),
        (Token.Operator, '<^'),
        (Token.Operator, '='),
        (Token.Operator, '>'),
        (Token.Operator, '>='),
        (Token.Operator, '>>'),
        (Token.Operator, '>^'),
        (Token.Operator, '?#'),
        (Token.Operator, '?-|'),
        (Token.Operator, '?|'),
        (Token.Operator, '?||'),
        (Token.Operator, '@-@'),
        (Token.Operator, '@>'),
        (Token.Operator, '@@'),
        (Token.Operator, '^'),
        (Token.Operator, '|&>'),
        (Token.Operator, '|/'),
        (Token.Operator, '|>>'),
        (Token.Operator, '||/'),
        (Token.Operator, '~'),
        (Token.Operator, '~*'),
        (Token.Operator, '~='),
        # there are more...
    ]:
        actual = retokenize.pygments_token_to_sftoken(token)
        expected = SFToken(SFTokenKind.SYMBOL, token[1])
        assert expected == actual

def test_translation_of_punctuation():
    for token in [
        (Token.Punctuation, '('),
        (Token.Punctuation, ')'),
        (Token.Punctuation, ','),
        (Token.Punctuation, '.'), # I've never observed "." to come out as Token.Punctuation rather than Token.Literal.Number.Float
        (Token.Punctuation, ':'), # when would this ever...?
        (Token.Punctuation, ';'),
        (Token.Punctuation, '['),
        (Token.Punctuation, ']'),
        (Token.Punctuation, '{'),
        (Token.Punctuation, '}'),
    ]:
        actual = retokenize.pygments_token_to_sftoken(token)
        expected = SFToken(SFTokenKind.SYMBOL, token[1])
        assert expected == actual

def test_translation_of_spaces():
    for token in [
        (Token.Text.Whitespace, " "),
        (Token.Text.Whitespace, "  "),
        (Token.Text.Whitespace, "   "),
        (Token.Text.Whitespace, "    "),
        # you get the point
    ]:
        actual = retokenize.pygments_token_to_sftoken(token)
        expected = SFToken(SFTokenKind.SPACES, token[1])
        assert expected == actual

def test_translation_of_newline():
    token = (Token.Text.Whitespace, "\n")
    actual = retokenize.pygments_token_to_sftoken(token)
    expected = SFToken(SFTokenKind.NEWLINE, token[1])
    assert expected == actual

def test_translation_of_block_comment():
    token = (Token.Comment.Multiline, "/* block comment */")
    actual = retokenize.pygments_token_to_sftoken(token)
    expected = SFToken(SFTokenKind.BLOCK_COMMENT, token[1])
    assert expected == actual

def test_translation_of_line_comment():
    token = (Token.Comment.Single, "--line comment\n")
    actual = retokenize.pygments_token_to_sftoken(token)
    expected = SFToken(SFTokenKind.LINE_COMMENT, token[1])
    assert expected == actual


### DRIVERS

def test_retokenize1_grouped_count():
    tokens = list(lexer.get_tokens("select foo, count(1) from bar where 1=1 group by foo order by foo"))
    actual_tokens = retokenize.retokenize1(tokens)
    expected_tokens = [
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'foo'),
        (Token.Punctuation, ','),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'count'),
        (Token.Punctuation, '('),
        (Token.Literal.Number.Float, '1'),
        (Token.Punctuation, ')'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'from'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'bar'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'where'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '1'),
        (Token.Operator, '='),
        (Token.Literal.Number.Float, '1'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'group by'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'foo'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'order by'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'foo'),
        (Token.Text.Whitespace, '\n'),
    ]
    assert expected_tokens == actual_tokens


def test_retokenize1_four_word_phrases():
    sql = (
        "select foo is not distinct from bar\n"
        "  from baz"
    )
    tokens = list(lexer.get_tokens(sql))
    actual_tokens = retokenize.retokenize1(tokens)
    expected_tokens = [
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'foo'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'is not distinct from'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'bar'),
        #(Token.Text.Whitespace, '\n'),
        #(Token.Text.Whitespace, '  '),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'from'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'baz'),
        (Token.Text.Whitespace, '\n'),
    ]
    assert expected_tokens == actual_tokens


def test_retokenize1_three_word_phrases():
    # this is not a sane query, btw
    sql = (
        "select foo is distinct from bar\n"
        "     , event_dt at time zone 'UTC'\n"
        "  from baz\n"
        "  left outer join table1\n"
        "  right outer join table2\n"
        "  full outer join table3\n"
        " where event_dt is not null\n"
        "   and flerb not between symmetric 1 and 9"
    )
    tokens = list(lexer.get_tokens(sql))
    actual_tokens = retokenize.retokenize1(tokens)
    expected_tokens = [
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'foo'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'is distinct from'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'bar'),
        (Token.Text.Whitespace, '\n     '),
        (Token.Punctuation, ','),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'event_dt'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'at time zone'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.String.Single, "'UTC'"),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'from'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'baz'),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'left outer join'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'table1'),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'right outer join'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'table2'),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'full outer join'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'table3'),
        (Token.Text.Whitespace, '\n '),
        (Token.Keyword, 'where'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'event_dt'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'is not null'),
        (Token.Text.Whitespace, '\n   '),
        (Token.Keyword, 'and'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'flerb'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'not between symmetric'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '1'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'and'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '9'),
        (Token.Text.Whitespace, '\n'),
    ]
    assert expected_tokens == actual_tokens


def test_retokenize1_two_word_phrases_group1():
    # this is not a sane or even valid query, btw
    sql = (
        "select distinct on(foo)\n"
        "     , foo\n"
        "     , count(bar) over(partition by foo)\n"
        "     , percentile_cont(0.5) within group(order by foo)\n"
        "  from baz\n"
        "  left join table1\n"
        "  right join table2\n"
        "  natural join table3\n"
        "  lateral join table4\n"
        "  cross join table5\n"
        " where something is null\n"
        "   and flerb not between 1 and 9\n"
        "   and flerb2 between symmetric 4 and 8\n"
        "   and flerb3 is false\n"
        "   and flerb4 is true\n"
        "   and flerb5 is unknown\n"
        " group by foo\n"
        " order by foo"
    )
    tokens = list(lexer.get_tokens(sql))
    actual_tokens = retokenize.retokenize1(tokens)
    expected_tokens = [
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'distinct on'),
        (Token.Punctuation, '('),
        (Token.Name, 'foo'),
        (Token.Punctuation, ')'),
        (Token.Text.Whitespace, '\n     '),
        (Token.Punctuation, ','),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'foo'),
        (Token.Text.Whitespace, '\n     '),
        (Token.Punctuation, ','),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'count'),
        (Token.Punctuation, '('),
        (Token.Name, 'bar'),
        (Token.Punctuation, ')'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'over'),
        (Token.Punctuation, '('),
        (Token.Keyword, 'partition by'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'foo'),
        (Token.Punctuation, ')'),
        (Token.Text.Whitespace, '\n     '),
        (Token.Punctuation, ','),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'percentile_cont'),
        (Token.Punctuation, '('),
        (Token.Literal.Number.Float, '0.5'),
        (Token.Punctuation, ')'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'within group'),
        (Token.Punctuation, '('),
        (Token.Keyword, 'order by'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'foo'),
        (Token.Punctuation, ')'),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'from'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'baz'),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'left join'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'table1'),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'right join'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'table2'),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'natural join'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'table3'),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'lateral join'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'table4'),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'cross join'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'table5'),
        (Token.Text.Whitespace, '\n '),
        (Token.Keyword, 'where'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'something'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'is null'),
        (Token.Text.Whitespace, '\n   '),
        (Token.Keyword, 'and'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'flerb'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'not between'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '1'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'and'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '9'),
        (Token.Text.Whitespace, '\n   '),
        (Token.Keyword, 'and'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'flerb2'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'between symmetric'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '4'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'and'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '8'),
        (Token.Text.Whitespace, '\n   '),
        (Token.Keyword, 'and'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'flerb3'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'is false'),
        (Token.Text.Whitespace, '\n   '),
        (Token.Keyword, 'and'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'flerb4'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'is true'),
        (Token.Text.Whitespace, '\n   '),
        (Token.Keyword, 'and'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'flerb5'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'is unknown'),
        (Token.Text.Whitespace, '\n '),
        (Token.Keyword, 'group by'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'foo'),
        (Token.Text.Whitespace, '\n '),
        (Token.Keyword, 'order by'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'foo'),
        (Token.Text.Whitespace, '\n'),
    ]
    assert expected_tokens == actual_tokens


def test_retokenize1_two_word_phrases_group2():
    # this is not a sane or even valid query, btw
    sql = (
        "select 1\n"
        "union all\n"
        "select 2\n"
        "union distinct\n"
        "select 3\n"
        "except all\n"
        "select 4\n"
        "except distinct\n"
        "select 5\n"
        "intersect all\n"
        "select 6\n"
        "intersect distinct\n"
        "select 7"
    )
    tokens = list(lexer.get_tokens(sql))
    actual_tokens = retokenize.retokenize1(tokens)
    expected_tokens = [
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '1'),
        (Token.Text.Whitespace, '\n'),
        (Token.Keyword, 'union all'),
        (Token.Text.Whitespace, '\n'),
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '2'),
        (Token.Text.Whitespace, '\n'),
        (Token.Keyword, 'union distinct'),
        (Token.Text.Whitespace, '\n'),
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '3'),
        (Token.Text.Whitespace, '\n'),
        (Token.Keyword, 'except all'),
        (Token.Text.Whitespace, '\n'),
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '4'),
        (Token.Text.Whitespace, '\n'),
        (Token.Keyword, 'except distinct'),
        (Token.Text.Whitespace, '\n'),
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '5'),
        (Token.Text.Whitespace, '\n'),
        (Token.Keyword, 'intersect all'),
        (Token.Text.Whitespace, '\n'),
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '6'),
        (Token.Text.Whitespace, '\n'),
        (Token.Keyword, 'intersect distinct'),
        (Token.Text.Whitespace, '\n'),
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '7'),
        (Token.Text.Whitespace, '\n'),
    ]
    assert expected_tokens == actual_tokens


def test_retokenize1_single_quoted_literal():
    sql = (
        "select 'foo'\n"
        "  from bar\n"
        " where baz = 'words'"
    )
    tokens = list(lexer.get_tokens(sql))
    actual_tokens = retokenize.retokenize1(tokens)
    expected_tokens = [
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.String.Single, "'foo'"),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'from'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'bar'),
        (Token.Text.Whitespace, '\n '),
        (Token.Keyword, 'where'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'baz'),
        (Token.Text.Whitespace, ' '),
        (Token.Operator, '='),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.String.Single, "'words'"),
        (Token.Text.Whitespace, '\n'),
    ]
    assert expected_tokens == actual_tokens


def test_retokenize1_dollar_quoted_literal():
    # both styles
    sql = (
        "select $$foo$$\n"
        "  from bar\n"
        " where baz = $special$words$special$"
    )
    tokens = list(lexer.get_tokens(sql))
    actual_tokens = retokenize.retokenize1(tokens)
    expected_tokens = [
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.String, '$$foo$$'),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'from'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'bar'),
        (Token.Text.Whitespace, '\n '),
        (Token.Keyword, 'where'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'baz'),
        (Token.Text.Whitespace, ' '),
        (Token.Operator, '='),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.String, '$special$words$special$'),
        (Token.Text.Whitespace, '\n'),
    ]
    assert expected_tokens == actual_tokens


def test_retokenize1_double_and_backtick_quoted_literals():
    sql = (
        "select \"foo\" as \"Foo\"\n"
        "  from `bar`\n"
        " where 1=1"
    )
    tokens = list(lexer.get_tokens(sql))
    actual_tokens = retokenize.retokenize1(tokens)
    expected_tokens = [
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.String.Name, '"foo"'),
        (Token.Text.Whitespace, ' '),
        (Token.Keyword, 'as'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.String.Name, '"Foo"'),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'from'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.String.Name, '`bar`'),
        (Token.Text.Whitespace, '\n '),
        (Token.Keyword, 'where'),
        (Token.Text.Whitespace, ' '),
        (Token.Literal.Number.Float, '1'),
        (Token.Operator, '='),
        (Token.Literal.Number.Float, '1'),
        (Token.Text.Whitespace, '\n'),
    ]
    assert expected_tokens == actual_tokens


# not a fully isolated test of retokenize2 because it calls retokenize1...
def test_retokenize2_qualified_identifiers():
    sql = (
        "select table_name.column_name\n"
        "     , schema_name.table_name.column_name\n"
        "     , db_name.schema_name.table_name.column_name\n"
        "     , \"Quoted\".\"Name\"\n"
        "     , \"Longer\".\"Quoted\".\"Name\"\n"
        "  from foo"
    )
    tokens = list(lexer.get_tokens(sql))
    actual_tokens = retokenize.retokenize2(retokenize.retokenize1(tokens))
    expected_tokens = [
        (Token.Keyword, 'select'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'table_name.column_name'),
        (Token.Text.Whitespace, '\n     '),
        (Token.Punctuation, ','),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'schema_name.table_name.column_name'),
        (Token.Text.Whitespace, '\n     '),
        (Token.Punctuation, ','),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'db_name.schema_name.table_name'),
        (Token.Literal.Number.Float, '.'),
        (Token.Name, 'column_name'),
        (Token.Text.Whitespace, '\n     '),
        (Token.Punctuation, ','),
        (Token.Text.Whitespace, ' '),
        (Token.Name, '"Quoted"."Name"'),
        (Token.Text.Whitespace, '\n     '),
        (Token.Punctuation, ','),
        (Token.Text.Whitespace, ' '),
        (Token.Name, '"Longer"."Quoted"."Name"'),
        (Token.Text.Whitespace, '\n  '),
        (Token.Keyword, 'from'),
        (Token.Text.Whitespace, ' '),
        (Token.Name, 'foo'),
        (Token.Text.Whitespace, '\n'),
    ]
    assert expected_tokens == actual_tokens
