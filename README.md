# Commas First
Format SQL my way instead of the wrong way everyone else does it

I'm working on a long explanation of why this does what it does, and why conventional approaches to formatting SQL are misguided and ineffective. In the meantime I'll let the output speak for itself.

```
$ cat my_ugly_query.sql | python formatter2.py

# use --trim-leading-whitespace when converting trailing to leading commas

# use --compact-expressions to get VERY ugly SQL to a decent starting point
```
