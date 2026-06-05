"""
Point d'entrée principal.

Usage :
  python main.py <fichier>              -- résout une instance (col. gen. mixte)
  python main.py <fichier> --compare    -- compare les 3 heuristiques
  python main.py --all                  -- résout toutes les instances connues
  python main.py <fichier> --verbose    -- affiche les itérations col. gen.
"""

import sys
import os
from data import load
from lp_solver import print_solution
from column_generation import column_generation
from analysis import compare_heuristics, run_all_instances

INSTANCES = [
    "fichier-exemple.txt",
    "moyen_test_2.txt",
    "moyen_test_3.txt",
    "gros_test_1.txt",
    "maxi_test_1.txt",
]


def main():
    args = sys.argv[1:]

    if not args or "--help" in args:
        print(__doc__)
        return

    if "--all" in args:
        paths = [f for f in INSTANCES if os.path.exists(f)]
        print(f"Résolution de {len(paths)} instances...\n")
        run_all_instances(paths, n_configs=30)
        return

    filepath = args[0]
    if not os.path.exists(filepath):
        print(f"Fichier introuvable : {filepath}")
        sys.exit(1)

    problem = load(filepath)
    print(f"Instance : {filepath}")
    print(f"  {problem.N} capteurs, {problem.M} zones")
    print(f"  Borne superieure : {problem.upper_bound():.4f}")
    print()

    if "--compare" in args:
        n_configs = 30
        print(f"Comparaison des heuristiques (pool={n_configs} configs, 5 runs)\n")
        compare_heuristics(problem, n_configs=n_configs)
        return

    verbose = "--verbose" in args
    method = "mixed"
    for a in args:
        if a in ("--exact", "--heuristic", "--mixed"):
            method = a.lstrip("-")

    print(f"Methode : generation de colonnes ({method})")
    print()

    result = column_generation(
        problem, n_initial=10, method=method, verbose=verbose, seed=42
    )
    print_solution(result, problem)


if __name__ == "__main__":
    main()
