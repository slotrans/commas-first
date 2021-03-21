# Hand-Written Lexer

Pygment's Postgres lexer creates certain difficulties, and this exercise is aimed at exploring solutions by way of dropping down to a lower level and confronting the reality of reading SQL syntax directly.


## Reference: types of tokens found in SQL

This is my classification, informed by -- but not directly based on -- descriptions of the formal grammar.

Many of the exotic 2- and 3-character operators are Postgres-specific.

* words  (keywords, identifiers, and some functions that don't require parens)
* --line comments
* /* block comments */
* 'string literals'
* e'special string literals'  (not sure what prefix letters are valid?)
* "quoted words"  (identifiers, aliases)
* `backtick-quoted identifiers` (MySQL, Hive, BigQuery, ...)
* numeric literals e.g. 0, 1, 478, -0.5, +1.23, 4.32e9, 1e-5
* qualified.identifiers
* double.qualified.identifiers
* "quoted_and_qualified"."identifiers" (also double-qualified)
* array_construction[1, 2, 3] and subscripts[0]
* function(calls) and function(calls, with, delimited, arguments) and function_calls_with_empty_arguments()
* function 'calls'  (that mysteriously don't need parens... "interval" and "date" are the ones I know of)
* expression delimiter: ,
* statement delimiter: ;
* (parenthesized expressions) (logical expressions, arithmetic expressions, CTEs, inline views, correlated subqueries, others?)
* 1-character operators: = + - / * % ^ ? | & # ~ :
* 2-character operators: or || ** >= <= <> != -> => #> @> <@ ?| ?& #- @? @@ |/ << >> ## && &< &> <^ >^ ?# ?- ~= !! :: !~ ~*
* 3-character operators: and ->> #>> ||/ @-@ <-> <<| |>> &<| |&> ?-| ?|| <<= >>= @@@ -|- !~*
* Snowflake variant expressions e.g. colname:foo.bar[0].baz
* BETWEEN x AND y  (the O'Reilly lex/yacc book notes that this irregular bit of syntax requires some hacks to support)


## Goal

Remember that the goal here is not parsing valid SQL so that it can be executed. We only need to recognize enough of its structure to lay its text out methodically. 

The SQL that we are operating on may have syntax errors. It may also have unusal or vendor-specific syntax fragments that are unknown to us. There are two competing goals when handling SQL that is invalid or not understood:
- We would like to identify and surface errors
- We would like to lay out the overall SQL structure as readably as possible (which in turn helps find errors)

One place this surfaces is in parsing numeric literals. If the SQL contains "1.23.45" (minus the quotes), how should we handle that? One argument would be that this is clearly an error, and we should report that error then exit early. A counterargument would be that if this mistake is embedded in a big mess of an unreadable query, we are better off allowing it, and laying it out _as if_ it were a valid literal, and let the user discover it by running or planning the query.

Another place is in qualified identifiers. Postgres supports a single level of qualification: `schema.relation`, but Snowflake supports two levels: `database.schema.relation`. No system that I know of supports more than two levels. So if we support two levels at all, then we allow _some_ invalid SQL through. Do we support _more_ than two levels just in case? Or in order to be permissive? If we don't support it, then input of "a.b.c.d" likely ends up as a token stream of ["a.b.c", ".", "d"], and what do we do with that? Again it's unclear whether erroring or being overly permissive is more beneficial to the user.
(Also: Postgres does support two levels when writing `schema.relation.column`... does that imply Snowflake supports three?)


In any event, the goal is to produce a stream of tokens or lexemes or [other name] that represent meaningful logical units, and carry some of that meaning in structured metadata in addition to their text. For example `select` is a keyword, `-1.23` is a numeric literal, `'foo'` is a string literal, `u.user_id` is a qualified identifier, `!=` is an operator, `/* blergh */` is a block comment, and so on.

It should not be necessary for the layout engine to understand that (Token.Operator, '-'), followed by (Token.Literal.Number.Float, '1.23') must be taken together to form the numeric literal `-1.23`. Though technically whitespace is allowed -- e.g. `- 1.23`, `+\n4` -- it produces hard-to-read code so we would never lay it out that way. Instead, the layout engine should receive _as input_ a datum that describes the numeric literal `-1.23`. The metadata "numeric literal" can inform certain layout choices, but wherever it is laid out the text `-1.23` will be inserted literally.

It should not be necessary for the layout engine to understand that the sequence ["is", "not", "null"] should be taken together as "is not null". We will always write it as "is not null", never "is\nnot\nnull" or any such nonsense, so it is helpful for the phrase to come pre-assembled. SQL has several multi-word "key phrases" of this nature such as "order by", "union all", "within group" that should generally be treated as units.

It should not be necessary for the layout engine to understand that the sequence ["u", ".", "user_id"] forms the qualified identifier `u.user_id`. Since we are only laying out text and not resolving symbols, we will not need any knowledge of the name and namespace parts of this identifier. If we do want that for some reason, it is better carried in structured metadata attached to the assembled text.

It should not be necessary for the layout engine to understand that the sequence ["'", "foo", "'"] forms the string literal `'foo'`. Perhaps more illustrative: the sequence ["'", "don", "''", "t", "'"] forms the string literal `'don''t'`. String literals cannot be re-arranged in any way, so there is no benefit to carrying them around as sequences of tokens rather than assembled text.


## First pass: pure text operations

In the first pass we should break the stream of text into a sequence of atomic units. "Atomic" used in the formal sense that such units should represent indivisible things that we cannot (or would never) change the contents of. For example, we cannot print the string literal `'apples and oranges'` in any way other than exactly how it is written, because doing so would change its value. Likewise we cannot change how we print a `/* block comment */` or `--line comment` without changing what text is commented. Nor would we ever print `-1.23` or `is not null` in a different way, not because we can't (we can!), but because no other printing is _sensible_ so we may as well treat them as atomic. Lastly, even though `>` and `=` are operators in their own right, `>=` is a _different_ operator, so emitting the sequence [">", "="] would not be accurate.

In summary, the first pass should result in a sequence of:
- words
- "quoted words"
- comments (block and line)
- numeric literals e.g. 1.23
- string literals e.g. 'red'
- operators e.g. +, -, !=, and, or
- separating/delimiting punctuation: parens, brackets, commas, semicolons
- NO WHITESPACE (except within literals and comments)


## Second pass: phrases, identifiers

In the second pass we should apply more knowledge of how SQL works in practice by assembling certain sequences of atomic units into larger units which, though not truly atomic, we will subsequently treat as such.

To the output of the first pass, this will add:
- phrased keywords and operators such as...
    - "order by", "left join", "within group"
    - "is not null", "is distinct from"
- qualified identifiers
    - u.user_id
    - catalog.listing
    - analytics.main.orginfo
    - "DOUBLE"."QUOTED"."STUFF"


## Third pass(?): aggregates

I suspect that there is value in creating wrappers for certain sequences, which would allow treating them as a unit.
- CTEs, inline views, correlated subqueries
- select-list expressions
- function calls
- parenthesized expressions
- ON clause expressions

In particular... 

Laying out parenthesized expressions such as...
(a.email not like '%test%' or a.email is null)
...thusly...
(   a.email not like '%test%'
 or a.email is null
)
...requires knowing whether the expression is linked using ANDs or ORs

Laying out a function call like...
some_function(a.some_column, b.another_column, another_function(c.foo + c.bar)) as ALIAS
...as...
some_function( a.some_column
             , b.another_column
             , another_function(c.foo + c.bar)
             ) as ALIAS
...would be based on heuristics around the number of arguments and/or the total length of the function call.

Inserting parentheses into an ON clause expression...
on a.foo = b.foo and b.is_deleted = false
...thusly...
on(a.foo = b.foo and b.is_deleted = false)
...requires knowing where the expression starts and ends in the token sequence.

Gracefully laying out oddball functions -- like window functions, within-group functions, or Oracle's keep-dense-rank -- *without* deep understanding of their syntax, seems like it would be greatly aided by knowing where the expression starts and ends.
