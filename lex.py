import sys

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token


if __name__ == '__main__':
    unformatted_code = sys.stdin.read()

    lexer = get_lexer_by_name("postgres", stripall=True)
    tokens = list(lexer.get_tokens(unformatted_code))

    print(f'count={len(tokens)}')
    for t in tokens:
        print(t)
