select foo
     , bar
     , baz
     , count(1)
  from table1
  join table2
       on(table1.id = table2.table1_id)
 where 1=1
   and foo > bar
 group by foo
        , bar
        , baz
