import pulp
from heuristics import rendre_elementaire

def pricing_problem(problem, pi):
    """
    Cherche la configuration de capteurs u qui maximise le coût réduit.
    Le coût réduit est : 1 - sum(pi_k pour k in u).
    Comme on veut que le coût réduit soit > 0, on cherche à minimiser
    le "poids" sum(pi_k pour k in u) de la configuration tout en couvrant 
    toutes les zones.
    
    C'est un problème classique de couverture d'ensemble (Set Cover)
    que l'on résout facilement via PLNE (Programme Linéaire en Nombres Entiers).
    """
    pricing = pulp.LpProblem("Pricing", pulp.LpMinimize)
    
    # Variables binaires : x_k = 1 si le capteur k est recruté, 0 sinon
    x = {k: pulp.LpVariable(f"x_{k}", cat=pulp.LpBinary) for k in range(problem.N)}
    
    # Objectif : minimiser le poids dual de la configuration
    pricing += pulp.lpSum(pi[k] * x[k] for k in range(problem.N))
    
    # Contraintes : chaque zone doit être couverte par au moins 1 capteur actif
    sensors_for_zone = [[] for _ in range(problem.M)]
    for k, zones in enumerate(problem.coverage):
        for z in zones:
            sensors_for_zone[z].append(k)
            
    for z in range(problem.M):
        pricing += pulp.lpSum(x[k] for k in sensors_for_zone[z]) >= 1, f"Cover_zone_{z}"
        
    # Résolution
    solver = pulp.getSolver("PULP_CBC_CMD", msg=False)
    pricing.solve(solver)
    
    # Si le solveur n'a pas pu résoudre
    if pricing.status != pulp.LpStatusOptimal:
        return None
        
    poids_total = pulp.value(pricing.objective)
    
    # Condition d'arrêt de la génération de colonnes : 
    # S'il n'y a plus aucune configuration avec un poids < 1 (coût réduit <= 0)
    # on a mathématiquement prouvé qu'on a atteint l'optimum absolu.
    if 1.0 - poids_total <= 1e-5:
        return None
        
    # Extraire les capteurs sélectionnés
    config = set()
    for k in range(problem.N):
        if pulp.value(x[k]) and pulp.value(x[k]) > 0.5:
            config.add(k)
            
    # La rendre rigoureusement élémentaire (enlever les superflus)
    return rendre_elementaire(config, problem)
