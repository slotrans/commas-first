# The "constants" defined in this module will be mutated by:
# 1. the top-level "main", after parsing command-line args
# 2. unit tests
# During any given execution they will be set, and then never change.

TRIM_LEADING_WHITESPACE = False

def reset_to_defaults():
    global TRIM_LEADING_WHITESPACE
    TRIM_LEADING_WHITESPACE = False
    