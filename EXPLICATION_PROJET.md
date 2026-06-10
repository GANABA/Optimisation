# Synthèse du Projet : Maximisation de la Durée de Vie d'un Réseau de Capteurs (MLCP)

Ce document a pour but de résumer à l'équipe l'ensemble des travaux, des constats et des choix d'architecture réalisés sur ce projet d'optimisation.

---

## 1. L'enjeu du projet (Le Problème MLCP)
L'objectif est de surveiller un ensemble de zones $M$ à l'aide de capteurs $N$ qui fonctionnent sur batteries. Pour économiser l'énergie, on n'allume pas tous les capteurs en même temps : on crée des **"configurations élémentaires"** (des groupes de capteurs juste suffisants pour couvrir toutes les zones, sans aucun capteur inutile). 

Le but mathématique est de déterminer **combien de temps on doit activer chaque configuration** pour que le réseau tienne le plus longtemps possible avant qu'une zone ne tombe dans le noir.

---

## 2. Étape 1 : L'Approche Heuristique (Branche `exercices`)
Dans un premier temps, nous avons utilisé une approche "statique" en 2 étapes :

1. **Générer un pool de configurations**. Nous avons implémenté trois heuristiques :
   - **Glouton (Greedy)** : Recrute toujours le capteur qui couvre le plus grand nombre de zones restantes.
   - **HEF (High-Energy-First)** : Recrute le capteur qui a la plus grosse batterie initiale.
   - **Aléatoire** : Prend des capteurs totalement au hasard pour couvrir les zones.
2. **Résoudre avec `PuLP`**. Le solveur trouve la meilleure combinaison de temps d'activation parmi le pool qu'on lui a fourni.

### Le constat empirique
L'analyse graphique a prouvé que les heuristiques déterministes (Greedy et HEF) manquent cruellement de diversité. Sur de grands réseaux, elles génèrent en boucle les mêmes configurations. L'Aléatoire fonctionne beaucoup mieux car la diversité est le carburant du solveur mathématique. 
Cependant, l'aléatoire s'effondre lui aussi sur les réseaux massifs, ne trouvant qu'une durée de vie de 1% à 10% par rapport à l'idéal théorique.

---

## 3. Étape 2 : L'Approche Exacte (Branche `v2-column-generation`)
Pour résoudre les très grands réseaux, nous avons implémenté la méthode de la **Génération de Colonnes**. Plutôt que de générer des configurations à l'aveugle, on rend le système intelligent grâce à une boucle itérative :

- **Le Programme Maître** résout le problème avec un tout petit pool de départ. Il identifie les "points de friction" (les capteurs dont les batteries se vident trop vite) et génère des **valeurs duales ($\pi_k$)** agissant comme des pénalités mathématiques.
- **Le Problème de Pricing** récupère ces pénalités et résout un sous-problème (Set Cover pondéré) pour inventer *exactement* la configuration parfaite qui contourne les capteurs pénalisés.
- Dès qu'il la trouve, il l'ajoute au Programme Maître, et on recommence. 

**Le Résultat** : Le solveur n'a plus besoin de générer 50 000 configurations hasardeuses. Quelques dizaines générées sur mesure suffisent à faire exploser le score pour atteindre l'optimum.

---

## 4. La Borne Supérieure et le "Tailing-Off Effect"
Afin de jauger nos résultats, nous avons codé la **Borne Supérieure** (la durée de vie maximale dictée par la zone la plus fragile).

- Sur les instances classiques, la Génération de Colonnes prouve sa supériorité en atteignant **100% de la Borne**.
- Sur l'instance titanesque (`maxi_test_1.txt`, 1000 capteurs), nous avons observé l'effet de **"Tailing-Off"** (la longue traîne). L'algorithme trouve très vite une solution à plus de 75% de la borne (là où les heuristiques stagnaient à 1%), mais met un temps exponentiel à converger pour les derniers pourcents d'amélioration. Ce phénomène illustre une des grandes limites pratiques de l'optimisation exacte sur des NP-difficiles relaxés.
