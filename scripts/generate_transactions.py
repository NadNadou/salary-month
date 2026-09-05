"""Génère seeds/transactions.csv : un export bancaire français fictif.

Période couverte : 2025-12-29 -> 2026-04-07, un seul compte courant.
Les données sont entièrement synthétiques (aucune donnée personnelle réelle).
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "seeds" / "transactions.csv"

COLUMNS = [
    "dateOp",
    "dateVal",
    "label",
    "tags",
    "suggestedLabel",
    "category",
    "categoryParent",
    "amount",
    "comment",
    "accountNum",
    "accountLabel",
    "accountbalance",
    "mark",
]

ACCOUNT_NUM = "00000000000"
ACCOUNT_LABEL = "COMPTE COURANT"
OPENING_BALANCE = 1200.00

START_DATE = date(2025, 12, 29)
END_DATE = date(2026, 4, 7)

SALARY_DATES = [date(2025, 12, 31), date(2026, 1, 30), date(2026, 2, 27), date(2026, 3, 31)]
SALARY_AMOUNT = 2800.00

# Prélèvements récurrents : (jour du mois, label, libellé lisible, montant, category, categoryParent)
RECURRING = [
    (5, "PRLV SEPA LOYER", "Loyer", -950.00, "Loyer", "Logement"),
    (7, "PRLV SEPA TotalEnergies", "TotalEnergies", -68.00, "Energie", "Logement"),
    (15, "PRLV SEPA FREE MOBILE", "Free Mobile", -19.99, "Télécom", "Abonnements"),
]

# Commerçants ponctuels : (enseigne, libellé lisible, category, categoryParent, min, max)
MERCHANTS = [
    ("CARREFOUR", "Carrefour", "Alimentation", "Vie quotidienne", -95.00, -18.00),
    ("MONOPRIX", "Monoprix", "Alimentation", "Vie quotidienne", -72.00, -12.00),
    ("FRANPRIX", "Franprix", "Alimentation", "Vie quotidienne", -48.00, -8.00),
    ("BOULANGERIE DU COIN", "Boulangerie du Coin", "Alimentation", "Vie quotidienne", -14.00, -4.50),
    ("LE BISTROT", "Le Bistrot", "Restaurants, bars", "Loisirs et sorties", -52.00, -16.00),
    ("PIZZERIA ROMA", "Pizzeria Roma", "Restaurants, bars", "Loisirs et sorties", -38.00, -11.00),
    ("CAFE DES SPORTS", "Café des Sports", "Restaurants, bars", "Loisirs et sorties", -19.00, -4.50),
    ("NAVIGO", "Navigo", "Transports en commun", "Transports", -88.80, -30.00),
    ("SNCF CONNECT", "SNCF Connect", "Train", "Transports", -95.00, -22.00),
    ("VELIB", "Vélib", "Transports en commun", "Transports", -12.00, -4.50),
    ("CINEMA LE REX", "Cinéma Le Rex", "Loisirs", "Loisirs et sorties", -32.00, -9.00),
    ("LIBRAIRIE CENTRALE", "Librairie Centrale", "Loisirs", "Loisirs et sorties", -55.00, -7.00),
    ("SALLE DE SPORT", "Salle de Sport", "Sport", "Loisirs et sorties", -49.00, -25.00),
]


def daterange(start, end):
    """Toutes les dates de start à end inclus."""
    days = (end - start).days
    return [start + timedelta(days=i) for i in range(days + 1)]


def make_transaction(day, label, suggested, amount, category, parent, is_card):
    return {
        "dateOp": day,
        "dateVal": day,
        "label": label,
        "suggestedLabel": suggested,
        "category": category,
        "categoryParent": parent,
        "amount": round(amount, 2),
        "is_card": is_card,
    }


def make_card_expense(rng, day):
    """Une dépense carte ponctuelle, montant tiré dans la fourchette du commerçant."""
    name, suggested, category, parent, low, high = rng.choice(MERCHANTS)
    amount = rng.uniform(low, high)
    label = "CARTE {} {}".format(day.strftime("%d/%m/%y"), name)
    return make_transaction(day, label, suggested, amount, category, parent, True)


def pick_days(rng, days, count):
    """Tire count jours parmi days (avec remise : plusieurs achats le même jour)."""
    return [rng.choice(days) for _ in range(count)]


def build_transactions(rng):
    transactions = []

    # Salaires : les seules opérations positives.
    for day in SALARY_DATES:
        transactions.append(
            make_transaction(
                day,
                "VIR SEPA SALAIRE ACME SAS",
                "Salaire ACME SAS",
                SALARY_AMOUNT,
                "Salaire",
                "Revenus",
                False,
            )
        )

    # Prélèvements récurrents, uniquement ceux qui tombent dans la période.
    for month_day, label, suggested, amount, category, parent in RECURRING:
        for year, month in [(2026, 1), (2026, 2), (2026, 3), (2026, 4)]:
            day = date(year, month, month_day)
            if START_DATE <= day <= END_DATE:
                transactions.append(
                    make_transaction(day, label, suggested, amount, category, parent, False)
                )

    expenses = [t for t in transactions if t["amount"] < 0]

    # Fin décembre : au moins 2 dépenses sur les deux premiers jours de la période.
    december_window = daterange(START_DATE, date(2025, 12, 30))
    for day in pick_days(rng, december_window, rng.randint(2, 3)):
        transactions.append(make_card_expense(rng, day))

    # Fenêtres de fin de mois : au moins 3 dépenses du 28 au 31.
    for year, month, last_day in [(2026, 1, 31), (2026, 2, 28), (2026, 3, 31)]:
        window = daterange(date(year, month, 28), date(year, month, last_day))
        already = sum(1 for t in expenses if t["dateOp"] in window)
        target = rng.randint(3, 4)
        for day in pick_days(rng, window, max(0, target - already)):
            transactions.append(make_card_expense(rng, day))

    # Début avril : 5 à 7 dépenses entre le 1er et le 7 (loyer et énergie compris).
    april_window = daterange(date(2026, 4, 1), END_DATE)
    april_already = sum(1 for t in transactions if t["amount"] < 0 and t["dateOp"] in april_window)
    april_target = rng.randint(5, 7)
    for day in pick_days(rng, april_window, max(0, april_target - april_already)):
        transactions.append(make_card_expense(rng, day))

    # Complément réparti sur le reste de la période pour atteindre 55 à 65 dépenses.
    filler_days = daterange(START_DATE, date(2026, 3, 31))
    total_target = rng.randint(55, 65)
    current = sum(1 for t in transactions if t["amount"] < 0)
    for day in pick_days(rng, filler_days, max(0, total_target - current)):
        transactions.append(make_card_expense(rng, day))

    # Exactement 5 opérations carte dont la date de valeur est décalée de 1 ou 2 jours.
    card_transactions = [t for t in transactions if t["is_card"]]
    for transaction in rng.sample(card_transactions, 5):
        transaction["dateVal"] = transaction["dateOp"] + timedelta(days=rng.randint(1, 2))

    transactions.sort(key=lambda t: t["dateOp"])
    return transactions


def write_csv(transactions, path):
    balance_cents = int(round(OPENING_BALANCE * 100))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=";", lineterminator="\n")
        writer.writerow(COLUMNS)
        for transaction in transactions:
            balance_cents += int(round(transaction["amount"] * 100))
            writer.writerow(
                [
                    transaction["dateOp"].isoformat(),
                    transaction["dateVal"].isoformat(),
                    transaction["label"],
                    "",
                    transaction["suggestedLabel"],
                    transaction["category"],
                    transaction["categoryParent"],
                    "{:.2f}".format(transaction["amount"]),
                    "",
                    ACCOUNT_NUM,
                    ACCOUNT_LABEL,
                    "{:.2f}".format(balance_cents / 100),
                    "",
                ]
            )


def main():
    random.seed(42)
    rng = random
    transactions = build_transactions(rng)
    write_csv(transactions, OUTPUT_PATH)
    expenses = sum(1 for t in transactions if t["amount"] < 0)
    print(
        "{} lignes écrites dans {} ({} dépenses, {} salaires)".format(
            len(transactions),
            OUTPUT_PATH.relative_to(PROJECT_ROOT),
            expenses,
            len(transactions) - expenses,
        )
    )


if __name__ == "__main__":
    main()
