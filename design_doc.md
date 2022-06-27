# Constraints

- take input on STDIN and produce formatted output on STDOUT
    - not 100% sure this is binding but seems like the simplest way to integrate it as an external tool

- total execution time should stay small, ideally under 1 second for a large query

- be installable on common developer machines without major brain damage (ideally packaged as a single executable)


# Non-constraints

- no need to be "scalable"
    - largest likely input is perhaps a few KB of text
    - even a *very* large query won't tokenize to more than a few thousand tokens

- no need to be single-pass
    - per the above, all input comfortably fits in memory
    - materializing lazy sequences into lists is OK
    - making extra copies is OK
    - accumulating output into a buffer and printing once at the end would be OK
        - perhaps after a post-processing pass

- no need to support other formatting styles
    - formatters for other styles exist
    - whole point is to do it MY WAY
    - no intent to support commas-last
    - no intent to support block-indentation style formatting approaches

- no need to support every statement
    - SELECT, INSERT, UPDATE, DELETE, CREATE TABLE are all very valuable
    - probably ignore everything else (pass-through)


# Unknowns

- dialect-specific features
    - how much do we need to handle them?
    - example: the Postgres cast operator `::` may need special handling, but hopefully just won't be present (as a token) in dialects where it's not used
    - odd function forms like `max(foo) keep(dense_rank last order by bar)` or `percentile_disc(0.99) within group(order by response_time)` can hopefully be handled generically
    - dollar-quoting?
    - backtick-quoting?
    - Snowflake's flatten() uses an arrow operator (-> or =>, not sure), not necessary to lay this out smartly but can we at least avoid choking on it?
    - Oracle's `(+)` operator? meh probably not
    - Postgres' array constructor: `array[1,2,3]`
        - and array subscript syntax: `foo[1]` or `bar[2][3]`

- very long function calls: splitting/aligning
    - sometimes seen with window functions?
    - example: `lead(page, 1) over(partition by user_id, request_time::date, some_other_thing order by request_time, and_something_else, a_third_thing)` ideally line-breaks before `order by` and aligns underneath `partition by`, and if the partitioning/ordering expression lists are sufficiently long they should be broken onto lines as well
    - likely requires explicit handling of window syntax
    - not a critical feature; needing to hand-tweak stuff like this after auto-formatting is OK

- long on() clauses and compound predicates? (similar to long function calls)
    - detecting this is hard because it requires looking forward an unknown number of tokens of unknown types
    - probably want to split/align only once the whole expression gets beyond a certain length, which would require accumulating all the tokens before making the layout decision
    - not a critical feature for basic usefulness but would save a lot of time hand-formatting complex queries

- case expressions (again similar)
    - should a multi-line layout always be performed, or should it be length-sensitive?
    - in a multi-line layout, alignment of and/or predicates should match that of `where`
    - the presence/absence of "else null" should not be meddled with, writing it out can add clarity even though it's the default

- line comments
    - some dialects treat `#` as equivalent to, or a substitute for `--`, do we need to support that? maybe a CLI flag?
    - an important part of formatting is putting line breaks where they belong, but line comments are line-break sensitive (obviously)... are there any scenarios where moving a token to a different line changes whether it's commented?
    - similarly, if we move a comment, specifically a real *comment* rather than disabled code, can that create confusion by distancing it from the code it's commenting on?
    - enforce a space before `--`?

- block comments
    - a block comment is inherently pre-formatted, we shouldn't change it
    - also I think the lexer gives it to us as ['/*', 'the whole comment as one token with embedded newlines', '*/']
    - maybe anchor it to the left margin?
    - maybe there's a smarter handling strategy based on whether it starts on its own line, or at the end of a line with other tokens?
    - maybe there's no good solution?

- aliasing
    - some desire to support inserting auto-generated column aliases
    - potential to change semantics, especially when done to CTEs/inline views
    - inserting table aliases is also desirable but harder
        - column references qualified with the full table name would need to be changed to the alias
        - not possible to add the alias qualification to un-qualified column references without knowledge of the schema
    - definitely possible and safe: enforcing the use of `as` in column aliases and removing it from table aliases
    - also possible: right-aligntment of column aliases
    - I prefer aliases to be capitalized (when not double-quoted), but it may be desirable to make this switchable

- should the `outer` keyword be automatically stripped from `left outer join`?
    - yes

- how to lay out `cross join`?

