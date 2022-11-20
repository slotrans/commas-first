import pytest

from pathlib import Path

import sf_flags
from formatter2 import do_format


# pytest magic
def setup_module():
    sf_flags.reset_to_defaults()


class QueriesForTest:
    def get_ids(self):
        return [name for name, queries in self.__dict__.items()]

    def get_inputs(self):
        return [queries["input"].rstrip("\n") for name, queries in self.__dict__.items()]

    def get_outputs__default(self):
        return [queries["default"].rstrip("\n") for name, queries in self.__dict__.items()]

    def get_outputs__trim_leading_whitespace(self):
        return [queries["trim_leading_whitespace"].rstrip("\n") for name, queries in self.__dict__.items()]

    def get_outputs__compact_expressions(self):
        return [queries["compact_expressions"].rstrip("\n") for name, queries in self.__dict__.items()]


qft = QueriesForTest()


qft.cte_with_typescript_string_templating = dict(
input="""\
with cte1 as (select 1 from bar where 1=1)
, cte2 as (${blergh})
, cte3 as (select 2 from baz where 1=1)
select foo from table1 where 1=1
""",

default="""\
with cte1 as
(
    select 1
      from bar
     where 1=1
)
, cte2 as
(
    ${blergh}
)
, cte3 as
(
    select 2
      from baz
     where 1=1
)
select foo
  from table1
 where 1=1
""",

trim_leading_whitespace="""\
with cte1 as
(
    select 1
      from bar
     where 1=1
)
, cte2 as
(
    ${blergh}
)
, cte3 as
(
    select 2
      from baz
     where 1=1
)
select foo
  from table1
 where 1=1
""",

compact_expressions="""\
with cte1 as
(
    select 1
      from bar
     where 1=1
)
, cte2 as
(
    ${blergh}
)
, cte3 as
(
    select 2
      from baz
     where 1=1
)
select foo
  from table1
 where 1=1
""",
)

qft.limit_offset = dict(
input="""\
select foo from table1 where 1=1 order by foo limit 9 offset 0
""",

default="""\
select foo
  from table1
 where 1=1
 order by foo
 limit 9
offset 0
""",

trim_leading_whitespace="""\
select foo
  from table1
 where 1=1
 order by foo
 limit 9
offset 0
""",

compact_expressions="""\
select foo
  from table1
 where 1=1
 order by foo
 limit 9
offset 0
""",
)

qft.nested_inline_views = dict(
input="""\
select x.foo, current_date, 111
from (
    select y.foo, current_timestamp, 222
    from (
        select foo, random(), 333
        from bar
        where 1=1
        and foo is not null
    ) y
    where 1=1 and y.foo > 0
) x
where 1=1 and mod(x.foo, 2) = 0
""",

default="""\
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
""",

trim_leading_whitespace="""\
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
""",

compact_expressions="""\
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
""",
)

qft.select_from_join = dict(
input="""\
select foo, bar, baz from table1 join table2 on(table1.id = table2.table1_id)
""",

default="""\
select foo
     , bar
     , baz
  from table1
  join table2 on(table1.id = table2.table1_id)
""",

trim_leading_whitespace="""\
select foo
     , bar
     , baz
  from table1
  join table2 on(table1.id = table2.table1_id)
""",

compact_expressions="""\
select foo
     , bar
     , baz
  from table1
  join table2 on(table1.id = table2.table1_id)
""",
)

qft.scalar_subquery = dict(
input="""\
select foo, (select 1 from baz where 1=1) as SCALAR_SUBQUERY from bar where 1=1
""",

default="""\
select foo
     , (select 1
          from baz
         where 1=1
       ) as SCALAR_SUBQUERY
  from bar
 where 1=1
""",

trim_leading_whitespace="""\
select foo
     , (select 1
          from baz
         where 1=1
       ) as SCALAR_SUBQUERY
  from bar
 where 1=1
""",

compact_expressions="""\
select foo
     , (select 1
          from baz
         where 1=1
       ) as SCALAR_SUBQUERY
  from bar
 where 1=1
""",
)

