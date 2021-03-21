import sys
import re

PUNCTUATION = set([
    '`',
    '~',
    '@',
    '#',
    '$',
    '%',
    '^',
    '&',
    '*',
    '(',
    ')',
    '_',
    '+',
    '-',
    '=',
    '[',
    ']',
    '\\',
    '{',
    '}',
    '|',
    ';',
    "'",
    ':',
    '"',
    ',',
    '.',
    '/',
    '<',
    '>',
    '?',
])

# ascii ranges of punctuation
# 33 through 47
# 58 through 64
# 91 through 96
# 123 through 126

# words  (keywords, identifiers, and some functions that don't require parens)
# --line comments
# /* block comments */
# 'string literals'
# e'special string literals'  (not sure what prefix letters are valid?)
# "quoted identifiers"
# `backtick-quoted identifiers` (MySQL, Hive, BigQuery)
# numeric literals e.g. 0, 1, 478, -0.5, +1.23, 4.32e9, 1e-5
# qualified.identifiers
# double.qualified.identifiers
# "quoted_and_qualified"."identifiers" (also double-qualified)
# array_construction[1, 2, 3] and subscripts[0]
# function(calls) and function(calls, with, delimited, arguments) and function_calls_with_empty_arguments()
# delimiter: ,
# statement terminator: ;
# 1-character operators: = + - / * % ^ ? | & # ~ :
# 2-character operators: || ** >= <= <> != -> => #> @> <@ ?| ?& #- @? @@ |/ << >> ## && &< &> <^ >^ ?# ?- ~= !! :: !~ ~*
# 3-character operators: ->> #>> ||/ @-@ <-> <<| |>> &<| |&> ?-| ?|| <<= >>= @@@ -|- !~*


RGX_WORD = re.compile(r"\w+") # doesn't require that words start with a letter or underscore
RGX_WHITESPACE = re.compile(r"\s+")
RGX_NUMERIC_LITERAL = re.compile(r"[+-]?([0-9][0-9Ee.]+|(\.[0-9Ee]+))") # deliberately sloppy: accepts repeated decimals, E's, other nonsense

# doesn't support "no digits left of the decimal" e.g. "-.5" but otherwise follows the spec
# preserving here in case strictness ends up being preferable to sloppiness
RGX_STRICT_NUMERIC_LITERAL = re.compile(r"""([+-])?             # sign
                                            ([0-9]+)            # digits
                                            (\.[0-9]+)?         # decimal and digits after
                                            ([Ee][+-]?[0-9]+)?  # scientific notation
                                            (\W|$)              # non-word character or end-of-string
                                         """, re.X)

def get_token(stream):
    numeric_match = RGX_NUMERIC_LITERAL.match(stream)
    if numeric_match:
        #print(f"found numeric literal [{numeric_match.group(0)}] length={len(numeric_match.group(0))}")
        return numeric_match.group(0)

    word_match = RGX_WORD.match(stream)
    if word_match:
        #print(f"found word [{word_match.group(0)}] length={len(word_match.group(0))}")
        return word_match.group(0)

    whitespace_match = RGX_WHITESPACE.match(stream)
    if whitespace_match:
        #print(f"found whitespace length={len(whitespace_match.group(0))}")
        return whitespace_match.group(0)

    return stream[0]


def tokenize(stream):
    tokens = []
    
    while len(stream) > 0:
        tok = get_token(stream)
        tokens.append(tok)
        stream = stream[len(tok):]
    
    return tokens


if __name__ == '__main__':
    input_raw = sys.stdin.read()

    token_strings = tokenize(input_raw)

    for i in token_strings:
        print(f"[{i}]")