- can/should we automatically add `1=1` to the `where` clause if not present?
    - desirable.
    - also desirable: adding `where 1=1` when no `where` clause is present at all

- how to handle the set operators: UNION (ALL), INTERSECT, EXCEPT/MINUS ???

- subqueries (both correlated subqueries and inline views)
    - initially I started tracking paren depth to differentiate commas-as-function-arg-separators from commas-as-expression-list-separators
    - being inside parens and encountering SELECT is also significant, and needs to be tracked in order to get indentation correct
    - problem is subqueries are expressions and can be embedded anywhere, e.g. (foo + (select 1) + bar), and the paren depth needs to be remembered and then restored upon exiting the subquery context (suggests a stack)
    - for inline views we can set the left margin just by knowing the nesting depth adding padding before every newline
    - for correlated subqueries that doesn't work because SELECT could be at any arbitrary distance from the left margin and we need to align to it
        - good news is this generalizes to the inline view case so really we only need to solve *this* problem
        - bad news is it means knowing how far we are from the left margin at all times

- how to enforce the use of parens with ON/USING?
    - e.g. `on x.foo = y.foo` should always be `on(x.foo = y.foo)` even though the syntax does not require this
    - inserting parens requires knowing the boundaries of expressions

- tabs to spaces conversion?
    - actually i think we get this for free because we discard all input whitespace


# Basic layout

- strip all tokens that are entirely whitespace, since we will be handling spacing and newlines
    - it _may_ be desirable to preserve whitespace that occurs immediately before a block comment

## SELECT

- initial `select` starts at column 1, the `t` in column 6 becomes the alignment ruler for the major clause keywords

- if present, `distinct` (or `all`) immediately follows `select` and pushes the first select expression to the next line

- for each select expression
    - for the first:
        - if DISTINCT or ALL, bump to next line and left-pad with 7 spaces
        - otherwise immediately follow `select` plus a space
    - for all subsequent, add a newline then left-pad with 5 spaces, a comma, and another space (`     , `), aligning the comma under the `t` in `select`
        - note the comma is present as Token.Puncutation<,> and will need to be consumed; this token marks the boundary between expressions
    - print to the end of the line, including `as` and the alias if present

## FROM/JOIN

- left-pad `from` with 2 spaces, aligning the `m` in `from` under the `t` in `select`

- the first table in the `from` clause immediately follows, including alias if present, then a line break

- if tables are listed in `from` SQL-92 style, lay them out as per select expressions above, beginning each line with spaces and a comma aligned under `t` and `m`

- if SQL-99 `join` clauses are used, align `join` or `left` directly under `from`
    - (if some jerk uses `right join` align the `r` under `f` which is terrible but whatever)
    - print the `on` or `using` clause out to the end of the line
    - the next `join|left|right` token marks the boundary
    - `where` marks the end of the from/join scope

## WHERE

- left-pad `where` with 1 space, aligning the `e` in `where` under the `t` in `select`

- the first predicate immediately follows on the same line

- before each `and` or `or` insert a line break and 3 or 4 spaces respectively

- treat parentheses-wrapped compound expressions as a single expression and print on a single line (TODO: specify breaking/alignment for long compound predicates)

## GROUP BY

- left-pad `group by` with 1 space, aligning the `p` in `group` under the `t` in `select`

- lay out group-by expressions as per select expressions, but note that the line of commas aligns to the `y` in `by`!

## HAVING

- `having` prints at column 1 (no padding)

- lay out having expressions _exactly_ as per where expressions

## ORDER BY

- lay out _exactly_ as per group-by expressions

## LIMIT, OFFSET

- left-pad `limit` with one space, print its argument on the same line

- `offset` is the same but with no padding

## CTEs

- `with` prints at column 1 (no padding), followed by the name, followed by `as`, followed by a line break

- then a single left paren in column 1

- the contents of a CTE will be a `select` statement (TODO: support INSERT/UPDATE/DELETE in CTEs, which are a thing in Postgres), which will be laid out exactly as if it were not inside a CTE, except that the left margin will be moved over by N spaces
    - N has typically been 2 or 4, I'm not sure which I prefer, and it should be easy to specify this as a CLI argument
    - all absolute positioning described here (e.g. "left pad with 2 spaces") is *relative to this margin*

- followed by a single right paren in column 1

- if additional CTEs are present, follow the above closing parent with a line break, then a comma in column 1, the name, `as`, and then repeat the CTE layout starting from the left paren

