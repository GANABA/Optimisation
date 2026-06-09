import random
from data import Problem

# Un Config est un ensemble (frozenset) d'indices de capteurs (0-based)
Config = frozenset
print(f"{Config}")


def couvre_tout(config, problem):
    """Retourne True si la config couvre toutes les zones."""
    zones_couvertes = set()
    for k in config:
        print(f"k = {k}, zones couvertes par le capteur n°{k+1} = {problem.coverage[k]}")
        zones_couvertes |= problem.coverage[k]
    print(f"zones_couvertes = {zones_couvertes}")
    return len(zones_couvertes) == problem.M


def rendre_elementaire(config, problem):
    """
    Supprime les capteurs superflus d'une config valide.
    Ordre de test aléatoire -> configs différentes à chaque appel.
    """
    capteurs = list(config)
    print(f"\ncapteurs = {capteurs}")
    random.shuffle(capteurs)
    print(f"capteurs après shuffle = {capteurs}")


    config_courante = set(config)
    print(f"\nconfig_courante = {config_courante}")
    for k in capteurs:
        config_courante.remove(k)
        print(f"config_courante après suppression de k = {k} = {config_courante}")
        if couvre_tout(config_courante, problem):
            pass  # k était superflu, on le laisse supprimé
        else:
            config_courante.add(k)  # k est nécessaire, on le remet
    print(f"\nconfig finale = {config_courante}")

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
            print(f"\nk = {k}, zones couvertes par le capteur n°{k+1} = {problem.coverage[k]}")
            print(f"zones_non_couvertes = {zones_non_couvertes}")
            apport[k] = len(problem.coverage[k] & zones_non_couvertes)
            print(f"apport[k] = {apport[k]}")
        print(f"\napport de tous les capteurs = {apport}")



        # Garder uniquement les capteurs qui apportent quelque chose
        utiles = [k for k, v in apport.items() if v > 0]
        print(f"capteurs utiles = {utiles}")
        if not utiles:
            return None  # impossible de couvrir toutes les zones

        # Choisir au hasard parmi ceux qui apportent le plus
        max_apport = max(apport[k] for k in utiles)
        print(f"max_apport = {max_apport}")
        meilleurs = [k for k in utiles if apport[k] == max_apport]
        print(f"meilleurs = {meilleurs}")
        choisi = random.choice(meilleurs)
        print(f"choisi = {choisi}")

        config.add(choisi)
        print(f"new config = {config}")
        zones_non_couvertes -= problem.coverage[choisi]
        print(f"zones_non_couvertes = {zones_non_couvertes}")
        capteurs_disponibles.remove(choisi)
        print(f"\nliste des capteurs_disponibles = {capteurs_disponibles}")

    return rendre_elementaire(config, problem)


def generer_pool(problem, n_configs=10, seed=None):
    """
    Genere un pool de n_configs configurations elementaires distinctes.
    """
    if seed is not None:
        random.seed(seed)

    pool = []
    vus = set()

    tentatives = 0
    while len(pool) < n_configs and tentatives < n_configs * 10:
        tentatives += 1
        cfg = construire_config(problem)
        if cfg is not None and cfg not in vus:
            pool.append(cfg)
            vus.add(cfg)
        print(f"\npool = {pool}, vus = {vus}, tentatives = {tentatives}")

    return pool
