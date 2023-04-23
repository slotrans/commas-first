import re
import enum
from dataclasses import dataclass
from types import SimpleNamespace


class CFTokenKind(enum.Enum):
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
class CFToken:
    kind: CFTokenKind
    value: str
    is_whitespace: bool


    def __init__(self, kind, value):
        CFToken._validate(kind, value)

        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "value", value)

        object.__setattr__(self, "is_whitespace", kind in (CFTokenKind.SPACES, CFTokenKind.NEWLINE))


    @staticmethod
    def _validate(kind, value):
        if kind == CFTokenKind.NEWLINE and value != "\n":
            raise ValueError("NEWLINE tokens can only have the value '\\n'")
        elif kind == CFTokenKind.SPACES and (value == "" or any([c != " " for c in value])):
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
            if self.kind == CFTokenKind.WORD:
                return (self.kind, self.value.lower()) == (other.kind, other.value.lower())
            else:
                return (self.kind, self.value) == (other.kind, other.value)
        return NotImplemented


    def __hash__(self):
        if self.kind == CFTokenKind.WORD:
            return hash((self.kind, self.value.lower()))
        else:
            return hash((self.kind, self.value))


    def __str__(self):
        return f"CFToken({self.kind.name}, '{self.value}', {self.is_whitespace})"


    def __repr__(self):
        return f"CFToken(CFTokenKind.{self.kind.name}, '{self.value}')"


Keywords = SimpleNamespace(
    ALL                = CFToken(CFTokenKind.WORD, "all"),
    AND                = CFToken(CFTokenKind.WORD, "and"),
    CROSS_JOIN         = CFToken(CFTokenKind.WORD, "cross join"),
    DISTINCT           = CFToken(CFTokenKind.WORD, "distinct"),
    DISTINCT_ON        = CFToken(CFTokenKind.WORD, "distinct on"),
    EXCEPT             = CFToken(CFTokenKind.WORD, "except"),
    EXCEPT_ALL         = CFToken(CFTokenKind.WORD, "except all"),
    EXCEPT_DISTINCT    = CFToken(CFTokenKind.WORD, "except distinct"),
    FROM               = CFToken(CFTokenKind.WORD, "from"),
    FULL_JOIN          = CFToken(CFTokenKind.WORD, "full join"),
    FULL_OUTER_JOIN    = CFToken(CFTokenKind.WORD, "full outer join"),
    GROUP_BY           = CFToken(CFTokenKind.WORD, "group by"),
    HAVING             = CFToken(CFTokenKind.WORD, "having"),
    INNER_JOIN         = CFToken(CFTokenKind.WORD, "inner join"),
    INTERSECT          = CFToken(CFTokenKind.WORD, "intersect"),
    INTERSECT_ALL      = CFToken(CFTokenKind.WORD, "intersect all"),
    INTERSECT_DISTINCT = CFToken(CFTokenKind.WORD, "intersect distinct"),
    JOIN               = CFToken(CFTokenKind.WORD, "join"),
    LATERAL_JOIN       = CFToken(CFTokenKind.WORD, "lateral join"),
    LEFT_JOIN          = CFToken(CFTokenKind.WORD, "left join"),
    LEFT_OUTER_JOIN    = CFToken(CFTokenKind.WORD, "left outer join"),
    LIMIT              = CFToken(CFTokenKind.WORD, "limit"),
    MINUS              = CFToken(CFTokenKind.WORD, "minus"),
    NATURAL_JOIN       = CFToken(CFTokenKind.WORD, "natural"),
    NOT                = CFToken(CFTokenKind.WORD, "not"),
    OFFSET             = CFToken(CFTokenKind.WORD, "offset"),
    ON                 = CFToken(CFTokenKind.WORD, "on"),
    OR                 = CFToken(CFTokenKind.WORD, "or"),
    ORDER_BY           = CFToken(CFTokenKind.WORD, "order by"),
    RIGHT_JOIN         = CFToken(CFTokenKind.WORD, "right join"),
    RIGHT_OUTER_JOIN   = CFToken(CFTokenKind.WORD, "right outer join"),
    SELECT             = CFToken(CFTokenKind.WORD, "select"),
    UNION              = CFToken(CFTokenKind.WORD, "union"),
    UNION_ALL          = CFToken(CFTokenKind.WORD, "union all"),
    UNION_DISTINCT     = CFToken(CFTokenKind.WORD, "union distinct"),
    USING              = CFToken(CFTokenKind.WORD, "using"),
    WHERE              = CFToken(CFTokenKind.WORD, "where"),
    WITH               = CFToken(CFTokenKind.WORD, "with"),
)

Symbols = SimpleNamespace(
    COMMA       = CFToken(CFTokenKind.SYMBOL, ","),
    DOT         = CFToken(CFTokenKind.SYMBOL, "."),
    LEFT_PAREN  = CFToken(CFTokenKind.SYMBOL, "("),
    RIGHT_PAREN = CFToken(CFTokenKind.SYMBOL, ")"),
)

Whitespace = SimpleNamespace(
    NEWLINE   = CFToken(CFTokenKind.NEWLINE, "\n"),
    ONE_SPACE = CFToken(CFTokenKind.SPACES, " "),
)
