select foo, (select 1 from baz where 1=1) as SCALAR_SUBQUERY from bar where 1=1
