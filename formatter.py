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
ON = (Token.Keyword, 'on')
USING = (Token.Keyword, 'using')
UNION_ALL = [(Token.Keyword, 'union'), (Token.Keyword, 'all')]
UNION = (Token.Keyword, 'union')
INTERSECT = (Token.Keyword, 'intersect')
MINUS = (Token.Name, 'minus') # PG lexer doesn't consider this a keyword
EXCEPT = (Token.Keyword, 'except')

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
    JOIN_PREDICATE = 'JOIN_PREDICATE'


ALL_WHITESPACE = re.compile(r'^\s+$')
def is_only_whitespace(token):
    ttype, value = token
    return (ttype == Token.Text and ALL_WHITESPACE.match(value))


def do_format_recursive(tokenlist, scope, paren_depth, line_length):
    token_count = len(tokenlist)
    print(f'token_count={token_count} scope={scope}, parenD={paren_depth}, lineLen={line_length} / ', end='', file=sys.stderr)
    # recursion terminal case
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
    print(f'{ttype}<{value}> / ', file=sys.stderr)
    
    next_token = tokenlist[1] if token_count >= 2 else (Token, '') # bogus token that should always be not-equal to anything
    next_ttype, next_value = next_token

    two_tokens = tokenlist[0:2] if token_count >= 2 else []
    three_tokens = tokenlist[0:3] if token_count >= 3 else []    

    # SELECT
    if token == SELECT: 
        fragment = 'select '
        return fragment + do_format_recursive(tokenlist[1:], Scope.SELECT, paren_depth, len(fragment))

    # FROM
    elif token == FROM and scope is Scope.SELECT and paren_depth == 0:
        fragment = '\n  from '
        return fragment + do_format_recursive(tokenlist[1:], Scope.FROM, paren_depth, len(fragment))

    # JOIN
    elif token == JOIN:
        fragment = '\n  join '
        return fragment + do_format_recursive(tokenlist[1:], Scope.FROM, paren_depth, len(fragment))

    # LEFT JOIN
    elif two_tokens == LEFT_JOIN:
        fragment = '\n  left join '
        return fragment + do_format_recursive(tokenlist[2:], Scope.FROM, paren_depth, len(fragment))

    # LEFT OUTER JOIN
    elif three_tokens == LEFT_OUTER_JOIN:
        # strip the useless "outer"
        fragment = '\n  left join '
        return fragment + do_format_recursive(tokenlist[3:], Scope.FROM, paren_depth, len(fragment))

    # RIGHT JOIN
    elif two_tokens == RIGHT_JOIN:
        fragment = '\n  right join '
        return fragment + do_format_recursive(tokenlist[2:], Scope.FROM, paren_depth, len(fragment))

    # RIGHT OUTER JOIN
    elif three_tokens == RIGHT_OUTER_JOIN:
        # strip the useless "outer"
        fragment = '\n  right join '
        return fragment + do_format_recursive(tokenlist[3:], Scope.FROM, paren_depth, len(fragment))

    # ON / USING
    elif token in (ON, USING):
        fragment = value + ' '
        return fragment + do_format_recursive(tokenlist[1:], Scope.JOIN_PREDICATE, paren_depth, line_length+len(fragment))

    # WHERE
    elif token == WHERE:
        fragment = '\n where '
        return fragment + do_format_recursive(tokenlist[1:], Scope.WHERE, paren_depth, len(fragment))

    # GROUP BY
    elif two_tokens == GROUP_BY:
        fragment = '\n group by '
        return fragment + do_format_recursive(tokenlist[2:], Scope.GROUP_BY, paren_depth, len(fragment))

    # HAVING
    elif token == HAVING:
        fragment = '\nhaving '
        return fragment + do_format_recursive(tokenlist[1:], Scope.HAVING, paren_depth, len(fragment))

    # ORDER BY
    # unless we're in select scope, where "order by" can appear in certain function calls
    elif two_tokens == ORDER_BY and scope is not Scope.SELECT:
        fragment = '\n order by '
        return fragment + do_format_recursive(tokenlist[2:], Scope.ORDER_BY, paren_depth, len(fragment))

    # UNION ALL
    elif two_tokens == UNION_ALL:
        fragment = '\nunion all\n'
        return fragment + do_format_recursive(tokenlist[2:], scope, paren_depth, len(fragment))

    # UNION, INTERSECT, MINUS, EXCEPT
    elif token in (UNION, INTERSECT, MINUS, EXCEPT):
        fragment = '\n' + value + '\n'
        return fragment + do_format_recursive(tokenlist[1:], scope, paren_depth, len(fragment))

    # left/opening paren
    elif token == LEFT_PAREN:
        if next_token != SELECT:
            fragment = '('
            return fragment + do_format_recursive(tokenlist[1:], scope, paren_depth + 1, line_length+len(fragment))
        else: # we are entering a subquery
            subquery_tokens = []
            subquery_paren_depth = 0
            for i_token in tokenlist[1:]:
                if i_token == RIGHT_PAREN and subquery_paren_depth == 0:
                    # must be the subquery's closing paren
                    break

                subquery_tokens.append(i_token)

                if i_token == LEFT_PAREN:
                    subquery_paren_depth += 1
                elif i_token == RIGHT_PAREN:
                    subquery_paren_depth -= 1

            formatted_subquery = do_format_recursive(subquery_tokens, Scope.INITIAL, paren_depth=0, line_length=0)
            formatted_and_aligned_subquery = formatted_subquery.replace('\n', ('\n' + ' ' * line_length)) # this is how we bump the margin over           
            fragment = '('
            fragment += formatted_and_aligned_subquery
            fragment += '\n'
            fragment += (' ' * (line_length - 1))
            fragment += ') '
            return fragment + do_format_recursive(tokenlist[(len(subquery_tokens)+2):], scope, paren_depth, line_length)


    # right/closing paren
    elif token == RIGHT_PAREN:
        fragment = ') '
        return fragment + do_format_recursive(tokenlist[1:], scope, paren_depth - 1, line_length+len(fragment))

    # COMMA
    # if paren_depth > 0 it means we are inside some expression's parens and this comma must be part of a function call,
    # whereas if paren_depth == 0 then this comma is an expression separator
    elif token == COMMA:
        if paren_depth == 0:
            if scope in (Scope.GROUP_BY, Scope.ORDER_BY):
                fragment = '\n        , '
            else:
                fragment = '\n     , '
            return fragment + do_format_recursive(tokenlist[1:], scope, paren_depth, len(fragment))
        else:
            fragment = ', '
            return fragment + do_format_recursive(tokenlist[1:], scope, paren_depth, line_length+len(fragment))

    # "and" alignment for where clause
    elif scope is Scope.WHERE and token == AND:
        fragment = '\n   and '
        return fragment + do_format_recursive(tokenlist[1:], scope, paren_depth, len(fragment))

    # basic string literals
    elif token == SINGLE_QUOTE:
        tokens_consumed = ["'"]        
        for t, v in tokenlist[1:]:
            if t is Token.Literal.String.Single:
                tokens_consumed.append(v)
            else:
                break
        fragment = ''.join(tokens_consumed) + ' '
        return fragment + do_format_recursive(tokenlist[len(tokens_consumed):], scope, paren_depth, line_length+len(fragment))

    # semicolon
    elif token == SEMICOLON and token_count == 1:
        return '\n;'

    # spacing between most ordinary tokens
    elif (    any(ttype in t for t in (Token.Text, Token.Name, Token.Keyword, Token.Literal.Number.Float, Token.Operator))
          and value != '.'
          and any(next_ttype in t for t in (Token.Text, Token.Name, Token.Keyword, Token.Literal.Number.Float, Token.Operator, Token.Punctuation))
          and next_value not in ( '.', ')' )
         ):
        fragment = value + ' '
        return fragment + do_format_recursive(tokenlist[1:], scope, paren_depth, line_length+len(fragment))

    # default
    else:
        fragment = value
        return fragment + do_format_recursive(tokenlist[1:], scope, paren_depth, line_length+len(fragment))


def pre_process_tokens(tokenlist):
    out = []
    for t in tokenlist:
        ttype, value = t
        if is_only_whitespace(t):
            continue

        if ttype is Token.Keyword:
            value = value.lower()

        out.append( (ttype, value) )

    return out


def post_process_text(text):
    # no-op for now
    return text

    #TODO:
    # collapse extra space around :: operator e.g. 'foo :: int' -> 'foo::int'
    # collapse extra space inside closing parens e.g. ' )' -> ')'        


if __name__ == '__main__':
    unformatted_code = sys.stdin.read()

    lexer = get_lexer_by_name("postgres", stripall=True)
    tokens = pre_process_tokens(lexer.get_tokens(unformatted_code))

    print(f'count={len(tokens)}', file=sys.stderr)
    print(tokens, file=sys.stderr)

    formatted_code = do_format_recursive(
        tokenlist=tokens, 
        scope=Scope.INITIAL, 
        paren_depth=0, 
        line_length=0,
    )

    post_processed_code = post_process_text(formatted_code)

    print(post_processed_code)
    sys.exit(0)
