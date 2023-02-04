import re

from sftoken import SFToken, SFTokenKind


SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
BACKTICK = "`"
BLOCK_COMMENT_OPEN = "/*"
BLOCK_COMMENT_CLOSE = "*/"
LINE_COMMENT_START = "--"


# alternate approach...
def lex(input_string):
    if input_string is None or len(input_string) == 0:
        return []

    RE_SPACES = re.compile(r"[ ]+")
    RE_SINGLE_QUOTED_STRING = re.compile(r"(')(\\.|''|[^'\\])*(')")
    RE_DOUBLE_QUOTED_STRING = re.compile(r'(")(\\.|""|[^"\\])*(")')
    RE_BACKTICK_QUOTED_STRING = re.compile(r"(`)(\\.|``|[^`\\])*(`)")
    RE_DOLLAR_QUOTED_STRING = re.compile(r"(\$[A-Za-z0-9_]*\$)(.*?)(\1)", flags=re.DOTALL)
    RE_LINE_COMMENT = re.compile(r"--.*?(\n|$)")
    RE_BLOCK_COMMENT = re.compile(r"(/\*)(.*?)(\*/)", flags=re.DOTALL)
    RE_ALPHANUMERIC_WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

    tokens = []

    i = 0
    while i < len(input_string):
        # https://www.postgresql.org/docs/current/sql-syntax-lexical.html

        # newline
        if "\n" == input_string[i]:
            tokens.append(SFToken(SFTokenKind.NEWLINE, "\n"))
            i += 1
            continue

        # space(s)
        match_res = RE_SPACES.match(input_string[i:])
        if match_res:
            string_of_spaces = match_res[0]
            tokens.append(SFToken(SFTokenKind.SPACES, string_of_spaces))
            i += len(string_of_spaces)
            continue

        # supposedly the (ANTLR) grammar for quotes...
        # fragment DQUOTA_STRING : '"' ( '\\'. | '""' | ~('"' | '\\') )* '"';
        # fragment SQUOTA_STRING : '\'' ('\\'. | '\'\'' | ~('\'' | '\\'))* '\'';
        # fragment BQUOTA_STRING : '`' ( '\\'. | '``' | ~('`' | '\\'))* '`';

        # all kinds of quoted strings
        match_res = RE_SINGLE_QUOTED_STRING.match(input_string[i:])
        if not match_res:
            match_res = RE_DOUBLE_QUOTED_STRING.match(input_string[i:])
        if not match_res:
            match_res = RE_BACKTICK_QUOTED_STRING.match(input_string[i:])
        if not match_res:
            match_res = RE_DOLLAR_QUOTED_STRING.match(input_string[i:])
        if match_res:
            string_literal = match_res[0]
            tokens.append(SFToken(SFTokenKind.LITERAL, string_literal))
            i += len(string_literal)
            continue

        # line comment
        match_res = RE_LINE_COMMENT.match(input_string[i:])
        if match_res:
            line_comment = match_res[0]
            tokens.append(SFToken(SFTokenKind.LINE_COMMENT, line_comment))
            i += len(line_comment)
            continue

        # block comment
        match_res = RE_BLOCK_COMMENT.match(input_string[i:])
        if match_res:
            block_comment = match_res[0]
            tokens.append(SFToken(SFTokenKind.BLOCK_COMMENT, block_comment))
            i += len(block_comment)
            continue

        # alphanumeric word (incl. underscore)
        # TODO: also PG allows dollar-number placeholders e.g. $1
        # TODO: and dollar signs in identifiers e.g. foo$bar (not SQL standard?)
        match_res = RE_ALPHANUMERIC_WORD.match(input_string[i:])
        if match_res:
            word = match_res[0]
            tokens.append(SFToken(SFTokenKind.WORD, word))
            i += len(word)
            continue

        # numeric word (integer literals, float literals, scientific literals)
        # r"[0-9]+"
        # r"[0-9]+\.([0-9]+)?([eE][-+]?[0-9]+)?"
        # r"([0-9]+)?\.[0-9]+([eE][-+]?[0-9]+)?"
        # r"[0-9]+[eE][-+]?[0-9]+"
        # but, it may be preferable to use the sloppy approach below, or a regex equivalent...
        if input_string[i].isdigit() or (
            "." == input_string[i] and len(input_string) >= 2 and input_string[i+1].isdigit()
        ): # btw there are some wonky characters where isdigit()=True like "¹"
            j = i + 1
            while j < len(input_string):
                if not (input_string[j].isdigit() or input_string[j] in [".", "e", "E"]): # not strict, matches crap like 1.e37E5e.8. etc
                    break
                j += 1
            numeric_word = input_string[i:j]
            tokens.append(SFToken(SFTokenKind.WORD, numeric_word))
            i = j
            continue

        # symbol
        #   this is our dumping ground... if we haven't matched anything else, it must(?) be a symbol, which in practice means
        #   actual symbols, control characters, plus most weird unicode stuff if it appears outside of quotes
        tokens.append(SFToken(SFTokenKind.SYMBOL, input_string[i]))
        i += 1
        continue

    return tokens


