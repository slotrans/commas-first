import pytest

import cflexer
from cftoken import CFToken, CFTokenKind


def test_none():
    text = None
    expected = []
    actual = cflexer.lex(text)
    assert expected == actual


def test_empty():
    text = ""
    expected = []
    actual = cflexer.lex(text)
    assert expected == actual


def test_newline():
    text = "\n"
    expected = [CFToken(CFTokenKind.NEWLINE, "\n")]
    actual = cflexer.lex(text)
    assert expected == actual


def test_spaces():
    for i in range(1, 10): # arbitrary
        i_spaces = " " * i
        expected = [CFToken(CFTokenKind.SPACES, i_spaces)]
        actual = cflexer.lex(i_spaces)
        assert expected == actual


def test_integer_literal():
    text = "1"
    expected = [CFToken(CFTokenKind.WORD, "1")]
    actual = cflexer.lex(text)
    assert expected == actual


def test_decimal_literal():
    text = "3.14"
    expected = [CFToken(CFTokenKind.WORD, "3.14")]
    actual = cflexer.lex(text)
    assert expected == actual


def test_scientific_literal():
    text = "1.23e4"
    expected = [CFToken(CFTokenKind.WORD, "1.23e4")]
    actual = cflexer.lex(text)
    assert expected == actual


def test_word():
    text = "foo"
    expected = [CFToken(CFTokenKind.WORD, "foo")]
    actual = cflexer.lex(text)
    assert expected == actual


def test_words_with_spaces():
    text = "foo bar baz"
    expected = [
        CFToken(CFTokenKind.WORD, "foo"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "bar"),
        CFToken(CFTokenKind.SPACES, " "),
        CFToken(CFTokenKind.WORD, "baz"),
    ]
    actual = cflexer.lex(text)
    assert expected == actual


def test_words_with_newlines():
    text = "foo\nbar\nbaz"
    expected = [
        CFToken(CFTokenKind.WORD, "foo"),
        CFToken(CFTokenKind.NEWLINE, "\n"),
        CFToken(CFTokenKind.WORD, "bar"),
        CFToken(CFTokenKind.NEWLINE, "\n"),
        CFToken(CFTokenKind.WORD, "baz"),
    ]
    actual = cflexer.lex(text)
    assert expected == actual


def test_single_quoted_literal():
    text = "'literal'"
    expected = [CFToken(CFTokenKind.LITERAL, "'literal'")]
    actual = cflexer.lex(text)
    assert expected == actual


def test_single_quoted_literal_with_escaped_quote1():
    text = "'bob''s'"
    expected = [CFToken(CFTokenKind.LITERAL, "'bob''s'")]
    actual = cflexer.lex(text)
    assert expected == actual


def test_single_quoted_literal_with_escaped_quote2():
    text = r"'bob\'s'"
    expected = [CFToken(CFTokenKind.LITERAL, r"'bob\'s'")]
    actual = cflexer.lex(text)
    assert expected == actual


def test_single_quoted_literal_multiline():
    text = "'line one\nline two'"
    expected = [CFToken(CFTokenKind.LITERAL, "'line one\nline two'")]
    actual = cflexer.lex(text)
    assert expected == actual


def test_double_quoted_identifier():
    text = '"identifier"'
    expected = [CFToken(CFTokenKind.LITERAL, '"identifier"')]
    actual = cflexer.lex(text)
    assert expected == actual


def test_double_quoted_identifier_with_escaped_quote1():
    text = '"this is a ""bad"" identifier"'
    expected = [CFToken(CFTokenKind.LITERAL, '"this is a ""bad"" identifier"')]
    actual = cflexer.lex(text)
    assert expected == actual


def test_double_quoted_identifier_with_escaped_quote2():
    text = r'"this is a \"bad\" identifier"'
    expected = [CFToken(CFTokenKind.LITERAL, r'"this is a \"bad\" identifier"')]
    actual = cflexer.lex(text)
    assert expected == actual


