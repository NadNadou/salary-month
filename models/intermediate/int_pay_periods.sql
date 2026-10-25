with months as (
    select unnest(generate_series(
        date '{{ var("first_month", "2025-11-01") }}',
        date '{{ var("last_month", "2026-06-01") }}',
        interval 1 month
    ))::date as month_start
),

month_ends as (
    select
        month_start,
        (month_start + interval 1 month - interval 1 day)::date as month_end
    from months
),

paydays as (
    -- last day of the month that is neither a weekend nor a holiday
    select
        m.month_start,
        max(d.day)::date as payday
    from month_ends m,
        unnest(generate_series(m.month_end - 6, m.month_end, interval 1 day)) as d(day)
    where dayofweek(d.day) not in (0, 6)   -- 0 = sunday, 6 = saturday
      and d.day::date not in (select holiday_date from {{ ref('holidays') }})
    group by m.month_start
)

select
    strftime(month_start + interval 1 month, '%Y-%m') as salary_month,
    payday                                            as period_start,
    lead(payday) over (order by payday) - 1           as period_end
from paydays