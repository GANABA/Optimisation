# Projet : Activation de capteurs pour surveillance de zones

**IUT Nord Franche-Comté** — Techniques d'optimisation  
**Enseignante** : Karine Deschinkel (2023-2024)

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
├── data.py                  # Partie 1 : lecture des données
├── heuristics.py            # Partie 2 : construction des configurations
├── lp_solver.py             # Partie 3 : résolution du programme linéaire
├── analyse.py               # Partie 5 : analyse des résultats
├── main.py                  # Point d'entrée principal
│
├── fichier-exemple.txt      # Instance jouet  (N=4,  M=3)
├── moyen_test_2.txt         # Instance moyenne (N=20, M=10)
├── moyen_test_3.txt         # Instance moyenne (N=10, M=10)
├── gros_test_1.txt          # Grande instance  (N=100, M=200)
├── maxi_test_1.txt          # Très grande instance (N=1000, M=500)
│
└── projet-plcapteurs-2024.pdf  # Sujet complet
```

---

## Installation

**Prérequis** : Python 3.10+

Installer la dépendance :
```bash
pip install pulp
```

PuLP inclut le solveur CBC — pas besoin d'installer GLPK séparément.

---

## Utilisation

### Résoudre une instance
```bash
python main.py fichier-exemple.txt
python main.py moyen_test_2.txt
python main.py gros_test_1.txt
```

### Résoudre toutes les instances (Partie 4)
```bash
python main.py --all
```

### Lancer l'analyse comparative (Partie 5)
```bash
python analyse.py
```

---

## Description des fichiers

### `data.py` — Partie 1 : manipulation des données

Contient la classe `Problem` et la fonction `load(filepath)`.

```python
from data import load

problem = load("fichier-exemple.txt")
print(problem.N)           # nombre de capteurs
print(problem.M)           # nombre de zones
print(problem.lifetimes)   # [6.0, 3.0, 2.0, 6.0]
print(problem.coverage[0]) # zones du capteur 0 : {0, 1}
```

**Format des fichiers d'instance :**
```
4          ← N (nombre de capteurs)
3          ← M (nombre de zones)
6 3 2 6    ← durées de vie T_1 ... T_N
1 2        ← zones du capteur 1 (indices 1-based dans le fichier)
2 3        ← zones du capteur 2
3          ← zones du capteur 3
1 3        ← zones du capteur 4
```
> Les indices sont convertis en **0-based** à la lecture.

---

### `heuristics.py` — Partie 2 : configurations élémentaires

Une **configuration élémentaire** est un ensemble de capteurs qui :
- couvre toutes les zones
- ne contient aucun capteur superflu (si on en retire un, une zone n'est plus couverte)

Deux heuristiques sont implémentées :

**Greedy** (Cardei & Du, 2005) : à chaque étape, choisit le capteur couvrant le plus de zones non encore couvertes. En cas d'égalité, choix aléatoire.

**Aléatoire** (Deschinkel, 2011) : parcourt les zones dans un ordre aléatoire et choisit n'importe quel capteur couvrant la zone courante.

```python
from data import load
from heuristics import generer_pool

problem = load("moyen_test_2.txt")

# Générer 10 configs avec l'heuristique greedy
pool = generer_pool(problem, n_configs=10, seed=42, heuristique="greedy")

# Générer 10 configs avec l'heuristique aléatoire
pool = generer_pool(problem, n_configs=10, seed=42, heuristique="aleatoire")
```

---

### `lp_solver.py` — Partie 3 : programme linéaire

Formulation du LP :

```
max   t_u1 + t_u2 + ... + t_un

s.c.  pour chaque capteur k :
        somme des t_u (pour les configs u contenant k) <= T_k

      t_u >= 0
```

```python
from data import load
from heuristics import generer_pool
from lp_solver import resoudre, afficher_solution

problem = load("fichier-exemple.txt")
pool = generer_pool(problem, n_configs=10, seed=42)
model, t = resoudre(problem, pool)
afficher_solution(model, t, pool, problem)
```

Sortie :
```
Statut       : Optimal
Duree de vie : 8.5000

Planning d'activation :
  Capteurs [1, 4] -> actifs pendant 3.5000 unites de temps
  Capteurs [1, 3] -> actifs pendant 2.0000 unites de temps
  ...
```

---

### `analyse.py` — Partie 5 : analyse des résultats

Deux analyses sont disponibles :

**1. Influence du nombre de configurations :**
Fait varier n_configs (1, 2, 3, 5, 10, 15, 20) et mesure la durée de vie obtenue.

**2. Influence du type d'heuristique :**
Compare greedy vs aléatoire avec le même nombre de configurations.

```bash
python analyse.py
```

---

## Résultats obtenus (Partie 4)

| Instance        |   N |   M | Configs | Durée de vie | Temps (s) |
|-----------------|-----|-----|---------|-------------|-----------|
| fichier-exemple |   4 |   3 |       4 |      8.5000 |     0.13s |
| moyen_test_2    |  20 |  10 |       3 |     15.0000 |     0.17s |
| moyen_test_3    |  10 |  10 |      10 |    358.0000 |     0.06s |
| gros_test_1     | 100 | 200 |      10 |    177.0000 |     0.20s |

> Ces résultats sont obtenus avec `n_configs=10, seed=42`. Augmenter le nombre de configurations améliore la durée de vie (voir Partie 5).

---

## Branches Git

| Branche            | Contenu                                      |
|--------------------|----------------------------------------------|
| `exercices`        | Code construit partie par partie (ce README) |
| `solution-complete`| Implémentation avancée avec génération de colonnes (Deschinkel 2011) |
| `master`           | Version initiale                             |

---

## Références

| Auteurs | Année | Contribution |
|---------|-------|--------------|
| [Cardei & Du](https://link.springer.com/article/10.1007/s11276-005-6615-6) | 2005 | Heuristique greedy, organisation en cover sets |
| [Manju & Pujari](https://arxiv.org/abs/1103.4769) | 2011 | Heuristique HEF, borne supérieure de l'optimal |
| [Deschinkel](https://www.researchgate.net/publication/283458855) | 2011 | Génération de colonnes, heuristique aléatoire |

---

## Pistes d'amélioration

- Ajouter l'heuristique **HEF** (High-Energy-First) de Manju & Pujari 2011 : priorité aux capteurs avec la plus grande énergie résiduelle
- Implémenter la **génération de colonnes** (branche `solution-complete`) pour trouver l'optimal garanti
- Tester sur `maxi_test_1.txt` (N=1000, M=500) avec une méthode rapide
- Produire des **graphiques** (matplotlib) pour la Partie 5
