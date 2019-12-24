import sys
import re
import enum

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.token import Token


# keywords
SELECT = (Token.Keyword, 'select')
FROM = (Token.Keyword, 'from')
JOIN = (Token.Keyword, 'join')
LEFT_JOIN = [(Token.Keyword, 'left'), (Token.Keyword, 'join')]
LEFT_OUTER_JOIN = [(Token.Keyword, 'left'), (Token.Keyword, 'outer'), (Token.Keyword, 'join')]
RIGHT_JOIN = [(Token.Keyword, 'right'), (Token.Keyword, 'join')]
RIGHT_OUTER_JOIN = [(Token.Keyword, 'right'), (Token.Keyword, 'outer'), (Token.Keyword, 'join')]
WHERE = (Token.Keyword, 'where')
GROUP_BY = [(Token.Keyword, 'group'), (Token.Keyword, 'by')]
HAVING = (Token.Keyword, 'having')
ORDER_BY = [(Token.Keyword, 'order'), (Token.Keyword, 'by')]
WINDOW = (Token.Keyword, 'window')
LIMIT = (Token.Keyword, 'limit')
OFFSET = (Token.Keyword, 'offset')
AND = (Token.Keyword, 'and')
OR = (Token.Keyword, 'or')

# punctuation etc
LEFT_PAREN = (Token.Punctuation, '(')
RIGHT_PAREN = (Token.Punctuation, ')')
COMMA = (Token.Punctuation, ',')
SEMICOLON = (Token.Punctuation, ';')
SINGLE_QUOTE = (Token.Literal.String.Single, "'")
CAST = (Token.Operator, '::')


class Scope(enum.Enum):
    INITIAL = 'INITIAL'
    SELECT = 'SELECT'
    FROM = 'FROM'
    WHERE = 'WHERE'
    GROUP_BY = 'GROUP_BY'
    HAVING = 'HAVING'
    ORDER_BY = 'ORDER_BY'
    WINDOW = 'WINDOW'


ALL_WHITESPACE = re.compile(r'^\s+$')
def is_only_whitespace(token):
    ttype, value = token
    return (ttype == Token.Text and ALL_WHITESPACE.match(value))


