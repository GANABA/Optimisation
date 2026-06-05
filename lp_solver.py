"""
Construction et résolution du programme linéaire avec PuLP.

Formulation (Deschinkel 2011, Cardei 2005) :
  max   Σ_u  t_u
  s.c.  Σ_u  a_{ku} · t_u ≤ T_k   ∀k  (contrainte batterie)
        t_u ≥ 0                    ∀u

Les variables sont les durées d'activation t_u de chaque configuration u.
Les contraintes sont une par capteur k.
"""

import pulp
from data import Problem
from heuristics import Config


class LPResult:
    """Résultat d'une résolution LP."""

    def __init__(self,
                 status: str,
                 lifetime: float,
                 schedule: dict[Config, float],
                 duals: dict[int, float]):
        self.status = status          # 'Optimal', 'Infeasible', ...
        self.lifetime = lifetime      # valeur de la fonction objectif
        self.schedule = schedule      # config → durée d'activation (t_u > 0)
        self.duals = duals            # capteur k → multiplicateur dual π_k

    def __repr__(self) -> str:
        active = {c: v for c, v in self.schedule.items() if v > 1e-9}
        return (f"LPResult(status={self.status!r}, "
                f"lifetime={self.lifetime:.4f}, "
                f"configs_actives={len(active)})")


def solve(problem: Problem, configs: list[Config]) -> LPResult:
    """
    Résout le LP sur l'ensemble de configurations fourni.

    Retourne un LPResult avec la durée de vie optimale, le planning
    et les multiplicateurs duaux (utiles pour la génération de colonnes).
    """
    if not configs:
        raise ValueError("La liste de configurations est vide.")

    model = pulp.LpProblem("SensorScheduling", pulp.LpMaximize)

    # Variables : t_u ≥ 0 pour chaque configuration u
    t = {
        cfg: pulp.LpVariable(f"t_{i}", lowBound=0)
        for i, cfg in enumerate(configs)
    }

    # Fonction objectif : maximiser la durée de vie totale
    model += pulp.lpSum(t[cfg] for cfg in configs)

    # Contraintes batterie : pour chaque capteur k, usage total ≤ T_k
    battery_constraints: dict[int, pulp.LpConstraint] = {}
    for k in range(problem.N):
        configs_using_k = [cfg for cfg in configs if k in cfg]
        if not configs_using_k:
            continue  # capteur k inutilisé : pas de contrainte nécessaire
        constraint = pulp.lpSum(t[cfg] for cfg in configs_using_k) <= problem.lifetimes[k]
        name = f"battery_{k}"
        model += constraint, name
        battery_constraints[k] = constraint

    # Résolution
    solver = pulp.getSolver("PULP_CBC_CMD", msg=False)
    model.solve(solver)

    status = pulp.LpStatus[model.status]
    lifetime = pulp.value(model.objective) or 0.0

    # Planning : t_u pour chaque configuration (on garde t_u > 0 uniquement)
    schedule = {cfg: pulp.value(t[cfg]) or 0.0 for cfg in configs}

    # Multiplicateurs duaux π_k (shadow prices des contraintes batterie)
    # Utiles pour la génération de colonnes
    duals: dict[int, float] = {}
    for k, constraint in battery_constraints.items():
        pi = constraint.pi  # multiplicateur dual de la contrainte k
        duals[k] = pi if pi is not None else 0.0

    return LPResult(status=status, lifetime=lifetime, schedule=schedule, duals=duals)


def print_solution(result: LPResult, problem: Problem) -> None:
    """Affiche la solution de façon lisible."""
    ub = problem.upper_bound()
    ratio = result.lifetime / ub * 100 if ub > 0 else 0

    print(f"Statut       : {result.status}")
    print(f"Durée de vie : {result.lifetime:.4f}")
    print(f"Borne sup.   : {ub:.4f}")
    print(f"Qualité      : {ratio:.1f}% de la borne supérieure")
    print(f"Configs actives ({sum(1 for v in result.schedule.values() if v > 1e-9)}) :")

    active = sorted(
        [(cfg, v) for cfg, v in result.schedule.items() if v > 1e-9],
        key=lambda x: -x[1]
    )
    for cfg, duration in active:
        capteurs = sorted(k + 1 for k in cfg)  # affichage 1-based
        print(f"  Capteurs {capteurs} -> actifs pendant {duration:.4f}")
