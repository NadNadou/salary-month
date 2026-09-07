"""Act 3: the agent reads the dbt model output and interprets it.

It receives rows that are already computed (fct_transactions_by_salary_month),
explains the calendar-month vs salary-month gap, flags anything unusual and
infers the payday rule. It computes nothing: the rule executes, the agent interprets.
"""

import argparse
import csv
import os
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

TODAY = "2026-04-07"  # simulated "today": first week of April
MODEL = "claude-sonnet-5"

PROMPT = """You are a financial analyst reviewing a personal-finance data model.
Answer in English, concisely, in three numbered sections. Do not recompute totals from the rows; reason from what is given.

1. EXPLAIN THE GAP — For April 2026, the calendar_month view and the salary_month view give different totals. Explain in plain language why, for someone who has never heard of a salary month.
2. FLAG THE UNUSUAL — Among transactions with salary_month = 2026-04, point out anything unusual compared with the other months (amount, timing, category). Say "nothing notable" if that is the honest answer.
3. INFER THE RULE — From the rows where is_salary is true, state the rule that most likely decides the payday. Give one candidate rule, your confidence, and predict the next payday after {today}.

Today is {today}.

## Data (one row per transaction, output of the dbt model)
{context}"""


def load_rows(csv_path, delimiter=";"):
    """Return the CSV rows as a list of dicts."""
    with open(csv_path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def rows_to_text(rows, keep=("date_op", "label", "category", "amount", "is_salary", "calendar_month", "salary_month")):
    """Keep only the useful columns and render them as tab-separated text."""
    header = "\t".join(keep)
    body = "\n".join("\t".join(str(r.get(k, "")) for k in keep) for r in rows)
    return f"{header}\n{body}"


def build_client():
    """Instantiate the Anthropic client from ANTHROPIC_API_KEY."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY missing: set it in .env")
    return anthropic.Anthropic(api_key=api_key)


def parse_args():
    parser = argparse.ArgumentParser(description="Interpret the salary-month model output.")
    parser.add_argument("csv_path", type=Path, help="path to the CSV to analyze")
    parser.add_argument("--delimiter", default=";", help="CSV delimiter (default: ;)")
    return parser.parse_args()


def main():
    load_dotenv(PROJECT_ROOT / ".env")
    args = parse_args()
    rows = load_rows(args.csv_path, args.delimiter)
    print(f"{len(rows)} rows loaded from {args.csv_path}")

    client = build_client()
    prompt = PROMPT.format(today=TODAY, context=rows_to_text(rows))
    resp = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "\n".join(block.text for block in resp.content if block.type == "text")

    # Each run is saved with a timestamp (not overwritten) so runs can be compared.
    if not text:
        raise SystemExit(f"Empty answer. stop_reason={resp.stop_reason}, blocks={[b.type for b in resp.content]}")
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = PROJECT_ROOT / "agent" / f"output-{stamp}.md"
    out.write_text(f"# Agent run {stamp} — {MODEL}\n\n{text}\n", encoding="utf-8")
    print(text)
    print(f"\n→ saved to {out.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()