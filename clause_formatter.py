import enum

import cf_flags
from cftoken import CFToken, CFTokenKind, Keywords, Symbols, Whitespace


def next_real_token(tokens):
    for t in tokens:
        if not t.is_whitespace:
            return t
    return None


def next_real_token_and_position(tokens):
    for i, t in enumerate(tokens):
        if not t.is_whitespace:
            return (t, i)
    return (None, None)


def get_paren_block(tokens):
    if len(tokens) == 0:
        raise ValueError("tokens must be non-empty")

    if tokens[0] != Symbols.LEFT_PAREN:
        raise ValueError("first token must be \"(\"")

    depth = 0
    block = []
    block_found = False
    for t in tokens:
        if t == Symbols.LEFT_PAREN:
            depth += 1
        elif t == Symbols.RIGHT_PAREN:
            depth -= 1
        block.append(t)

        if t == Symbols.RIGHT_PAREN and depth == 0:
            block_found = True
            break

    if block_found:
        return block
    else:
        return None


# I'm not sure what my original concept for this function was. It's currently unused, and left here as a breadcrumb.
def collapse_whitespace(tokens):
    i = 0
    out = []
    while i < len(tokens):
        if not tokens[i].is_whitespace:
            out.append(tokens[i])
        elif tokens[i] == Whitespace.NEWLINE:
            pass #idk yet

    #thoughts:
    # 1. Any sequence of [newline, newline, newline] (etc) can be collapsed to a single newline.
    #
    # 2. I suspect any sequence of whitespace that's a *mix* of newline and spaces, like...
    #  [newline, spaces, newline]
    #  [spaces, newline, spaces, newline, spaces]
    #  [spaces, newline, newline]
    #  [newline, newline, spaces]
    #  ...can be collapsed to a single newline followed by the last chunk of spaces.
    #  This might be a multi-step process, like:
    #  a. any sequence of [newline, spaces, newline] becomes [newline, newline]
    #  b. any sequence of [newline, newline] becomes [newline]
    #  (or maybe not, I can see ways those can be done in a single pass)
    #
    # 3. a tougher problem, which probably doesn't belong in this function, is trimming the left margin
    #  from blocks of spaces

    return out


def trim_trailing_whitespace(tokens):
    i = len(tokens) - 1
    while i >= 0 and tokens[i].is_whitespace:
        i -= 1

    return tokens[:i+1]


def trim_leading_whitespace(tokens):
    i = 0
    while i < len(tokens) and tokens[i].is_whitespace:
        i += 1

    return tokens[i:]


def trim_one_leading_space(tokens):
    if len(tokens) == 0:
        return tokens

    first_token = tokens[0]
    if first_token.kind != CFTokenKind.SPACES:
        return tokens

    if first_token.value == " ":
        # for a single space, simply discard that token and return the rest
        return tokens[1:]
    else:
        # for multiple spaces, replace it with a token having 1 fewer spaces
        length = len(first_token.value)
        one_shorter = CFToken(CFTokenKind.SPACES, " "*(length-1))
        return [one_shorter] + tokens[1:]


