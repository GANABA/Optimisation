# Projet : Activation de capteurs pour surveillance de zones

**IUT Nord Franche-Comté** — Techniques d'optimisation  
**Enseignante** : Karine Deschinkel (2025-2026)

---

## Présentation du problème

On dispose d'un réseau de **N capteurs** déployés pour surveiller **M zones**. Chaque capteur a une durée de vie limitée (batterie). L'objectif est de planifier l'activation des capteurs pour **maximiser la durée de vie du réseau** tout en garantissant que chaque zone est toujours surveillée.

**Exemple** : 4 capteurs, 3 zones

| Capteur | Zones couvertes | Durée de vie |
|---------|----------------|--------------|
| s1      | z1, z2         | 6            |
| s2      | z2, z3         | 3            |
| s3      | z3             | 2            |
| s4      | z1, z3         | 6            |

Solution optimale : durée de vie = **8.5** unités de temps.

---

## Structure du projet

```
optimisation/
│
├── data.py                  # Partie 1 : lecture des données + borne supérieure
├── heuristics.py            # Partie 2 : construction des configurations (greedy, HEF, aléatoire)
├── lp_solver.py             # Partie 3 : résolution du programme linéaire + prix duaux
├── column_generation.py     # V2 : problème de pricing (génération de colonnes)
├── analyse.py               # Partie 5 : analyse des résultats + graphiques
├── main.py                  # Point d'entrée V1 (heuristiques)
├── main_v2.py               # Point d'entrée V2 (génération de colonnes exacte)
│
├── fichier-exemple.txt      # Instance jouet        (N=4,   M=3)
├── moyen_test_2.txt         # Instance moyenne      (N=20,  M=10)
├── moyen_test_3.txt         # Instance moyenne      (N=10,  M=10)
├── gros_test_1.txt          # Grande instance       (N=100, M=200)
├── maxi_test_1.txt          # Très grande instance  (N=1000, M=500)
│
└── projet-plcapteurs-2024.pdf  # Sujet complet
```

---

## Installation

**Prérequis** : Python 3.10+

```bash
pip install pulp
```

PuLP inclut le solveur CBC — pas besoin d'installer GLPK séparément.

---

## Utilisation

### V1 — Résolution par heuristiques

```bash
# Résoudre une instance (heuristique greedy par défaut)
python main.py fichier-exemple.txt
python main.py moyen_test_2.txt greedy
python main.py moyen_test_3.txt hef
python main.py gros_test_1.txt aleatoire

# Comparer les 3 heuristiques sur toutes les instances
python main.py --all

# Générer un graphique (évolution de la durée de vie selon le nombre de configs)
python main.py --plot moyen_test_3.txt
```

### V2 — Résolution exacte par génération de colonnes

```bash
python main_v2.py fichier-exemple.txt
python main_v2.py moyen_test_3.txt
```

La V2 génère automatiquement les configurations manquantes via un problème de pricing (PLNE),
et s'arrête dès qu'elle prouve mathématiquement que l'optimum est atteint.

### Analyse comparative (Partie 5)

```bash
python analyse.py
```

---

## Description des fichiers

### `data.py` — Partie 1 : données et borne supérieure

Contient la classe `Problem` et la fonction `load(filepath)`.  
La méthode `upper_bound()` calcule la borne supérieure théorique (Manju & Pujari, 2011) :

```
upper_bound = min_z ( somme des T_k pour tous les capteurs k couvrant la zone z )
```

```python
from data import load

problem = load("fichier-exemple.txt")
print(problem.N)              # 4
print(problem.upper_bound())  # 9.0
```

---

### `heuristics.py` — Partie 2 : configurations élémentaires

Une **configuration élémentaire** est un ensemble minimal de capteurs couvrant toutes les zones.

Trois heuristiques sont implémentées :

**Greedy** (Cardei & Du, 2005) : choisit à chaque étape le capteur couvrant le plus de zones non encore couvertes. En cas d'égalité, choix aléatoire.

**HEF — High-Energy-First** (Manju & Pujari, 2011) : choisit parmi les capteurs utiles celui ayant la plus grande durée de vie initiale. Très déterministe, génère peu de configs distinctes.

