import sys
import re

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

from sftoken import SFToken, SFTokenKind


IS_NOT_DISTINCT_FROM = [(Token.Keyword, 'is'), (Token.Keyword, 'not'), (Token.Keyword, 'distinct'), (Token.Keyword, 'from')]

FOUR_WORD_PHRASES = [
    IS_NOT_DISTINCT_FROM,
]
FOUR_WORD_PHRASE_STARTERS = [x[0] for x in FOUR_WORD_PHRASES]


LEFT_OUTER_JOIN = [(Token.Keyword, 'left'), (Token.Keyword, 'outer'), (Token.Keyword, 'join')]
RIGHT_OUTER_JOIN = [(Token.Keyword, 'right'), (Token.Keyword, 'outer'), (Token.Keyword, 'join')]
FULL_OUTER_JOIN = [(Token.Keyword, 'full'), (Token.Keyword, 'outer'), (Token.Keyword, 'join')]
IS_NOT_NULL = [(Token.Keyword, 'is'), (Token.Keyword, 'not'), (Token.Keyword, 'null')]
IS_DISTINCT_FROM = [(Token.Keyword, 'is'), (Token.Keyword, 'distinct'), (Token.Keyword, 'from')]
NOT_BETWEEN_SYMMETRIC = [(Token.Keyword, 'not'), (Token.Keyword, 'between'), (Token.Keyword, 'symmetric')]
AT_TIME_ZONE = [(Token.Keyword, 'at'), (Token.Name.Builtin, 'time'), (Token.Keyword, 'zone')]

THREE_WORD_PHRASES = [
    LEFT_OUTER_JOIN,
    RIGHT_OUTER_JOIN,
    FULL_OUTER_JOIN,
    IS_NOT_NULL,
    IS_DISTINCT_FROM,
    NOT_BETWEEN_SYMMETRIC,
    AT_TIME_ZONE,
]
THREE_WORD_PHRASE_STARTERS = [x[0] for x in THREE_WORD_PHRASES]

#THREE_WORD_PHRASE_MAP = {
#    ((Token.Keyword, 'left'), (Token.Keyword, 'outer'), (Token.Keyword, 'join')):        (Token.Keyword, 'left outer join'),
#    ((Token.Keyword, 'right'), (Token.Keyword, 'outer'), (Token.Keyword, 'join')):       (Token.Keyword, 'right outer join'),
#    ((Token.Keyword, 'is'), (Token.Keyword, 'not'), (Token.Keyword, 'null')):            (Token.Keyword, 'is not null'),
#    ((Token.Keyword, 'is'), (Token.Keyword, 'distinct'), (Token.Keyword, 'from')):       (Token.Keyword, 'is distinct from'),
#    ((Token.Keyword, 'not'), (Token.Keyword, 'between'), (Token.Keyword, 'symmetric')):  (Token.Keyword, 'not between symmetric'),
#    ((Token.Keyword, 'at'), (Token.Name.Builtin, 'time'), (Token.Keyword, 'zone')):      (Token.Keyword, 'at time zone'),
#}

CROSS_JOIN = [(Token.Keyword, 'cross'), (Token.Keyword, 'join')]
DISTINCT_ON = [(Token.Keyword, 'distinct'), (Token.Keyword, 'on')]
LEFT_JOIN = [(Token.Keyword, 'left'), (Token.Keyword, 'join')]
RIGHT_JOIN = [(Token.Keyword, 'right'), (Token.Keyword, 'join')]
NATURAL_JOIN = [(Token.Keyword, 'natural'), (Token.Keyword, 'join')]
LATERAL_JOIN = [(Token.Keyword, 'lateral'), (Token.Keyword, 'join')]
GROUP_BY = [(Token.Keyword, 'group'), (Token.Keyword, 'by')]
ORDER_BY = [(Token.Keyword, 'order'), (Token.Keyword, 'by')]
PARTITION_BY = [(Token.Keyword, 'partition'), (Token.Keyword, 'by')]
WITHIN_GROUP = [(Token.Keyword, 'within'), (Token.Keyword, 'group')]
IS_NULL = [(Token.Keyword, 'is'), (Token.Keyword, 'null')]
NOT_BETWEEN = [(Token.Keyword, 'not'), (Token.Keyword, 'between')]
BETWEEN_SYMMETRIC = [(Token.Keyword, 'between'), (Token.Keyword, 'symmetric')]
UNION_ALL = [(Token.Keyword, 'union'), (Token.Keyword, 'all')]
UNION_DISTINCT = [(Token.Keyword, 'union'), (Token.Keyword, 'distinct')]
EXCEPT_ALL = [(Token.Keyword, 'except'), (Token.Keyword, 'all')]
EXCEPT_DISTINCT = [(Token.Keyword, 'except'), (Token.Keyword, 'distinct')]
INTERSECT_ALL = [(Token.Keyword, 'intersect'), (Token.Keyword, 'all')]
INTERSECT_DISTINCT = [(Token.Keyword, 'intersect'), (Token.Keyword, 'distinct')]


