import sys
import time
import pulp

from data import load
from heuristics import generer_pool
from lp_solver import resoudre, get_duals, afficher_solution
from column_generation import pricing_problem

MAX_ITER = 500


def solve_column_generation(fichier):
    problem = load(fichier)
    print(f"=== Resolution V2 par Generation de Colonnes : {fichier} ===")
    print(f"Reseau : N={problem.N} capteurs, M={problem.M} zones")
    print(f"Borne Superieure Theorique : {problem.upper_bound():.1f}")

    debut = time.perf_counter()

    print("\n[Etape 1] Generation du pool initial (30 configurations aleatoires)...")
    pool = generer_pool(problem, n_configs=30, seed=42, heuristique="aleatoire")
    pool_set = set(pool)
    print(f"Pool initial genere : {len(pool)} configurations distinctes.")

    print("\n[Etape 2] Lancement de l'algorithme exact...")
    iteration = 1

    while iteration <= MAX_ITER:
        # A. Resoudre le Programme Maitre
        model, t_vars = resoudre(problem, pool)
        lt_actuelle = pulp.value(model.objective) or 0.0

        # B. Extraire les prix duaux
        pi = get_duals(model, problem)

        # C. Pricing : trouver la configuration a cout reduit positif
        new_config = pricing_problem(problem, pi)

        # Condition d'arret : plus aucune colonne ameliorante
        if new_config is None or new_config in pool_set:
            break

        pool.append(new_config)
        pool_set.add(new_config)

        if iteration % 5 == 0:
            print(f"  Iteration {iteration:3} | Pool : {len(pool):4} configs | Duree de vie : {lt_actuelle:.2f}")

        iteration += 1

    else:
        print(f"  Arret apres {MAX_ITER} iterations (limite atteinte).")

    temps_total = time.perf_counter() - debut

    # Resultat final
    model, t_vars = resoudre(problem, pool)
    lt_finale = pulp.value(model.objective) or 0.0
    ub = problem.upper_bound()
    pct = (lt_finale / ub) * 100 if ub > 0 else 0.0

    print(f"\nOK : Algorithme termine en {iteration} iterations ({temps_total:.2f} secondes).")
    print(f"  Pool final : {len(pool)} configurations.")
    print(f"  Duree de vie optimale prouvee : {lt_finale:.4f} ({pct:.2f}% de la borne superieure)")
    print()
    afficher_solution(model, t_vars, pool, problem)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python main_v2.py <fichier.txt>")
        sys.exit(1)

    solve_column_generation(sys.argv[1])
