import enum

from sftoken import SFToken, SFTokenKind, Keywords, Symbols, Whitespace


def next_real_token(tokens):
    for t in tokens:
        if not t.is_whitespace:
            return t
    return None


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

    return tokens[0:i+1]


class Expression:
    def __init__(self, elements):
        self.elements = elements

    def starts_with_whitespace(self):
        return len(self.elements) > 0 and self.elements[0].is_whitespace

    @property
    def is_whitespace(self):
        return all([e.is_whitespace for e in self.elements])

    def is_empty(self):
        return len(self.elements) == 0

    def render(self, indent):
        #return "".join([e.render(indent) for e in self.elements])
        out = ""
        effective_indent = indent
        for e in self.elements:
            fragment = e.render(effective_indent)
            out += fragment
            effective_indent += len(fragment)
            if e == Whitespace.NEWLINE:
                #PONDER: what if we made the newline itself responsible for adding the indent, in render()?
                out += " " * indent
                effective_indent = indent

        return out


# TODO
class WithClause:
    def __init__(self, tokens):
        self.tokens = tokens

    def render(self):
        pass


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
        delimiters = [self.STARTING_DELIMITER]
        expressions = []
        paren_depth = 0
        buffer = []
        while i < len(tokens):
            if paren_depth == 0 and tokens[i] in self.OTHER_DELIMITERS:
                delimiters.append(tokens[i])
                expressions.append(Expression(trim_trailing_whitespace(buffer)))
                buffer = []
            elif tokens[i] == Symbols.LEFT_PAREN and next_real_token(tokens[i+1:]) == Keywords.SELECT:
                subquery_tokens = get_paren_block(tokens[i:])
                if subquery_tokens is None:
                    # unbalanced parens
                    pass
                else:
                    buffer.append(Symbols.LEFT_PAREN)
                    buffer.append(Statement(subquery_tokens[1:-1]))
                    buffer.append(Symbols.RIGHT_PAREN)
                    i += len(subquery_tokens)
                    continue
            else:
                if tokens[i] == Symbols.LEFT_PAREN:
                    paren_depth += 1
                elif tokens[i] == Symbols.RIGHT_PAREN:
                    #TODO: detect unbalanced parens
                    paren_depth -= 1
                #TODO: detect and handle paren-wrapped subqueries
                buffer.append(tokens[i])
            i += 1
        # one final expression, empty in the weird/broken case where the final token was JOIN or etc
        if len(buffer) > 0 or len(delimiters) > len(expressions):
            expressions.append(Expression(trim_trailing_whitespace(buffer)))

        assert len(delimiters) == len(expressions)

        return (delimiters, expressions)


    def _render_delimiter(self, delimiter):
        return delimiter.value.rjust(self.PADDING)


    def render(self, indent):
        parts = []
        i = 0
        effective_indent = indent
        while i < len(self.delimiters):
            if i > 0:
                parts.append("\n")
                parts.append(" " * indent)
                effective_indent = indent

            #parts.append(self._render_delimiter(self.delimiters[i]))
            #parts.append(self.expressions[i].render(indent))

            fragment = self._render_delimiter(self.delimiters[i])
            effective_indent += len(fragment)
            parts.append(fragment)

            parts.append(self.expressions[i].render(effective_indent))

            i += 1

        out = "".join(parts)
        return out