## Inline Views

- in the from/join scope, a table may be replaced with a `select` statement surrounded by parentheses

- print the opening/left paren on the same line as `from|join|left` and follow with a line break
    - I have sometimes preferred to start the enclosed statement on the same line as the opening paren, so perhaps make that switchable

- the contents of the inline view will be laid out exactly as a bare `select` statement, with the left margin moved over so that the `s` in `select` is one column to the right of the left paren (column 9, for the first level of nesting, or column 14 in the case of `left join`)

- print the closing/right paren in the same column as the opening/left paren, on its own line immediately following the last line of the enclosed statement

- print the `on|using` clause immediately following the closing/right paren, on the same line, exactly as if it were following a from/join identifier

- note that inline views can be nested arbitrarily deep

## Statement terminator

- the trailing semicolon, if present, prints in column 1 on its own line


# Special cases

- `where 1=1` is preferred, though this would normally lay out as `where 1 = 1`
    - probably easiest to fix with post-processing


# Notes on "postgres" lexer behavior

- `x.foo` lexes to:
    - Token.Name<x>, Token.Literal.Number.Float<.>, Token.Name<foo>
    - may need specific handling for the `.` token

- some functions like `greatest` lex to Token.Keyword despite not being keywords

- phrases
    - `group by` and `order by` lex as two tokens, not one
    - `is not null` lexes as three tokens
    - basically assume any N-word keyword phrase lexes as N tokens
    - might be worth modifying the lexer if this turns out to be super annoying

- `'string literal'` lexes to:
    - (Token.Literal.String.Single, "'"), (Token.Literal.String.Single, 'string literal'), (Token.Literal.String.Single, "'")
    - ugh

- `'don''t` lexes to:
    -  (Token.Literal.String.Single, "'"), (Token.Literal.String.Single, 'don'), (Token.Literal.String.Single, "''"), (Token.Literal.String.Single, 't'), (Token.Literal.String.Single, "'")
    - blergh

- `$$dollar literal$$` lexes to:
    - (Token.Literal.String, '$'), (Token.Literal.String.Delimiter, ''), (Token.Literal.String, '$'), (Token.Literal.String, 'dollar literal'), (Token.Literal.String, '$'), (Token.Literal.String.Delimiter, ''), (Token.Literal.String, '$')
    - sweet jesus


# Ideas

- is it worth splitting the statement's token stream into chunks based on keyword scope, as the first pass?
    - with, select, from/join, where, group, having, order, window, limit, offset
    - does this actually yield simpler sub-problems or does it result in duplication (e.g. of depth tracking)?

- making constants for the keywords / keyword phrases seems to be working very well -- e.g. SELECT = (Token.Keyword, 'select') -- but the tests,
especially for phrases, are wordy and depend on the phrase length being tested
    - is it worth making a class for this, where an instance corresponds to a word/phrase and knows how to test for itself given a token list?
    - the recursive call still needs to specify how many tokens are consumed so maybe it doesn't help much

- would it be worth re-building the initial token list as namedtuples just to better enable both referring to a token as a unit and referring to its type or value?

- random thought: is it worth doing an initial paren-matching pass?
    - this would give us a quick short-circuit, and hopefully the ability to give a good error message, if the input has unbalanced parens
    - for good input, we would replace the stream of 2-tuple (type, value) tokens with 3-tuples of (type, value, [reference to matching paren])
    - then instead of turning the 3-tuple tokens into strings, we turn them into 5-tuples of (type, value, [matching paren], line, indent)
    - ugh maybe they need to be mutable objects instead of tuples...
    - in any case the methodology is to say, i have a closing paren, bump it to the next line and set its indentation equal to the matching opening paren
    - then once you have a list of these tuples/objects, the actual layout step is to just map them to their indicated X (line) and Y (indent) positions

- quick thought on long compound expressions: it might be simpler to just always do the break-and-align style formatting, then check the length of the result and if shorter than [threshold], unwind it by collapsing whitespace

- I initially switched to a recursive solution becuase I couldn't see how to consume multiple tokens in an iterative fashion, but I figured it out. I don't know why it wasn't obvious to me before... perhaps I've gotten so accustomed to using only for-each style loops or while-true loops that my brain just wasn't prepared for it. Anyway, in the recursive pattern we can consume N tokens by calling the next function with `tokenlist[N:]` as the input argument. The iterative isomorphism is to use an index variable with a while loop, and to advance the index variable by N (instead of always by 1 as a for-each loop does).