def test_backtick_quoted_identifier():
    text = "`identifier`"
    expected = [CFToken(CFTokenKind.LITERAL, "`identifier`")]
    actual = cflexer.lex(text)
    assert expected == actual


def test_backtick_quoted_identifier_with_escaped_quote1():
    text = "`one ``two`` three`"
    expected = [CFToken(CFTokenKind.LITERAL, "`one ``two`` three`")]
    actual = cflexer.lex(text)
    assert expected == actual


def test_backtick_quoted_identifier_with_escaped_quote2():
    text = r"`one \`two\` three`"
    expected = [CFToken(CFTokenKind.LITERAL, r"`one \`two\` three`")]
    actual = cflexer.lex(text)
    assert expected == actual


def test_dotted_identifier():
    text = "foo.bar"
    expected = [CFToken(CFTokenKind.WORD, "foo"), CFToken(CFTokenKind.SYMBOL, "."), CFToken(CFTokenKind.WORD, "bar")]
    actual = cflexer.lex(text)
    assert expected == actual


def test_line_comment(): # this one case is probably not sufficient
    text = "foo\n--hey\nbar"
    expected = [
        CFToken(CFTokenKind.WORD, "foo"),
        CFToken(CFTokenKind.NEWLINE, "\n"),
        CFToken(CFTokenKind.LINE_COMMENT, "--hey\n"),
        CFToken(CFTokenKind.WORD, "bar"),
    ]
    actual = cflexer.lex(text)
    assert expected == actual


def test_block_comment(): # this one case is probably not sufficient
    text = "foo/* hey */bar"
    expected = [
        CFToken(CFTokenKind.WORD, "foo"),
        CFToken(CFTokenKind.BLOCK_COMMENT, "/* hey */"),
        CFToken(CFTokenKind.WORD, "bar"),
    ]
    actual = cflexer.lex(text)
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
        expected = [CFToken(CFTokenKind.SYMBOL, s)]
        actual = cflexer.lex(s)
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
        expected = [CFToken(CFTokenKind.WORD, phrase)]
        actual = cflexer.lex(phrase)
        assert expected == actual
    for phrase in [p.upper() for p in phrases]:
        expected = [CFToken(CFTokenKind.WORD, phrase)]
        actual = cflexer.lex(phrase)
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
        expected = [CFToken(CFTokenKind.WORD, phrase)]
        actual = cflexer.lex(phrase)
        assert expected == actual
    for phrase in [p.upper() for p in phrases]:
        expected = [CFToken(CFTokenKind.WORD, phrase)]
        actual = cflexer.lex(phrase)
        assert expected == actual


def test_four_word_key_phrases():
    phrases = [
        'is not distinct from',
    ]
    for phrase in phrases:
        expected = [CFToken(CFTokenKind.WORD, phrase)]
        actual = cflexer.lex(phrase)
        assert expected == actual
    for phrase in [p.upper() for p in phrases]:
        expected = [CFToken(CFTokenKind.WORD, phrase)]
        actual = cflexer.lex(phrase)
        assert expected == actual