TWO_WORD_PHRASES = [
    CROSS_JOIN,
    DISTINCT_ON,
    LEFT_JOIN,
    RIGHT_JOIN,
    NATURAL_JOIN,
    LATERAL_JOIN,
    GROUP_BY,
    ORDER_BY,
    PARTITION_BY,
    WITHIN_GROUP,
    IS_NULL,
    NOT_BETWEEN,
    BETWEEN_SYMMETRIC,
    UNION_ALL,
    UNION_DISTINCT,
    EXCEPT_ALL,
    EXCEPT_DISTINCT,
    INTERSECT_ALL,
    INTERSECT_DISTINCT,
]
TWO_WORD_PHRASE_STARTERS = [x[0] for x in TWO_WORD_PHRASES]

#TWO_WORD_PHRASE_MAP = {
#    ((Token.Keyword, 'cross'), (Token.Keyword, 'join')):         (Token.Keyword, 'cross join'),
#    ((Token.Keyword, 'left'), (Token.Keyword, 'join')):          (Token.Keyword, 'left join'),
#    ((Token.Keyword, 'right'), (Token.Keyword, 'join')):         (Token.Keyword, 'right join'),
#    ((Token.Keyword, 'group'), (Token.Keyword, 'by')):           (Token.Keyword, 'group by'),
#    ((Token.Keyword, 'order'), (Token.Keyword, 'by')):           (Token.Keyword, 'order by'),
#    ((Token.Keyword, 'partition'), (Token.Keyword, 'by')):       (Token.Keyword, 'partition by'),
#    ((Token.Keyword, 'within'), (Token.Keyword, 'group')):       (Token.Keyword, 'within group'),
#    ((Token.Keyword, 'is'), (Token.Keyword, 'null')):            (Token.Keyword, 'is null'),
#    ((Token.Keyword, 'not'), (Token.Keyword, 'between')):        (Token.Keyword, 'not between'),
#    ((Token.Keyword, 'between'), (Token.Keyword, 'symmetric')):  (Token.Keyword, 'between symmetric'),
#}


SINGLE_QUOTE = (Token.Literal.String.Single, "'")
DOUBLE_QUOTE = (Token.Literal.String.Name, '"')
BACKTICK_QUOTE = (Token.Operator, '`')
DOLLAR_QUOTE = (Token.Literal.String, '$')
DOT = (Token.Literal.Number.Float, '.')
BLOCK_COMMENT_OPEN = (Token.Comment.Multiline, '/*')
BLOCK_COMMENT_CLOSE = (Token.Comment.Multiline, '*/')


### FIRST PASS FUNCTIONS

def pre_process_tokens(tokenlist):
    out = []
    for t in tokenlist:
        ttype, value = t

        # This makes dealing with keyphrases much easier, and I prefer lower-case keywords anyway.
        # If we want to support uppercasing keywords or passing them through unmodified, this would have to be removed
        # and get_key_phrase() refactored to do case-insensitive comaparisons.
        if ttype is Token.Keyword:
            value = value.lower()

        out.append( (ttype, value) )

    return out


def get_single_quoted_literal(tokens):
    length = len(tokens)
    if length < 3 or tokens[0] != SINGLE_QUOTE:
        return (None, None)

    j = 1 # we already know the 0th token is a single quote
    while j < length:
        if tokens[j] == SINGLE_QUOTE:
            phrase = tokens[0:j+1]
            quoted_literal = ''.join([t[1] for t in phrase])
            return ((Token.Literal.String.Single, quoted_literal), j+1)
        else:
            j += 1

    return (None, None)


