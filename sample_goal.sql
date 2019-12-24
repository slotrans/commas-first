select x.foo
     , x.bar
     , x.whatever as "Double Quoted Alias"
     , greatest(x.baz, x.blip) as BUILTIN_FUNCTION
     , my_udf(x.baz) as SCALAR_UDF
     , (x.baz + x.blip)::int as PG_STYLE_CAST
     , x.baz::int as ANOTHER_CAST
     , percentile_cont(0.99) within group(order by reponse_time) as WITHIN_GROUP_FUNCTION
  from (
        select foo
             , bar
             , baz
             , blip
             , dense_rank(foo) over(order by bar) as A_WINDOW_FUNCTION
          from my_cool_table --line comment
/*from
    a_lame_view  block comment */
         where foo >= bar
           and (blip is not null or baz != 0)
           and foo != 'string literal'
       ) x
 where 1=1
 order by x.foo
; 