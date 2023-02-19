import pytest

import sflexer
from sftoken import SFToken, SFTokenKind


def test_none():
    text = None
    expected = []
    actual = sflexer.lex(text)
    assert expected == actual


def test_empty():
    text = ""
    expected = []
    actual = sflexer.lex(text)
    assert expected == actual


def test_newline():
    text = "\n"
    expected = [SFToken(SFTokenKind.NEWLINE, "\n")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_spaces():
    for i in range(1, 10): # arbitrary
        i_spaces = " " * i
        expected = [SFToken(SFTokenKind.SPACES, i_spaces)]
        actual = sflexer.lex(i_spaces)
        assert expected == actual


def test_integer_literal():
    text = "1"
    expected = [SFToken(SFTokenKind.WORD, "1")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_decimal_literal():
    text = "3.14"
    expected = [SFToken(SFTokenKind.WORD, "3.14")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_scientific_literal():
    text = "1.23e4"
    expected = [SFToken(SFTokenKind.WORD, "1.23e4")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_word():
    text = "foo"
    expected = [SFToken(SFTokenKind.WORD, "foo")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_words_with_spaces():
    text = "foo bar baz"
    expected = [
        SFToken(SFTokenKind.WORD, "foo"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "bar"),
        SFToken(SFTokenKind.SPACES, " "),
        SFToken(SFTokenKind.WORD, "baz"),
    ]
    actual = sflexer.lex(text)
    assert expected == actual


def test_words_with_newlines():
    text = "foo\nbar\nbaz"
    expected = [
        SFToken(SFTokenKind.WORD, "foo"),
        SFToken(SFTokenKind.NEWLINE, "\n"),
        SFToken(SFTokenKind.WORD, "bar"),
        SFToken(SFTokenKind.NEWLINE, "\n"),
        SFToken(SFTokenKind.WORD, "baz"),
    ]
    actual = sflexer.lex(text)
    assert expected == actual


def test_single_quoted_literal():
    text = "'literal'"
    expected = [SFToken(SFTokenKind.LITERAL, "'literal'")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_single_quoted_literal_with_escaped_quote1():
    text = "'bob''s'"
    expected = [SFToken(SFTokenKind.LITERAL, "'bob''s'")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_single_quoted_literal_with_escaped_quote2():
    text = r"'bob\'s'"
    expected = [SFToken(SFTokenKind.LITERAL, r"'bob\'s'")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_single_quoted_literal_multiline():
    text = "'line one\nline two'"
    expected = [SFToken(SFTokenKind.LITERAL, "'line one\nline two'")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_double_quoted_identifier():
    text = '"identifier"'
    expected = [SFToken(SFTokenKind.LITERAL, '"identifier"')]
    actual = sflexer.lex(text)
    assert expected == actual


def test_double_quoted_identifier_with_escaped_quote1():
    text = '"this is a ""bad"" identifier"'
    expected = [SFToken(SFTokenKind.LITERAL, '"this is a ""bad"" identifier"')]
    actual = sflexer.lex(text)
    assert expected == actual


def test_double_quoted_identifier_with_escaped_quote2():
    text = r'"this is a \"bad\" identifier"'
    expected = [SFToken(SFTokenKind.LITERAL, r'"this is a \"bad\" identifier"')]
    actual = sflexer.lex(text)
    assert expected == actual


def test_backtick_quoted_identifier():
    text = "`identifier`"
    expected = [SFToken(SFTokenKind.LITERAL, "`identifier`")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_backtick_quoted_identifier_with_escaped_quote1():
    text = "`one ``two`` three`"
    expected = [SFToken(SFTokenKind.LITERAL, "`one ``two`` three`")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_backtick_quoted_identifier_with_escaped_quote2():
    text = r"`one \`two\` three`"
    expected = [SFToken(SFTokenKind.LITERAL, r"`one \`two\` three`")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_dotted_identifier():
    text = "foo.bar"
    expected = [SFToken(SFTokenKind.WORD, "foo"), SFToken(SFTokenKind.SYMBOL, "."), SFToken(SFTokenKind.WORD, "bar")]
    actual = sflexer.lex(text)
    assert expected == actual


def test_line_comment(): # this one case is probably not sufficient
    text = "foo\n--hey\nbar"
    expected = [
        SFToken(SFTokenKind.WORD, "foo"),
        SFToken(SFTokenKind.NEWLINE, "\n"),
        SFToken(SFTokenKind.LINE_COMMENT, "--hey\n"),
        SFToken(SFTokenKind.WORD, "bar"),
    ]
    actual = sflexer.lex(text)
    assert expected == actual


def test_block_comment(): # this one case is probably not sufficient
    text = "foo/* hey */bar"
    expected = [
        SFToken(SFTokenKind.WORD, "foo"),
        SFToken(SFTokenKind.BLOCK_COMMENT, "/* hey */"),
        SFToken(SFTokenKind.WORD, "bar"),
    ]
    actual = sflexer.lex(text)
    assert expected == actual


def test_symbols():
    symbols = [
        "~",
        "!",
        "@",
        "#",
        "$",
        "%",
        "^",
        "&",
        "*",
        "(",
        ")",
        "-",
        "+",
        "=",
        "[",
        "]",
        "{",
        "}",
        "|",
        ",",
        "<",
        ">",
        "?",
        "/",
        ":",
        ";",
        ",",
        ".",
    ]
    for s in symbols:
        expected = [SFToken(SFTokenKind.SYMBOL, s)]
        actual = sflexer.lex(s)
        assert expected == actual


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
        expected = [SFToken(SFTokenKind.WORD, phrase)]
        actual = sflexer.lex(phrase)
        assert expected == actual
    for phrase in [p.upper() for p in phrases]:
        expected = [SFToken(SFTokenKind.WORD, phrase)]
        actual = sflexer.lex(phrase)
        assert expected == actual


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
        expected = [SFToken(SFTokenKind.WORD, phrase)]
        actual = sflexer.lex(phrase)
        assert expected == actual
    for phrase in [p.upper() for p in phrases]:
        expected = [SFToken(SFTokenKind.WORD, phrase)]
        actual = sflexer.lex(phrase)
        assert expected == actual


def test_four_word_key_phrases():
    phrases = [
        'is not distinct from',
    ]
    for phrase in phrases:
        expected = [SFToken(SFTokenKind.WORD, phrase)]
        actual = sflexer.lex(phrase)
        assert expected == actual
    for phrase in [p.upper() for p in phrases]:
        expected = [SFToken(SFTokenKind.WORD, phrase)]
        actual = sflexer.lex(phrase)
        assert expected == actual


def test_qualified_identifier_one_dot():
    tokens = sflexer.lex("foo.bar") # [(WORD, 'foo'), (SYMBOL, '.'), (WORD, 'bar')]
    actual_token, actual_consumed = sflexer.get_qualified_identifier(tokens)
    expected_token = SFToken(SFTokenKind.WORD, "foo.bar")
    expected_consumed = 3
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_two_dots():
    tokens = sflexer.lex("foo.bar.baz") # [(WORD, 'foo'), (SYMBOL, '.'), (WORD, 'bar'), (SYMBOL, '.'), (WORD, 'baz')]
    actual_token, actual_consumed = sflexer.get_qualified_identifier(tokens)
    expected_token = SFToken(SFTokenKind.WORD, "foo.bar.baz")
    expected_consumed = 5
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_three_dots():
    tokens = sflexer.lex("foo.bar.baz.idk") # [(WORD, 'foo'), (SYMBOL, '.'), (WORD, 'bar'), (SYMBOL, '.'), (WORD, 'baz'), (SYMBOL, '.'), (WORD, 'idk')]
    actual_token, actual_consumed = sflexer.get_qualified_identifier(tokens)
    expected_token = SFToken(SFTokenKind.WORD, "foo.bar.baz.idk")
    expected_consumed = 7
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_with_quotes_one_dot():
    tokens = sflexer.lex('"Alice"."Bob"') # [(WORD, '"Alice"'), (SYMBOL, '.'), (WORD, '"Bob"')]
    actual_token, actual_consumed = sflexer.get_qualified_identifier(tokens)
    expected_token = SFToken(SFTokenKind.LITERAL, '"Alice"."Bob"')
    expected_consumed = 3
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_with_quotes_two_dots():
    tokens = sflexer.lex('"Alice"."Bob"."Cindy"') # [(WORD, '"Alice"'), (SYMBOL, '.'), (WORD, '"Bob"'), (SYMBOL, '.'), (WORD, '"Cindy"')]
    actual_token, actual_consumed = sflexer.get_qualified_identifier(tokens)
    expected_token = SFToken(SFTokenKind.LITERAL, '"Alice"."Bob"."Cindy"')
    expected_consumed = 5
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_with_mixed_quotes():
    tokens = sflexer.lex('alice."Bob"') # [(Token.Name, 'alice'), (Token.Literal.Number.Float, '.'), (Token.Name, '"Bob"')]
    actual_token, actual_consumed = sflexer.get_qualified_identifier(tokens)
    expected_token = SFToken(SFTokenKind.LITERAL, 'alice."Bob"')
    expected_consumed = 3
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_collapse_identifiers():
    sql = (
        "select table_name.column_name\n"
        "     , schema_name.table_name.column_name\n"
        "     , db_name.schema_name.table_name.column_name\n"
        "     , \"Quoted\".\"Name\"\n"
        "     , \"Longer\".\"Quoted\".\"Name\"\n"
        "  from foo"
    )
    tokens = sflexer.lex(sql)
    actual_tokens = sflexer.collapse_identifiers(tokens)
    expected_tokens = [
        SFToken(SFTokenKind.WORD, 'select'),
        SFToken(SFTokenKind.SPACES, ' '),
        SFToken(SFTokenKind.WORD, 'table_name.column_name'),
        SFToken(SFTokenKind.NEWLINE, '\n'),
        SFToken(SFTokenKind.SPACES, '     '),
        SFToken(SFTokenKind.SYMBOL, ','),
        SFToken(SFTokenKind.SPACES, ' '),
        SFToken(SFTokenKind.WORD, 'schema_name.table_name.column_name'),
        SFToken(SFTokenKind.NEWLINE, '\n'),
        SFToken(SFTokenKind.SPACES, '     '),
        SFToken(SFTokenKind.SYMBOL, ','),
        SFToken(SFTokenKind.SPACES, ' '),
        SFToken(SFTokenKind.WORD, 'db_name.schema_name.table_name'),
        SFToken(SFTokenKind.SYMBOL, '.'),
        SFToken(SFTokenKind.WORD, 'column_name'),
        SFToken(SFTokenKind.NEWLINE, '\n'),
        SFToken(SFTokenKind.SPACES, '     '),
        SFToken(SFTokenKind.SYMBOL, ','),
        SFToken(SFTokenKind.SPACES, ' '),
        SFToken(SFTokenKind.LITERAL, '"Quoted"."Name"'),
        SFToken(SFTokenKind.NEWLINE, '\n'),
        SFToken(SFTokenKind.SPACES, '     '),
        SFToken(SFTokenKind.SYMBOL, ','),
        SFToken(SFTokenKind.SPACES, ' '),
        SFToken(SFTokenKind.LITERAL, '"Longer"."Quoted"."Name"'),
        SFToken(SFTokenKind.NEWLINE, '\n'),
        SFToken(SFTokenKind.SPACES, '  '),
        SFToken(SFTokenKind.WORD, 'from'),
        SFToken(SFTokenKind.SPACES, ' '),
        SFToken(SFTokenKind.WORD, 'foo'),
    ]
    for t in actual_tokens:
        print(t)
    assert expected_tokens == actual_tokens
