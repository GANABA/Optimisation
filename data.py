class Problem:
    def __init__(self, N, M, lifetimes, coverage):
        self.N = N                  # nombre de capteurs
        self.M = M                  # nombre de zones
        self.lifetimes = lifetimes  # lifetimes[k] = duree de vie du capteur k
        self.coverage = coverage    # coverage[k] = set de zones couvertes par capteur k

    def __str__(self):
        lines = [f"N={self.N} capteurs, M={self.M} zones"]
        for k in range(self.N):
            zones = sorted(self.coverage[k])
            lines.append(f"  capteur {k+1} : zones {zones}, T={self.lifetimes[k]}")
        return "\n".join(lines)

    def upper_bound(self):
        """
        Borne superieure theorique de la duree de vie du reseau.
        La duree de vie ne peut pas exceder la somme des batteries des capteurs
        couvrant la zone la plus 'faible' (Manju & Pujari 2011).
        """
        sensors_of = [set() for _ in range(self.M)]
        for k, zones in enumerate(self.coverage):
            for z in zones:
                sensors_of[z].add(k)
                
        return min(
            sum(self.lifetimes[k] for k in sensors_of[z])
            for z in range(self.M)
        )


def load(filepath):
    with open(filepath) as f:
        lines = [line.strip() for line in f if line.strip()]

    N = int(lines[0])
    M = int(lines[1])
    lifetimes = list(map(float, lines[2].split()))

    coverage = []
    for i in range(N):
        zones = {int(z) - 1 for z in lines[3 + i].split()}  # 1-based -> 0-based
        coverage.append(zones)

    return Problem(N, M, lifetimes, coverage)
