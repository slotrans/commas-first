import pytest

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

import retokenize


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
        'is null',
        'not between',
        'between symmetric',
        'union all',
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
        'is not null',
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