def make_compact(tokens):
    #- any NEWLINE...
    #    - that is preceded or followed by SPACES can be discarded
    #    - otherwise replace with a single space
    #- any SPACES token longer than 1 can be shrunk to 1
    #- (left_paren, space) -> drop the space
    #- (space, right_paren) -> drop the space
    #- (space, comma) -> drop the space
    #- (word, space, left_paren) -> drop the space

    # The general pattern here is that after making any change that might affect future pattern matches,
    # we jump back to the top of the loop. And if we changed the "current" token, we move the index variable
    # back by one (if possible), again to make sure we can see any patterns that created.

    out = tokens.copy()

    out = trim_leading_whitespace(trim_trailing_whitespace(out))

    i = 0
    while i < len(out):
        tok = out[i]

        # skip non-tokens (e.g. CompoundStatement)
        # this check is repeated in the multi-token blocks
        if type(tok) is not CFToken:
            i += 1
            continue


        # shrink all strings of spaces down to 1
        if tok.kind == CFTokenKind.SPACES and len(tok.value) > 1:
            tok = Whitespace.ONE_SPACE
            out[i] = tok


        # 3-token sequences
        if i+2 < len(out):
            next_tok = out[i+1]
            after_next_tok = out[i+2]

            if type(after_next_tok) is not CFToken:
                i += 1
                continue

            # "word", " ", "("
            # EXCEPT if the word is "in": we want to treat `in (...)` differently from `func(...)`
            if (    tok.kind == CFTokenKind.WORD
                and next_tok.kind == CFTokenKind.SPACES
                and after_next_tok.value == "("
                and tok.value.lower() != "in"
                ):
                out.pop(i+1)
                continue


        # 2-token sequences
        if i+1 < len(out):
            next_tok = out[i+1]

            if type(next_tok) is not CFToken:
                i += 1
                continue

            # " ", "\n"
            if tok.kind == CFTokenKind.SPACES and next_tok.kind == CFTokenKind.NEWLINE:
                out.pop(i+1)
                continue

            # "\n", " "
            if tok.kind == CFTokenKind.NEWLINE and next_tok.kind == CFTokenKind.SPACES:
                out.pop(i)
                i = max(i - 1, 0)
                continue

            # " ", " "  (doesn't occur naturally but this process can create it as an intermediate state)
            if tok.kind == CFTokenKind.SPACES and next_tok.kind == CFTokenKind.SPACES:
                out.pop(i)
                i = max(i - 1, 0)
                continue

            # "(", " "
            if tok.value == "(" and next_tok.kind == CFTokenKind.SPACES:
                out.pop(i+1)
                continue

            # " ", ")"
            if tok.kind == CFTokenKind.SPACES and next_tok.value == ")":
                out.pop(i)
                i = max(i - 1, 0)
                continue

            # " ", ","
            if tok.kind == CFTokenKind.SPACES and next_tok.value == ",":
                out.pop(i)
                i = max(i - 1, 0)
                continue
        # end of 2-token sequences


        # replace any newlines left (not caught by sequence matches) with a single space
        if tok.kind == CFTokenKind.NEWLINE:
            out[i] = Whitespace.ONE_SPACE
            i = max(i - 1, 0)
            continue

        i += 1

    return out


def is_parenthesized_subquery(elements):
    return (
            len(elements) >= 3
        and elements[0] == Symbols.LEFT_PAREN
        and (   isinstance(elements[1], Statement)
             or isinstance(elements[1], CompoundStatement)
            )
        and elements[2] == Symbols.RIGHT_PAREN
    )


