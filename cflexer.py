import re

from cftoken import CFToken, CFTokenKind, Symbols


SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
BACKTICK = "`"
BLOCK_COMMENT_OPEN = "/*"
BLOCK_COMMENT_CLOSE = "*/"
LINE_COMMENT_START = "--"

FOUR_WORD_PHRASES = [
    'is not distinct from',
]

THREE_WORD_PHRASES = [
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

TWO_WORD_PHRASES = [
    'cross join',
    'distinct on',
    'inner join',
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


def lex(input_string):
    if input_string is None or len(input_string) == 0:
        return []

    RE_SPACES = re.compile(r"[ ]+")
    RE_SINGLE_QUOTED_STRING = re.compile(r"(')(\\.|''|[^'\\])*(')")
    RE_DOUBLE_QUOTED_STRING = re.compile(r'(")(\\.|""|[^"\\])*(")')
    RE_BACKTICK_QUOTED_STRING = re.compile(r"(`)(\\.|``|[^`\\])*(`)")
    RE_DOLLAR_QUOTED_STRING = re.compile(r"(\$[A-Za-z0-9_]*\$)(.*?)(\1)", flags=re.DOTALL)
    RE_LINE_COMMENT = re.compile(r"--.*?(\n|$)")
    RE_BLOCK_COMMENT = re.compile(r"(/\*)(.*?)(\*/)", flags=re.DOTALL)
    RE_ALPHANUMERIC_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    RE_FOUR_WORD_KEYPHRASE = re.compile(f"({'|'.join(FOUR_WORD_PHRASES)})", flags=re.IGNORECASE)
    RE_THREE_WORD_KEYPHRASE = re.compile(f"({'|'.join(THREE_WORD_PHRASES)})", flags=re.IGNORECASE)
    RE_TWO_WORD_KEYPHRASE = re.compile(f"({'|'.join(TWO_WORD_PHRASES)})", flags=re.IGNORECASE)

    tokens = []

    i = 0
    while i < len(input_string):
        # https://www.postgresql.org/docs/current/sql-syntax-lexical.html

        # newline
        if "\n" == input_string[i]:
            tokens.append(CFToken(CFTokenKind.NEWLINE, "\n"))
            i += 1
            continue

        # space(s)
        match_res = RE_SPACES.match(input_string[i:])
        if match_res:
            string_of_spaces = match_res[0]
            tokens.append(CFToken(CFTokenKind.SPACES, string_of_spaces))
            i += len(string_of_spaces)
            continue

        # supposedly the (ANTLR) grammar for quotes...
        # fragment DQUOTA_STRING : '"' ( '\\'. | '""' | ~('"' | '\\') )* '"';
        # fragment SQUOTA_STRING : '\'' ('\\'. | '\'\'' | ~('\'' | '\\'))* '\'';
        # fragment BQUOTA_STRING : '`' ( '\\'. | '``' | ~('`' | '\\'))* '`';

        # all kinds of quoted strings
        match_res = RE_SINGLE_QUOTED_STRING.match(input_string[i:])
        if not match_res:
            match_res = RE_DOUBLE_QUOTED_STRING.match(input_string[i:])
        if not match_res:
            match_res = RE_BACKTICK_QUOTED_STRING.match(input_string[i:])
        if not match_res:
            match_res = RE_DOLLAR_QUOTED_STRING.match(input_string[i:])
        if match_res:
            string_literal = match_res[0]
            tokens.append(CFToken(CFTokenKind.LITERAL, string_literal))
            i += len(string_literal)
            continue

        # line comment
        match_res = RE_LINE_COMMENT.match(input_string[i:])
        if match_res:
            line_comment = match_res[0]
            tokens.append(CFToken(CFTokenKind.LINE_COMMENT, line_comment))
            i += len(line_comment)
            continue

        # block comment
        match_res = RE_BLOCK_COMMENT.match(input_string[i:])
        if match_res:
            block_comment = match_res[0]
            tokens.append(CFToken(CFTokenKind.BLOCK_COMMENT, block_comment))
            i += len(block_comment)
            continue

        # keyphrases
        match_res = RE_FOUR_WORD_KEYPHRASE.match(input_string[i:])
        if not match_res:
            match_res = RE_THREE_WORD_KEYPHRASE.match(input_string[i:])
        if not match_res:
            match_res = RE_TWO_WORD_KEYPHRASE.match(input_string[i:])
        if match_res:
            keyphrase = match_res[0]
            tokens.append(CFToken(CFTokenKind.WORD, keyphrase))
            i += len(keyphrase)
            continue

        # alphanumeric word (incl. underscore)
        # TODO: also PG allows dollar-number placeholders e.g. $1
        # TODO: and dollar signs in identifiers e.g. foo$bar (not SQL standard?)
        match_res = RE_ALPHANUMERIC_WORD.match(input_string[i:])
        if match_res:
            word = match_res[0]
            tokens.append(CFToken(CFTokenKind.WORD, word))
            i += len(word)
            continue

        # numeric word (integer literals, float literals, scientific literals)
        # r"[0-9]+"
        # r"[0-9]+\.([0-9]+)?([eE][-+]?[0-9]+)?"
        # r"([0-9]+)?\.[0-9]+([eE][-+]?[0-9]+)?"
        # r"[0-9]+[eE][-+]?[0-9]+"
        # but, it may be preferable to use the sloppy approach below, or a regex equivalent...
        if input_string[i].isdigit() or (
            "." == input_string[i] and len(input_string) >= 2 and input_string[i+1].isdigit()
        ): # btw there are some wonky characters where isdigit()=True like "¹"
            j = i + 1
            while j < len(input_string):
                if not (input_string[j].isdigit() or input_string[j] in [".", "e", "E"]): # not strict, matches crap like 1.e37E5e.8. etc
                    break
                j += 1
            numeric_word = input_string[i:j]
            tokens.append(CFToken(CFTokenKind.WORD, numeric_word))
            i = j
            continue

        # symbol
        #   this is our dumping ground... if we haven't matched anything else, it must(?) be a symbol, which in practice means
        #   actual symbols, control characters, plus most weird unicode stuff if it appears outside of quotes
        tokens.append(CFToken(CFTokenKind.SYMBOL, input_string[i]))
        i += 1
        continue

    return tokens


# TODO: should this be a method on CFToken???
def is_potential_identifier(token):
    if token.kind == CFTokenKind.WORD:
        return True

    if token.kind == CFTokenKind.LITERAL and token.value[0] != SINGLE_QUOTE:
        return True

    return False


def get_qualified_identifier(tokens):
    """
    Consumes a series of dot-separated names, of any length.
    Only foo.bar and foo.bar.baz are typically found in SQL, but: 
    1) there are weird dialects out there,
    2) we wish to be sloppy rather than strict in our parsing.
    """
    length = len(tokens)
    if length < 3 or not is_potential_identifier(tokens[0]):
        return (None, None)

    consumed = [tokens[0]]
    j = 1
    while j+1 < length and tokens[j] == Symbols.DOT and is_potential_identifier(tokens[j+1]):
        consumed.append(tokens[j])
        consumed.append(tokens[j+1])
        j += 2

    if any([t.kind == CFTokenKind.LITERAL for t in consumed]):
        out_kind = CFTokenKind.LITERAL
    else:
        out_kind = CFTokenKind.WORD    
    assembled_token = CFToken(out_kind, ''.join([t.value for t in consumed]))
    return (assembled_token, len(consumed))


def collapse_identifiers(tokens):
    out = []
    i = 0
    length = len(tokens)
    while i < length:
        if i+2 < length:
            phrase = tokens[i:i+5]
            qualified_identifier, tokens_consumed = get_qualified_identifier(phrase)
            if qualified_identifier:
                out.append(qualified_identifier)
                i += tokens_consumed
                continue

        out.append(tokens[i])
        i += 1

    return out
