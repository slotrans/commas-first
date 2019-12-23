import sys
import re

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

ALL_WHITESPACE = re.compile(r'^\s+$')

# keywords
SELECT = (Token.Keyword, 'select')
FROM = (Token.Keyword, 'from')
WHERE = (Token.Keyword, 'where')
GROUP_BY = (Token.Keyword, 'group by')
HAVING = (Token.Keyword, 'having')
ORDER_BY = (Token.Keyword, 'order by')
LIMIT = (Token.Keyword, 'limit')
OFFSET = (Token.Keyword, 'offset')

# punctuation
LEFT_PAREN = (Token.Punctuation, '(')
RIGHT_PAREN = (Token.Punctuation, ')')
COMMA = (Token.Punctuation, ',')


def should_change_scope(token):
    if token in (FROM, WHERE, GROUP_BY, HAVING, ORDER_BY, LIMIT, OFFSET):
        return True
    else:
        return False


if __name__ == '__main__':
    unformatted_code = sys.stdin.read()

    lexer = get_lexer_by_name("postgres", stripall=True)
    tokens = list(lexer.get_tokens(unformatted_code))

    paren_depth = 0
    outbuffer = ''
    for ttype, value in tokens:
        token = (ttype, value)

        if ttype is Token.Text and ALL_WHITESPACE.match(value):
            continue

        if token == SELECT:
            outbuffer = 'select '

        elif token == LEFT_PAREN:
            paren_depth += 1
            outbuffer += value

        elif token == RIGHT_PAREN:
            paren_depth -= 1
            outbuffer += value

        elif token == COMMA and paren_depth == 0: # expression is over
            outbuffer += '\n, '
            print(outbuffer, end='')
            outbuffer = ''

        else:
            outbuffer += value

    print(outbuffer)

    if paren_depth != 0:
        print('/* WARNING: unbalanced parens */')
        # would probably be better to delay all output until the end, do this check, and if true just return the input
        # unmodified along with this warning
        # this is fine for now though


