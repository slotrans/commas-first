select x.foo
     , current_date
     , 111
  from (select y.foo
             , current_timestamp
             , 222
          from (select foo
                     , random()
                     , 333
                  from bar
                 where 1=1
                   and foo is not null
               ) y
         where 1=1
           and y.foo > 0
       ) x
 where 1=1
   and mod(x.foo, 2) = 0
