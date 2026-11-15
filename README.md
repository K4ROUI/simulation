# Simulation d'un protocole MAC avec backoff exponentiel

**Projet universitaire — réseaux informatiques · Python · simulation à événements discrets**

Ce dépôt contient un **simulateur pédagogique de partage d'un canal entre plusieurs stations**. Chaque station reçoit des paquets, les place dans une file d'attente et tente de les transmettre. Lorsque deux émissions se chevauchent, le modèle enregistre une collision et programme de nouvelles tentatives avec un **temps d'attente aléatoire de moyenne croissante**.

Il permet d'étudier l'influence du **nombre de stations N**, du **taux d'arrivée λ**, de la **capacité de file K** et du **paramètre de backoff τ** sur le débit et les pertes liées à la saturation des files.

> Il s'agit d'un **modèle MAC simplifié**, pas d'une implémentation conforme d'Ethernet IEEE 802.3 ou du Wi-Fi IEEE 802.11. Aucune performance réseau physique n'est mesurée.

## Démarrer en quelques minutes

Prévoir **Python 3.10 ou plus récent** et installer les dépendances :

```bash
python -m pip install -r requirements.txt
```

Pour exécuter le programme historique avec ses graphiques interactifs :

```bash
python simulation.py
```

Pour obtenir une exécution **reproductible**, fixer une graine et une durée :

```bash
python exemple_reproductible.py --graine 2026 --horizon 3000
```

Pour générer une étude reproductible en fonction de λ, des fichiers CSV et des graphiques :

```bash
python analyse_lambda.py --graine 2026 --repetitions 5 --horizon 3000
```

Le dossier `resultats/` est généré localement et ignoré par Git ; les valeurs numériques affichées sont issues de **chaque exécution réelle**, et non d'un résultat codé en dur.

## Paramètres

| Paramètre | Sens | Exemple |
| --- | --- | --- |
| `N` | Nombre de stations | 5 |
| `K` | Capacité maximale de la file par station | 10 |
| `lam` (λ) | Taux d'arrivée des paquets *par station* | 0,1 |
| `tau` (τ) | Paramètre de base du temps d'attente | 1,0 |
| `TEMPS_MAX` | Horizon de simulation dans le code original | 20 000 |

Les arrivées sont tirées avec `np.random.exponential(1 / lam)`, donnant un temps moyen entre arrivées de `1 / λ`. Un paquet déjà dans la file reste à transmettre ; une **nouvelle arrivée** est comptée comme perdue lorsque la file est pleine.

## Fonctionnement du simulateur

Les événements planifiés dans une **file de priorité** (`heapq`) sont :

1. `ARRIVEE` — réception d'un paquet par une station ;
2. `DEBUT_EMISSION` — début de transmission et test de chevauchement ;
3. `FIN_EMISSION` — succès ou collision, puis éventuelle retransmission.

Chaque transmission occupe **une unité de temps** dans le modèle. Le délai de backoff suit une loi exponentielle de moyenne `2^i × τ`, où `i` est l'état de la station. **Le code commence à l'état 1 et incrémente cet état après le tirage du délai suivant une collision** : la première retransmission conserve donc la moyenne `2τ`, avant une augmentation aux collisions suivantes.

Voir [la lecture critique du modèle](docs/modele-et-limites.md).

## API Python

```python
import numpy as np
from simulation import simulateur_mac

np.random.seed(2026)  # reproductibilité
historique_debit, historique_moyen, taux_perte, debit_final = simulateur_mac(
    N=5, K=10, lam=0.1, tau=1.0
)

print("Débit final du modèle :", debit_final)
print("Part d'arrivées perdues :", taux_perte)
```

La fonction renvoie :

- `historique_debit` : paires `(temps, succès_cumulés / temps)`, **débit cumulé moyen**, et non débit instantané ;
- `historique_moyen` : paires `(temps, aire_de_l'occupation / temps)`, approximation du **nombre moyen de paquets dans le système** ;
- `taux_perte` : fraction des arrivées rejetées parce que leur file était pleine ; **les collisions ne sont pas comptées directement comme pertes définitives** ;
- `debit_final` : nombre de transmissions réussies divisé par le temps final du simulateur.

Le code historique démarre à `t = 1`. Il traite l'événement suivant tant que la boucle a commencé avant `TEMPS_MAX` ; le dernier événement peut donc dépasser légèrement l'horizon configuré.

## Analyse reproductible

Le script `analyse_lambda.py` :

- utilise une **graine initiale explicite** et des graines distinctes pour chaque répétition ;
- exécute plusieurs simulations pour chaque valeur de λ ;
- calcule le **débit moyen simulé** et la **perte moyenne par saturation** ;
- exporte un CSV et deux graphiques dans `resultats/`.

Les courbes ne sont pas universelles : elles dépendent du modèle, des paramètres, de l'horizon et des graines. **On ne peut pas affirmer que le débit baisse toujours quand N ou λ augmente.**

## Vérifications

```bash
python -m unittest discover -s tests -v
```

Les tests portent sur la **forme des sorties, les bornes des statistiques, la reproductibilité à graine fixée et l'ordre chronologique des historiques**. Ils ne prouvent ni l'exactitude d'un modèle de norme IEEE, ni les performances d'un réseau réel.

## Fichiers

```text
simulation.py                # Simulateur original et graphiques historiques
exemple_reproductible.py     # Exécution avec paramètres et graine explicites
analyse_lambda.py            # Répétitions et export CSV/PNG
requirements.txt             # Dépendances Python
tests/test_simulation.py     # Vérifications automatiques simples
docs/modele-et-limites.md    # Hypothèses et limites techniques
Rapport_Simulation.pdf       # Rapport académique conservé
projet_2026.pdf              # Document académique conservé
```

Les deux PDF sont fournis à titre de documents du projet ; leur contenu n'est pas requis pour exécuter le code.

**Ce que démontre ce projet :** programmation Python, simulation événementielle, gestion d'une file de priorité, métriques de réseaux et analyse expérimentale. Les scripts historiques restent inchangés.
