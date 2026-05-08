# Simulation de Protocole MAC avec Exponential Backoff

## 📋 Vue d'ensemble

Ce projet simule un **protocole MAC (Medium Access Control)** avec algorithme **Exponential Backoff**. L'objectif est de modéliser comment plusieurs stations partagent un canal de communication sans collision, en utilisant des délais aléatoires progressifs.

---

## 🎯 Idée générale

### Le problème
- **N stations** veulent transmettre des paquets sur un **même canal**
- Si 2+ stations transmettent simultanément → **COLLISION** (perte de paquets)
- Comment éviter les collisions ?

### La solution : Exponential Backoff
Quand une collision se produit :
1. La station attend un délai aléatoire
2. Ce délai **double** à chaque collision successive
3. Après succès → retour à l'état initial

**Bénéfice :** Éloigne les tentatives de transmission, réduit les collisions

---

## ⚙️ Algorithme expliqué

### État et transitions
Chaque station maintient un **état i** (commence à i=1) :

```
Queue vide → Arrive un paquet
   ↓
État i = 1 → Attendre Exp(mean=2¹×τ)
   ↓
TRANSMISSION (1 unité de temps)
   ↓
Collision? → État i → i+1, attendre Exp(mean=2^i×τ)
Succès? → État i → 1, continuer
```

### Exemple concret
- **État 1** : délai moyen = 2×τ = 2 secondes
- **État 2** : délai moyen = 4×τ = 4 secondes (collision 1)
- **État 3** : délai moyen = 8×τ = 8 secondes (collision 2)
- **État 4** : délai moyen = 16×τ = 16 secondes (collision 3)

Les délais **doublent** à chaque collision !

---

## 📊 La loi exponentielle

### Formule mathématique
$$f(x) = \frac{1}{\mu} e^{-x/\mu}$$

où μ = mean (valeur moyenne)

### Propriétés clés
1. **Génère des durées aléatoires** très variables
   - Peuvent être très courtes ou très longues
   - Modélise des arrivals naturelles

2. **"Sans mémoire"** (memoryless)
   - Peu importe le temps passé
   - La durée restante suit toujours la même distribution
   - Idéal pour simuler des événements indépendants

3. **À x = μ** : 63.2% des durées ≤ mean

### Utilisation dans le code

**Inter-arrivées (paquets qui arrivent):**
```python
duree_exp(lam)  →  np.random.exponential(1/lam)
```
- Si λ = 0.2 → mean = 5 secondes
- Chaque paquet arrive après ~5 sec en moyenne

**Délais de backoff (après collision):**
```python
np.random.exponential((2**etats[s]) * tau)
```
- État i → délai moyen = 2^i × τ
- Délais augmentent exponentiellement

---

## 🔧 Utilisation

### Installation
```bash
pip install numpy
```

### Importer et utiliser
```python
from simulation import simulateur_mac

# Lancer une simulation
N = 5              # 5 stations
K = 10             # queue capacity
lam = 0.2          # taux d'arrivée (inter-arrivées moyennes = 1/0.2 = 5 sec)
tau = 1.0          # base backoff parameter

hist_debit, hist_moyen, taux_perte, debit_final = simulateur_mac(N, K, lam, tau)

print(f"Débit final: {debit_final:.4f} paquets/s")
print(f"Taux de perte: {taux_perte*100:.2f}%")
```

### Paramètres
| Paramètre | Description | Exemple |
|-----------|-------------|---------|
| `N` | Nombre de stations | 2-10 |
| `K` | Capacité de queue par station | 10 |
| `lam` (λ) | Taux d'arrivée par station | 0.1-0.6 |
| `tau` (τ) | Base backoff parameter | 1.0 |

