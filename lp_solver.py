import pulp
from data import Problem
from heuristics import Config


def resoudre(problem, configs):
    """
    Construit et resout le programme lineaire :

      max   sum(t_u)
      s.c.  pour chaque capteur k : sum(t_u pour u contenant k) <= T_k
            t_u >= 0
    """
    # --- Creation du modele ---
    model = pulp.LpProblem("SensorScheduling", pulp.LpMaximize)

    # Une variable t_u par configuration (>= 0)
    t = {cfg: pulp.LpVariable(f"t_{i}", lowBound=0)
         for i, cfg in enumerate(configs)}

    # --- Objectif : maximiser la duree de vie totale ---
    model += pulp.lpSum(t[cfg] for cfg in configs)

    # --- Contraintes batterie : une par capteur ---
    for k in range(problem.N):
        configs_avec_k = [cfg for cfg in configs if k in cfg]
        if configs_avec_k:
            model += pulp.lpSum(t[cfg] for cfg in configs_avec_k) <= problem.lifetimes[k]

    # --- Resolution ---
    solver = pulp.getSolver("PULP_CBC_CMD", msg=False)
    model.solve(solver)

    return model, t


def afficher_solution(model, t, configs, problem):
    """Affiche la solution optimale de facon lisible."""
    statut = pulp.LpStatus[model.status]
    duree_vie = pulp.value(model.objective)

    print(f"Statut       : {statut}")
    print(f"Duree de vie : {duree_vie:.4f}")
    print()
    print("Planning d'activation :")
    for cfg in configs:
        valeur = pulp.value(t[cfg])
        if valeur > 1e-6:  # on n'affiche que les configs actives
            capteurs = sorted(k + 1 for k in cfg)
            print(f"  Capteurs {capteurs} -> actifs pendant {valeur:.4f} unites de temps")
