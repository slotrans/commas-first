select x.foo, x.bar, 
        x.whatever as "Double Quoted Alias",
       greatest(x.baz, x.blip) as BUILTIN_FUNCTION,
    my_udf(x.baz) as SCALAR_UDF,
       (x.baz + x.blip)::int as PG_STYLE_CAST,
         x.baz::int as ANOTHER_CAST,
       ( x.blip :: int ) as CAST_IN_PARENS,

       percentile_cont(0.99) within group(order by reponse_time) as WITHIN_GROUP_FUNCTION,
(select max(created)
from some_other_table) as Correlated_Subquery
from (
    select foo, bar,
      baz,
       blip,
       dense_rank(foo) over(order by bar) as A_WINDOW_FUNCTION
    from 
        my_cool_table --line comment
    /*from
        a_lame_view  block comment */
    where
        foo >= bar and
        (blip is not null or baz != 0)
      and foo != 'string literal'
) x
join another_table y 
  on x.foo=y.foo and y.flerb is not null
where 1 = 1
and   x.baz is not null
 and (x.baz > 0 
      or x.blip > 0 
      or x.baz < 0)
and x.whatever in (select s.whatever from source_of_whatever s where 1=1 and s.whatever is not null)
order by x.foo; 
