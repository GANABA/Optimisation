import pulp
from data import load
from heuristics import generer_pool
from lp_solver import resoudre


def duree_vie(problem, n_configs, heuristique, seed=42):
    """Retourne la duree de vie obtenue avec n_configs configs de type heuristique."""
    pool = generer_pool(problem, n_configs=n_configs, seed=seed, heuristique=heuristique)
    if not pool:
        return 0.0
    model, t = resoudre(problem, pool)
    return pulp.value(model.objective) or 0.0


def analyse_nombre(problem, nom_instance):
    """
    Analyse l'influence du NOMBRE de configurations sur la duree de vie.
    On fait varier n_configs et on observe le resultat.
    """
    print(f"\n--- Influence du nombre de configs ({nom_instance}) ---")
    print(f"{'N configs':>10} {'Greedy':>12} {'HEF':>12} {'Aleatoire':>12}")
    print("-" * 51)

    for n in [1, 2, 3, 5, 10, 15, 20]:
        lt_greedy = duree_vie(problem, n, "greedy")
        lt_hef    = duree_vie(problem, n, "hef")
        lt_alea   = duree_vie(problem, n, "aleatoire")
        print(f"{n:>10} {lt_greedy:>12.4f} {lt_hef:>12.4f} {lt_alea:>12.4f}")


def analyse_type(problem, nom_instance, n_configs=10):
    """
    Analyse l'influence du TYPE d'heuristique sur la duree de vie.
    On compare greedy et aleatoire avec le meme nombre de configs.
    """
    print(f"\n--- Influence du type d'heuristique ({nom_instance}, {n_configs} configs) ---")
    print(f"{'Heuristique':<15} {'Duree de vie':>14} {'Nb configs reels':>18}")
    print("-" * 50)

    for nom_h in ["greedy", "hef", "aleatoire"]:
        pool = generer_pool(problem, n_configs=n_configs, seed=42, heuristique=nom_h)
        model, t = resoudre(problem, pool)
        lt = pulp.value(model.objective) or 0.0
        print(f"{nom_h:<15} {lt:>14.4f} {len(pool):>18}")


def plot_heuristics(problem, nom_instance, max_configs=30, step=5, seed=42):
    """
    Génère un graphique montrant l'évolution de la durée de vie en fonction 
    du nombre de configurations pour les différentes heuristiques.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Erreur : matplotlib n'est pas installé. Lancez 'pip install matplotlib'.")
        return

    n_values = list(range(step, max_configs + 1, step))
    
    heuristics = ["greedy", "hef", "aleatoire"]
    colors = {"greedy": "blue", "hef": "green", "aleatoire": "red"}
    markers = {"greedy": "-o", "hef": "-s", "aleatoire": "-^"}
    
    results = {h: [] for h in heuristics}
    
    print(f"\nCalcul en cours pour le graphique ({nom_instance})...")
    for n in n_values:
        for h in heuristics:
            lt = duree_vie(problem, n, h, seed)
            results[h].append(lt)
            
    plt.figure(figsize=(10, 6))
    for h in heuristics:
        plt.plot(n_values, results[h], markers[h], color=colors[h], label=h.capitalize())
        
    plt.title(f"Influence du nombre de configurations ({nom_instance})")
    plt.xlabel("Nombre de configurations initiales")
    plt.ylabel("Durée de vie optimale")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    
    filename = f"graphique_{nom_instance}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"OK : graphique sauvegarde sous {filename}")


if __name__ == "__main__":
    instances = [
        ("fichier-exemple.txt",  "fichier-exemple"),
        ("moyen_test_2.txt",     "moyen_test_2"),
        ("moyen_test_3.txt",     "moyen_test_3"),
    ]

    print("=== Partie 5 : analyse des resultats ===")

    for fichier, nom in instances:
        problem = load(fichier)
        analyse_nombre(problem, nom)
        analyse_type(problem, nom, n_configs=10)

