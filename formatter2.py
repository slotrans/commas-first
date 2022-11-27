import sys
import argparse

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

import sf_flags
from retokenize import pre_process_tokens, retokenize1, retokenize2, sftokenize
from clause_formatter import CompoundStatement


def trim_trailing_whitespace_from_lines(input_string):
    lines = input_string.split("\n")
    trimmed_lines = [l.rstrip() for l in lines]
    reassembled_string = "\n".join(trimmed_lines)
    return reassembled_string


def get_renderable(unformatted_code):
    lexer = get_lexer_by_name("postgres", stripall=True)
    tokens = pre_process_tokens(lexer.get_tokens(unformatted_code))

    tokens_after_first_pass = retokenize1(tokens)
    tokens_after_second_pass = retokenize2(tokens_after_first_pass)
    translated_tokens = sftokenize(tokens_after_second_pass)

    # this is not yet equipped to handle multiple ;-separated statements
    compound_statement = CompoundStatement(translated_tokens)
    return compound_statement


def do_format(unformatted_code):
    renderable = get_renderable(unformatted_code)
    rendered = renderable.render(indent=0)
    trimmed = trim_trailing_whitespace_from_lines(rendered)
    return trimmed


def main(args):
    # set global flags
    if args.trim_leading_whitespace:
        sf_flags.FORMAT_MODE = sf_flags.FormatMode.TRIM_LEADING_WHITESPACE
    elif args.compact_expressions:
        sf_flags.FORMAT_MODE = sf_flags.FormatMode.COMPACT_EXPRESSIONS
    else:
        sf_flags.FORMAT_MODE = sf_flags.FormatMode.DEFAULT

    # read
    unformatted_code = sys.stdin.read()

    # process
    formatted_code = do_format(unformatted_code)

    # write
    print(formatted_code)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    mx_group = parser.add_mutually_exclusive_group(required=False)
    mx_group.add_argument("--trim-leading-whitespace", action="store_true", help="Trim leading whitespace from expressions")
    mx_group.add_argument("--compact-expressions", action="store_true", help="Remove most internal space from expressions (strictly more aggressive than --trim-leading-whitespace)")

    args = parser.parse_args()

    sys.exit(main(args))
