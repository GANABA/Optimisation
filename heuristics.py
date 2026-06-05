"""
Génération de configurations élémentaires (cover sets minimaux).

Une configuration élémentaire est un ensemble de capteurs qui :
  1. Couvre toutes les zones
  2. Est minimal : retirer n'importe quel capteur laisse une zone découverte

Trois heuristiques implémentées :
  A. greedy_critical_target  — priorité aux zones couvertes par peu de capteurs (Cardei 2005)
  B. greedy_high_energy      — priorité aux capteurs à plus haute énergie résiduelle (HEF, Manju & Pujari 2011)
  C. random_cover            — sélection aléatoire (Deschinkel 2011)

Dans les trois cas, make_elementary() retire ensuite les capteurs superflus.
"""

import random
from data import Problem

Config = frozenset[int]  # ensemble d'indices de capteurs (0-indexed)


# ---------------------------------------------------------------------------
# Étape de minimalisation — commune aux trois heuristiques
# ---------------------------------------------------------------------------

def make_elementary(config: set[int], problem: Problem) -> Config:
    """
    Rend une configuration minimale en retirant les capteurs superflus.
    Un capteur k est superflu si les autres capteurs de la config
    couvrent encore toutes les zones.
    L'ordre de retrait est aléatoire pour diversifier les configs produites.
    """
    sensors = list(config)
    random.shuffle(sensors)
    current = set(config)

    for k in sensors:
        current.remove(k)
        covered = set().union(*(problem.coverage[s] for s in current))
        if len(covered) < problem.M:
            current.add(k)  # k est indispensable, on le remet

    return frozenset(current)


# ---------------------------------------------------------------------------
# Heuristique A — Greedy Cible Critique (Cardei et al., 2005)
# ---------------------------------------------------------------------------

def greedy_critical_target(problem: Problem,
                           lifetimes_remaining: list[float] | None = None) -> Config | None:
    """
    Construit une configuration en couvrant en priorité les zones les plus
    critiques (couvertes par le moins de capteurs encore utilisables).

    lifetimes_remaining : durées de vie résiduelles (si None, utilise problem.lifetimes).
    Retourne None si aucune configuration valide n'est possible.
    """
    remaining = lifetimes_remaining if lifetimes_remaining is not None else problem.lifetimes
    active = {k for k in range(problem.N) if remaining[k] > 0}

    uncovered = set(range(problem.M))
    selected: set[int] = set()

    while uncovered:
        # Zones encore accessibles depuis les capteurs actifs non encore sélectionnés
        reachable_zones = set()
        for k in active - selected:
            reachable_zones |= problem.coverage[k] & uncovered

        if not reachable_zones:
            return None  # impossible de couvrir toutes les zones

        # Zone critique : celle couverte par le moins de capteurs actifs disponibles
        def zone_score(z: int) -> int:
            return sum(1 for k in active - selected if z in problem.coverage[k])

        critical_zone = min(reachable_zones, key=zone_score)

        # Parmi les capteurs couvrant cette zone critique, choisir celui qui
        # couvre le plus de zones non encore couvertes
        candidates = [k for k in active - selected if critical_zone in problem.coverage[k]]
        best = max(candidates, key=lambda k: len(problem.coverage[k] & uncovered))

        selected.add(best)
        uncovered -= problem.coverage[best]

    return make_elementary(selected, problem)


# ---------------------------------------------------------------------------
# Heuristique B — High Energy First / HEF (Manju & Pujari, 2011)
# ---------------------------------------------------------------------------

def greedy_high_energy(problem: Problem,
                       lifetimes_remaining: list[float] | None = None) -> Config | None:
    """
    Construit une configuration en sélectionnant à chaque étape le capteur
    avec la plus haute énergie résiduelle qui couvre au moins une zone non couverte.

    Retourne None si aucune configuration valide n'est possible.
    """
    remaining = lifetimes_remaining if lifetimes_remaining is not None else problem.lifetimes
    active = {k for k in range(problem.N) if remaining[k] > 0}

    uncovered = set(range(problem.M))
    selected: set[int] = set()

    while uncovered:
        # Capteurs actifs non sélectionnés couvrant encore au moins une zone non couverte
        candidates = [k for k in active - selected
                      if problem.coverage[k] & uncovered]

        if not candidates:
            return None  # impossible de couvrir toutes les zones

        # Priorité : énergie résiduelle maximale
        # En cas d'égalité : nombre de zones non couvertes couvertes (pour diversifier)
        best = max(candidates,
                   key=lambda k: (remaining[k], len(problem.coverage[k] & uncovered)))

        selected.add(best)
        uncovered -= problem.coverage[best]

    return make_elementary(selected, problem)


# ---------------------------------------------------------------------------
# Heuristique C — Aléatoire + minimalisation (Deschinkel, 2011)
# ---------------------------------------------------------------------------

def random_cover(problem: Problem,
                 lifetimes_remaining: list[float] | None = None) -> Config | None:
    """
    Génère une configuration en couvrant les zones dans un ordre aléatoire
    avec un capteur aléatoire parmi ceux disponibles.

    Retourne None si aucune configuration valide n'est possible.
    """
    remaining = lifetimes_remaining if lifetimes_remaining is not None else problem.lifetimes
    active = {k for k in range(problem.N) if remaining[k] > 0}

    uncovered = list(range(problem.M))
    random.shuffle(uncovered)
    selected: set[int] = set()

    for z in uncovered:
        if z in set().union(*(problem.coverage[k] for k in selected)):
            continue  # zone déjà couverte

        candidates = [k for k in active - selected if z in problem.coverage[k]]
        if not candidates:
            return None

        selected.add(random.choice(candidates))

    return make_elementary(selected, problem)


# ---------------------------------------------------------------------------
# Génération d'un pool de configurations
# ---------------------------------------------------------------------------

def generate_pool(problem: Problem,
                  n_configs: int = 30,
                  seed: int | None = None) -> list[Config]:
    """
    Génère un pool de configurations élémentaires en alternant les trois
    heuristiques. Les doublons sont éliminés.

    n_configs : nombre cible de configurations distinctes.
    """
    if seed is not None:
        random.seed(seed)

    heuristics = [greedy_critical_target, greedy_high_energy, random_cover]
    pool: set[Config] = set()
    max_attempts = n_configs * 20  # éviter la boucle infinie si peu de configs existent

    attempts = 0
    while len(pool) < n_configs and attempts < max_attempts:
        h = heuristics[attempts % len(heuristics)]
        cfg = h(problem)
        if cfg is not None:
            pool.add(cfg)
        attempts += 1

    return list(pool)