- The main use case I was pursuing with this program is the initial reformatting of ugly queries handed to me by others. There is a different use case though, which is handling the tedious reformatting necessitated by certain changes made while working on a query.
    - For example, if you have `and foo.bar in (select ...)`, and the subquery has line breaks and nice alignment, then you change `foo.bar` to `flerb.baz`, the subquery needs to be re-aligned because the first line is now 2 characters further right.
    - Or if you have `join some_table on(...)`, and the on() clause is compound and nicely aligned, and you replace `some_table` with `some.longer_identifier`, the on() clause needs to be re-aligned.
    - So it would be great if you could pass your in-progress query back through the formatter after making one of these kinds of changes...
    - ...but the key is that when you do that, it's not acceptable for the formatter to re-arrange stuff you may have laid out by hand. Typically this is stuff like long select-clause expressions doing string concatenation or arithmetic, multi-level nested function calls, or particularly elaborate `case` expressions. Because these live in the land of "stuff that a formatting algorithm can't anticipate", the author's layout needs to be respected.
    - Conclusion: in order to support this use case, the formatter needs to be *less* opinionated about how select-clause expressions are laid out, and in particular probably needs to preserve certain whitespace in the input (likely any whitespace not related to indenting expression-separator commas).

### 2020-01-01
- Really starting to think it's time to modify the lexer
    - it would be much simpler if things we need to _treat_ as a single token -- group by, 1.5, 'blergh', >=, x.foo -- actually lexed as a single token rather than a series
    - some of these phrases may need to be assembled in a pre-processing pass over the lexer output, rather than in the lexer itself, we'll see
    - also Pygments' postgres lexer marks some things as Keyword which are not keywords, like "greatest", and I would prefer to be able to consistently differentiate between identifiers and true keywords

- Need to write some code that understands expressions
    - doesn't need to be perfect, ok to allow plausible-looking but invalid constructs
    - doesn't need to understand enough to _evaluate_ expressions, really just know where they begin and end, and the nesting level
    - may want to look up the formal expression grammar
        - https://github.com/ronsavage/SQL
        - https://www.jooq.org/doc/latest/manual/sql-building/sql-parser/sql-parser-grammar/
    - probably need a whitelist of binary operators: + - / * = <> != >= <= > < ||
        - maybe also >> << ->> & | ^
    - unary operators???
    - don't need a list of functions, assume any identifier used as such -- `foo(1, 2)` -- is a function call


### 2022-03-24
- Theme: new design built around breaking the problem into smaller parts

- Use our own token class
    - decouple from Pygments
    - carry the data we think is important
    - divide tokens into types for our purposes, not Pygments' purposes
    - start by translating Pygments' output into a stream of our tokens
    - later, could replace that with our own lexer if desired

- `Query` class (or maybe `Statement`?) to wrap a whole statement's worth of tokens
    - not directly though, break them into clauses
    - give `Query` and each `FooClause` class a `.render()` method
        - a `Query` renders by concatenating the output of all its clauses' rendered output
        - a clause renders by laying out its tokens, this can work because any given clause can be laid out (relative to the left margin) without knowledge of the details of any other clause
    - instances of `Query` might be nested, e.g. inline views, scalar subqueries
        - this works because nested queries can be rendered without knowledge of their nesting context
        - outer query rendering just needs to keep track of the margin

