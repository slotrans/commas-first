select foo from bar where 1=1 and id in (select bar_id from bar_baz_map where 1=1)
