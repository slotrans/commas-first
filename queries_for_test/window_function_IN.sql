select foo, lead(foo, 1) over(order by event_datetime) as NEXT_FOO from bar where 1=1
