
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
    for t in tokens:
        if t == Symbols.LEFT_PAREN:
            depth += 1
        elif t == Symbols.RIGHT_PAREN:
            depth -= 1
        block.append(t)

        if t == Symbols.RIGHT_PAREN and depth == 0:
            break

    return block


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


class Statement:
    def __init__(self, tokens):
        #self.with_clause = WithClause(...)
        #self.select_clause = SelectClause(...)
        #self.from_clause = FromClause(...)
        #self.where_clause = WhereClause(...)
        #self.group_by_clause = GroupByClause(...)
        #self.having_clause = HavingClause(...)
        #self.window_clause = WindowClause(...)
        #self.order_by_clause = OrderByClause(...)
        #self.limit_clause = LimitClause(...)
        #self.offset_clause = OffsetClause(...)
        pass

    def render(self):
        pass


class WithClause:
    def __init__(self, tokens):
        self.tokens = tokens

    def render(self):
        pass


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
            raise ValueError("SelectClause must begin with \"select\" keyword")

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
                expressions.append(Expression(buffer))
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
            expressions.append(Expression(buffer))

        return (qualifier, expressions)


    def render(self):
        if not self.qualifier and not self.expressions:
            return "select\n"

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
                parts.append(expr.render())
            else:
                parts.append("\n     ,")
                # If the expression is like [" ", "foo"] then print it as-is, preserving any oddball spacing it might have.
                # OTOH in cases like "select foo,bar,baz", we need to add a space to get to a good baseline.
                # This might need to change if expression rendering gets smarter.
                if not expr.starts_with_whitespace:
                    parts.append(" ")
                parts.append(expr.render())

        out = "".join(parts)
        return out


class FromClause:
    def __init__(self, tokens):
        self.tokens = tokens

    def render(self):
        pass


class WhereClause:
    def __init__(self, tokens):
        self.tokens = tokens

    def render(self):
        pass


class Expression:
    def __init__(self, tokens):
        self.tokens = tokens

    def starts_with_whitespace(self):
        return len(self.tokens) > 0 and self.tokens[0].is_whitespace

    def render(self):
        return "".join([t.value for t in self.tokens])