def test_qualified_identifier_one_dot():
    tokens = cflexer.lex("foo.bar") # [(WORD, 'foo'), (SYMBOL, '.'), (WORD, 'bar')]
    actual_token, actual_consumed = cflexer.get_qualified_identifier(tokens)
    expected_token = CFToken(CFTokenKind.WORD, "foo.bar")
    expected_consumed = 3
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_two_dots():
    tokens = cflexer.lex("foo.bar.baz") # [(WORD, 'foo'), (SYMBOL, '.'), (WORD, 'bar'), (SYMBOL, '.'), (WORD, 'baz')]
    actual_token, actual_consumed = cflexer.get_qualified_identifier(tokens)
    expected_token = CFToken(CFTokenKind.WORD, "foo.bar.baz")
    expected_consumed = 5
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_three_dots():
    tokens = cflexer.lex("foo.bar.baz.idk") # [(WORD, 'foo'), (SYMBOL, '.'), (WORD, 'bar'), (SYMBOL, '.'), (WORD, 'baz'), (SYMBOL, '.'), (WORD, 'idk')]
    actual_token, actual_consumed = cflexer.get_qualified_identifier(tokens)
    expected_token = CFToken(CFTokenKind.WORD, "foo.bar.baz.idk")
    expected_consumed = 7
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_with_quotes_one_dot():
    tokens = cflexer.lex('"Alice"."Bob"') # [(WORD, '"Alice"'), (SYMBOL, '.'), (WORD, '"Bob"')]
    actual_token, actual_consumed = cflexer.get_qualified_identifier(tokens)
    expected_token = CFToken(CFTokenKind.LITERAL, '"Alice"."Bob"')
    expected_consumed = 3
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_with_quotes_two_dots():
    tokens = cflexer.lex('"Alice"."Bob"."Cindy"') # [(WORD, '"Alice"'), (SYMBOL, '.'), (WORD, '"Bob"'), (SYMBOL, '.'), (WORD, '"Cindy"')]
    actual_token, actual_consumed = cflexer.get_qualified_identifier(tokens)
    expected_token = CFToken(CFTokenKind.LITERAL, '"Alice"."Bob"."Cindy"')
    expected_consumed = 5
    assert expected_token == actual_token
    assert expected_consumed == actual_consumed


def test_qualified_identifier_with_mixed_quotes():
    tokens = cflexer.lex('alice."Bob"') # [(Token.Name, 'alice'), (Token.Literal.Number.Float, '.'), (Token.Name, '"Bob"')]
    actual_token, actual_consumed = cflexer.get_qualified_identifier(tokens)
    expected_token = CFToken(CFTokenKind.LITERAL, 'alice."Bob"')
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
    tokens = cflexer.lex(sql)
    actual_tokens = cflexer.collapse_identifiers(tokens)
    expected_tokens = [
        CFToken(CFTokenKind.WORD, 'select'),
        CFToken(CFTokenKind.SPACES, ' '),
        CFToken(CFTokenKind.WORD, 'table_name.column_name'),
        CFToken(CFTokenKind.NEWLINE, '\n'),
        CFToken(CFTokenKind.SPACES, '     '),
        CFToken(CFTokenKind.SYMBOL, ','),
        CFToken(CFTokenKind.SPACES, ' '),
        CFToken(CFTokenKind.WORD, 'schema_name.table_name.column_name'),
        CFToken(CFTokenKind.NEWLINE, '\n'),
        CFToken(CFTokenKind.SPACES, '     '),
        CFToken(CFTokenKind.SYMBOL, ','),
        CFToken(CFTokenKind.SPACES, ' '),
        CFToken(CFTokenKind.WORD, 'db_name.schema_name.table_name'),
        CFToken(CFTokenKind.SYMBOL, '.'),
        CFToken(CFTokenKind.WORD, 'column_name'),
        CFToken(CFTokenKind.NEWLINE, '\n'),
        CFToken(CFTokenKind.SPACES, '     '),
        CFToken(CFTokenKind.SYMBOL, ','),
        CFToken(CFTokenKind.SPACES, ' '),
        CFToken(CFTokenKind.LITERAL, '"Quoted"."Name"'),
        CFToken(CFTokenKind.NEWLINE, '\n'),
        CFToken(CFTokenKind.SPACES, '     '),
        CFToken(CFTokenKind.SYMBOL, ','),
        CFToken(CFTokenKind.SPACES, ' '),
        CFToken(CFTokenKind.LITERAL, '"Longer"."Quoted"."Name"'),
        CFToken(CFTokenKind.NEWLINE, '\n'),
        CFToken(CFTokenKind.SPACES, '  '),
        CFToken(CFTokenKind.WORD, 'from'),
        CFToken(CFTokenKind.SPACES, ' '),
        CFToken(CFTokenKind.WORD, 'foo'),
    ]
    for t in actual_tokens:
        print(t)
    assert expected_tokens == actual_tokens
