import sys

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

from retokenize import pre_process_tokens, retokenize1, retokenize2, sftokenize
from clause_formatter import CompoundStatement


def do_format(input_string):
    lexer = get_lexer_by_name("postgres", stripall=True)
    tokens = pre_process_tokens(lexer.get_tokens(unformatted_code))

    tokens_after_first_pass = retokenize1(tokens)
    tokens_after_second_pass = retokenize2(tokens_after_first_pass)
    translated_tokens = sftokenize(tokens_after_second_pass)

    # this is not yet equipped to handle multiple ;-separated statements
    compound_statement = CompoundStatement(translated_tokens)
    return compound_statement


def main():
    unformatted_code = sys.stdin.read()

    renderable = do_format(unformatted_code)

    print(renderable.render(indent=0))

    return 0


if __name__ == "__main__":
    # TODO: argparse
    sys.exit(main())
