"""Exécution reproductible du simulateur MAC sans modifier simulation.py."""

import argparse

import numpy as np

import simulation


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("Une valeur entière positive est requise")
    return number


def positive_float(value):
    number = float(value)
    if not np.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("Une valeur strictement positive est requise")
    return number


def main():
    parser = argparse.ArgumentParser(description="Exemple reproductible de simulation MAC")
    parser.add_argument("--stations", type=positive_int, default=5, help="Nombre de stations N")
    parser.add_argument("--capacite", type=positive_int, default=10, help="Capacité de file K")
    parser.add_argument("--lambda-arrivee", type=positive_float, default=0.1, help="Taux d'arrivée par station")
    parser.add_argument("--tau", type=positive_float, default=1.0, help="Paramètre de backoff")
    parser.add_argument("--graine", type=int, default=2026, help="Graine aléatoire")
    parser.add_argument("--horizon", type=positive_int, default=3000, help="Horizon du simulateur")
    args = parser.parse_args()

    np.random.seed(args.graine)
    simulation.TEMPS_MAX = args.horizon
    debit_t, occupation_t, perte, debit_final = simulation.simulateur_mac(
        N=args.stations,
        K=args.capacite,
        lam=args.lambda_arrivee,
        tau=args.tau,
    )

    print(f"Paramètres : N={args.stations}, K={args.capacite}, lambda={args.lambda_arrivee}, "
          f"tau={args.tau}, graine={args.graine}, horizon={args.horizon}")
    print(f"Nombre de points historiques : {len(debit_t)}")
    print(f"Débit cumulé final : {debit_final:.6f} paquet(s)/unité de temps")
    print(f"Arrivées rejetées (file pleine) : {perte:.2%}")
    if occupation_t:
        print(f"Occupation moyenne historique : {occupation_t[-1][1]:.6f} paquet(s)")
    print("Résultats du modèle simulé, pas mesures d'un réseau physique.")


if __name__ == "__main__":
    main()
