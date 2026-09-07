# Build notes — salary-month

Friction log, kept in the open. One entry per surprise.

## 2026-09-07 — the answer was not in position 0
Assumed `resp.content[0]` was the text. It was a thinking block. Filter by `block.type == "text"` instead.
Lesson: never assume the order of an unordered result — that applies to LLM output too.

## 2026-09-07 — empty answer
Got a file with a header and nothing else. `max_tokens` was eaten by reasoning before the model wrote its answer. Raised it and added a guard that fails loudly.

## 2026-09-07 — the agent misread a date, then explained it away
Run 1: the agent found the right rule (last business day) and the right prediction (April 30),
but stated the December salary landed on the 29th. The seed says the 31st. Instead of flagging
uncertainty, it invented a reason ("year-end payroll processing") to keep its rule at 3/4 fit.
A rule in SQL cannot do this. It fails loudly or it is right. Confidence was reported at 70%.

## 2026-09-07 — leading zeros lost
account_num "00000000000" became 0: dbt seed inferred an integer. Identifiers are strings.
Fix: column_types in dbt_project.yml. Test case for #2.

## 2026-09-07 — run 2: correct on everything
Same data, same prompt. Run 1 misread a date and rationalised it (70% confidence).
Run 2 read all four dates correctly (85% confidence). Both predicted April 30.
Interpretation was stable and useful across both runs (nothing notable, partial month).
Rule inference was not. Give the agent computed facts, not raw rows to count.