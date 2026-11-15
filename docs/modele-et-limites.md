# Hypothèses et limites du modèle MAC

Cette page est fondée sur **le code de `simulation.py`**, pas sur des performances supposées du réseau.

## Hypothèses implémentées

- `N` stations partagent un même canal simulé.
- Les temps entre arrivées dans chaque station suivent une loi exponentielle de moyenne `1/lam`.
- Chaque station possède une file de capacité `K`.
- Un événement de transmission occupe **1 unité de temps**.
- Deux transmissions qui se chevauchent dans le modèle entraînent une collision ; la tentative sera reprogrammée.
- Le backoff est un **délai exponentiel** de moyenne `(2 ** etats[s]) * tau`.

### Particularité importante du backoff

Dans le code, `etats[s]` est initialisé à 1. Après une collision, le délai est d'abord **tiré avec l'état courant**, puis l'état est incrémenté. Par conséquent, la première tentative et la première retransmission peuvent avoir la **même moyenne 2τ**. Ce comportement ne correspond pas à la formulation simplifiée « double immédiatement après chaque collision ».

## Signification exacte des statistiques

**Débit :** `n_success / t` désigne le nombre total de réussites divisé par le temps courant depuis l'origine utilisée par le code. Malgré le libellé historique « débit instantané », cette courbe représente un **débit cumulé moyen**.

**Occupation moyenne :** `n_cumul / t` utilise l'aire sous l'occupation du système (accumulée à chaque événement). Ce n'est **pas** une mesure directe du temps d'attente moyen `W` : la loi de Little `L = λW` ne peut pas être vérifiée sans davantage d'informations.

**Pertes :** `n_lost` est incrémenté pour les **arrivées rejetées lorsque la file est pleine**. Une collision n'est pas une perte définitive : elle provoque ici une **retransmission**. Le « taux de perte » ne désigne donc pas la fraction de tentatives entrées en collision.

**Horizon :** la simulation démarre à `t = 1` et le code teste la condition `t < TEMPS_MAX` avant de prélever le prochain événement. L'événement final peut se situer **au-delà de TEMPS_MAX**. Les moyennes utilisent `t` et non `t - 1`.

## Interprétation des expériences

- Une graine de nombres aléatoires fixée rend les résultats d'une configuration reproductibles dans le même environnement, mais n'en fait pas une vérité générale.
- Une expérience à graine unique ne suffit pas à conclure à un comportement universel.
- Plusieurs répétitions, les paramètres exacts et les écarts-types permettent une discussion plus rigoureuse des tendances.
- Le code historique utilise `1.96 × s / √n` comme approximation d'une marge à 95 % pour **5 répétitions**. Avec un échantillon aussi petit, cette approximation normale est fragile ; une approche fondée sur Student serait généralement préférable si les hypothèses sont adaptées.
- Un « nombre optimal de stations » est **relatif à la plage et aux paramètres testés**, pas une propriété universelle du protocole.

## Rapport avec les normes réelles

Le simulateur est **inspiré par des mécanismes MAC et de retransmission**. Il ne reproduit pas fidèlement toutes les règles d'Ethernet CSMA/CD (fenêtres discrètes et créneaux) ou du Wi-Fi DCF/CSMA-CA (écoute du canal, contention, acquittements et temporisations). Il ne doit pas être utilisé pour prédire directement le débit ou la latence d'un réseau réel.

## Améliorations possibles (non réalisées ici)

- Ajouter des compteurs séparés de **collisions** et de **tentatives**.
- Comparer plusieurs politiques de backoff à charge identique.
- Ajouter des intervalles de confiance adaptés au nombre de répétitions.
- Étudier la validation par rapport à un modèle analytique connu.
- Clarifier la sémantique du temps et la gestion de l'événement franchissant l'horizon.

Ces pistes ne sont pas présentées comme déjà développées.
