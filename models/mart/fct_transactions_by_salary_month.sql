select
    t.*,
    strftime(t.date_op, '%Y-%m') as calendar_month,
    p.salary_month,
    p.period_start,
    p.period_end
from {{ ref('stg_transactions') }} t
left join {{ ref('int_pay_periods') }} p
    on t.date_op between p.period_start and p.period_end