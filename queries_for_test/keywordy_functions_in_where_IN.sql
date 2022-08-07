select 1 from bar where 1=1 and substring(foo from 2 for 3) != 'xxx' and extract('year' from event_datetime) > 2000
