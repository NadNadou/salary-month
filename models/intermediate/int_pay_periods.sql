with months as (
    select unnest(generate_series(
        date '2025-11-01', date '2026-06-01', interval 1 month
    ))::date as month_start
),

month_ends as (
    select
        month_start,
        (month_start + interval 1 month - interval 1 day)::date as month_end
    from months
),

paydays as (
    select
        month_start,
        case dayofweek(month_end)
            when 6 then month_end - 1   -- saturday -> friday
            when 0 then month_end - 2   -- sunday   -> friday
            else month_end
        end as payday
    from month_ends
)

select
    strftime(month_start + interval 1 month, '%Y-%m') as salary_month,
    payday                                            as period_start,
    lead(payday) over (order by payday) - 1           as period_end
from paydays