def get_dollar_quoted_literal(tokens):
    length = len(tokens)
    if length < 7:
        return (None, None)
    if not (tokens[0] == DOLLAR_QUOTE and tokens[1][0] is Token.Literal.String.Delimiter and tokens[2] == DOLLAR_QUOTE):
        return (None, None)

    delimiter = tokens[1]
    j = 3 # we already know the first 3 tokens are $, delimiter, $
    while j+2 < length:
        if tokens[j:j+3] == [DOLLAR_QUOTE, delimiter, DOLLAR_QUOTE]:
            phrase = tokens[0:j+3]
            quoted_literal = ''.join([t[1] for t in phrase])
            return ((Token.Literal.String, quoted_literal), j+3)
        else:
            j += 1

    return (None, None)


def get_quoted_name(tokens):
    length = len(tokens)
    if length < 3 or tokens[0] not in (DOUBLE_QUOTE, BACKTICK_QUOTE):
        return (None, None)

    quote_token = tokens[0]
    j = 1 # we already know the 0th token is quote_token
    while j < length:
        if tokens[j] == quote_token:
            phrase = tokens[0:j+1]
            quoted_name = ''.join([t[1] for t in phrase])
            return ((Token.Literal.String.Name, quoted_name), j+1)
        j += 1

    return (None, None)


def get_block_comment(tokens):
    length = len(tokens)
    if length < 2:
        return (None, None)

    j = 1
    nested_depth = 0
    while j < length:
        if tokens[j] == BLOCK_COMMENT_OPEN:
            nested_depth += 1
        elif tokens[j] == BLOCK_COMMENT_CLOSE:
            if nested_depth == 0:
                phrase = tokens[0:j+1]
                assembled_comment = ''.join([t[1] for t in phrase])
                return ((Token.Comment.Multiline, assembled_comment), j+1)
            else:
                nested_depth -= 1
        elif tokens[j][0] is not Token.Comment.Multiline:
            break
        j += 1

    return (None, None)


# these three functions could be written as a single generic function,
# but this is clearer and easier to get right

def get_two_word_key_phrase(tokens):
    length = len(tokens)
    tokens_in_phrase = 3
    if length < tokens_in_phrase:
        return (None, None)

    for phrase in TWO_WORD_PHRASES:
        if (    tokens[0] == phrase[0]
            and tokens[1][0] is Token.Text.Whitespace
            and tokens[2] == phrase[1]
           ):
            assembled_phrase = ' '.join([t[1] for t in phrase])
            return ((Token.Keyword, assembled_phrase), tokens_in_phrase)

    return (None, None)


def get_three_word_key_phrase(tokens):
    length = len(tokens)
    tokens_in_phrase = 5
    if length < tokens_in_phrase:
        return (None, None)

    for phrase in THREE_WORD_PHRASES:
        if (    tokens[0] == phrase[0]
            and tokens[1][0] is Token.Text.Whitespace
            and tokens[2] == phrase[1]
            and tokens[3][0] is Token.Text.Whitespace
            and tokens[4] == phrase[2]
           ):
            assembled_phrase = ' '.join([t[1] for t in phrase])
            return ((Token.Keyword, assembled_phrase), tokens_in_phrase)

    return (None, None)


def get_four_word_key_phrase(tokens):
    length = len(tokens)
    tokens_in_phrase = 7
    if length < tokens_in_phrase:
        return (None, None)

    for phrase in FOUR_WORD_PHRASES:
        if (    tokens[0] == phrase[0]
            and tokens[1][0] is Token.Text.Whitespace
            and tokens[2] == phrase[1]
            and tokens[3][0] is Token.Text.Whitespace
            and tokens[4] == phrase[2]
            and tokens[5][0] is Token.Text.Whitespace
            and tokens[6] == phrase[3]
           ):
            assembled_phrase = ' '.join([t[1] for t in phrase])
            return ((Token.Keyword, assembled_phrase), tokens_in_phrase)

    return (None, None)


### SECOND PASS FUNCTIONS

def get_qualified_identifier(tokens):
    """
    Consumes a series of dot-separated names, of any length.
    Only foo.bar and foo.bar.baz are typically found in SQL, but 1) there are weird dialects out there,
    and 2) we wish to be sloppy rather than strict in our parsing.
    """
    length = len(tokens)
    if length < 3 or tokens[0][0] not in (Token.Name, Token.Literal.String.Name):
        return (None, None)

    consumed = [tokens[0]]
    j = 1
    while j+1 < length and tokens[j] == DOT and tokens[j+1][0] in (Token.Name, Token.Literal.String.Name):
        consumed.append(tokens[j])
        consumed.append(tokens[j+1])
        j += 2

    assembled_token = (Token.Name, ''.join([t[1] for t in consumed]))
    return (assembled_token, len(consumed))


