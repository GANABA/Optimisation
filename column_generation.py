"""
Génération de colonnes pour le problème MLCP (Deschinkel 2011).

Principe :
  1. Résoudre le LP sur un pool initial de configurations (Problème Maître Restreint)
  2. Chercher une configuration "attractive" via le problème auxiliaire :
       min  Σ_k  π_k · y_k
       s.c. Σ_{k couvrant z}  y_k >= 1   pour toute zone z
            y_k ∈ {0, 1}
     Si le coût réduit r = 1 - Σ_k π_k·y*_k > 0, la config améliore le LP.
  3. Ajouter la config au pool et recommencer.
  4. S'arrêter quand aucune config attractive n'existe : la solution est optimale.

Le problème auxiliaire est résolu de deux façons :
  - Exacte  : MIP via PuLP/CBC (garantit l'optimalité)
  - Heuristique : greedy sur les coûts duaux (rapide, quasi-optimal en pratique)
"""

import pulp
from data import Problem
from heuristics import Config, make_elementary, generate_pool
from lp_solver import solve, LPResult


# ---------------------------------------------------------------------------
# Problème auxiliaire — version exacte (MIP)
# ---------------------------------------------------------------------------

def _aux_exact(problem: Problem, duals: dict[int, float]) -> tuple[Config | None, float]:
    """
    Résout le problème auxiliaire à l'optimalité par branch-and-bound.
    Retourne (config, coût_réduit) ou (None, ≤0) si aucune config attractive.
    """
    model = pulp.LpProblem("Auxiliary", pulp.LpMinimize)
    y = [pulp.LpVariable(f"y_{k}", cat="Binary") for k in range(problem.N)]

    # Objectif : minimiser le coût dual total
    model += pulp.lpSum(duals.get(k, 0.0) * y[k] for k in range(problem.N))

    # Contraintes : chaque zone doit être couverte
    for z in range(problem.M):
        covering = problem.sensors_of[z]
        if not covering:
            return None, 0.0  # zone impossible à couvrir
        model += pulp.lpSum(y[k] for k in covering) >= 1

    solver = pulp.getSolver("PULP_CBC_CMD", msg=False)
    model.solve(solver)

    if pulp.LpStatus[model.status] != "Optimal":
        return None, 0.0

    cost = pulp.value(model.objective) or 0.0
    reduced_cost = 1.0 - cost

    if reduced_cost <= 1e-8:
        return None, reduced_cost  # pas de config attractive

    selected = frozenset(k for k in range(problem.N) if pulp.value(y[k]) > 0.5)
    config = make_elementary(set(selected), problem)
    return config, reduced_cost


# ---------------------------------------------------------------------------
# Problème auxiliaire — version heuristique
# ---------------------------------------------------------------------------

def _aux_heuristic(problem: Problem, duals: dict[int, float],
                   n_tries: int = 20) -> tuple[Config | None, float]:
    """
    Résout le problème auxiliaire par une heuristique gloutonne :
    pour chaque zone non couverte, choisir le capteur de coût dual minimal.
    Plusieurs tentatives avec ordres de zones mélangés.

    Beaucoup plus rapide que la version exacte, quasi-optimal en pratique.
    """
    import random

    best_config: Config | None = None
    best_rc = -float("inf")

    for _ in range(n_tries):
        zones = list(range(problem.M))
        random.shuffle(zones)
        selected: set[int] = set()
        covered: set[int] = set()

        for z in zones:
            if z in covered:
                continue
            candidates = list(problem.sensors_of[z] - selected)
            if not candidates:
                selected = set()
                break
            # Choisir le capteur de coût dual minimal parmi ceux disponibles
            best_k = min(candidates, key=lambda k: duals.get(k, 0.0))
            selected.add(best_k)
            covered |= problem.coverage[best_k]

        if not selected or len(covered) < problem.M:
            continue

        config = make_elementary(selected, problem)
        cost = sum(duals.get(k, 0.0) for k in config)
        rc = 1.0 - cost

        if rc > best_rc:
            best_rc = rc
            best_config = config

    if best_rc <= 1e-8:
        return None, best_rc
    return best_config, best_rc


# ---------------------------------------------------------------------------
# Boucle principale de génération de colonnes
# ---------------------------------------------------------------------------

def column_generation(problem: Problem,
                      n_initial: int = 10,
                      method: str = "heuristic",
                      max_iter: int = 500,
                      seed: int | None = None,
                      verbose: bool = False) -> LPResult:
    """
    Résout le MLCP par génération de colonnes.

    method : 'exact'     — problème auxiliaire résolu à l'optimalité (lent)
             'heuristic' — problème auxiliaire résolu par heuristique (rapide)
             'mixed'     — heuristique d'abord, exact si elle échoue

    Retourne le LPResult optimal (ou quasi-optimal pour method='heuristic').
    """
    import random
    if seed is not None:
        random.seed(seed)

    # Initialisation : pool de départ
    pool: list[Config] = generate_pool(problem, n_configs=n_initial, seed=seed)
    if not pool:
        raise ValueError("Impossible de générer des configurations initiales.")

    pool_set: set[Config] = set(pool)

    for iteration in range(max_iter):
        # Résoudre le LP restreint
        result = solve(problem, list(pool_set))

        if result.status != "Optimal":
            break

        # Chercher une config attractive via le problème auxiliaire
        if method == "exact":
            new_cfg, rc = _aux_exact(problem, result.duals)
        elif method == "heuristic":
            new_cfg, rc = _aux_heuristic(problem, result.duals)
        else:  # mixed
            new_cfg, rc = _aux_heuristic(problem, result.duals)
            if new_cfg is None:
                new_cfg, rc = _aux_exact(problem, result.duals)

        if verbose:
            print(f"  iter {iteration:3d} | lifetime={result.lifetime:.4f} "
                  f"| pool={len(pool_set)} | rc={rc:.6f}")

        if new_cfg is None or new_cfg in pool_set:
            # Aucune config attractive : solution optimale atteinte
            break

        pool_set.add(new_cfg)

    # Résolution finale sur le pool complet
    return solve(problem, list(pool_set))
