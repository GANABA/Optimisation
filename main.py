import sys
import time
from data import load
from heuristics import generer_pool
from lp_solver import resoudre, afficher_solution

INSTANCES = [
    "fichier-exemple.txt",
    "moyen_test_2.txt",
    "moyen_test_3.txt",
    "gros_test_1.txt",
]


def resoudre_instance(fichier):
    """Resout une instance et retourne les resultats."""
    problem = load(fichier)
    pool = generer_pool(problem, n_configs=10, seed=42)

    debut = time.perf_counter()
    model, t = resoudre(problem, pool)
    duree = time.perf_counter() - debut

    import pulp
    duree_vie = pulp.value(model.objective) or 0.0
    statut = pulp.LpStatus[model.status]

    return problem, pool, model, t, duree_vie, duree, statut


def mode_instance(fichier):
    """Affiche le detail complet pour une instance."""
    problem, pool, model, t, duree_vie, duree, statut = resoudre_instance(fichier)

    print("=== Partie 1 : donnees ===")
    print(problem)

    print()
    print("=== Partie 2 : configurations elementaires ===")
    print(f"{len(pool)} configurations generees :")
    for i, cfg in enumerate(pool):
        capteurs = sorted(k + 1 for k in cfg)
        print(f"  u{i+1} = capteurs {capteurs}")

    print()
    print("=== Partie 3 : resolution du programme lineaire ===")
    afficher_solution(model, t, pool, problem)


def mode_all():
    """Partie 4 : tableau de resultats sur toutes les instances."""
    print("=== Partie 4 : experimentation ===")
    print()

    # En-tete du tableau
    print(f"{'Instance':<22} {'N':>5} {'M':>5} {'Configs':>8} {'Duree de vie':>14} {'Temps (s)':>10} {'Statut':>10}")
    print("-" * 78)

    for fichier in INSTANCES:
        try:
            problem, pool, model, t, duree_vie, duree, statut = resoudre_instance(fichier)
            nom = fichier.replace(".txt", "")
            print(f"{nom:<22} {problem.N:>5} {problem.M:>5} {len(pool):>8} {duree_vie:>14.4f} {duree:>10.3f} {statut:>10}")
        except FileNotFoundError:
            nom = fichier.replace(".txt", "")
            print(f"{nom:<22} {'fichier introuvable':>49}")


# --- Point d'entree ---

if len(sys.argv) < 2:
    print("Usage :")
    print("  python main.py <fichier.txt>   -- resout une instance")
    print("  python main.py --all           -- resout toutes les instances")
    sys.exit(1)

if sys.argv[1] == "--all":
    mode_all()
else:
    mode_instance(sys.argv[1])