### TRANSLATION FUNCTION(S)

def pygments_token_to_sftoken(token):
    ttype, value = token

    # cases are alphabetical
    if ttype == Token.Comment.Multiline:
        return SFToken(SFTokenKind.BLOCK_COMMENT, value)
    elif ttype == Token.Comment.Single:
        return SFToken(SFTokenKind.LINE_COMMENT, value)
    elif ttype == Token.Keyword:
        return SFToken(SFTokenKind.WORD, value)
    elif ttype == Token.Literal.Number.Float:
        pass
    elif ttype == Token.Literal.String.Name:
        pass
    elif ttype == Token.Literal.String.Single:
        pass
    elif ttype == Token.Name:
        pass
    elif ttype == Token.Name.Builtin:
        pass
    elif ttype == Token.Operator:
        pass
    elif ttype == Token.Punctuation:
        pass
    elif ttype == Token.Text.Whitespace:
        pass
    else:
        # we need to be comprehensive so explode loudly on any unhandled case
        raise ValueError(f"unexpected Pygments token type '{ttype}' with value '{value}'")


### DRIVER FUNCTIONS

def retokenize1(tokens):
    out = []
    i = 0
    length = len(tokens)
    while i < length:
        # single-quoted string literals
        #TODO: support affixed literals E'...', B'...', U&'...', x'...'
        if tokens[i] == SINGLE_QUOTE:
            quoted_literal, tokens_consumed = get_single_quoted_literal(tokens[i:])
            if quoted_literal:
                out.append(quoted_literal)
                i += tokens_consumed
                continue

        # dollar-quoted string literals
        if tokens[i] == DOLLAR_QUOTE:
            quoted_literal, tokens_consumed = get_dollar_quoted_literal(tokens[i:])
            if quoted_literal:
                out.append(quoted_literal)
                i += tokens_consumed
                continue

        # double-quoted/backtick-quoted identifiers
        if tokens[i] in (DOUBLE_QUOTE, BACKTICK_QUOTE):
            quoted_name, tokens_consumed = get_quoted_name(tokens[i:])
            if quoted_name:
                out.append(quoted_name)
                i += tokens_consumed
                continue

        # multi-keyword phrases
        keyphrase = None
        if i+3 < length and tokens[i] in (FOUR_WORD_PHRASE_STARTERS):
            keyphrase, tokens_consumed = get_four_word_key_phrase(tokens[i:])
        elif i+2 < length and tokens[i] in (THREE_WORD_PHRASE_STARTERS):
            keyphrase, tokens_consumed = get_three_word_key_phrase(tokens[i:])
        elif i+1 < length and tokens[i] in (TWO_WORD_PHRASE_STARTERS):
            keyphrase, tokens_consumed = get_three_word_key_phrase(tokens[i:])

        if keyphrase:
            out.append(keyphrase)
            i += tokens_consumed
            continue

        # whitespace
        if tokens[i][0] is Token.Text.Whitespace:
            #TODO: convert tabs to spaces
            #TODO: split newlines apart from other whitespace
            pass

        # everything else passes through unmodified
        out.append(tokens[i])
        i += 1

    return out


def retokenize2(tokens):
    out = []
    i = 0
    length = len(tokens)
    while i < length:
        if i+2 < length: # qualified identifiers
            phrase = tokens[i:i+5]
            qualified_identifier, tokens_consumed = get_qualified_identifier(phrase)
            if qualified_identifier:
                out.append(qualified_identifier)
                i += tokens_consumed
                continue

        out.append(tokens[i])
        i += 1

    return out


def sftokenize(tokens):
    return [pygments_token_to_sftoken(t) for t in tokens]


if __name__ == '__main__':
    unformatted_code = sys.stdin.read()

    lexer = get_lexer_by_name("postgres", stripall=True)
    tokens = pre_process_tokens(lexer.get_tokens(unformatted_code))

    print(f'count={len(tokens)}')
    for t in tokens:
        print(t)

    tokens_after_first_pass = retokenize1(tokens)
    tokens_after_second_pass = retokenize2(tokens_after_first_pass)

    print(f'count={len(tokens_after_second_pass)}')
    for t in tokens_after_second_pass:
        print(t)
