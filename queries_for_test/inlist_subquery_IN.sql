select foo, id in (select bar_id from baz where 1=1) as INLIST_SUBQUERY from bar where 1=1