class Expression:
    __slots__ = (
        "input_tokens",
        "elements",
    )

    def __init__(self, tokens):
        self.input_tokens = tokens
        self.elements = self._parse(tokens)

    @property
    def is_whitespace(self):
        return all([e.is_whitespace for e in self.elements])

    def is_empty(self):
        return len(self.elements) == 0

    def _parse(self, tokens):
        temp = trim_trailing_whitespace(tokens)

        if cf_flags.FORMAT_MODE == cf_flags.FormatMode.TRIM_LEADING_WHITESPACE:
            temp2 = trim_leading_whitespace(temp)
        else:
            temp2 = trim_one_leading_space(temp)

        if cf_flags.FORMAT_MODE == cf_flags.FormatMode.COMPACT_EXPRESSIONS:
            temp3 = make_compact(temp2)
        else:
            temp3 = temp2

        return temp3

    def render(self, indent):
        out = ""
        effective_indent = indent
        immediately_after_newline = False
        i = 0
        while i < len(self.elements):
            e = self.elements[i]
            next_e = self.elements[i+1] if i+1 < len(self.elements) else None

            if immediately_after_newline:
                if e.kind == CFTokenKind.NEWLINE:
                    # we should probably collapse consecutive newlines, but if they do happen, no indentation is needed
                    pass
                elif e.kind == CFTokenKind.SPACES:
                    # if the newline IS followed by spaces, but not enough spaces to reach the indent, add more so that it will
                    # UNLESS the next token is a comment!
                    if next_e is not None and next_e.kind in (CFTokenKind.LINE_COMMENT, CFTokenKind.BLOCK_COMMENT):
                        pass
                    else:
                        extra_spaces = indent - len(e.value)
                        if extra_spaces > 0:
                            out += " " * extra_spaces
                            effective_indent = extra_spaces
                else:
                    # otherwise, add enough spaces to reach the indent
                    out += " " * indent
                    effective_indent = indent
                immediately_after_newline = False

            fragment = e.render(effective_indent)
            out += fragment
            effective_indent += len(fragment)

            if e == Whitespace.NEWLINE or e.kind == CFTokenKind.LINE_COMMENT:
                #PONDER: what if we made the newline itself responsible for adding the indent, in render()?
                immediately_after_newline = True
            elif e == Symbols.LEFT_PAREN and is_parenthesized_subquery(self.elements[i:i+3]):
                paren_indent = effective_indent - 1
                out += self.elements[i+1].render(effective_indent)
                out += "\n"
                out += " " * paren_indent
                out += ")"
                i += 3 # left paren, subquery, right paren
                continue

            i += 1

        # I'm not *quite* confident that doing this in Expresion is desirable...
        out = out.rstrip("\n")
        return out


