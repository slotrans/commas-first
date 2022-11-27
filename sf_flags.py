import enum
# The "constants" defined in this module will be mutated by:
# 1. the top-level "main", after parsing command-line args
# 2. unit tests
# During any given execution they will be set, and then never change.


class FormatMode(enum.Enum):
    DEFAULT = "DEFAULT"
    TRIM_LEADING_WHITESPACE = "TRIM_LEADING_WHITESPACE"
    COMPACT_EXPRESSIONS = "COMPACT_EXPRESSIONS"


FORMAT_MODE = FormatMode.DEFAULT


def reset_to_defaults():
    global FORMAT_MODE
    FORMAT_MODE = FormatMode.DEFAULT
