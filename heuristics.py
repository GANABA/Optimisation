import random
from data import Problem

# Un Config est un ensemble (frozenset) d'indices de capteurs (0-based)
Config = frozenset


def couvre_tout(config, problem):
    """Retourne True si la config couvre toutes les zones."""
    zones_couvertes = set()
    for k in config:
        zones_couvertes |= problem.coverage[k]
    return len(zones_couvertes) == problem.M


def rendre_elementaire(config, problem):
    """
    Supprime les capteurs superflus d'une config valide.
    Ordre de test aléatoire -> configs différentes à chaque appel.
    """
    capteurs = list(config)
    random.shuffle(capteurs)

    config_courante = set(config)
    for k in capteurs:
        config_courante.remove(k)
        if couvre_tout(config_courante, problem):
            pass  # k était superflu, on le laisse supprimé
        else:
            config_courante.add(k)  # k est nécessaire, on le remet

    return frozenset(config_courante)


def construire_config(problem):
    """
    Heuristique gloutonne : construit une configuration valide.
    A chaque etape, choisit au hasard parmi les capteurs couvrant
    le plus de zones non encore couvertes.
    Retourne une config elementaire, ou None si impossible.
    """
    zones_non_couvertes = set(range(problem.M))
    capteurs_disponibles = set(range(problem.N))
    config = set()

    while zones_non_couvertes:
        # Compter combien de zones non couvertes chaque capteur apporte
        apport = {}
        for k in capteurs_disponibles:
            apport[k] = len(problem.coverage[k] & zones_non_couvertes)

        # Garder uniquement les capteurs qui apportent quelque chose
        utiles = [k for k, v in apport.items() if v > 0]
        if not utiles:
            return None  # impossible de couvrir toutes les zones

        # Choisir au hasard parmi ceux qui apportent le plus
        max_apport = max(apport[k] for k in utiles)
        meilleurs = [k for k in utiles if apport[k] == max_apport]
        choisi = random.choice(meilleurs)

        config.add(choisi)
        zones_non_couvertes -= problem.coverage[choisi]
        capteurs_disponibles.remove(choisi)

    return rendre_elementaire(config, problem)


def construire_config_aleatoire(problem):
    """
    Heuristique aleatoire : parcourt les zones dans un ordre aleatoire,
    et pour chaque zone non couverte choisit n'importe quel capteur
    qui la couvre (sans critere de qualite).
    Retourne une config elementaire, ou None si impossible.
    """
    zones = list(range(problem.M))
    random.shuffle(zones)

    config = set()
    zones_couvertes = set()

    for z in zones:
        if z in zones_couvertes:
            continue
        candidats = [k for k in range(problem.N) if z in problem.coverage[k]]
        if not candidats:
            return None
        choisi = random.choice(candidats)
        config.add(choisi)
        zones_couvertes |= problem.coverage[choisi]

    return rendre_elementaire(config, problem)


def generer_pool(problem, n_configs=10, seed=None, heuristique="greedy"):
    """
    Genere un pool de n_configs configurations elementaires distinctes.
    """
    if seed is not None:
        random.seed(seed)

    pool = []
    vus = set()

    fn = construire_config if heuristique == "greedy" else construire_config_aleatoire

    tentatives = 0
    while len(pool) < n_configs and tentatives < n_configs * 10:
        tentatives += 1
        cfg = fn(problem)
        if cfg is not None and cfg not in vus:
            pool.append(cfg)
            vus.add(cfg)

    return pool
