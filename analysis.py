"""
Analyse comparative des heuristiques et affichage des résultats (Partie 5).

Fonctions :
  - compare_heuristics : compare les 3 heuristiques sur une instance
  - run_all_instances  : résout toutes les instances et présente un tableau
"""

import time
import random
from data import Problem, load
from heuristics import (
    greedy_critical_target, greedy_high_energy, random_cover,
    generate_pool, Config
)
from lp_solver import solve, LPResult
from column_generation import column_generation


def _run_with_pool(problem: Problem, heuristic_fn, n_configs: int,
                   n_runs: int, seed: int) -> tuple[float, float]:
    """
    Lance n_runs expériences avec l'heuristique donnée et retourne
    (durée_de_vie_moyenne, temps_moyen_secondes).
    """
    random.seed(seed)
    lifetimes = []
    times = []

    for _ in range(n_runs):
        pool: list[Config] = []
        for _ in range(n_configs * 5):  # tentatives max
            cfg = heuristic_fn(problem)
            if cfg is not None and cfg not in pool:
                pool.append(cfg)
            if len(pool) >= n_configs:
                break

        if not pool:
            continue

        t0 = time.perf_counter()
        result = solve(problem, pool)
        elapsed = time.perf_counter() - t0

        if result.status == "Optimal":
            lifetimes.append(result.lifetime)
            times.append(elapsed)

    avg_lt = sum(lifetimes) / len(lifetimes) if lifetimes else 0.0
    avg_t = sum(times) / len(times) if times else 0.0
    return avg_lt, avg_t


def compare_heuristics(problem: Problem,
                       n_configs: int = 30,
                       n_runs: int = 5,
                       seed: int = 0) -> None:
    """
    Compare les trois heuristiques + la génération de colonnes sur une instance.
    Affiche un tableau récapitulatif.
    """
    ub = problem.upper_bound()
    print(f"Borne supérieure : {ub:.4f}")
    print()

    header = f"{'Methode':<25} {'Lifetime moy':>13} {'% borne sup':>12} {'Temps moy (s)':>14}"
    print(header)
    print("-" * len(header))

    heuristics = [
        ("Greedy-Critique (A)", greedy_critical_target),
        ("HEF (B)",             greedy_high_energy),
        ("Aleatoire (C)",       random_cover),
    ]

    for name, fn in heuristics:
        lt, t = _run_with_pool(problem, fn, n_configs, n_runs, seed)
        pct = lt / ub * 100 if ub > 0 else 0
        print(f"{name:<25} {lt:>13.4f} {pct:>11.1f}% {t:>13.4f}s")

    # Génération de colonnes (méthode mixte)
    t0 = time.perf_counter()
    result_cg = column_generation(problem, n_initial=5, method="mixed", seed=seed)
    t_cg = time.perf_counter() - t0
    pct_cg = result_cg.lifetime / ub * 100 if ub > 0 else 0
    print(f"{'Col. generation (mixte)':<25} {result_cg.lifetime:>13.4f} "
          f"{pct_cg:>11.1f}% {t_cg:>13.4f}s")

    print()


def run_all_instances(filepaths: list[str],
                      n_configs: int = 30,
                      seed: int = 0) -> None:
    """
    Résout toutes les instances avec les 3 heuristiques + col. gen.
    Affiche un tableau de synthèse (Partie 4 et 5).
    """
    col_w = 14
    hdr = (f"{'Instance':<22} {'N':>5} {'M':>5} {'Borne':>10} "
           f"{'Grd-Crit':>{col_w}} {'HEF':>{col_w}} "
           f"{'Aleat':>{col_w}} {'Col.Gen':>{col_w}}")
    print(hdr)
    print("-" * len(hdr))

    for fp in filepaths:
        name = fp.split("\\")[-1].replace(".txt", "")
        problem = load(fp)
        ub = problem.upper_bound()

        results = {}
        for label, fn in [("grd", greedy_critical_target),
                           ("hef", greedy_high_energy),
                           ("rnd", random_cover)]:
            lt, _ = _run_with_pool(problem, fn, n_configs, n_runs=3, seed=seed)
            results[label] = lt

        cg = column_generation(problem, n_initial=10, method="mixed", seed=seed)
        results["cg"] = cg.lifetime

        def fmt(v):
            return f"{v:.1f} ({v/ub*100:.0f}%)"

        print(f"{name:<22} {problem.N:>5} {problem.M:>5} {ub:>10.1f} "
              f"{fmt(results['grd']):>{col_w}} "
              f"{fmt(results['hef']):>{col_w}} "
              f"{fmt(results['rnd']):>{col_w}} "
              f"{fmt(results['cg']):>{col_w}}")
