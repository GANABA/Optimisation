# Rapport de Projet : Ordonnancement Adaptatif de Capteurs (MLCP)

**Module** : Techniques d'optimisation  
**Auteur** : [Votre Nom]

---

## 1. Construction des Configurations Élémentaires (Parties 2 & 3)

Le problème consiste à maximiser la durée de vie d'un réseau de capteurs en garantissant une couverture totale. Pour cela, nous générons des *configurations élémentaires* (ensembles minimaux de capteurs couvrant toutes les zones) et nous utilisons la Programmation Linéaire (librairie `PuLP`) pour trouver leur temps d'activation optimal ($t_u$).

Nous avons implémenté et comparé trois méthodes de construction de configurations :
1. **Greedy-Critique (inspiré de Cardei & Du, 2005)** : À chaque étape, on sélectionne le capteur couvrant le plus de zones restantes. 
2. **High-Energy-First (HEF) (Manju & Pujari, 2011)** : Variante gloutonne qui sélectionne en priorité le capteur ayant l'énergie résiduelle ($T_k$) la plus élevée pour préserver la durée de vie globale du réseau.
3. **Génération Aléatoire (Deschinkel, 2011)** : Approche stochastique qui construit des configurations au hasard. Les capteurs superflus sont ensuite retirés un à un pour rendre la configuration strictement élémentaire.

Pour aller plus loin et garantir la solution optimale, une méthode de **Génération de Colonnes** a été implémentée. Elle utilise les variables duales ($\pi_k$) du Programme Maître pour générer intelligemment de nouvelles configurations (via la résolution d'un Problème de Pricing) au lieu de se limiter à un pool statique.

---

## 2. Solutions Obtenues (Partie 4)

Les expérimentations ont été menées sur 5 instances de tailles variables. Le tableau ci-dessous présente la durée de vie optimale trouvée (avec un pool statique de 30 configurations pour les heuristiques), comparée à la **Borne Supérieure** théorique (capacité maximale absolue du réseau basée sur la zone la plus faible).

| Instance | N | M | Borne Sup. | Greedy | HEF | Aléatoire | Génération de Colonnes |
|---|---|---|---|---|---|---|---|
| `fichier-exemple` | 4 | 3 | 9.0 | 3.0 (33%) | 6.0 (67%) | 8.5 (94%) | **8.5 (94%)** |
| `moyen_test_2` | 20 | 10 | 104.0 | 13.0 (12%) | 19.0 (18%) | 104.0 (100%) | **104.0 (100%)** |
| `moyen_test_3` | 10 | 10 | 463.0 | 55.0 (12%) | 166.0 (36%) | 395.0 (85%) | **395.0 (85%)** |
| `gros_test_1` | 100 | 200 | 3437.0 | 42.0 (1%) | 196.0 (6%) | 954.3 (28%) | **2835.6 (83%)** |
| `maxi_test_1` | 1000 | 500 | 27245.0 | 42.0 (0%) | 197.0 (1%) | 1171.0 (4%) | **5869.1 (22%)** |

---

## 3. Analyse des Résultats (Partie 5)

L'analyse de ces résultats et du graphique d'évolution (`comparaison_heuristiques.png`) révèle plusieurs points fondamentaux :

1. **La diversité est la clé (Le succès de l'Aléatoire)** : De manière contre-intuitive, l'heuristique Aléatoire surpasse largement les heuristiques gloutonnes (Greedy et HEF). Les méthodes gloutonnes sont trop déterministes et génèrent un pool de configurations quasi-identiques (bloquant le solveur dans un optimum très faible). Le hasard, au contraire, fournit un pool extrêmement diversifié, offrant une multitude de combinaisons d'activation au Programme Linéaire.
2. **HEF vs Greedy** : La prise en compte de la batterie restante (HEF) améliore systématiquement la durée de vie par rapport au choix purement centré sur la couverture (Greedy), validant l'hypothèse de l'article de *Manju & Pujari*.
3. **L'apport critique de la Génération de Colonnes** : Sur les instances complexes (`gros_test_1` et `maxi_test_1`), se reposer sur un pool de configurations aléatoires n'est plus suffisant (seulement 4% à 28% de la borne). La Génération de Colonnes, en "inventant" itérativement les configurations manquantes idéales grâce aux coûts duaux, permet de multiplier par 3 à 5 la durée de vie trouvée !
4. **Influence du nombre de configurations** : La durée de vie croît de manière asymptotique avec la taille du pool initial $u$. Cependant, augmenter aveuglément ce nombre ralentit considérablement la résolution sans garantir d'atteindre l'optimum, ce qui justifie pleinement l'utilisation finale de la méthode de Génération de Colonnes pour clore le problème de manière exacte.