def do_format_recursive(tokenlist, scope, paren_depth, subquery_depth):
    token_count = len(tokenlist)
    print(f'token_count={token_count} scope={scope}, parenD={paren_depth}, subqueryD={subquery_depth} / ', end='', file=sys.stderr)
    if token_count == 0:
        if paren_depth == 0:
            return ''
        else:
            # might be better to throw an exception if this check fails and handle it at the outermost level by
            # returning the input unmodified along with this warning...
            # this is fine for now though
            return '\n/* WARNING: unbalanced parens detected */'

    token = tokenlist[0]
    ttype, value = token
    print(f'{ttype}<{value}> / ', end='', file=sys.stderr)
    
    next_token = tokenlist[1] if token_count >= 2 else (Token, '') # bogus token that should always be not-equal to anything
    next_ttype, next_value = next_token

    two_tokens = tokenlist[0:2] if token_count >= 2 else []
    three_tokens = tokenlist[0:3] if token_count >= 3 else []    

    margin = (subquery_depth * 8 * ' ')
    print(f'margin={len(margin)}', file=sys.stderr)

    # SELECT
    if token == SELECT: 
        return 'select ' + do_format_recursive(tokenlist[1:], Scope.SELECT, paren_depth, subquery_depth)

    # FROM
    elif token == FROM and scope is Scope.SELECT and paren_depth == 0:
        return margin + '\n  from ' + do_format_recursive(tokenlist[1:], Scope.FROM, paren_depth, subquery_depth)

    # JOIN
    elif token == JOIN:
        return margin + '\n  join ' + do_format_recursive(tokenlist[1:], Scope.FROM, paren_depth, subquery_depth)

    # LEFT JOIN
    elif two_tokens == LEFT_JOIN:
        return margin + '\n  left join ' + do_format_recursive(tokenlist[2:], Scope.FROM, paren_depth, subquery_depth)

    # LEFT OUTER JOIN
    elif three_tokens == LEFT_OUTER_JOIN:
        # strip the useless "outer"
        return margin + '\n  left join ' + do_format_recursive(tokenlist[3:], Scope.FROM, paren_depth, subquery_depth)

    # RIGHT JOIN
    elif two_tokens == RIGHT_JOIN:
        return margin + '\n  right join ' + do_format_recursive(tokenlist[2:], Scope.FROM, paren_depth, subquery_depth)

    # RIGHT OUTER JOIN
    elif three_tokens == RIGHT_OUTER_JOIN:
        # strip the useless "outer"
        return margin + '\n  right join ' + do_format_recursive(tokenlist[3:], Scope.FROM, paren_depth, subquery_depth)

    # WHERE
    elif token == WHERE:
        return margin + '\n where ' + do_format_recursive(tokenlist[1:], Scope.WHERE, paren_depth, subquery_depth)

    # GROUP BY
    elif two_tokens == GROUP_BY:
        return margin + '\n group by ' + do_format_recursive(tokenlist[2:], Scope.GROUP_BY, paren_depth, subquery_depth)

    # HAVING
    elif token == HAVING:
        return margin + '\nhaving ' + do_format_recursive(tokenlist[1:], Scope.HAVING, paren_depth, subquery_depth)

    # ORDER BY
    # unless we're in select scope, where "order by" can appear in certain function calls
    elif two_tokens == ORDER_BY and scope is not Scope.SELECT:
        return margin + '\n order by ' + do_format_recursive(tokenlist[2:], Scope.ORDER_BY, paren_depth, subquery_depth)

    # left/opening paren
    elif token == LEFT_PAREN:
        return '(' + do_format_recursive(tokenlist[1:], scope, paren_depth + 1, subquery_depth)

    # right/closing paren
    elif token == RIGHT_PAREN:
        return ') ' + do_format_recursive(tokenlist[1:], scope, paren_depth - 1, subquery_depth)

    # COMMA
    # if paren_depth > 0 it means we are inside some expression's parens and this comma must be part of a function call,
    # whereas if paren_depth == 0 then this comma is an expression separator
    elif token == COMMA:
        if paren_depth == 0:
            return margin + '\n     , ' + do_format_recursive(tokenlist[1:], scope, paren_depth, subquery_depth)
        else:
            return ', ' + do_format_recursive(tokenlist[1:], scope, paren_depth, subquery_depth)

    # "and" alignment for where clause
    elif scope is Scope.WHERE and token == AND:
        return margin + '\n   and ' + do_format_recursive(tokenlist[1:], scope, paren_depth, subquery_depth)

    # basic string literals
    elif token == SINGLE_QUOTE:
        tokens_consumed = ["'"]        
        for t, v in tokenlist[1:]:
            if t is Token.Literal.String.Single:
                tokens_consumed.append(v)
            else:
                break
        return ''.join(tokens_consumed) + ' ' + do_format_recursive(tokenlist[len(tokens_consumed):], scope, paren_depth, subquery_depth)

    # semicolon
    elif token == SEMICOLON and token_count == 1:
        return '\n;'

    # spacing between most ordinary tokens
    elif (    any(ttype in t for t in (Token.Text, Token.Name, Token.Keyword, Token.Literal.Number.Float, Token.Operator))
          and value != '.'
          and any(next_ttype in t for t in (Token.Text, Token.Name, Token.Keyword, Token.Literal.Number.Float, Token.Operator))
          and next_value != '.'
         ):
        return value + ' ' + do_format_recursive(tokenlist[1:], scope, paren_depth, subquery_depth)

    # default
    else:
        return value + do_format_recursive(tokenlist[1:], scope, paren_depth, subquery_depth)


def post_process(text):
    return text
    # collapse extra space around :: operator e.g. 'foo :: int' -> 'foo::int'
    # collapse extra space inside closing parens e.g. ' )' -> ')'        


if __name__ == '__main__':
    unformatted_code = sys.stdin.read()

    lexer = get_lexer_by_name("postgres", stripall=True)
    tokens = list([t for t in lexer.get_tokens(unformatted_code) if not is_only_whitespace(t)])

    print(f'count={len(tokens)}', file=sys.stderr)
    print(tokens, file=sys.stderr)

    formatted_code = do_format_recursive(tokens, Scope.INITIAL, 0, 0)

    post_processed_code = post_process(formatted_code)

    print(post_processed_code)