# see https://www.postgresql.org/docs/14/queries-with.html
class WithClause:
    __slots__ = (
        "input_tokens",
        "delimiters",
        "before_stuff", # e.g. "identifier as" or "identifier as materialized" or "identifier(<col list>) as"
        "statements",
        "after_stuff", # SEARCH clause for recursive CTEs, rarely used. Also used to capture broken syntax
    )
    STARTING_DELIMITER = CFToken(CFTokenKind.WORD, "with")
    OTHER_DELIMITERS = set([Symbols.COMMA])
    CTE_INDENT_SPACES = 4

    def __init__(self, tokens):
        self._validate(tokens)

        self.input_tokens = tokens

        (
            self.delimiters,
            self.before_stuff,
            self.statements,
            self.after_stuff,
        ) = self._parse(tokens)


    def _validate(self, tokens):
        if not tokens:
            raise ValueError("tokens must be non-empty")

        if tokens[0] != self.STARTING_DELIMITER:
            raise ValueError(f"WithClause must begin with \"WITH\" keyword")

        return True


    def _parse_pieces(self, tokens):
        i = 0
        while i < len(tokens):
            if is_parenthesized_subquery(tokens[i:i+3]):
                # discard the parens
                before = tokens[:i]
                statement = tokens[i+1]
                after = tokens[i+3:]
                return (before, statement, after)
            i += 1

        # if we end up here, the input was not particularly well-formed
        # we may be able to salvage it into something that at least has the *shape* of a CTE

        # (should log a warning?)

        i = 0
        left_paren_index = None
        right_paren_index = None
        while i < len(tokens):
            if tokens[i] == Symbols.LEFT_PAREN:
                left_paren_index = i
            elif tokens[i] == Symbols.RIGHT_PAREN:
                right_paren_index = i

            if left_paren_index and right_paren_index:
                # as in the well-formed case, discard the parens
                before = tokens[:left_paren_index]
                junk = Expression(tokens[left_paren_index+1:right_paren_index])
                after = tokens[right_paren_index+1:]
                return (before, junk, after)

            i += 1

        # welp.
        raise ValueError(f"could not divide CTE tokens: {tokens}")


    def _parse(self, tokens):
        i = 1 # we already know token 0 is the starting delimiter
        delimiters = [self.STARTING_DELIMITER]
        before_stuff = []
        statements = []
        after_stuff = []
        paren_depth = 0
        buffer = []
        while i < len(tokens):
            if paren_depth == 0 and tokens[i] in self.OTHER_DELIMITERS:
                delimiters.append(tokens[i])
                before_tokens, stmt, after_tokens = self._parse_pieces(buffer)
                before_stuff.append(Expression(before_tokens))
                statements.append(stmt)
                after_stuff.append(Expression(after_tokens))
                buffer = []
            else:
                if tokens[i] == Symbols.LEFT_PAREN:
                    paren_depth += 1
                elif tokens[i] == Symbols.RIGHT_PAREN:
                    #TODO: detect unbalanced parens
                    paren_depth -= 1
                buffer.append(tokens[i])
            i += 1
        # one final expression, empty in the weird/broken case where the final token was JOIN or etc
        if (len(buffer) > 0
            or len(delimiters) > len(before_stuff)
            or len(delimiters) > len(statements)
            or len(delimiters) > len(after_stuff)):
            before_tokens, stmt, after_tokens = self._parse_pieces(buffer)
            before_stuff.append(Expression(before_tokens))
            statements.append(stmt)
            after_stuff.append(Expression(after_tokens))

        assert len(delimiters) == len(before_stuff)
        assert len(delimiters) == len(statements)
        assert len(delimiters) == len(after_stuff)

        return (delimiters, before_stuff, statements, after_stuff)


    def render(self, indent):
        parts = []
        i = 0
        effective_indent = indent
        while i < len(self.delimiters):
            # indent
            if i > 0:
                parts.append("\n")
                parts.append(" " * indent)
                effective_indent = indent

            # delimiter
            fragment = self.delimiters[i].render(effective_indent)
            effective_indent += len(fragment)
            parts.append(fragment)

            # before stuff
            fragment = self.before_stuff[i].render(effective_indent)
            fragment = (" " + fragment) if fragment else ""
            effective_indent += len(fragment)
            parts.append(fragment)

            # open paren
            parts.append("\n")
            parts.append(" " * indent)
            effective_indent = indent
            parts.append("(")
            parts.append("\n")

            # subquery
            parts.append(" " * (effective_indent+self.CTE_INDENT_SPACES))
            parts.append(self.statements[i].render(effective_indent+self.CTE_INDENT_SPACES))

            # close paren
            parts.append("\n")
            parts.append(" " * indent)
            effective_indent = indent
            parts.append(")")
            effective_indent = effective_indent + 1

            # after stuff
            fragment = self.after_stuff[i].render(effective_indent)
            fragment = (" " + fragment) if fragment else ""
            parts.append(fragment)

            i += 1

        out = "".join(parts)
        out = out.rstrip("\n")
        return out


class BasicClause:
    __slots__ = (
        "input_tokens",
        "delimiters",
        "expressions",
    )
    STARTING_DELIMITER = None
    OTHER_DELIMITERS = set()
    PADDING = 6

    def __init__(self, tokens):
        self._validate(tokens)

        self.input_tokens = tokens

        self.delimiters, self.expressions = self._parse(tokens)


    def _validate(self, tokens):
        if not tokens:
            raise ValueError("tokens must be non-empty")

        if tokens[0] != self.STARTING_DELIMITER:
            raise ValueError(f"{self.__class__} must begin with \"{self.STARTING_DELIMITER.value}\" keyword")

        return True


    def _parse(self, tokens):
        i = 1 # we already know token 0 is the starting delimiter
        delimiters = [tokens[0]]
        expressions = []
        paren_depth = 0
        buffer = []
        while i < len(tokens):
            if paren_depth == 0 and tokens[i] in self.OTHER_DELIMITERS:
                delimiters.append(tokens[i])
                expressions.append(Expression(buffer))
                buffer = []
            else:
                if tokens[i] == Symbols.LEFT_PAREN:
                    paren_depth += 1
                elif tokens[i] == Symbols.RIGHT_PAREN:
                    #TODO: detect unbalanced parens
                    paren_depth -= 1
                buffer.append(tokens[i])
            i += 1
        # one final expression, empty in the weird/broken case where the final token was JOIN or etc
        if len(buffer) > 0 or len(delimiters) > len(expressions):
            expressions.append(Expression(buffer))

        assert len(delimiters) == len(expressions)

        return (delimiters, expressions)


    def _render_delimiter(self, delimiter):
        return delimiter.value.rjust(self.PADDING)


    def render(self, indent):
        parts = []
        i = 0
        effective_indent = indent
        suppress_newline = False
        while i < len(self.delimiters):
            if i > 0:
                if not suppress_newline:
                    parts.append("\n")
                parts.append(" " * indent)
                effective_indent = indent
            suppress_newline = False

            delim_fragment = self._render_delimiter(self.delimiters[i])
            effective_indent += len(delim_fragment)
            parts.append(delim_fragment)

            if not self.expressions[i].is_empty(): # don't render the expr at all if it's empty
                # always print one space after the delimiter
                parts.append(" ")
                effective_indent += 1

                expr_fragment = self.expressions[i].render(effective_indent)
                parts.append(expr_fragment)

                if expr_fragment.endswith("\n"): # happens when an Expression ends with a line comment
                    suppress_newline = True

            i += 1

        out = "".join(parts)
        out = out.rstrip("\n")
        return out


