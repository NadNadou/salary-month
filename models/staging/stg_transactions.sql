select
    cast(dateOp as date)               as date_op,
    cast(dateVal as date)              as date_val,
    label,
    suggestedLabel                     as suggested_label,
    category,
    categoryParent                     as category_parent,
    cast(amount as decimal(10, 2))     as amount,
    accountNum                         as account_num,
    accountLabel                       as account_label,
    cast(accountbalance as decimal(10, 2)) as account_balance,
    category = 'Salaire'               as is_salary
from {{ ref('transactions') }}