class SelectClause:
    __slots__ = (
        "input_tokens",
        "qualifier",
        "expressions",
    )

    def __init__(self, tokens):
        SelectClause._validate(tokens)

        self.input_tokens = tokens

        self.qualifier, self.expressions = self._parse(tokens[1:])


    @staticmethod
    def _validate(tokens):
        if not tokens:
            raise ValueError("tokens must be non-empty")

        if tokens[0] != Keywords.SELECT:
            raise ValueError("SelectClause must begin with \"SELECT\" keyword")

        return True


    def _parse(self, tokens):
        if len(tokens) == 0: # degenerate case
            return (None, [])

        i = 0

        # first, skip past any whitespace
        while i < len(tokens):
            if not tokens[i].is_whitespace:
                break
            i += 1
        if i == len(tokens):
            # we were passed *only* whitespace tokens
            return (None, [])

        # check for ALL, DISTINCT, DISTINCT ON(...)
        qualifier = None
        if tokens[i] == Keywords.ALL:
            qualifier = tokens[i].value
            i += 1
        elif tokens[i] == Keywords.DISTINCT:
            #TODO: support DISTINCT ON
            qualifier = tokens[i].value
            i += 1

        # parse the remaining tokens into expressions
        expressions = []
        paren_depth = 0
        buffer = []
        while i < len(tokens):
            if tokens[i] == Symbols.COMMA and paren_depth == 0:
                expressions.append(Expression(trim_trailing_whitespace(buffer)))
                buffer = []
            else:
                if tokens[i] == Symbols.LEFT_PAREN:
                    paren_depth += 1
                elif tokens[i] == Symbols.RIGHT_PAREN:
                    #TODO: detect unbalanced parens
                    paren_depth -= 1
                #TODO: detect and handle paren-wrapped subqueries
                buffer.append(tokens[i])

            i += 1
        if len(buffer) > 0: # one final expression
            expressions.append(Expression(trim_trailing_whitespace(buffer)))

        return (qualifier, expressions)


    def render(self, indent):
        if not self.qualifier and not self.expressions:
            return "select"

        parts = ["select"]

        if self.qualifier:
            parts.append(" ")
            parts.append(self.qualifier)
            parts.append("\n")
            if self.expressions:
                parts.append(" " * 5)

        for i, expr in enumerate(self.expressions):
            if i == 0:
                parts.append(" ")
                parts.append(expr.render(indent))
            else:
                parts.append("\n")
                parts.append(" " * indent)
                parts.append("     ,")
                # If the expression is like [" ", "foo"] then print it as-is, preserving any oddball spacing it might have.
                # OTOH in cases like "select foo,bar,baz", we need to add a space to get to a good baseline.
                # This might need to change if expression rendering gets smarter.
                if not expr.starts_with_whitespace:
                    parts.append(" ")
                parts.append(expr.render(indent))

        out = "".join(parts)
        return out


class FromClause(BasicClause):
    STARTING_DELIMITER = Keywords.FROM
    OTHER_DELIMITERS = set([
        Keywords.CROSS_JOIN,
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

        limit_expression = Expression(trim_trailing_whitespace(limit_buffer))
        offset_expression = Expression(trim_trailing_whitespace(offset_buffer))

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
        return out


class ClauseScope(enum.IntEnum):
    INITIAL = 1
    #WITH = 2 #NYI
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
    #Keywords.WITH: ClauseScope.WITH,
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
    #ClauseScope.WITH: WithClause,
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
        i = 0
        buffer = []
        while i < len(tokens):
            tok = tokens[i]

            # subqueries are not valid in all scopes but we'll punt on that for now
            if tok == Symbols.LEFT_PAREN and next_real_token(tokens[i+1:]) == Keywords.SELECT:
                subquery_tokens = get_paren_block(tokens[i:])
                if subquery_tokens is None:
                    # unbalanced parens
                    pass
                else:
                    buffer.append(Symbols.LEFT_PAREN)
                    buffer.append(Statement(subquery_tokens[1:-1]))
                    buffer.append(Symbols.RIGHT_PAREN)
                    i += len(subquery_tokens)
                    continue                 

            potential_new_scope = KEYWORD_SCOPE_MAP.get(tok, None)
            if potential_new_scope:
                if current_scope is ClauseScope.INITIAL:
                    buffer.append(tok)
                    current_scope = potential_new_scope
                elif potential_new_scope == current_scope and current_scope == ClauseScope.LIMIT_OFFSET:
                    # LIMIT/OFFSET is a weird clause because OFFSET/LIMIT is also valid, so any time
                    # both keywords are used, we'll hit this case. It's normal.
                    buffer.append(tok)
                elif potential_new_scope <= current_scope:
                    raise ValueError(f"unexpected token {tok} in scope {current_scope}")
                else:
                    clause_class = SCOPE_CLAUSE_MAP[current_scope]
                    clause_map[current_scope] = clause_class(buffer)

                    current_scope = potential_new_scope
                    buffer = [tok]
            else:
                buffer.append(tok)

            i += 1

        # last clause
        clause_class = SCOPE_CLAUSE_MAP[current_scope]
        clause_map[current_scope] = clause_class(buffer)

        return clause_map


    def starts_with_whitespace(self):
        return False


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