class SelectClause:
    __slots__ = (
        "input_tokens",
        "delimiters",
        "expressions",
        "qualifier",
    )
    STARTING_DELIMITER = Keywords.SELECT
    OTHER_DELIMITERS = set([Symbols.COMMA])
    PADDING = 6

    def __init__(self, tokens):
        self._validate(tokens)

        self.input_tokens = tokens

        self.delimiters, self.expressions, self.qualifier = self._parse(tokens)


    def _validate(self, tokens):
        if not tokens:
            raise ValueError("tokens must be non-empty")

        if tokens[0] != Keywords.SELECT:
            raise ValueError("SelectClause must begin with \"SELECT\" keyword")

        return True


    def _parse(self, tokens):
        i = 1
        delimiters = [tokens[0]]

        # check for ALL, DISTINCT, DISTINCT ON(...)
        qualifier = None
        tok, pos = next_real_token_and_position(tokens[i:])
        if tok in (Keywords.DISTINCT, Keywords.ALL):
            qualifier = tok
            i += pos+1
        elif tok == Keywords.DISTINCT_ON:
            i += pos+1
            while i < len(tokens):
                if tokens[i].is_whitespace:
                    i += 1
                elif tokens[i] == Symbols.LEFT_PAREN:
                    on_clause_tokens = get_paren_block(tokens[i:])
                    if on_clause_tokens is None:
                        raise Exception("broken DISTINCT ON(): unbalanced parens")
                    else:
                        qualifier = Expression([Keywords.DISTINCT_ON]+on_clause_tokens)
                        i += len(on_clause_tokens)
                        break
                else:
                    raise Exception(f"broken DISTINCT ON(): expected ( found {tokens[i]}")

        # parse the remaining tokens into expressions
        expressions = []
        paren_depth = 0
        buffer = []
        while i < len(tokens):
            if paren_depth == 0 and tokens[i] in self.OTHER_DELIMITERS:
                delimiters.append(tokens[i])
                expressions.append(Expression(buffer))
                buffer = []
            else:
                if tokens[i] == Symbols.LEFT_PAREN:
                    paren_depth += 1
                elif tokens[i] == Symbols.RIGHT_PAREN:
                    #TODO: detect unbalanced parens
                    paren_depth -= 1
                buffer.append(tokens[i])
            i += 1
        # one final expression, empty in the weird/broken case where the final token was JOIN or etc
        if len(buffer) > 0 or len(delimiters) > len(expressions):
            expressions.append(Expression(buffer))

        assert len(delimiters) == len(expressions), f"{len(delimiters)} delimiters : {len(expressions)} expressions"

        return (delimiters, expressions, qualifier)


    def _render_delimiter(self, delimiter):
        return delimiter.value.rjust(self.PADDING)

    def render(self, indent):
        parts = []
        i = 0
        effective_indent = indent
        suppress_newline = False
        while i < len(self.delimiters):
            if i > 0:
                if not suppress_newline:
                    parts.append("\n")
                parts.append(" " * indent)
                effective_indent = indent
            suppress_newline = False

            delim_fragment = self._render_delimiter(self.delimiters[i])
            effective_indent += len(delim_fragment)
            parts.append(delim_fragment)

            if i == 0 and self.qualifier:
                parts.append(" ")
                parts.append(self.qualifier.render(indent))
                if not self.expressions[0].is_empty():
                    parts.append("\n")
                    parts.append(" " * 6)

            if not self.expressions[i].is_empty(): # don't render the expr at all if it's empty
                # always print one space after the delimiter
                parts.append(" ")
                effective_indent += 1

                expr_fragment = self.expressions[i].render(effective_indent)
                if i == 0 and self.qualifier:
                    # when there's a qualifier, we add a newline and indentation (see above), but if the input was already
                    # formatted correctly, then that's redundant and we need to back it out
                    expr_fragment = expr_fragment.removeprefix("\n" + " " * 7)
                parts.append(expr_fragment)

                if expr_fragment.endswith("\n"): # happens when an Expression ends with a line comment
                    suppress_newline = True

            i += 1

        out = "".join(parts)
        out = out.rstrip("\n")
        return out