**Aléatoire** (Deschinkel, 2011) : parcourt les zones dans un ordre aléatoire et choisit n'importe quel capteur couvrant la zone courante. Maximise la diversité du pool.

```python
from data import load
from heuristics import generer_pool

problem = load("moyen_test_2.txt")
pool = generer_pool(problem, n_configs=30, seed=42, heuristique="greedy")
pool = generer_pool(problem, n_configs=30, seed=42, heuristique="hef")
pool = generer_pool(problem, n_configs=30, seed=42, heuristique="aleatoire")
```

---

### `lp_solver.py` — Partie 3 : programme linéaire

Formulation du LP :

```
max   sum(t_u)
s.c.  pour chaque capteur k : sum(t_u pour u contenant k) <= T_k
      t_u >= 0
```

`get_duals(model, problem)` extrait les prix duaux des contraintes de batterie,
utilisés par la génération de colonnes (V2).

---

### `column_generation.py` + `main_v2.py` — V2 : génération de colonnes

La génération de colonnes est une méthode **exacte** qui construit automatiquement
les configurations nécessaires sans les énumérer toutes :

1. **Programme maître** (LP) : résout sur le pool courant, donne des prix duaux π_k
2. **Problème de pricing** (PLNE) : cherche la configuration u qui minimise `sum(π_k pour k dans u)`.
   Si le coût réduit `1 - sum(π_k)` est ≤ 0, l'optimum est prouvé.
3. La nouvelle configuration est ajoutée au pool et on reboucle.

```bash
python main_v2.py moyen_test_3.txt
```

Sortie typique :
```
[Etape 1] Generation du pool initial (30 configurations aleatoires)...
[Etape 2] Lancement de l'algorithme exact...

OK : Algorithme termine en 1 iterations (0.04 secondes).
  Duree de vie optimale prouvee : 395.0000 (85.31% de la borne superieure)
```

---

### `analyse.py` — Partie 5 : analyse des résultats

Deux analyses disponibles, plus un graphique :

**1. Influence du nombre de configurations :** fait varier n_configs et mesure la durée de vie.

**2. Influence du type d'heuristique :** compare greedy, HEF et aléatoire à pool égal.

```bash
python analyse.py
python main.py --plot moyen_test_3.txt
```

---

## Résultats (V1 — heuristiques, N_CONFIGS=30, seed=42)

| Instance        |    N |   M | Borne sup. | Greedy (%)  | HEF (%)     | Aléatoire (%)  |
|-----------------|------|-----|------------|-------------|-------------|----------------|
| fichier-exemple |    4 |   3 |        9.0 | 8.5 (94 %)  | 6.0 (66 %)  | 8.5 (94 %)     |
| moyen_test_2    |   20 |  10 |      104.0 | 15.0 (14 %) | 19.0 (18 %) | 104.0 (100 %) |
| moyen_test_3    |   10 |  10 |      463.0 | 358.0 (77 %)| 166.0 (35 %)| 395.0 (85 %)  |
| gros_test_1     |  100 | 200 |     3437.0 | 177.0 (5 %) | 196.0 (5 %) | 992.0 (28 %)  |
| maxi_test_1     | 1000 | 500 |    27245.0 | 506.0 (1 %) | 197.0 (0 %) | 1463.0 (5 %)  |

---

## Branches Git

| Branche                 | Contenu                                                        |
|-------------------------|----------------------------------------------------------------|
| `exercices`             | Code construit partie par partie (V1 heuristiques)             |
| `v2-column-generation`  | V2 : génération de colonnes exacte (ce README)                 |
| `solution-complete`     | Implémentation de référence avancée                            |
| `master`                | Version initiale                                               |

---

## Références

| Auteurs | Année | Contribution |
|---------|-------|--------------|
| Cardei & Du | 2005 | Heuristique greedy, organisation en cover sets |
| Manju & Pujari | 2011 | Heuristique HEF, borne supérieure de l'optimal |
| Deschinkel | 2011 | Génération de colonnes, heuristique aléatoire |
