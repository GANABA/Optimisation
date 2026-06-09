import sys
import time
import pulp
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

N_CONFIGS = 30


def resoudre_instance(fichier, heuristique="greedy"):
    """Resout une instance et retourne les resultats."""
    problem = load(fichier)
    pool = generer_pool(problem, n_configs=N_CONFIGS, seed=42, heuristique=heuristique)

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
    print(f"Borne superieure theorique : {problem.upper_bound():.4f}")

    print()
    print("=== Partie 2 : configurations elementaires ===")
    print(f"{len(pool)} configurations generees :")
    for i, cfg in enumerate(pool[:5]):
        capteurs = sorted(k + 1 for k in cfg)
        print(f"  u{i+1} = capteurs {capteurs}")
    if len(pool) > 5:
        print(f"  ... et {len(pool) - 5} autres configurations")

    print()
    print("=== Partie 3 : resolution du programme lineaire ===")
    afficher_solution(model, t, pool, problem)


def mode_all():
    """Partie 4 : tableau de resultats sur toutes les instances."""
    print("=== Partie 4 : experimentation ===")
    print()

    # En-tete du tableau
    print(f"{'Instance':<22} {'N':>5} {'M':>5} {'Borne':>8} {'Cfgs':>5} {'Greedy':>14} {'HEF':>14} {'Aleatoire':>14} {'Temps (s)':>10} {'Statut':>10}")
    print("-" * 116)

    for fichier in INSTANCES:
        try:
            problem = load(fichier)
            nom = fichier.replace(".txt", "")
            
            res = {}
            temps_total = 0.0
            statut_final = "Inconnu"
            ub = problem.upper_bound()
            nb_cfgs_set = set()

            for h in ["greedy", "hef", "aleatoire"]:
                pool = generer_pool(problem, n_configs=N_CONFIGS, seed=42, heuristique=h)
                nb_cfgs_set.add(len(pool))
                if not pool:
                    res[h] = "0.0"
                    continue
                debut = time.perf_counter()
                model, _ = resoudre(problem, pool)
                temps_total += (time.perf_counter() - debut)
                
                lt = pulp.value(model.objective) or 0.0
                pct = int((lt / ub) * 100) if ub > 0 else 0
                res[h] = f"{lt:.1f} ({pct}%)"
                
                statut_final = pulp.LpStatus[model.status]
                
            cfgs_str = "/".join(map(str, sorted(nb_cfgs_set)))
            print(f"{nom:<22} {problem.N:>5} {problem.M:>5} {ub:>8.1f} {cfgs_str:>5} {res['greedy']:>14} {res['hef']:>14} {res['aleatoire']:>14} {temps_total:>10.3f} {statut_final:>10}")
        except FileNotFoundError:
            nom = fichier.replace(".txt", "")
            print(f"{nom:<22} {'fichier introuvable':>49}")


# --- Point d'entree ---

if len(sys.argv) < 2:
    print("Usage :")
    print("  python main.py <fichier.txt> [greedy|hef|aleatoire]")
    print("  python main.py --all")
    print("  python main.py --plot <fichier.txt>")
    sys.exit(1)

if sys.argv[1] == "--all":
    mode_all()
elif sys.argv[1] == "--plot":
    fichier = sys.argv[2] if len(sys.argv) > 2 else "moyen_test_2.txt"
    problem = load(fichier)
    nom = fichier.replace(".txt", "")
    from analyse import plot_heuristics
    plot_heuristics(problem, nom)
else:
    heuristique = sys.argv[2] if len(sys.argv) > 2 else "greedy"
    mode_instance(sys.argv[1], heuristique)
