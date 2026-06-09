# Audit du projet — branche `exercices`

Date : 09/06/2026

---

## Ajouts récents bien faits

| Fichier | Ajout | Statut |
|---|---|---|
| `data.py` | Méthode `upper_bound()` (Manju & Pujari 2011) | OK |
| `heuristics.py` | Heuristique HEF (`construire_config_hef`) | OK |
| `heuristics.py` | HEF intégré dans `generer_pool` | OK |
| `main.py` | Mode `--plot` pour générer un graphique | OK |
| `main.py` | Affichage de la borne supérieure dans `mode_instance` | OK |
| `analyse.py` | HEF ajouté dans `analyse_nombre` et `analyse_type` | OK |
| `analyse.py` | Fonction `plot_heuristics()` avec matplotlib | OK |

---

## Problèmes identifiés

### P1 — `N_CONFIGS = 5000` : valeur irréaliste (critique)

**Fichier :** `main.py`, ligne 15

`fichier-exemple` ne possède que 4 configurations élémentaires possibles. Avec
`N_CONFIGS = 5000`, la boucle de génération effectue jusqu'à `5000 × 10 = 50 000`
tentatives pour n'en trouver que 4 — temps perdu inutilement.
Sur `gros_test_1`, un LP avec 5000 variables serait extrêmement lent à résoudre.

**Correction suggérée :** passer à `N_CONFIGS = 20` ou `30`.

---

### P2 — `import time` et `import pulp` dans la boucle `for` (mauvais style)

**Fichier :** `main.py`, lignes 73 et 76

```python
for fichier in INSTANCES:
    ...
    import time       # ← dans la boucle
    import pulp       # ← dans la boucle
```

Les imports doivent toujours être en haut du fichier. Bien que Python mette les
modules en cache (pas de rechargement réel), c'est une mauvaise pratique qui nuit
à la lisibilité.

**Correction suggérée :** déplacer `import pulp` en haut du fichier avec les autres imports.
(`import time` est déjà en ligne 2 — le doublon dans la boucle est à supprimer.)

---

### P3 — `plot_heuristics()` définie après `if __name__ == "__main__":` (incohérence)

**Fichier :** `analyse.py`, lignes 48-100

```python
if __name__ == "__main__":   # ligne 48 — bloc principal
    ...                      # ligne 60 — fin du bloc

def plot_heuristics(...):    # ligne 63 — fonction définie APRÈS
    ...
```

La convention Python est : fonctions d'abord, bloc `__main__` en dernier.
L'ordre actuel est trompeur pour un lecteur.

**Correction suggérée :** déplacer `plot_heuristics()` avant le bloc `if __name__ == "__main__":`.

---

### P4 — Emoji `✅` dans `plot_heuristics` (bug potentiel Windows)

**Fichier :** `analyse.py`, ligne 99

```python
print(f"✅ Graphique généré et sauvegardé sous : {filename}")
```

Sur Windows avec l'encodage `cp1252` (encodage par défaut du terminal),
ce caractère provoque une `UnicodeEncodeError`. Ce bug avait déjà été rencontré
en début de projet avec le caractère `→`.

**Correction suggérée :** remplacer `✅` par du texte simple, ex. `OK :`.

---

### P5 — `mode_instance` affiche toutes les configurations (inutilisable)

**Fichier :** `main.py`, lignes 43-47

```python
print(f"{len(pool)} configurations generees :")
for i, cfg in enumerate(pool):           # affiche TOUTES les configs
    capteurs = sorted(k + 1 for k in cfg)
    print(f"  u{i+1} = capteurs {capteurs}")
```

Avec `N_CONFIGS = 5000`, cela produirait des milliers de lignes. Même avec 30,
l'affichage exhaustif est peu utile sur les grandes instances.

**Correction suggérée :** afficher uniquement les 5 premières configs et résumer le reste,
ex. `... et 25 autres configurations`.

---

### P6 — Rapport PDF non mis à jour après ajout de HEF (incohérence)

**Fichier :** `rapport_capteurs.pdf` / `generer_rapport.py`

Le rapport mentionne **2 heuristiques** (Greedy + Aléatoire) alors que le code
en implémente désormais **3** (Greedy + HEF + Aléatoire). HEF est absent du
tableau de la Section 1 et des tableaux d'analyse.

**Correction suggérée :** mettre à jour `generer_rapport.py` pour intégrer HEF
dans le tableau des heuristiques et dans les tableaux de résultats.

---

### P7 — README.md non mis à jour (documentation incomplète)

**Fichier :** `README.md`

Le README ne mentionne pas :
- l'heuristique HEF et sa référence (Manju & Pujari 2011)
- le mode `--plot`
- la méthode `upper_bound()`
- la nouvelle syntaxe : `python main.py <fichier.txt> [greedy|hef|aleatoire]`

---

## Résumé par priorité

| Priorité | ID | Description |
|---|---|---|
| Critique | P1 | N_CONFIGS = 5000 trop élevé |
| Important | P2 | Imports dans la boucle for |
| Important | P3 | plot_heuristics après __main__ |
| Important | P4 | Emoji UnicodeEncodeError Windows |
| Important | P5 | Affichage de toutes les configs |
| Important | P6 | Rapport PDF non mis à jour (HEF absent) |
| Mineur | P7 | README non mis à jour |
