import sys
import re

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token


LEFT_OUTER_JOIN = [(Token.Keyword, 'left'), (Token.Keyword, 'outer'), (Token.Keyword, 'join')]
RIGHT_OUTER_JOIN = [(Token.Keyword, 'right'), (Token.Keyword, 'outer'), (Token.Keyword, 'join')]

THREE_WORD_PHRASES = [
    LEFT_OUTER_JOIN, 
    RIGHT_OUTER_JOIN,
]

CROSS_JOIN = [(Token.Keyword, 'cross'), (Token.Keyword, 'join')]
LEFT_JOIN = [(Token.Keyword, 'left'), (Token.Keyword, 'join')]
RIGHT_JOIN = [(Token.Keyword, 'right'), (Token.Keyword, 'join')]
GROUP_BY = [(Token.Keyword, 'group'), (Token.Keyword, 'by')]
ORDER_BY = [(Token.Keyword, 'order'), (Token.Keyword, 'by')]
PARTITION_BY = [(Token.Keyword, 'partition'), (Token.Keyword, 'by')]
WITHIN_GROUP = [(Token.Keyword, 'within'), (Token.Keyword, 'group')]

TWO_WORD_PHRASES = [
    CROSS_JOIN,
    LEFT_JOIN,
    RIGHT_JOIN,
    GROUP_BY,
    ORDER_BY,
    PARTITION_BY,
    WITHIN_GROUP,
]

SINGLE_QUOTE = (Token.Literal.String.Single, "'")


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


def merge_tokens(token_phrase):
    text = ' '.join([t[1] for t in token_phrase])
    return (Token.Keyword, text)


def assemble_quoted_literal(tokens):
    length = len(tokens)
    j = 1 # not zero! we already know the 0th token is a single quote
    while j < length:
        if tokens[j] == SINGLE_QUOTE:
            phrase = tokens[0:j+1]
            quoted_literal = ''.join([t[1] for t in phrase])
            return ((Token.Literal.String.Single, quoted_literal), j+1)
        j += 1
    return (None, None)


def retokenize(tokens):
    out = []

    i = 0
    length = len(tokens)
    while i < length:
        if i+2 < length: # 3-token phrases
            phrase = tokens[i:i+3]
            if phrase in THREE_WORD_PHRASES:
                out.append(merge_tokens(phrase))
                i += 3
                continue
        
        if i+1 < length: # 2-token phrases
            phrase = tokens[i:i+2]
            if phrase in TWO_WORD_PHRASES:
                out.append(merge_tokens(phrase))
                i += 2
                continue
        
        if tokens[i] == SINGLE_QUOTE:
            quoted_literal, tokens_consumed = assemble_quoted_literal(tokens[i:])
            if quoted_literal:
                out.append(quoted_literal)
                i += tokens_consumed
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

    tokens2 = retokenize(tokens)

    print(f'count={len(tokens2)}')
    for t in tokens2:
        print(t)
