import sys
import time
import pulp

from data import load
from heuristics import generer_pool
from lp_solver import resoudre, get_duals
from column_generation import pricing_problem

def solve_column_generation(fichier):
    problem = load(fichier)
    print(f"=== Résolution V2 par Génération de Colonnes : {fichier} ===")
    print(f"Réseau : N={problem.N} capteurs, M={problem.M} zones")
    print(f"Borne Supérieure Théorique : {problem.upper_bound():.1f}")
    
    debut = time.perf_counter()
    
    # 1. Initialisation : créer un tout petit pool de configurations au hasard
    # (Pas besoin de 50 000 comme dans le stress test !)
    print("\n[Etape 1] Génération du pool initial (30 configurations aléatoires)...")
    pool = generer_pool(problem, n_configs=30, seed=42, heuristique="aleatoire")
    print(f"Pool initial généré : {len(pool)} configurations distinctes.")
    
    # 2. La grande boucle "Magique" de la Génération de Colonnes
    print("\n[Etape 2] Lancement de l'algorithme exact...")
    iteration = 1
    
    while True:
        # A. Résoudre le Programme Maître (Restreint aux configs actuelles)
        model, t_vars = resoudre(problem, pool)
        lt_actuelle = pulp.value(model.objective) or 0.0
        
        # B. Extraire la "connaissance" du Maître sous forme de prix duaux (pi)
        pi = get_duals(model, problem)
        
        # C. Confier ces informations au "Pricing" pour qu'il invente 
        #    exactement la configuration qui nous manque
        new_config = pricing_problem(problem, pi)
        
        # Condition d'arrêt
        if new_config is None or new_config in pool:
            break
            
        pool.append(new_config)
        
        if iteration % 10 == 0:
            print(f"  Itération {iteration:3} | Taille du pool : {len(pool):4} | Durée de vie : {lt_actuelle:.2f}")
            
        iteration += 1
        
    temps_total = time.perf_counter() - debut
    
    # 3. Résultat Final Prouvé
    model, t_vars = resoudre(problem, pool)
    lt_finale = pulp.value(model.objective) or 0.0
    pct = (lt_finale / problem.upper_bound()) * 100
    
    print(f"\n✅ Algorithme terminé en {iteration} itérations ({temps_total:.2f} secondes).")
    print(f"=> Le solveur n'a eu besoin que de {len(pool)} configurations générées intelligemment.")
    print(f"=> Durée de vie OPTIMALE ABSOLUE prouvée : {lt_finale:.2f} ({pct:.2f}% de la borne)")
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python main_v2.py <fichier.txt>")
        sys.exit(1)
        
    solve_column_generation(sys.argv[1])
