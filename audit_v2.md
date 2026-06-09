# Audit du projet — branche `v2-column-generation`

Date : 10/06/2026

---

## Nouveauté de cette branche

| Fichier | Apport | Statut |
|---|---|---|
| `column_generation.py` | Problème de pricing (PLNE) pour générer la colonne manquante | OK |
| `lp_solver.py` | Ajout de `get_duals()` pour extraire les prix duaux | OK |
| `main_v2.py` | Boucle complète de génération de colonnes (programme maître + pricing) | OK (crash emoji) |

La logique de génération de colonnes est **correcte** : pricing bien formulé, condition d'arrêt rigoureuse (coût réduit ≤ 0), initialisation avec pool aléatoire.

---

## Problèmes identifiés

### P1 — Emoji `✅` dans `main_v2.py` (crash Windows, critique)

**Fichier :** `main_v2.py`, ligne 58

```python
print(f"\n✅ Algorithme terminé en {iteration} itérations ({temps_total:.2f} secondes).")
```

Provoque une `UnicodeEncodeError` sur Windows (encodage cp1252 du terminal).
Le programme crashe **en toute fin d'exécution**, après avoir pourtant trouvé la solution.
Ce bug avait déjà été rencontré et corrigé sur `exercices`.

**Correction :** remplacer `✅` par texte ASCII (`"OK :"` ou similaire).

---

### P2 — Emoji `✅` dans `analyse.py` (crash Windows, critique)

**Fichier :** `analyse.py`, ligne 100

```python
print(f"✅ Graphique généré et sauvegardé sous : {filename}")
```

Même bug. Déjà corrigé sur `exercices`, pas reporté ici.

**Correction :** remplacer `✅` par `"OK :"`.

---

### P3 — `N_CONFIGS = 5000` dans `main.py` (régression P1 d'exercices)

**Fichier :** `main.py`, ligne 15

`fichier-exemple` ne possède que 4 configurations distinctes. Avec 5000,
la boucle effectue 50 000 tentatives inutiles. Sur `gros_test_1`, un LP
avec 5000 variables serait très lent.

**Correction :** `N_CONFIGS = 30`

---

### P4 — `import pulp` et `import time` dans fonctions/boucles (régression P2 d'exercices)

**Fichier :** `main.py`, lignes 27, 73, 76

```python
def resoudre_instance(...):
    ...
    import pulp   # ← dans une fonction

for h in ["greedy", "hef", "aleatoire"]:
    import time   # ← dans la boucle
    import pulp   # ← dans la boucle
```

Les imports doivent être en haut du fichier. Déjà corrigé sur `exercices`.

**Correction :** déplacer `import pulp` et `import time` en haut du fichier.

---

### P5 — `mode_instance` affiche toutes les configs sans limite (régression P5 d'exercices)

**Fichier :** `main.py`, ligne 45

```python
for i, cfg in enumerate(pool):   # ← TOUTES les configs
    capteurs = sorted(k + 1 for k in cfg)
    print(f"  u{i+1} = capteurs {capteurs}")
```

Avec `N_CONFIGS = 5000`, produit des milliers de lignes. Déjà corrigé sur `exercices`.

**Correction :** limiter à 5 premières + `"... et N autres"`.

---

### P6 — `plot_heuristics()` définie après `if __name__ == "__main__":` (régression P3 d'exercices)

**Fichier :** `analyse.py`, ligne 63

La fonction `plot_heuristics` est déclarée **après** le bloc principal.
Convention Python : fonctions d'abord, `__main__` en dernier. Déjà corrigé sur `exercices`.

**Correction :** déplacer `plot_heuristics()` avant le bloc `if __name__ == "__main__":`.

---

### P7 — Pas de limite d'itérations dans `main_v2.py` (risque de boucle longue)

**Fichier :** `main_v2.py`, ligne 28

```python
while True:
    ...
    if new_config is None or new_config in pool:
        break
```

Sur `gros_test_1` (N=100, M=200) ou `maxi_test_1` (N=1000, M=500), la boucle
peut tourner plusieurs centaines d'itérations sans message de progression visible
(le `print` n'apparaît que tous les 10 tours). Si le pricing plante silencieusement,
la boucle devient infinie.

**Correction suggérée :** ajouter une limite haute (`MAX_ITER = 500`) et un message
de progression à chaque itération (ou toutes les 5).

---

### P8 — `new_config in pool` sur une liste (complexité O(n))

**Fichier :** `main_v2.py`, ligne 41

```python
if new_config is None or new_config in pool:   # pool est une liste
    break
```

Le test `in` sur une liste est O(n). Pour des centaines d'itérations c'est négligeable,
mais un `set` dédié (comme le `vus` de `generer_pool`) serait plus rigoureux.

**Correction suggérée :** maintenir un `set` parallèle à la liste `pool`.

---

### P9 — `main_v2.py` n'appelle pas `afficher_solution` (planning absent)

**Fichier :** `main_v2.py`, lignes 53-61

La V2 affiche la durée de vie finale mais pas le planning d'activation
(quels capteurs actifs pendant combien de temps). La V1 (`afficher_solution`)
le fait. L'utilisateur ne voit pas le résultat concret.

**Correction suggérée :** appeler `afficher_solution(model, t_vars, pool, problem)`
après la boucle.

---

### P10 — `README.md` non mis à jour (documentation incomplète)

**Fichier :** `README.md`

- Année : **2023-2024** → devrait être **2025-2026**
- Heuristiques : mentionne encore **deux** heuristiques (greedy + aléatoire), HEF absent
- `main_v2.py` n'est **pas mentionné** (ni `column_generation.py`)
- Piste d'amélioration `"Ajouter HEF"` : déjà implémentée, à retirer
- Piste `"Implémenter la génération de colonnes"` : déjà fait, à transformer en description
- Tableau résultats : absent de `maxi_test_1`, valeurs figées à N_CONFIGS=10

---

### P11 — `generer_rapport.py` ancienne version (incohérences avec le code actuel)

**Fichier :** `generer_rapport.py`

Le rapport PDF de cette branche est la version **avant** toutes les améliorations
faites sur `exercices` :
- Section 1 : **"Deux heuristiques"** alors que le code en implémente trois
- Section 1 tableau : HEF **absent**
- Section 2 : pas de borne supérieure, pas de %, absent de `maxi_test_1`, N_CONFIGS=10
- Section 3.1 : ligne HEF absente du tableau
- Section 3.2 : données périmées (10 configs, sans `gros_test_1` ni `maxi_test_1`)
- Génération de colonnes (**apport majeur de cette branche**) : **totalement absente du rapport**

---

## Résumé par priorité

| Priorité | ID | Description |
|---|---|---|
| Critique | P1 | Emoji `✅` dans `main_v2.py` — crash Windows immédiat |
| Critique | P2 | Emoji `✅` dans `analyse.py` — crash Windows |
| Important | P3 | `N_CONFIGS = 5000` — régression depuis exercices |
| Important | P4 | Imports dans fonctions/boucles — régression depuis exercices |
| Important | P5 | Affichage illimité des configs — régression depuis exercices |
| Important | P6 | `plot_heuristics` après `__main__` — régression depuis exercices |
| Important | P7 | Pas de limite d'itérations dans V2 — risque de boucle longue |
| Mineur | P8 | `in pool` sur liste — O(n) au lieu de O(1) |
| Important | P9 | Planning d'activation absent de la sortie V2 |
| Important | P10 | README non mis à jour (année, HEF, V2, résultats) |
| Important | P11 | Rapport PDF incohérent (ancienne version, V2 absente) |