### Sorties
- `hist_debit` : débit instantané n(t)/t au fil du temps
- `hist_moyen` : nombre moyen de paquets L(t) = n_cumul/t (Little's Law)
- `taux_perte` : % paquets perdus (queue full)
- `debit_final` : débit final après 20000 secondes

---

## 📈 Métriques clés

### Débit du système
$$d = \frac{\text{paquets succès}}{\text{temps total}}$$
- Plus N augmente → débit baisse (plus de collisions)
- Plus λ augmente → débit baisse (plus de charge)

### Taux de perte
$$\text{perte} = \frac{\text{paquets perdus (queue full)}}{\text{paquets entrés}}$$
- Dépend de K (capacité queue) et charge (λ)

### Nombre moyen dans le système (Little's Law)
$$L = \lambda W$$
où :
- L = nombre moyen de paquets en système
- λ = taux d'arrivée
- W = temps moyen en système

**Calcul via intégrale :**
$$L = \frac{1}{T} \int_0^T n(t) \, dt$$

Dans le code :
```python
n_cumul += n_paquets_systeme * (evt[0] - t)  # Accumule aire sous courbe
L_moyen = n_cumul / t_final
```

---

## 🔍 Structure du code

### Fonction principale
```python
def simulateur_mac(N, K, lam, tau):
    # Initialisation
    t = 1
    queues = {s: 0 for s in range(N)}           # Nb paquets par station
    etats = {s: 1 for s in range(N)}            # État backoff par station
    transmissions_en_cours = {}                  # Stations transmettant maintenant
    
    # Boucle principale (événements discrets)
    while echeancier and t < TEMPS_MAX:
        # Traiter événement le plus proche
        evt = heappop(echeancier)
        
        if evt[1] == "ARRIVEE":
            # Nouveau paquet arrive
            # Si queue non pleine → ajouter, sinon perdre
            # Si queue était vide → commencer transmission
            
        elif evt[1] == "DEBUT_EMISSION":
            # Détection collision
            if len(transmissions_en_cours) > 0:  # Quelqu'un déjà transmet
                collision = True
            # Ajouter à transmissions_en_cours
            
        elif evt[1] == "FIN_EMISSION":
            # Transmission finit
            if collision:
                # Attendre délai backoff (double)
            else:
                # Succès! Reset état, continuer queue
```

### Événements (Discrete Event Simulation)
1. **ARRIVEE** : Nouveau paquet pour une station
2. **DEBUT_EMISSION** : Station commence à transmettre
3. **FIN_EMISSION** : Transmission finie (1 sec), vérifier collision

### Structures de données
```python
queues = {0: 2, 1: 0, 2: 1, ...}           # Paquets en attente par station
etats = {0: 1, 1: 3, 2: 1, ...}            # État backoff (i) par station
transmissions_en_cours = {0: False, 2: True, ...}  # Qui transmet + collision?
echeancier = [(t1, type, s), (t2, type, s), ...]  # Heap d'événements triés par temps
```

---

## 🧪 Exemple de résultat

Pour N=2, λ=0.2, τ=1.0, K=10 :
```
Débit final: 0.2535 paquets/s
Taux de perte: 36.50%
Nombre moyen en système: ~3.2 paquets
```

Plus N augmente :
- Débit diminue (plus d'interférence)
- Collisions plus fréquentes
- Délais de backoff augmentent

---

## 📚 Concept clé : Pourquoi Exponential Backoff ?

| Sans backoff | Avec backoff simple | Avec Exp. Backoff |
|---|---|---|
| Collision → relancer immédiat | Collision → attendre fixe (ex: 1s) | Collision → attendre 2^i×τ |
| Collisions massives | Certaines relances coincident | Probabilité collision ↓↓ |
| Débit très bas | Débit moyen | Débit élevé |

Le **doubling** (2^i) est crucial : après 3 collisions, une station attend ~8 secondes avant de retenter, laissant le temps aux autres de transmettre. C'est une **priorisation naturelle et équitable** !

---

## 📝 Notes

- Simulation démarre à **t=1** (pas t=0)
- Transmission dure **1 unité de temps**
- Queue max **K=10** paquets par station
- Simulation s'arrête à **TEMPS_MAX = 20000 secondes**
- Collision détectée au **DÉBUT** de transmission (pas à la fin)

---

## 📊 Résultats

Voir `Rapport_Simulation (2).pdf` pour :
- Graphes de convergence du débit
- Variation en fonction de λ
- N optimal pour maximiser débit
- Intervalles de confiance à 95%

---

## 📖 Références

- **Protocole Ethernet**: IEEE 802.3 - Exponential Backoff
- **Protocole WiFi**: IEEE 802.11 - DCF (Distributed Coordination Function)

---

**Version:** Projet 2026
**Protocole:** MAC avec Exponential Backoff