class FromClause(BasicClause):
    STARTING_DELIMITER = Keywords.FROM
    OTHER_DELIMITERS = set([
        Keywords.CROSS_JOIN,
        Keywords.FULL_JOIN,
        Keywords.FULL_OUTER_JOIN,
        Keywords.INNER_JOIN,
        Keywords.JOIN,
        Keywords.LATERAL_JOIN,
        Keywords.LEFT_JOIN,
        Keywords.LEFT_OUTER_JOIN,
        Keywords.NATURAL_JOIN,
        Keywords.RIGHT_JOIN,
        Keywords.RIGHT_OUTER_JOIN,
        Symbols.COMMA,
    ])
    PADDING = 6

    def _render_delimiter(self, delimiter):
        if delimiter == Symbols.COMMA:
            return super()._render_delimiter(delimiter)
        else:
            return f"  {delimiter.value}"


class WhereClause(BasicClause):
    STARTING_DELIMITER = Keywords.WHERE
    OTHER_DELIMITERS = set([
        Keywords.AND,
        Keywords.OR,
    ])
    PADDING = 6


class GroupByClause(BasicClause):
    STARTING_DELIMITER = Keywords.GROUP_BY
    OTHER_DELIMITERS = set([Symbols.COMMA])
    PADDING = 9


class OrderByClause(BasicClause):
    STARTING_DELIMITER = Keywords.ORDER_BY
    OTHER_DELIMITERS = set([Symbols.COMMA])
    PADDING = 9


class LimitOffsetClause:
    __slots__ = (
        "input_tokens",
        "limit_expression",
        "offset_expression",
        "limit_first",
    )

    def __init__(self, tokens):
        self._validate(tokens)

        self.input_tokens = tokens

        self.limit_expression, self.offset_expression, self.limit_first = self._parse(tokens)


    def _validate(self, tokens):
        if not tokens:
            raise ValueError("tokens must be non-empty")

        if tokens[0] not in (Keywords.LIMIT, Keywords.OFFSET):
            raise ValueError("LimitOffsetClause must begin with \"LIMIT\" or \"OFFSET\" keyword")

        return True


    def _parse(self, tokens):
        limit_buffer = []
        offset_buffer = []

        if tokens[0] == Keywords.LIMIT:
            limit_first = True
        else:
            limit_first = False

        i = 0
        while i < len(tokens):
            if tokens[i] == Keywords.LIMIT:
                target_buffer = limit_buffer
            elif tokens[i] == Keywords.OFFSET:
                target_buffer = offset_buffer
            target_buffer.append(tokens[i])
            i += 1

        limit_expression = Expression(limit_buffer)
        offset_expression = Expression(offset_buffer)

        return limit_expression, offset_expression, limit_first


    def render(self, indent):
        parts = []

        if self.limit_first:
            parts.append(" " * indent)
            parts.append(" ")
            parts.append(self.limit_expression.render(indent))
            if not self.offset_expression.is_empty():
                parts.append("\n")
                parts.append(self.offset_expression.render(indent))
        else:
            parts.append(self.offset_expression.render(indent))
            if not self.limit_expression.is_empty():
                parts.append("\n")
                parts.append(" " * indent)
                parts.append(" ")
                parts.append(self.limit_expression.render(indent))

        out = "".join(parts)
        out = out.rstrip("\n")
        return out


