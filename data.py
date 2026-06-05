"""
Lecture et représentation des instances du problème d'activation de capteurs.

Format attendu :
  Ligne 1 : N  (nombre de capteurs)
  Ligne 2 : M  (nombre de zones)
  Ligne 3 : T_1 T_2 ... T_N  (durées de vie des capteurs)
  Lignes 4 à N+3 : zones couvertes par chaque capteur (indices 1-based dans le fichier)
"""

from dataclasses import dataclass, field


@dataclass
class Problem:
    N: int                      # nombre de capteurs
    M: int                      # nombre de zones
    lifetimes: list[float]      # lifetimes[k] = durée de vie du capteur k  (0-indexed)
    coverage: list[set[int]]    # coverage[k] = ensemble des zones couvertes par k (0-indexed)

    # Accès inverse : pour chaque zone, quels capteurs la couvrent
    sensors_of: list[set[int]] = field(init=False, repr=False)

    def __post_init__(self):
        self.sensors_of = [set() for _ in range(self.M)]
        for k, zones in enumerate(self.coverage):
            for z in zones:
                self.sensors_of[z].add(k)

    def upper_bound(self) -> float:
        """
        Borne supérieure sur la durée de vie optimale.
        OPT ≤ min_z  Σ_{k couvrant z}  T_k
        Source : Manju & Pujari 2011, Definition 6.
        """
        return min(
            sum(self.lifetimes[k] for k in self.sensors_of[z])
            for z in range(self.M)
        )

    def __repr__(self) -> str:
        return f"Problem(N={self.N}, M={self.M})"


def load(filepath: str) -> Problem:
    """Charge une instance depuis un fichier texte."""
    with open(filepath, encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    N = int(lines[0])
    M = int(lines[1])
    lifetimes = list(map(float, lines[2].split()))

    if len(lifetimes) != N:
        raise ValueError(
            f"Attendu {N} durées de vie, trouvé {len(lifetimes)}"
        )

    coverage: list[set[int]] = []
    for i in range(N):
        raw = lines[3 + i].split() if (3 + i) < len(lines) else []
        # les indices dans le fichier sont 1-based → on convertit en 0-based
        zones = {int(z) - 1 for z in raw}
        coverage.append(zones)

    return Problem(N=N, M=M, lifetimes=lifetimes, coverage=coverage)
