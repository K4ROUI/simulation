"""Expériences reproductibles selon lambda ; export des résultats calculés.

Ne modifie pas le moteur historique de simulation.py.
"""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import simulation


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("Une valeur entière positive est requise")
    return number


def main():
    parser = argparse.ArgumentParser(description="Variations du débit et des pertes selon lambda")
    parser.add_argument("--graine", type=int, default=2026)
    parser.add_argument("--repetitions", type=positive_int, default=5)
    parser.add_argument("--horizon", type=positive_int, default=3000)
    parser.add_argument("--sortie", type=Path, default=Path("resultats"))
    args = parser.parse_args()

    # Même paramètres pour chaque lambda, sauf la charge. Les graines sont explicites.
    simulation.TEMPS_MAX = args.horizon
    args.sortie.mkdir(parents=True, exist_ok=True)
    charges = np.linspace(0.05, 0.6, 10)
    lignes = []
    for numero, taux in enumerate(charges):
        debits, pertes = [], []
        for essai in range(args.repetitions):
            np.random.seed(args.graine + numero * args.repetitions + essai)
            _, _, perte, debit = simulation.simulateur_mac(
                N=5, K=10, lam=float(taux), tau=1.0
            )
            debits.append(debit)
            pertes.append(perte)
        lignes.append({
            "lambda": float(taux),
            "replications": args.repetitions,
            "debit_moyen": float(np.mean(debits)),
            "debit_ecart_type": float(np.std(debits, ddof=1)) if len(debits) > 1 else 0.0,
            "perte_moyenne": float(np.mean(pertes)),
            "perte_ecart_type": float(np.std(pertes, ddof=1)) if len(pertes) > 1 else 0.0,
        })

    csv_path = args.sortie / "experiences_lambda.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(lignes[0]))
        writer.writeheader()
        writer.writerows(lignes)

    for key, label, fichier in [
        ("debit_moyen", "Débit cumulé moyen simulé", "debit_vs_lambda.png"),
        ("perte_moyenne", "Proportion de nouvelles arrivées rejetées", "perte_vs_lambda.png"),
    ]:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot([r["lambda"] for r in lignes], [r[key] for r in lignes], marker="o")
        ax.set_xlabel("Taux d'arrivée λ par station")
        ax.set_ylabel(label)
        ax.set_title(f"Simulation MAC · N=5, K=10, τ=1 · {args.repetitions} répétitions")
        ax.grid(True)
        fig.tight_layout()
        fig.savefig(args.sortie / fichier, dpi=150)
        plt.close(fig)

    print(f"{len(charges) * args.repetitions} exécutions réalisées.")
    print(f"Résultats : {csv_path} et deux figures PNG dans {args.sortie}")
    print("Ces résultats sont des simulations reproductibles, non des mesures réseau.")


if __name__ == "__main__":
    main()
