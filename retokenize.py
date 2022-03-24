import sys
import re

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token


LEFT_OUTER_JOIN = [(Token.Keyword, 'left'), (Token.Keyword, 'outer'), (Token.Keyword, 'join')]
RIGHT_OUTER_JOIN = [(Token.Keyword, 'right'), (Token.Keyword, 'outer'), (Token.Keyword, 'join')]
IS_NOT_NULL = [(Token.Keyword, 'is'), (Token.Keyword, 'not'), (Token.Keyword, 'null')]

THREE_WORD_PHRASES = [
    LEFT_OUTER_JOIN,
    RIGHT_OUTER_JOIN,
    IS_NOT_NULL,
]

CROSS_JOIN = [(Token.Keyword, 'cross'), (Token.Keyword, 'join')]
LEFT_JOIN = [(Token.Keyword, 'left'), (Token.Keyword, 'join')]
RIGHT_JOIN = [(Token.Keyword, 'right'), (Token.Keyword, 'join')]
GROUP_BY = [(Token.Keyword, 'group'), (Token.Keyword, 'by')]
ORDER_BY = [(Token.Keyword, 'order'), (Token.Keyword, 'by')]
PARTITION_BY = [(Token.Keyword, 'partition'), (Token.Keyword, 'by')]
WITHIN_GROUP = [(Token.Keyword, 'within'), (Token.Keyword, 'group')]
IS_NULL = [(Token.Keyword, 'is'), (Token.Keyword, 'null')]

TWO_WORD_PHRASES = [
    CROSS_JOIN,
    LEFT_JOIN,
    RIGHT_JOIN,
    GROUP_BY,
    ORDER_BY,
    PARTITION_BY,
    WITHIN_GROUP,
    IS_NULL
]

SINGLE_QUOTE = (Token.Literal.String.Single, "'")
DOUBLE_QUOTE = (Token.Literal.String.Name, '"')


ALL_WHITESPACE = re.compile(r'^\s+$')
def is_only_whitespace(token):
    ttype, value = token
    return (ttype == Token.Text and ALL_WHITESPACE.match(value))


def pre_process_tokens(tokenlist):
    out = []
    for t in tokenlist:
        ttype, value = t
        if is_only_whitespace(t):
            continue

        if ttype is Token.Keyword:
            value = value.lower()

        out.append( (ttype, value) )

    return out


def merge_keyphrase(token_phrase):
    text = ' '.join([t[1] for t in token_phrase])
    return (Token.Keyword, text)


def merge_identifier(token_phrase):
    text = ''.join(t[1] for t in token_phrase)
    return (Token.Name, text)


def assemble_quoted_literal(tokens):
    length = len(tokens)
    j = 1 # not zero! we already know the 0th token is a single quote
    while j < length:
        if tokens[j] == SINGLE_QUOTE:
            phrase = tokens[0:j+1]
            quoted_literal = ''.join([t[1] for t in phrase])
            return ((Token.Literal.String.Single, quoted_literal), j+1)
        else:
            j += 1
    return (None, None)


def assemble_quoted_name(tokens):
    length = len(tokens)
    j = 1 # not zero! we already know the 0th token is a single quote
    while j < length:
        if tokens[j] == DOUBLE_QUOTE:
            phrase = tokens[0:j+1]
            quoted_name = ''.join([t[1] for t in phrase])
            return ((Token.Name, quoted_name), j+1)
        j += 1
    return (None, None)


def try_qualified_identifier(tokens):
    first_type, first_value = tokens[0]
    second_type, second_value = tokens[1]
    third_type, third_value = tokens[2]

    if (    first_type is Token.Name
        and second_type is Token.Literal.Number.Float
        and second_value == '.'
        and third_type is Token.Name
       ):
        return merge_identifier(tokens)
    else:
        return None


def try_double_qualified_identifier(tokens):
    first_type, first_value = tokens[0]
    second_type, second_value = tokens[1]
    third_type, third_value = tokens[2]
    fourth_type, fourth_value = tokens[3]
    fifth_type, fifth_value = tokens[4]

    if (    first_type is Token.Name
        and second_type is Token.Literal.Number.Float
        and second_value == '.'
        and third_type is Token.Name
        and fourth_type is Token.Literal.Number.Float
        and fourth_value == '.'
        and fifth_type is Token.Name
       ):
        return merge_identifier(tokens)
    else:
        return None


def retokenize1(tokens):
    out = []

    i = 0
    length = len(tokens)
    while i < length:
        if tokens[i] == SINGLE_QUOTE:
            quoted_literal, tokens_consumed = assemble_quoted_literal(tokens[i:])
            if quoted_literal:
                out.append(quoted_literal)
                i += tokens_consumed
                continue

        if tokens[i] == DOUBLE_QUOTE:
            quoted_name, tokens_consumed = assemble_quoted_name(tokens[i:])
            if quoted_name:
                out.append(quoted_name)
                i += tokens_consumed
                continue

        out.append(tokens[i])
        i += 1

    return out


def retokenize2(tokens):
    out = []

    i = 0
    length = len(tokens)
    while i < length:
        if i+4 < length: # double-qualified identifiers
            phrase = tokens[i:i+5]
            double_qualified_identifier = try_double_qualified_identifier(phrase)
            if double_qualified_identifier:
                out.append(double_qualified_identifier)
                i += 5
                continue

        if i+2 < length: # 3-token phrases, qualified identifiers
            phrase = tokens[i:i+3]
            if phrase in THREE_WORD_PHRASES:
                out.append(merge_keyphrase(phrase))
                i += 3
                continue
            else:
                qualified_identifier = try_qualified_identifier(phrase)
                if qualified_identifier:
                    out.append(qualified_identifier)
                    i += 3
                    continue

        if i+1 < length: # 2-token phrases
            phrase = tokens[i:i+2]
            if phrase in TWO_WORD_PHRASES:
                out.append(merge_keyphrase(phrase))
                i += 2
                continue

        out.append(tokens[i])
        i += 1

    return out


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