class JunkClause:
    __slots__ = (
        "input_tokens",
    )
    def __init__(self, tokens):
        self.input_tokens = tokens

    def render(self, indent):
        out = "".join([t.render(indent) for t in self.input_tokens])
        out = out.rstrip("\n")
        return out


class ClauseScope(enum.IntEnum):
    INITIAL = 1
    WITH = 2
    SELECT = 3
    FROM = 4
    WHERE = 5
    GROUP_BY = 6
    #HAVING = 7 #NYI
    #WINDOW = 8 #NYI
    ORDER_BY = 9
    LIMIT_OFFSET = 10
    #TERMINATOR = 11 #NYI (semicolon)


KEYWORD_SCOPE_MAP = {
    Keywords.WITH: ClauseScope.WITH,
    Keywords.SELECT: ClauseScope.SELECT,
    Keywords.FROM: ClauseScope.FROM,
    Keywords.WHERE: ClauseScope.WHERE,
    Keywords.GROUP_BY: ClauseScope.GROUP_BY,
    #Keywords.HAVING: ClauseScope.HAVING,
    #Keywords.WINDOW: ClauseScope.WINDOW,
    Keywords.ORDER_BY: ClauseScope.ORDER_BY,
    Keywords.LIMIT: ClauseScope.LIMIT_OFFSET,
    Keywords.OFFSET: ClauseScope.LIMIT_OFFSET,
}


SCOPE_CLAUSE_MAP = {
    ClauseScope.INITIAL: JunkClause,
    ClauseScope.WITH: WithClause,
    ClauseScope.SELECT: SelectClause,
    ClauseScope.FROM: FromClause,
    ClauseScope.WHERE: WhereClause,
    ClauseScope.GROUP_BY: GroupByClause,
    #ClauseScope.HAVING: HavingClause,
    #ClauseScope.WINDOW: WindowClause,
    ClauseScope.ORDER_BY: OrderByClause,
    ClauseScope.LIMIT_OFFSET: LimitOffsetClause,
}


