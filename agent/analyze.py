"""Squelette de l'agent d'analyse.

Charge la configuration (.env), lit un CSV passé en argument et prépare le
client Anthropic. Aucun prompt ni appel API à ce stade.
"""

import argparse
import csv
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_rows(csv_path, delimiter=";"):
    """Retourne les lignes du CSV sous forme de dictionnaires."""
    with open(csv_path, encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def build_client():
    """Instancie le client Anthropic à partir de ANTHROPIC_API_KEY."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit("ANTHROPIC_API_KEY manquant : renseignez-le dans .env")
    return anthropic.Anthropic(api_key=api_key)


def parse_args():
    parser = argparse.ArgumentParser(description="Analyse un export de transactions.")
    parser.add_argument("csv_path", type=Path, help="chemin du CSV à analyser")
    parser.add_argument("--delimiter", default=";", help="séparateur du CSV (défaut : ;)")
    return parser.parse_args()


def main():
    load_dotenv(PROJECT_ROOT / ".env")
    args = parse_args()
    rows = load_rows(args.csv_path, args.delimiter)
    client = build_client()
    # TODO : construire le prompt et appeler l'API à partir de `rows` et `client`.
    print("{} lignes chargées depuis {}".format(len(rows), args.csv_path))


if __name__ == "__main__":
    main()
