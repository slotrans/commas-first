import sys
import re

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token


LEFT_OUTER_JOIN = [(Token.Keyword, 'left'), (Token.Keyword, 'outer'), (Token.Keyword, 'join')]
RIGHT_OUTER_JOIN = [(Token.Keyword, 'right'), (Token.Keyword, 'outer'), (Token.Keyword, 'join')]

CROSS_JOIN = [(Token.Keyword, 'cross'), (Token.Keyword, 'join')]
LEFT_JOIN = [(Token.Keyword, 'left'), (Token.Keyword, 'join')]
RIGHT_JOIN = [(Token.Keyword, 'right'), (Token.Keyword, 'join')]
GROUP_BY = [(Token.Keyword, 'group'), (Token.Keyword, 'by')]
ORDER_BY = [(Token.Keyword, 'order'), (Token.Keyword, 'by')]
PARTITION_BY = [(Token.Keyword, 'partition'), (Token.Keyword, 'by')]
WITHIN_GROUP = [(Token.Keyword, 'within'), (Token.Keyword, 'group')]


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


def retokenize(tokens):
    out = []

    i = 0
    length = len(tokens)
    while i < length:
        if i+2 < length: # 3-token phrases
            phrase = tokens[i:i+3]
            if phrase == LEFT_OUTER_JOIN:
                out.append(merge_tokens(phrase))
                i += 3
                continue
            elif phrase == RIGHT_OUTER_JOIN:
                out.append(merge_tokens(phrase))
                i += 3
                continue
        
        if i+1 < length: # 2-token phrases
            phrase = tokens[i:i+2]
            if phrase == CROSS_JOIN:
                out.append(merge_tokens(phrase))
                i += 2
                continue
            elif phrase == LEFT_JOIN:
                out.append(merge_tokens(phrase))
                i += 2
                continue
            elif phrase == RIGHT_JOIN:
                out.append(merge_tokens(phrase))
                i += 2
                continue
            elif phrase == GROUP_BY:
                out.append(merge_tokens(phrase))
                i += 2
                continue
            elif phrase == ORDER_BY:
                out.append(merge_tokens(phrase))
                i += 2
                continue
            elif phrase == PARTITION_BY:
                out.append(merge_tokens(phrase))
                i += 2
                continue
            elif phrase == WITHIN_GROUP:
                out.append(merge_tokens(phrase))
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

    tokens2 = retokenize(tokens)

    print(f'count={len(tokens2)}')
    for t in tokens2:
        print(t)