class Statement:
    __slots__ = (
        "input_tokens",
        "clause_map", # map of ClauseScope -> clause object
    )

    def __init__(self, tokens):
        self.input_tokens = tokens

        self.clause_map = self._parse(tokens)


    def _parse(self, tokens):
        clause_map = {}

        current_scope = ClauseScope.INITIAL
        paren_depth = 0
        i = 0
        buffer = []
        while i < len(tokens):
            tok = tokens[i]

            # subqueries are not valid in all scopes but we'll punt on that for now
            if tok == Symbols.LEFT_PAREN and next_real_token(tokens[i+1:]) in [Keywords.SELECT, Keywords.WITH]:
                subquery_tokens = get_paren_block(tokens[i:])
                if subquery_tokens is None:
                    # unbalanced parens
                    pass
                else:
                    buffer.append(Symbols.LEFT_PAREN)
                    buffer.append(CompoundStatement(subquery_tokens[1:-1]))
                    buffer.append(Symbols.RIGHT_PAREN)
                    i += len(subquery_tokens)
                    continue

            if tok == Symbols.LEFT_PAREN:
                buffer.append(tok)
                paren_depth += 1
            elif tok == Symbols.RIGHT_PAREN:
                buffer.append(tok)
                paren_depth -= 1
            elif paren_depth == 0:
                # ONLY probe for a scope change if we are outside any misc parens (function calls etc)
                potential_new_scope = KEYWORD_SCOPE_MAP.get(tok, None)
                if potential_new_scope:
                    if potential_new_scope == current_scope and current_scope == ClauseScope.LIMIT_OFFSET:
                        # LIMIT/OFFSET is a weird clause because OFFSET/LIMIT is also valid, so any time
                        # both keywords are used, we'll hit this case. It's normal.
                        buffer.append(tok)
                    elif potential_new_scope <= current_scope:
                        raise ValueError(f"unexpected token {tok} in scope {current_scope.name}")
                    else:
                        if len(buffer) > 0:
                            clause_class = SCOPE_CLAUSE_MAP[current_scope]
                            clause_map[current_scope] = clause_class(buffer)

                        current_scope = potential_new_scope
                        buffer = [tok]
                else:
                    buffer.append(tok)
            else:
                buffer.append(tok)

            i += 1

        # last clause
        clause_class = SCOPE_CLAUSE_MAP[current_scope]
        clause_map[current_scope] = clause_class(buffer)

        return clause_map


    @property
    def is_whitespace(self):
        return False


    def render(self, indent):
        # the ClauseScope keys are numbered in order so sorted() does exactly what we want
        clauses_in_order = sorted(self.clause_map.items())

        # Each clause uses `indent` to bump over lines after the first (first line is the caller's responsibility).
        # This bit bumps over the first lines too, for every clause except the first, which makes the Statement
        # as a whole match the behavior of clauses.
        clause_joiner = "\n" + (" " * indent)

        out = clause_joiner.join([v.render(indent) for k,v in clauses_in_order])
        return out


class CompoundStatement:
    __slots__ = (
        "input_tokens",
        "statements",
        "set_operations",
    )
    SET_OP_KEYWORDS = set([
        # Postgres allows ALL and DISTINCT to be appended to any set operation...
        Keywords.UNION,
        Keywords.UNION_ALL,
        Keywords.UNION_DISTINCT,
        Keywords.INTERSECT,
        Keywords.INTERSECT_ALL,
        Keywords.INTERSECT_DISTINCT,
        Keywords.EXCEPT,
        Keywords.EXCEPT_ALL,
        Keywords.EXCEPT_DISTINCT,
        Keywords.MINUS, # ...but Oracle doesn't
    ])

    def __init__(self, tokens):
        self.input_tokens = tokens

        self.statements, self.set_operations = self._parse(tokens)


    def _parse(self, tokens):
        statements = []
        set_operations = []
        buffer = []
        seeking_statement_start = True
        for i, tok in enumerate(tokens):
            # TODO: "(statement) set_op (statement)" is allowed so some paren-awareness is needed
            if seeking_statement_start is True and tok.is_whitespace:
                # drop any whitespace that precedes SELECT/WITH
                pass
            elif tok in self.SET_OP_KEYWORDS:
                statements.append(Statement(buffer))
                set_operations.append(tok)
                buffer = []
                seeking_statement_start = True
            else:
                buffer.append(tok)
                if tok in (Keywords.SELECT, Keywords.WITH):
                    seeking_statement_start = False
        # final statement
        if len(buffer) > 0:
            statements.append(Statement(buffer))

        # if you do something dumb like "select ... union union select..." this will explode
        assert len(statements) == len(set_operations) + 1

        return (statements, set_operations)


    @property
    def is_whitespace(self):
        return False


    def render(self, indent):
        parts = [self.statements[0]]
        i = 0
        while i < len(self.set_operations):
            parts.append(self.set_operations[i])
            parts.append(self.statements[i+1])
            i += 1

        stmt_joiner = "\n" + (" " * indent)

        out = stmt_joiner.join([p.render(indent) for p in parts])
        return out
