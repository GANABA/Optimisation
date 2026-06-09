import sys
import time
import pulp

# Ajouter le dossier du projet au path
sys.path.append("/home/cbahouas/Desktop/IUT-NFC/BUT3/S6/R.O/RO_roject")
from data import load
from heuristics import generer_pool
from lp_solver import resoudre

def run_stress_test():
    fichier = "/home/cbahouas/Desktop/IUT-NFC/BUT3/S6/R.O/RO_roject/maxi_test_1.txt"
    problem = load(fichier)
    
    n_configs = 50000
    print(f"--- STRESS TEST sur maxi_test_1.txt ---")
    print(f"Borne Supérieure : {problem.upper_bound():.1f}")
    
    print(f"\nGénération de {n_configs} configurations aléatoires...")
    debut_gen = time.perf_counter()
    pool = generer_pool(problem, n_configs=n_configs, seed=42, heuristique="aleatoire")
    temps_gen = time.perf_counter() - debut_gen
    print(f"{len(pool)} configurations distinctes générées en {temps_gen:.2f} secondes.")
    
    print("\nRésolution du Programme Linéaire (Maître Restreint) avec PuLP...")
    debut_sol = time.perf_counter()
    model, t = resoudre(problem, pool)
    temps_sol = time.perf_counter() - debut_sol
    
    lt = pulp.value(model.objective) or 0.0
    pct = (lt / problem.upper_bound()) * 100
    
    print(f"Résolution terminée en {temps_sol:.2f} secondes.")
    print(f"\n=> Durée de vie optimale trouvée : {lt:.2f} ({pct:.2f}% de la borne)")
    print("=> Conclusion : Le temps explose ou la mémoire sature, mais on reste très loin de l'optimum !")

if __name__ == '__main__':
    run_stress_test()