qft.trivial_cte = dict(
input="""\
with cte1 as (select 1 from bar where 1=1) select foo from table1 where 1=1
""",

default="""\
with cte1 as
(
    select 1
      from bar
     where 1=1
)
select foo
  from table1
 where 1=1
""",

trim_leading_whitespace="""\
with cte1 as
(
    select 1
      from bar
     where 1=1
)
select foo
  from table1
 where 1=1
""",

compact_expressions="""\
with cte1 as
(
    select 1
      from bar
     where 1=1
)
select foo
  from table1
 where 1=1
""",
)

qft.trailing_commas = dict(
input="""\
select
    foo,
    bar,
    baz,
    count(1)
from
    table1
join
    table2
    on(table1.id = table2.table1_id)
where 1=1
    and foo > bar
group by
    foo,
    bar,
    baz
""",

default="""\
select
       foo
     ,
       bar
     ,
       baz
     ,
       count(1)
  from
       table1
  join
       table2
       on(table1.id = table2.table1_id)
 where 1=1
   and foo > bar
 group by
          foo
        ,
          bar
        ,
          baz
""",

trim_leading_whitespace="""\
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
""",

compact_expressions="""\
select foo
     , bar
     , baz
     , count(1)
  from table1
  join table2 on(table1.id = table2.table1_id)
 where 1=1
   and foo > bar
 group by foo
        , bar
        , baz
""",
)

qft.union_all = dict(
input="""\
select foo from table1 where 1=1 union all select foo from table2 where 1=1
""",

default="""\
select foo
  from table1
 where 1=1
union all
select foo
  from table2
 where 1=1
""",

trim_leading_whitespace="""\
select foo
  from table1
 where 1=1
union all
select foo
  from table2
 where 1=1
""",

compact_expressions="""\
select foo
  from table1
 where 1=1
union all
select foo
  from table2
 where 1=1
""",
)

qft.window_function = dict(
input="""\
select foo, lead(foo, 1) over(order by event_datetime) as NEXT_FOO from bar where 1=1
""",

default="""\
select foo
     , lead(foo, 1) over(order by event_datetime) as NEXT_FOO
  from bar
 where 1=1
""",

trim_leading_whitespace="""\
select foo
     , lead(foo, 1) over(order by event_datetime) as NEXT_FOO
  from bar
 where 1=1
""",

compact_expressions="""\
select foo
     , lead(foo, 1) over(order by event_datetime) as NEXT_FOO
  from bar
 where 1=1
""",
)

qft.leading_line_comment = dict(
input="""\
--comment
select foo from bar where 1=1
""",

default="""\
--comment
select foo
  from bar
 where 1=1
""",

trim_leading_whitespace="""\
--comment
select foo
  from bar
 where 1=1
""",

compact_expressions="""\
--comment
select foo
  from bar
 where 1=1
""",
)

qft.inline_view = dict(
input="""\
select x.foo from (select foo from bar where 1=1) x where 1=1
""",

default="""\
select x.foo
  from (select foo
          from bar
         where 1=1
       ) x
 where 1=1
""",

trim_leading_whitespace="""\
select x.foo
  from (select foo
          from bar
         where 1=1
       ) x
 where 1=1
""",

compact_expressions="""\
select x.foo
  from (select foo
          from bar
         where 1=1
       ) x
 where 1=1
""",
)

qft.keywordy_functions_in_where = dict(
input="""\
select 1 from bar where 1=1 and substring(foo from 2 for 3) != 'xxx' and extract('year' from event_datetime) > 2000
""",

default="""\
select 1
  from bar
 where 1=1
   and substring(foo from 2 for 3) != 'xxx'
   and extract('year' from event_datetime) > 2000
""",

trim_leading_whitespace="""\
select 1
  from bar
 where 1=1
   and substring(foo from 2 for 3) != 'xxx'
   and extract('year' from event_datetime) > 2000
""",

compact_expressions="""\
select 1
  from bar
 where 1=1
   and substring(foo from 2 for 3) != 'xxx'
   and extract('year' from event_datetime) > 2000
""",
)

qft.leading_block_comment = dict(
input="""\
/* comment */
select foo from bar where 1=1
""",

default="""\
/* comment */
select foo
  from bar
 where 1=1
""",

trim_leading_whitespace="""\
/* comment */
select foo
  from bar
 where 1=1
""",

compact_expressions="""\
/* comment */
select foo
  from bar
 where 1=1
""",
)

