import sys
from data import load
from heuristics import generer_pool
from lp_solver import resoudre, afficher_solution

if len(sys.argv) < 2:
    print("Usage : python main.py <fichier.txt>")
    sys.exit(1)

fichier = sys.argv[1]
problem = load(fichier)

print("=== Partie 1 : donnees ===")
print(problem)

print()
print("=== Partie 2 : configurations elementaires ===")
pool = generer_pool(problem, n_configs=10, seed=42)
print(f"{len(pool)} configurations generees :")
for i, cfg in enumerate(pool):
    capteurs = sorted(k + 1 for k in cfg)
    print(f"  u{i+1} = capteurs {capteurs}")

print()
print("=== Partie 3 : resolution du programme lineaire ===")
model, t = resoudre(problem, pool)
afficher_solution(model, t, pool, problem)
