import collections

from sftoken import SFToken, SFTokenKind


def get_char(deq):
    try:
        return deq.popleft()
    except IndexError:
        return None


def lex(input_string):
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
