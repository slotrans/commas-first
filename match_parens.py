from __future__ import annotations
import sys
import re
from dataclasses import dataclass
import enum

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token
import colorama


class MyTokenType(enum.Enum):
    WHITESPACE = 'WHITESPACE'
    KEYWORD = 'KEYWORD'
    OPERATOR = 'OPERATOR'
    PUNCTUATION = 'PUNCTUATION'
    IDENTIFIER = 'IDENTIFIER'
    LITERAL = 'LITERAL'
    COMMENT_LINE = 'COMMENT_LINE'
    COMMENT_BLOCK = 'COMMENT_BLOCK'


@dataclass
class InputToken():
    token_type: str
    string_value: str
    line: int
    column: int
    matching_token: InputToken = None
    color: str = None

    #output_line ??
    #output_indent ??


def derive_type(token):
    ttype, value = token
    if ttype in Token.Text and re.match(r'^\s+$', value):
        return MyTokenType.WHITESPACE
    elif ttype in Token.Text:
        raise Exception(f'non-whitespace Text token: {token}')
    elif ttype in Token.Keyword:
        return MyTokenType.KEYWORD # TODO: override non-keyword keywords like "greatest"
    elif ttype in Token.Operator:
        return MyTokenType.OPERATOR
    elif ttype in Token.Punctuation or (ttype in Token.Literal.Number.Float and value == '.'):
        return MyTokenType.PUNCTUATION
    elif ttype in Token.Name:
        return MyTokenType.IDENTIFIER
    elif ttype in Token.Literal:
        return MyTokenType.LITERAL
    elif ttype in Token.Comment.Single:
        return COMMENT_LINE
    elif ttype in Token.Comment.Multiline:
        return COMMENT_BLOCK
    else:
        raise Exception(f'unexpected token permutation: {token}')


def cursor_motion(init_x: int, init_y: int, instr: str): # Tuple(int, int)
    x = init_x
    y = init_y
    for c in instr:
        if '\n' == c:
            y += 1
            x = 1 # a newline resets the column to 1
        else:
            x += 1

    return (x, y)


def generate_color():
    yield colorama.Fore.RED
    yield colorama.Fore.GREEN
    yield colorama.Fore.YELLOW
    yield colorama.Fore.CYAN
    yield colorama.Fore.MAGENTA
    yield colorama.Fore.BLUE
    yield colorama.Fore.WHITE


if __name__ == '__main__':
    unformatted_code = sys.stdin.read()

    lexer = get_lexer_by_name("postgres", stripall=True)
    tokens = lexer.get_tokens(unformatted_code)

    paren_stack = []
    current_line = 1
    current_column = 1
    out = []
    color_picker = generate_color()
    for token in tokens:
        ttype, value = token
        itoken = InputToken(
            token_type = derive_type(token),
            string_value = value,
            line = current_line,
            column = current_column,
            matching_token = None,
        )      
        # for left/open parens: after constructing the object put it on a stack
        if '(' == itoken.string_value:
            itoken.color = next(color_picker)
            paren_stack.append(itoken)
        # for right/close parens: 1. pop from the stack 2. point the current token and the popped token at each other
        elif ')' == itoken.string_value:
            open_token = paren_stack.pop()
            open_token.matching_token = itoken
            itoken.matching_token = open_token
            itoken.color = open_token.color

        current_column, current_line = cursor_motion(current_column, current_line, itoken.string_value)

        out.append(itoken)

    for x in out:
        print(x)

    print('-------------------------------------------------------------------')

    colorama.init(autoreset=True)

    for x in out:
        color_escape = x.color if x.color else ''
        print(f'{color_escape}{x.string_value}', end='')
    print()
