"""Pay calendar: the salary lands on the last business day of the month.

Deliberately without public holidays: only Saturday and Sunday are excluded.
Stdlib only.
"""

import calendar
from datetime import date, timedelta

SATURDAY = 5


def last_business_day(year, month):
    """Last day of the month that is neither a Saturday nor a Sunday."""
    day = calendar.monthrange(year, month)[1]
    current = date(year, month, day)
    while current.weekday() >= SATURDAY:
        current -= timedelta(days=1)
    return current


def main():
    months = [(2025, 12)] + [(2026, m) for m in range(1, 7)]
    for year, month in months:
        pay_date = last_business_day(year, month)
        print(
            "{:04d}-{:02d} -> {} ({})".format(
                year, month, pay_date.isoformat(), calendar.day_name[pay_date.weekday()]
            )
        )


if __name__ == "__main__":
    main()
