import enum

from sftoken import SFToken, SFTokenKind, Keywords, Symbols, Whitespace


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
        immediately_after_newline = False
        i = 0
        while i < len(self.elements):
            e = self.elements[i]
            next_e = self.elements[i+1] if i+1 < len(self.elements) else None

            if immediately_after_newline:
                if e.kind == SFTokenKind.NEWLINE:
                    # we should probably collapse consecutive newlines, but if they do happen, no indentation is needed
                    pass
                elif e.kind == SFTokenKind.SPACES:
                    # if the newline IS followed by spaces, but not enough spaces to reach the indent, add more so that it will
                    # UNLESS the next token is a comment!
                    if next_e is not None and next_e.kind in (SFTokenKind.LINE_COMMENT, SFTokenKind.BLOCK_COMMENT):
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
            if e == Whitespace.NEWLINE or e.kind == SFTokenKind.LINE_COMMENT:
                #PONDER: what if we made the newline itself responsible for adding the indent, in render()?
                immediately_after_newline = True
            elif e == Symbols.LEFT_PAREN and is_parenthesized_subquery(self.elements[i:i+3]):
                paren_indent = effective_indent - 1
                out += self.elements[i+1].render(effective_indent)
                out += "\n"
                out += " " * paren_indent
                out += ")"
                i += 3
                continue

            i += 1

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
    STARTING_DELIMITER = SFToken(SFTokenKind.WORD, "with")
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
        paren_depth = 0
        buffer = []
        while i < len(tokens):
            if tokens[i] == Symbols.LEFT_PAREN and next_real_token(tokens[i+1:]) == Keywords.SELECT:
                subquery_tokens = get_paren_block(tokens[i:])
                if subquery_tokens is None:
                    # unbalanced parens
                    # idk whether we should handle it here or one level up
                    return (None, None, None)
                else:
                    # note that subquery_tokens includes the bounding parens, but we discard them here,
                    # so we can more easily place them deliberately in render()
                    subquery_length = len(subquery_tokens)
                    remaining_tokens = tokens[i+subquery_length:]
                    return (buffer, subquery_tokens[1:-1], remaining_tokens)
            else:
                if tokens[i] == Symbols.LEFT_PAREN:
                    paren_depth += 1
                elif tokens[i] == Symbols.RIGHT_PAREN:
                    #TODO: detect unbalanced parens
                    paren_depth -= 1
                buffer.append(tokens[i])
            i += 1

        # if we end up here, the input was not well-formed
        return (buffer, [], [])


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
                before_tokens, stmt_tokens, after_tokens = self._parse_pieces(buffer)
                before_stuff.append(Expression(trim_trailing_whitespace(before_tokens)))
                statements.append(CompoundStatement(stmt_tokens))
                after_stuff.append(Expression(trim_trailing_whitespace(after_tokens)))
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
            before_tokens, stmt_tokens, after_tokens = self._parse_pieces(buffer)
            before_stuff.append(Expression(trim_trailing_whitespace(before_tokens)))
            statements.append(CompoundStatement(stmt_tokens))
            after_stuff.append(Expression(trim_trailing_whitespace(after_tokens)))

        assert len(delimiters) == len(before_stuff)
        assert len(delimiters) == len(statements)
        assert len(delimiters) == len(after_stuff)

        return (delimiters, before_stuff, statements, after_stuff)


    def render(self, indent):
        parts = []
        i = 0
        effective_indent = indent
        while i < len(self.delimiters):
            if i > 0:
                parts.append("\n")
                parts.append(" " * indent)
                effective_indent = indent

            fragment = self.delimiters[i].render(effective_indent)
            effective_indent += len(fragment)
            parts.append(fragment)

            fragment = self.before_stuff[i].render(effective_indent)
            effective_indent += len(fragment)
            parts.append(fragment)

            parts.append("\n")
            parts.append(" " * indent)
            effective_indent = indent
            parts.append("(")
            parts.append("\n")

            parts.append(" " * (effective_indent+self.CTE_INDENT_SPACES))
            parts.append(self.statements[i].render(effective_indent+self.CTE_INDENT_SPACES))

            parts.append("\n")
            parts.append(" " * indent)
            effective_indent = indent
            parts.append(")")
            effective_indent = effective_indent + 1

            parts.append(self.after_stuff[i].render(effective_indent))

            i += 1

        out = "".join(parts)
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
                    buffer.append(CompoundStatement(subquery_tokens[1:-1]))
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
        suppress_newline = False
        while i < len(self.delimiters):
            if i > 0:
                if not suppress_newline:
                    parts.append("\n")
                parts.append(" " * indent)
                effective_indent = indent
            suppress_newline = False

            #parts.append(self._render_delimiter(self.delimiters[i]))
            #parts.append(self.expressions[i].render(indent))

            delim_fragment = self._render_delimiter(self.delimiters[i])
            effective_indent += len(delim_fragment)
            parts.append(delim_fragment)

            expr_fragment = self.expressions[i].render(effective_indent)
            parts.append(expr_fragment)

            if expr_fragment.endswith("\n"): # happens when an Expression ends with a line comment
                suppress_newline = True

            i += 1

        out = "".join(parts)
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
        delimiters = [self.STARTING_DELIMITER]

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
                expressions.append(Expression(trim_trailing_whitespace(buffer)))
                buffer = []
            elif tokens[i] == Symbols.LEFT_PAREN and next_real_token(tokens[i+1:]) == Keywords.SELECT:
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

        assert len(delimiters) == len(expressions), f"{len(delimiters)} delimiters : {len(expressions)} expressions"

        return (delimiters, expressions, qualifier)


    def render_old(self, indent):
        if not self.qualifier and not self.expressions:
            return "select"

        parts = ["select"]

        if self.qualifier:
            parts.append(" ")
            parts.append(self.qualifier.render(indent))
            if self.expressions:
                parts.append("\n")
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
                parts.append("\n")
                parts.append(" " * 6)

            expr_fragment = self.expressions[i].render(effective_indent)
            parts.append(expr_fragment)

            if expr_fragment.endswith("\n"): # happens when an Expression ends with a line comment
                suppress_newline = True

            i += 1

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
        paren_depth = 0
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
                    if current_scope is ClauseScope.INITIAL:
                        buffer.append(tok)
                        current_scope = potential_new_scope
                    elif potential_new_scope == current_scope and current_scope == ClauseScope.LIMIT_OFFSET:
                        # LIMIT/OFFSET is a weird clause because OFFSET/LIMIT is also valid, so any time
                        # both keywords are used, we'll hit this case. It's normal.
                        buffer.append(tok)
                    elif potential_new_scope <= current_scope:
                        raise ValueError(f"unexpected token {tok} in scope {current_scope.name}")
                    else:
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
        seeking_select = True
        for i, tok in enumerate(tokens):
            # TODO: "(statement) set_op (statement)" is allowed so some paren-awareness is needed
            if seeking_select is True and tok.is_whitespace:
                # drop any whitespace that precedes SELECT
                pass
            elif tok in self.SET_OP_KEYWORDS:
                statements.append(Statement(buffer))
                set_operations.append(tok)
                buffer = []
                seeking_select = True
            else:
                buffer.append(tok)
                if tok == Keywords.SELECT:
                    seeking_select = False
        # final statement
        if len(buffer) > 0:
            statements.append(Statement(buffer))

        # if you do something dumb like "select ... union union select..." this will explode
        assert len(statements) == len(set_operations) + 1

        return (statements, set_operations)


    def starts_with_whitespace(self):
        return False


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
