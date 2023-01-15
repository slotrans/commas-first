import collections

from sftoken import SFToken, SFTokenKind


SINGLE_QUOTE = "'"
DOUBLE_QUOTE = '"'
BACKTICK = "`"
BLOCK_COMMENT_OPEN = "/*"
BLOCK_COMMENT_CLOSE = "*/"
LINE_COMMENT_START = "--"


def get_char(deq):
    try:
        return deq.popleft()
    except IndexError:
        return None


def lex_stateful(input_string):
    if input_string is None or len(input_string) == 0:
        return []

    stream = collections.deque(input_string)
    tokens = []

    last_char = get_char(stream)
    while True:
        # exit condition
        if last_char is None:
            break
    
        # space(s)
        if " " == last_char:
            # this could be optimized(?) by just counting spaces rather than using a buffer, but I want to establish the pattern
            buffer = [last_char]
            while " " == last_char:
                buffer.append(last_char)
                last_char = get_char(stream)
            temp = "".join(buffer)
            tokens.append(SFToken(SFTokenKind.SPACES, temp))
            continue

        # newline
        if "\n" == last_char:
            tokens.append(SFToken(SFTokenKind.NEWLINE, "\n"))
            last_char = get_char(stream)
            continue

        # single-quoted string
        if "'" == last_char:
            raise NotImplementedError

        # double-quoted string
        if '"' == last_char:
            raise NotImplementedError

        # backtick-quoted string
        if "`" == last_char:
            raise NotImplementedError

        # dollar-quoted string
        #   ambiguous!!! $ only starts a dollar-quoted string if it's part of $$ or $foo$ etc.
        if "$" == last_char:
            raise NotImplementedError

        # line comment
        #   ambiguous!!! needs to be --
        if "-" == last_char:
            last_char = get_char(stream)
            if "-" != last_char:
                # not a comment starter, just a hyphen/minus
                tokens.append(SFToken(SFTokenKind.SYMBOL, "-"))
                continue
            else:
                buffer = ["-"] # the first one
                while True:
                    buffer.append(last_char)
                    last_char = get_char(stream)
                    if last_char is None:
                        break
                    elif "\n" == last_char:
                        buffer.append(last_char)
                        last_char = get_char(stream)
                        break
                temp = "".join(buffer)
                tokens.append(SFToken(SFTokenKind.LINE_COMMENT, "temp"))

        # block comment
        #   ambiguous!!! needs to be /*

        # alphanumeric word (incl. underscore)
        if last_char.isalpha() or "_" == last_char: # this may be too permissive, some non-ascii unicode have isalpha()=True
            raise NotImplementedError

        # numeric word (integer literals, float literals, scientific literals)
        if last_char.isdigit() or "." == last_char: # there are some wonky characters where isdigit()=True like "¹"
            raise NotImplementedError

        # symbol
        #   this is our dumping ground... if we haven't matched anything else, it must(?) be a symbol, which in practice means
        #   actual symbols, control characters, plus most weird unicode stuff if it appears outside of quotes
        tokens.append(SFToken(SFTokenKind.SYMBOL, last_char))

    return tokens


# alternate approach...
def lex(input_string):
    if input_string is None or len(input_string) == 0:
        return []

    tokens = []

    i = 0
    while i < len(input_string):
        # space(s)
        if " " == input_string[i]:
            j = i + 1
            while j < len(input_string):
                if input_string[j] != " ":
                    break
                j += 1
            spaces = j - i
            tokens.append(SFToken(SFTokenKind.SPACES, " "*spaces))
            i = j
            continue

        # newline
        if "\n" == input_string[i]:
            tokens.append(SFToken(SFTokenKind.NEWLINE, "\n"))
            i += 1
            continue

        # single-quoted string
        if SINGLE_QUOTE == input_string[i]:
            j = i + 1
            while j < len(input_string):
                if input_string[j] == SINGLE_QUOTE:
                    if input_string[j+1:j+2] == SINGLE_QUOTE:
                        # escaped quote
                        j += 2
                        continue
                    else:
                        break
                j += 1
            string_literal = input_string[i:j+1] # capture the closing quote
            tokens.append(SFToken(SFTokenKind.LITERAL, string_literal))
            i = j + 1
            continue

        # supposedly the (ANTLR) grammar for quotes...
        # fragment DQUOTA_STRING : '"' ( '\\'. | '""' | ~('"' | '\\') )* '"';
        # fragment SQUOTA_STRING : '\'' ('\\'. | '\'\'' | ~('\'' | '\\'))* '\'';
        # fragment BQUOTA_STRING : '`' ( '\\'. | '``' | ~('`' | '\\'))* '`';

        # double-quoted string
        if DOUBLE_QUOTE == input_string[i]:
            raise NotImplementedError

        # backtick-quoted string
        if BACKTICK == input_string[i]:
            raise NotImplementedError

        # dollar-quoted string
        if "$" == input_string[i]:
            # more to this, gotta look for $$ but also $foo$
            raise NotImplementedError

        # line comment
        if LINE_COMMENT_START == input_string[i:i+2]:
            j = i + 2
            while j < len(input_string):
                if input_string[j] == "\n":
                    break
                j += 1
            comment = input_string[i:j+1] # include the newline
            tokens.append(SFToken(SFTokenKind.LINE_COMMENT, comment))
            i = j + 1
            continue

        # block comment
        if BLOCK_COMMENT_OPEN == input_string[i:i+2]:
            j = i + 2
            while j < len(input_string):
                if input_string[j:j+2] == BLOCK_COMMENT_CLOSE:
                    break
                j += 1
            comment = input_string[i:j+2] # capture the comment close symbol
            tokens.append(SFToken(SFTokenKind.BLOCK_COMMENT, comment))
            i = j + 2
            continue

        # alphanumeric word (incl. underscore)
        if input_string[i].isalpha() or "_" == input_string[i]: # this may be too permissive, some non-ascii unicode have isalpha()=True
            j = i + 1
            while j < len(input_string):
                if not (input_string[j].isalpha() or "_" == input_string[j]):
                    break
                j += 1
            word = input_string[i:j]
            tokens.append(SFToken(SFTokenKind.WORD, word))
            i = j
            continue

        # numeric word (integer literals, float literals, scientific literals)
        if input_string[i].isdigit() or "." == input_string[i]: # there are some wonky characters where isdigit()=True like "¹"
            j = i + 1
            while j < len(input_string):
                if not (input_string[j].isdigit() or input_string[j] in [".", "e", "E"]): # not strict, matches crap like 1.e37E5e.8. etc
                    break
                j += 1
            word = input_string[i:j]
            tokens.append(SFToken(SFTokenKind.WORD, word))
            i = j
            continue

        # symbol
        #   this is our dumping ground... if we haven't matched anything else, it must(?) be a symbol, which in practice means
        #   actual symbols, control characters, plus most weird unicode stuff if it appears outside of quotes
        tokens.append(SFToken(SFTokenKind.SYMBOL, input_string[i]))
        i += 1
        continue

    return tokens
