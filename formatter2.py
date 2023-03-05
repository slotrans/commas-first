import sys
import argparse

import cf_flags
import cflexer
from retokenize import pre_process_tokens, initial_lex, retokenize1, retokenize2, cftokenize
from clause_formatter import CompoundStatement


def trim_trailing_whitespace_from_lines(input_string):
    lines = input_string.split("\n")
    trimmed_lines = [l.rstrip() for l in lines]
    reassembled_string = "\n".join(trimmed_lines)
    return reassembled_string


def get_renderable(unformatted_code, lexer_impl):
    if lexer_impl == "pygments":        
        initial_tokens = initial_lex(unformatted_code)
        pre_processed_tokens = pre_process_tokens(initial_tokens)
        tokens_after_first_pass = retokenize1(pre_processed_tokens)
        tokens_after_second_pass = retokenize2(tokens_after_first_pass)
        final_tokens = cftokenize(tokens_after_second_pass)
    elif lexer_impl == "cflexer":
        tokens = cflexer.lex(unformatted_code)
        final_tokens = cflexer.collapse_identifiers(tokens)
    else:
        raise ValueError(f"unknown lexer_impl {lexer_impl}")

    # this is not yet equipped to handle multiple ;-separated statements
    compound_statement = CompoundStatement(final_tokens)
    return compound_statement


def do_format(unformatted_code):
    renderable = get_renderable(unformatted_code, "cflexer")
    rendered = renderable.render(indent=0)
    trimmed = trim_trailing_whitespace_from_lines(rendered)
    return trimmed


def main(args):
    # set global flags
    if args.trim_leading_whitespace:
        cf_flags.FORMAT_MODE = cf_flags.FormatMode.TRIM_LEADING_WHITESPACE
    elif args.compact_expressions:
        cf_flags.FORMAT_MODE = cf_flags.FormatMode.COMPACT_EXPRESSIONS
    else:
        cf_flags.FORMAT_MODE = cf_flags.FormatMode.DEFAULT

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