- take more care with comments
    - current state of `formatter.py` gets line comments wrong somehow (at least that's what I remember from the last time I used it on real, gnarly queries found in the wild)
    - Pygments returns line comments as a unit, from the comment marker through the terminating newline, e.g. "--this is a comment\n", which is exactly what we want
    - whitespace (or anything, really) can be added _to the left_ of the comment marker, but nothing inside the comment can be re-arranged
    - in theory, line comments can be re-ordered with respect to other tokens, but we probably shouldn't!!

    - not quite clear what to do with block comments, probably reproduce them exactly as they're input, maybe ok to bump their left margin

- expressions
    - default behavior should be to _refrain_ from reformatting expressions
    - take each element of the `select` clause, place it after its comma with the proper left margin, but otherwise leave it alone

    - advantage 1: less work!
    - advantage 2: preserves hand-formatting of odd cases, and gives flexiblity to do different layouts of `case` etc.

    - can later add a CLI flag to enable expression formatting, and maybe an additional one for a simple each-expression-on-one-line mode

- token types
    - fewer are needed than previously thought
    - there's no practical difference between an identifier, quoted identifier, function name, string literal, numeric literal, or operator: these are all just strings that need to be printed exactly as they are
        - I guess there's _some_ difference in that identifiers, functions, and word-operators (and, or, not, etc.) are not typically case-sensitive and could be coerced to lower or upper case as per preference
        - whereas quoted identifiers, string literals, and comments cannot be manipulated at all
        - even still, lower/upper-casing could be done earlier, at the token assembly step, which would re-simplify and let us treat *all* of these things simply as "words"
        - arguably, even punctuation can be treated this way, e.g. ">=" is just a word that happens to be made of non-alphanum characters, but follows the same rules

- random notes
    - Pygments supports escaped literals (E'Bob\'s') and unicode-escaped identifiers (U&"d\0061t\+000061") but doesn't support hex literals (x'FF'), binary literals (B'1001'), or unicode-escaped literals (U&'...'), see https://www.postgresql.org/docs/current/sql-syntax-lexical.html#SQL-SYNTAX-CONSTANTS, and https://github.com/pygments/pygments/blob/master/pygments/lexers/sql.py (search for Affix), might be worth submitting a PR?
        - actually it looks like they're trying to support U&'...' but it didn't work when I tested it

    - since we're rendering each clause separately and concatenating the results, it's OK if one clause has broken syntax

    - optionally run as a simple web service on a local port, which would give a clear place to print warnings and debug messages (like "likely syntax error at ...")

    - upon reflection, collapsing quoted and/or qualified identifiers into a single token isn't _exactly_ necessary, since for the time being our expression formatter is "pass it through", and in other cases where we might encounter an identifier, like `from "foo"."bar"`, we can just print out what we're given, maybe replacing newlines with spaces or other light tweaks
        - it doesn't _hurt_ though and it's mostly written already
        - also helps find syntax errors in `from` clause

    - `from` is a bit tricky...
        - (in any case, a `from` item can be a paren-wrapped subquery, which would be handled recursively)
        - SQL-92 is `from foo, bar, baz`, or `from foo a, bar b, baz c`, or `from foo as a, bar as b, baz as c`, or any mix of those
        - SQL-99 is `from foo join bar on(...) join baz on (...)`, or aliased variants as above. Also `join` might be `inner join`, `left join`, `left outer join`, `right join`, `right outer join`, `cross join`, `natural join` (ugh), or `lateral join`, all of which can be mixed. Also `on` could be `using`, and these can be mixed.
        - Can 92 and 99 be mixed?!?! Like `from foo, bar join baz on (...)` or `from foo join bar on(...), baz`?
            - even if this is invalid syntax we may want to best-effort support it so users get a readable result
        - upon encountering a syntax error, it may be best to render the part that makes sense and spit out the rest either as-input or on-one-line, and log a warning

### 2022-04-17
- An idea I'd had earlier but not written down is for `render()` to take an argument, called "margin" or "bump" or something like that, which indicates how far from the zero left margin to move its output over.
    - I wasn't sure whether the margin argument should apply to _all_ lines emitted or just "lines after the first"
    - After writing a couple of clauses, I'm leaning towards 1) this argument is a good idea and 2) it should apply to "lines after the first"
    - As a clause renderer moves through its contents adding lines, there's a very easy place/time to add additional spaces
    - The difficulty may actually be on the _calling_ side... For example if a `SelectClause` is rendering and somewhere in one of its expressions is a scalar subquery, you would call `subquery.render(margin=M)` but what is M? Either something needs to keep track of the current X position of the (virtual) cursor, or just before calling a lower-level `render()` method you would need to somehow measure the distance back to the margin.

### 2022-05-01
- After writing SelectClause, WhereClause, and FromClause, I'm now realizing there's a common pattern that probably allows all or most clauses to derive from a common base, or even just be instances of a single class. The insight is that a query is laid out in two columns separated by a space, with "delimiters" on the left and "expressions" on the right:
```
select x.foo
     , y.bar
     , x.foo / y.bar as RATIO
  from blergh x
  join flerb y on(x.id = y.blergh_id)
 where 1=1 
   and y.bar > 0

^^^^^^----------- "delimiters"

       ^^^^^^---- "expressions"

      ^---------- separating column of spaces
```
    - Some caveats:
        - what I'm calling "delimiters" obviously aren't _literally_ delimiters, except for the basic comma used in `select`/`group by`/`order by`... `join` and `and` are only _metaphorically_ delimiters, but it works for our purposes here
        - similarly what I'm calling "expressions" includes many things that are not
            - a SELECT clause "expression" includes its alias, if any
            - a FROM clause "expression" includes identifiers, subqueries, `on`/`using`, etc
            - WHERE clause expressions actually are (sub-)expressions though
        - the column of spaces shifts over a little for `group by`/`order by`, and isn't well-behaved at all for FROM clause delimiters other than straight `join`
        - the SELECT clause has an optional qualifier -- ALL, DISTINCT, or DISTINCT ON(...) -- which goes between the first "delimiter" (`select`) and the first "expression"
            - GROUP BY may have a similar behavior with `rollup`/`cube` but that's pretty rare
    - All that varies amongst the different clauses is
        - the clause-beginning keyword, which is also the first delimiter
        - the set of tokens that can act as a delimiter
        - the amount of left padding: most clauses are padded to 6 but `group by`/`order by` are padded to 8
    - This would _drastically_ reduce the amount of layout code within the current design
    - One oddball is the WITH clause, which though it follows the pattern of having a sequence of "delimiters" (`with` and comma) and a sequence of "expressions", they are not laid out in the usual two-column fashion. This clause may require its own implementation.
    - The LIMIT and OFFSET clauses are a special case where there is only ever one delimiter and one expression
        - turns out limit/offset can also be written offset/limit... that's way more annoying that it sounds, and my implementation of it is gross, but probably good enough

### 2022-05-29
- SFToken, Expression, and Statement now all provide `is_whitespace`, `starts_with_whitespace()`, and `render()`, which adds some flexibility around what can be placed where. It's honestly a little hard to keep track of without type information, but whatever. It may make sense to define one or more mixin classes, or an abstract base class, to make the terms of the interface(s) clearer.
- A question around paren-wrapped subqueries is whether the parens should be part of the Statement or not.
    - logically they should be because they are "part" of that syntactic element and need to be carried with it
    - but Statement requires that `select` be the first token, so it would need to be re-worked a bit
    - layout-wise, it _may_ be easier to get the parens in the right spot if they're _not_ part of the Statement... hard to say for sure though until I actually implement margin bumping
    
### 2022-06-19
- Re-thinking how "indent" works a bit...
    - General principle is we don't want to mess with the formatting of expressions, so as to preserve any hand-formatting that's been done. So far I've taken that to mean not interfering *at all* with newlines and spacing within expressions. But implementing "indent" to support bumping over subqueries has accidentally introduced some of that interference. But it's made me question if maybe we _do_ want to interfere in a limited way.
    - Consider this input:
```
select foo
     , case when a > 1
then true
else false end
     , bar
```
        - The "then" and "else" lines are horribly misplaced, but our current approach won't touch them. That's _sort of_ ok, because the user can fix them once and then it'll stick. But we can probably do better with a simple rule...
        - Expressions that span more than one line must be indented to *at least* the alignment gutter.
        - Applying that rule to this example would yield:
```
select foo
     , case when a > 1
       then true
       else false end
     , bar
```
        - Not perfect, but obviously better!
    - Implementation strategy for this would be something like...
        - while rendering an Expression...
        - immediately after a newline...
        - if the next token isn't a SPACES (or NEWLINE?) token, insert spaces out to the gutter ("gutter" hasn't been reified up to this point, should it now be?)
        - if the next token *is* SPACES, check if it's _enough_ spaces to get to or beyond the gutter
            - if so, render it and continue as normal
            - if not, add additional spaces to get to the gutter

### 2022-06-26
- Line comments currently cause a bug where an extra newline gets added. This is because the line comment token itself has a newline in it, e.g. "--comment\n". Ordinarily when we build an Expression we call trim_trailing_whitespace() on the input tokens, which strips away any newlines at the end of the token list. But this doesn't touch the newline that's embedded in a line comment, so when we render, the line comment is printed with its newline, and then we add another one. Two potential strategies...
    - trim_trailing_whitespace() could be modified so that when the last token is a line comment, the embedded newline is removed
        - in theory this is safe since the rendering process adds the newlines back in
        - its still icky though because we're tampering with a comment
    - when rendering, we could keep track of cases when an Expression (or anything in expression position) ended with a newline, and if so then suppress adding our own
        - seems safer
        - but also kinda lame? idk there's an annoying statefulness to it
