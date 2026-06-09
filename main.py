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
    "maxi_test_1.txt"
]


def resoudre_instance(fichier, heuristique="greedy"):
    """Resout une instance et retourne les resultats."""
    problem = load(fichier)
    pool = generer_pool(problem, n_configs=100, seed=42, heuristique=heuristique)

    debut = time.perf_counter()
    model, t = resoudre(problem, pool)
    duree = time.perf_counter() - debut

    import pulp
    duree_vie = pulp.value(model.objective) or 0.0
    statut = pulp.LpStatus[model.status]

    return problem, pool, model, t, duree_vie, duree, statut


def mode_instance(fichier, heuristique="greedy"):
    """Affiche le detail complet pour une instance."""
    problem, pool, model, t, duree_vie, duree, statut = resoudre_instance(fichier, heuristique)

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
    print(f"{'Instance':<22} {'N':>5} {'M':>5} {'Greedy':>12} {'HEF':>12} {'Aleatoire':>12} {'Temps (s)':>10} {'Statut':>10}")
    print("-" * 95)

    for fichier in INSTANCES:
        try:
            problem = load(fichier)
            nom = fichier.replace(".txt", "")
            
            res = {}
            temps_total = 0.0
            statut_final = "Inconnu"
            import time
            
            for h in ["greedy", "hef", "aleatoire"]:
                import pulp
                pool = generer_pool(problem, n_configs=100, seed=42, heuristique=h)
                if not pool:
                    res[h] = 0.0
                    continue
                debut = time.perf_counter()
                model, _ = resoudre(problem, pool)
                temps_total += (time.perf_counter() - debut)
                res[h] = pulp.value(model.objective) or 0.0
                statut_final = pulp.LpStatus[model.status]
                
            print(f"{nom:<22} {problem.N:>5} {problem.M:>5} {res['greedy']:>12.4f} {res['hef']:>12.4f} {res['aleatoire']:>12.4f} {temps_total:>10.3f} {statut_final:>10}")
        except FileNotFoundError:
            nom = fichier.replace(".txt", "")
            print(f"{nom:<22} {'fichier introuvable':>49}")


# --- Point d'entree ---

if len(sys.argv) < 2:
    print("Usage :")
    print("  python main.py <fichier.txt> [greedy|hef|aleatoire]")
    print("  python main.py --all")
    sys.exit(1)

if sys.argv[1] == "--all":
    mode_all()
else:
    heuristique = sys.argv[2] if len(sys.argv) > 2 else "greedy"
    mode_instance(sys.argv[1], heuristique)
