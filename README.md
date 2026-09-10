# salary-month

A salary paid on the last business day of the month lands in the wrong month
of every calendar-based dashboard. This repo fixes that with one dbt rule,
then asks an LLM what it makes of the result.

Built in public, one iteration per month. Synthetic data only.

## The problem

April 7, 2026. Calendar view of April: five expenses, zero income, −1,137 €.
The salary of March 31 is filed in March.

Same transactions, salary-month view: +1,642 €. Nothing in the data changed.

## The rule

1. Payday = last business day of the month (weekends excluded, holidays ignored for now)
2. Period = from payday to the day before the next payday
3. Each transaction joins the period it falls in

The rule is generated from the calendar, not inferred from the data:
a period exists even if its payday is not in the seed.

## How it's built

seeds/transactions.csv synthetic bank export, 63 rows, Dec 2025 → Apr 7 2026
scripts/pay_calendar.py the rule in Python (prototype, 20 lines)
models/staging/stg_transactions types, is_salary
models/intermediate/int_pay_periods the rule in SQL, one row per salary month
models/mart/fct_transactions_by_salary_month each row gets its salary_month
agent/analyze.py LLM reads the fact table, computes nothing



Stack: dbt-core, dbt-duckdb, DuckDB, Python 3.12, Anthropic API.

## Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/generate_transactions.py
dbt seed --profiles-dir . && dbt run --profiles-dir .
dbt show --profiles-dir . --inline "select salary_month, sum(amount) from {{ ref('fct_transactions_by_salary_month') }} group by 1 order by 1"
```

Agent (optional): copy `.env.example` to `.env`, add your key, then

```bash
python3 -c "import duckdb; duckdb.connect('salary_month.duckdb', read_only=True).sql(\"copy (select * from fct_transactions_by_salary_month order by date_op) to 'agent/fct.csv' (header, delimiter ';')\")"
python3 agent/analyze.py agent/fct.csv
```

## What the agent did

Two runs, same data, same prompt. Both explained the gap and found nothing
unusual. One read the December payday as the 29th and gave a plausible reason.
The seed says the 31st.

The rule executes. The agent interprets.

## Series

- Sep 2026 — the rule (this)
- Oct 2026 — unit tests: weekends, holidays, missing payday
- Nov 2026 — observability with Elementary
- Dec 2026 — wrap-up

See `NOTES.md` for the friction log.