qft.inlist_subquery = dict(
input="""\
select foo, id in (select bar_id from baz where 1=1) as INLIST_SUBQUERY from bar where 1=1
""",

default="""\
select foo
     , id in (select bar_id
                from baz
               where 1=1
             ) as INLIST_SUBQUERY
  from bar
 where 1=1
""",

trim_leading_whitespace="""\
select foo
     , id in (select bar_id
                from baz
               where 1=1
             ) as INLIST_SUBQUERY
  from bar
 where 1=1
""",

compact_expressions="""\
select foo
     , id in (select bar_id
                from baz
               where 1=1
             ) as INLIST_SUBQUERY
  from bar
 where 1=1
""",
)

qft.subquery_in_where = dict(
input="""\
select foo from bar where 1=1 and id in (select bar_id from bar_baz_map where 1=1)
""",

default="""\
select foo
  from bar
 where 1=1
   and id in (select bar_id
                from bar_baz_map
               where 1=1
             )
""",

trim_leading_whitespace="""\
select foo
  from bar
 where 1=1
   and id in (select bar_id
                from bar_baz_map
               where 1=1
             )
""",

compact_expressions="""\
select foo
  from bar
 where 1=1
   and id in (select bar_id
                from bar_baz_map
               where 1=1
             )
""",
)

qft.inlist_in_where = dict(
input="""\
select foo from bar where 1=1
and id in
(1, 2, 3,
4, 5, 6)
""",

# not exactly desirable...
default="""\
select foo
  from bar
 where 1=1
   and id in
       (1, 2, 3,
       4, 5, 6)
""",

# same...
trim_leading_whitespace="""\
select foo
  from bar
 where 1=1
   and id in
       (1, 2, 3,
       4, 5, 6)
""",

compact_expressions="""\
select foo
  from bar
 where 1=1
   and id in (1, 2, 3, 4, 5, 6)
""",
)

qft.inlist_in_where_preformatted = dict(
input="""\
select foo
  from bar
 where 1=1
   and id in ( 1
             , 2
             , 3
             )
""",

# not exactly desirable...
default="""\
select foo
  from bar
 where 1=1
   and id in ( 1
             , 2
             , 3
             )
""",

# same...
trim_leading_whitespace="""\
select foo
  from bar
 where 1=1
   and id in ( 1
             , 2
             , 3
             )
""",

compact_expressions="""\
select foo
  from bar
 where 1=1
   and id in (1, 2, 3)
""",
)

qft.simple_grouped_count = dict(
input="""\
select foo, count(1) from bar where 1=1 group by foo
""",

default="""\
select foo
     , count(1)
  from bar
 where 1=1
 group by foo
""",

trim_leading_whitespace="""\
select foo
     , count(1)
  from bar
 where 1=1
 group by foo
""",

compact_expressions="""\
select foo
     , count(1)
  from bar
 where 1=1
 group by foo
""",
)


@pytest.mark.parametrize(
    "test_input,expected_output",
    zip(qft.get_inputs(), qft.get_outputs__default()),
    ids=qft.get_ids()
)
def test_do_format__default(test_input, expected_output):
    sf_flags.TRIM_LEADING_WHITESPACE = False
    sf_flags.COMPACT_EXPRESSIONS = False
    actual_output = do_format(test_input)
    print(actual_output)
    #print(actual_output.replace(" ", "⦁"))
    assert expected_output == actual_output


@pytest.mark.parametrize(
    "test_input,expected_output",
    zip(qft.get_inputs(), qft.get_outputs__trim_leading_whitespace()),
    ids=qft.get_ids()
)
def test_do_format__trim_leading_whitespace(test_input, expected_output):
    sf_flags.TRIM_LEADING_WHITESPACE = True
    sf_flags.COMPACT_EXPRESSIONS = False
    actual_output = do_format(test_input)
    print(actual_output)
    #print(actual_output.replace(" ", "⦁"))
    assert expected_output == actual_output


@pytest.mark.parametrize(
    "test_input,expected_output",
    zip(qft.get_inputs(), qft.get_outputs__compact_expressions()),
    ids=qft.get_ids()
)
def test_do_format__compact_expressions(test_input, expected_output):
    sf_flags.TRIM_LEADING_WHITESPACE = True
    sf_flags.COMPACT_EXPRESSIONS = True
    actual_output = do_format(test_input)
    print(actual_output)
    #print(actual_output.replace(" ", "⦁"))
    assert expected_output == actual_output
