import sys
import argparse

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

import sf_flags
from retokenize import pre_process_tokens, retokenize1, retokenize2, sftokenize
from clause_formatter import CompoundStatement


def do_format(unformatted_code):
    lexer = get_lexer_by_name("postgres", stripall=True)
    tokens = pre_process_tokens(lexer.get_tokens(unformatted_code))

    tokens_after_first_pass = retokenize1(tokens)
    tokens_after_second_pass = retokenize2(tokens_after_first_pass)
    translated_tokens = sftokenize(tokens_after_second_pass)

    # this is not yet equipped to handle multiple ;-separated statements
    compound_statement = CompoundStatement(translated_tokens)
    return compound_statement


def main(args):
    # set global flags
    sf_flags.TRIM_LEADING_WHITESPACE = args.trim_leading_whitespace

    # read
    unformatted_code = sys.stdin.read()

    # process
    renderable = do_format(unformatted_code)

    # write
    print(renderable.render(indent=0))

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trim-leading-whitespace", action="store_true", help="Trim leading whitespace from expressions")
    args = parser.parse_args()

    sys.exit(main(args))
