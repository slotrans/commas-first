import re
import enum
from dataclasses import dataclass
from types import SimpleNamespace


class SFTokenKind(enum.Enum):
    WORD = "WORD"
    LITERAL = "LITERAL"
    SYMBOL = "SYMBOL"
    LINE_COMMENT = "LINE_COMMENT"
    BLOCK_COMMENT = "BLOCK_COMMENT"
    SPACES = "SPACES"
    NEWLINE = "NEWLINE"

# a "word" is a case-insensitive token, e.g. keywords, non-quoted identifiers
# a "literal" is a case-sensitive token, e.g. string literals, quoted identifiers
# a "symbol" is a punctuation-only token, which may be multiple characters, e.g. + - / * -> || :: |&>

# Since 1.23e6 and 1.23E6 are equivalent, and numeric literals without e/E have no case at all,
# numeric literals are treated as WORD, not LITERAL.

# Qualified identifiers such as foo.bar or "Foo"."BAR" will be treated as words or literals depending
# on whether any part is quoted or not. The identifier as a whole is treated as a token, rather than
# each part and the dot separator being treated as separate tokens.

# Arguably line and block comments could be treated as literals, but for now they seem different enough
# to warrant their own types. We'll see.


@dataclass(frozen=True)
class SFToken:
    kind: SFTokenKind
    value: str
    is_whitespace: bool


    def __init__(self, kind, value):
        SFToken._validate(kind, value)

        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "value", value)

        object.__setattr__(self, "is_whitespace", kind in (SFTokenKind.SPACES, SFTokenKind.NEWLINE))


    @staticmethod
    def _validate(kind, value):
        if kind == SFTokenKind.NEWLINE and value != "\n":
            raise ValueError("NEWLINE tokens can only have the value '\\n'")
        elif kind == SFTokenKind.SPACES and (value == "" or any([c != " " for c in value])):
            raise ValueError("SPACES tokens must consist only of space characters")

        return True


    def starts_with_whitespace(self):
        return self.is_whitespace


    def render(self, indent):
        # indent has no effect at the token level
        return self.value


    def __eq__(self, other):
        # no need to include `is_whitespace` in the comparison since it is derived
        if self.__class__ is other.__class__:
            if self.kind == SFTokenKind.WORD:
                return (self.kind, self.value.lower()) == (other.kind, other.value.lower())
            else:
                return (self.kind, self.value) == (other.kind, other.value)
        return NotImplemented


    def __str__(self):
        return f"SFToken({self.kind.name}, '{self.value}', {self.is_whitespace})"


    def __repr__(self):
        return f"SFToken(SFTokenKind.{self.kind.name}, '{self.value}')"


Keywords = SimpleNamespace(
    ALL                = SFToken(SFTokenKind.WORD, "all"),
    AND                = SFToken(SFTokenKind.WORD, "and"),
    CROSS_JOIN         = SFToken(SFTokenKind.WORD, "cross join"),
    DISTINCT           = SFToken(SFTokenKind.WORD, "distinct"),
    DISTINCT_ON        = SFToken(SFTokenKind.WORD, "distinct on"),
    EXCEPT             = SFToken(SFTokenKind.WORD, "except"),
    EXCEPT_ALL         = SFToken(SFTokenKind.WORD, "except all"),
    EXCEPT_DISTINCT    = SFToken(SFTokenKind.WORD, "except distinct"),
    FROM               = SFToken(SFTokenKind.WORD, "from"),
    GROUP_BY           = SFToken(SFTokenKind.WORD, "group by"),
    INNER_JOIN         = SFToken(SFTokenKind.WORD, "inner join"),
    INTERSECT          = SFToken(SFTokenKind.WORD, "intersect"),
    INTERSECT_ALL      = SFToken(SFTokenKind.WORD, "intersect all"),
    INTERSECT_DISTINCT = SFToken(SFTokenKind.WORD, "intersect distinct"),
    JOIN               = SFToken(SFTokenKind.WORD, "join"),
    LATERAL_JOIN       = SFToken(SFTokenKind.WORD, "lateral join"),
    LEFT_JOIN          = SFToken(SFTokenKind.WORD, "left join"),
    LEFT_OUTER_JOIN    = SFToken(SFTokenKind.WORD, "left outer join"),
    LIMIT              = SFToken(SFTokenKind.WORD, "limit"),
    MINUS              = SFToken(SFTokenKind.WORD, "minus"),
    NATURAL_JOIN       = SFToken(SFTokenKind.WORD, "natural"),
    NOT                = SFToken(SFTokenKind.WORD, "not"),
    OFFSET             = SFToken(SFTokenKind.WORD, "offset"),
    ON                 = SFToken(SFTokenKind.WORD, "on"),
    OR                 = SFToken(SFTokenKind.WORD, "or"),
    ORDER_BY           = SFToken(SFTokenKind.WORD, "order by"),
    RIGHT_JOIN         = SFToken(SFTokenKind.WORD, "right join"),
    RIGHT_OUTER_JOIN   = SFToken(SFTokenKind.WORD, "right outer join"),
    SELECT             = SFToken(SFTokenKind.WORD, "select"),
    UNION              = SFToken(SFTokenKind.WORD, "union"),
    UNION_ALL          = SFToken(SFTokenKind.WORD, "union all"),
    UNION_DISTINCT     = SFToken(SFTokenKind.WORD, "union distinct"),
    USING              = SFToken(SFTokenKind.WORD, "using"),
    WHERE              = SFToken(SFTokenKind.WORD, "where"),
    WITH               = SFToken(SFTokenKind.WORD, "with"),
)

Symbols = SimpleNamespace(
    COMMA       = SFToken(SFTokenKind.SYMBOL, ","),
    DOT         = SFToken(SFTokenKind.SYMBOL, "."),
    LEFT_PAREN  = SFToken(SFTokenKind.SYMBOL, "("),
    RIGHT_PAREN = SFToken(SFTokenKind.SYMBOL, ")"),
)

Whitespace = SimpleNamespace(
    NEWLINE   = SFToken(SFTokenKind.NEWLINE, "\n"),
    ONE_SPACE = SFToken(SFTokenKind.SPACES, " "),
)
