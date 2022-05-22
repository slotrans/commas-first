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


def trim_trailing_whitespace(tokens):
    i = len(tokens) - 1
    while i >= 0 and tokens[i].is_whitespace:
        i -= 1

    return tokens[0:i+1]


class Expression:
    def __init__(self, tokens):
        self.tokens = tokens

    def starts_with_whitespace(self):
        return len(self.tokens) > 0 and self.tokens[0].is_whitespace

    def is_empty(self):
        return len(self.tokens) == 0

    def render(self):
        return "".join([t.value for t in self.tokens])


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


class Statement:
    __slots__ = (
        "input_tokens",
        #"with_clause", #NYI
        "select_clause",
        "from_clause",
        "where_clause",
        "group_by_clause",
        #"having_clause", #NYI
        #"window_clause", #NYI
        "order_by_clause",
        "limit_offset_clause",
    )

    def __init__(self, tokens):
        self.input_tokens = tokens

        # maybe better to initialize these to some kind of dummy value that we can call .render() on
        # instead of None?
        #self.with_clause = None
        self.select_clause = None
        self.from_clause = None
        self.where_clause = None
        self.group_by_clause = None
        #self.having_clause = None
        #self.window_clause = None
        self.order_by_clause = None
        self.limit_offset_clause = None

        clause_map = self._parse(tokens)
        for scope, obj in clause_map.items():
            #if scope is ClauseScope.WITH:
            #    self.with_clause = obj
            if scope is ClauseScope.SELECT:
                self.select_clause = obj
            elif scope is ClauseScope.FROM:
                self.from_clause = obj
            elif scope is ClauseScope.WHERE:
                self.where_clause = obj
            elif scope is ClauseScope.GROUP_BY:
                self.group_by_clause = obj
            #elif scope is ClauseScope.HAVING:
            #    self.having_clause = obj
            #elif scope is ClauseScope.WINDOW:
            #    self.window_clause = obj
            elif scope is ClauseScope.ORDER_BY:
                self.order_by_clause = obj
            elif scope is ClauseScope.LIMIT_OFFSET:
                self.limit_offset_clause = obj
            else:
                raise ValueError(f"Invalid clause scope {scope}")


    def _parse(self, tokens):
        clause_map = {}

        current_scope = ClauseScope.INITIAL
        # do stuff

        return clause_map


    def render(self):
        out = "".join([
            #self.with_clause.render() if self.with_clause else "",
            self.select_clause.render() if self.select_clause else "",
            self.from_clause.render() if self.from_clause else "",
            self.where_clause.render() if self.where_clause else "",
            self.group_by_clause.render() if self.group_by_clause else "",
            #self.having_clause.render() if self.having_clause else "",
            #self.window_clause.render() if self.window_clause else "",
            self.order_by_clause.render() if self.order_by_clause else "",
            self.limit_offset_clause.render() if self.limit_offset_clause else "",
        ])
        return out


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


    def render(self):
        parts = []
        i = 0
        while i < len(self.delimiters):
            if i > 0:
                parts.append("\n")

            parts.append(self._render_delimiter(self.delimiters[i]))
            parts.append(self.expressions[i].render())

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
    PADDING = 8


class OrderByClause(BasicClause):
    STARTING_DELIMITER = Keywords.ORDER_BY
    OTHER_DELIMITERS = set([Symbols.COMMA])
    PADDING = 8


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


    def render(self):
        parts = []
        
        if self.limit_first:
            parts.append(" ")
            parts.append(self.limit_expression.render())
            if not self.offset_expression.is_empty():
                parts.append("\n")
                parts.append(self.offset_expression.render())
        else:
            parts.append(self.offset_expression.render())
            if not self.limit_expression.is_empty():
                parts.append("\n")
                parts.append(" ")
                parts.append(self.limit_expression.render())

        out = "".join(parts)
        return out


