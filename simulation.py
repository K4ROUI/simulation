import heapq
import numpy as np
import matplotlib.pyplot as plt
import math

def duree_exp(p):
    """Génère une durée selon une loi exponentielle de taux p."""
    return np.random.exponential(1/p)

# ==========================================
# VARIABLES GLOBALES ET PARAMÈTRES PAR DÉFAUT
# ==========================================
TEMPS_MAX = 20000  # Temps max de simulation

# ==========================================
# MOTEUR DE SIMULATION
# ==========================================
def simulateur_mac(N, K, lam, tau):
    """
    Simule le protocole MAC avec Exponential Backoff.
    Structure calquée sur la correction du TP (départ à t=1).
    """
    # Variables d'état global
    t = 1  # <--- On commence à 1 (Comme le prof)
    n_success = 0
    n_lost = 0
    n_paquets_systeme = 0
    n_cumul = 0 
    
    queues = {s: 0 for s in range(N)}
    etats = {s: 1 for s in range(N)} 
    transmissions_en_cours = {}
    
    historique_debit = []
    historique_moyen = []
    echeancier = []
    
    # Initialisation : on programme la toute première arrivée à partir de t=1
    for s in range(N):
        heapq.heappush(echeancier, (t + duree_exp(lam), "ARRIVEE", s))
        
    # --- BOUCLE PRINCIPALE ---
    while echeancier and t < TEMPS_MAX:
        # 1. On récupère les données à afficher (AVANT de changer le temps)
        # Plus besoin de vérifier si t>0 puisqu'on commence à t=1 !
        historique_debit.append((t, n_success / t))
        historique_moyen.append((t, n_cumul / t))
        
        # 2. On extrait l'événement le plus proche dans le temps
        evt = heapq.heappop(echeancier)
        
        # 3. On traite l'évolution de l'intégrale (aire sous la courbe)
        n_cumul += n_paquets_systeme * (evt[0] - t)
        
        # 4. On met à jour la date
        t = evt[0]
        s = evt[2] 
        
        # =======================================================
        # TRAITEMENT DE L'ÉVÉNEMENT (équivalent du 'match evt[1]:')
        # =======================================================
        if evt[1] == "ARRIVEE":
            # On calcule la date d'arrivée du prochain client
            heapq.heappush(echeancier, (t + duree_exp(lam), "ARRIVEE", s))
            
            if queues[s] < K:
                queues[s] += 1
                n_paquets_systeme += 1
                
                # Si la file était vide, on commence l'émission
                if queues[s] == 1:
                    etats[s] = 1 
                    attente = np.random.exponential((2**etats[s]) * tau)
                    heapq.heappush(echeancier, (t + attente, "DEBUT_EMISSION", s))
            else:
                n_lost += 1 
                
        elif evt[1] == "DEBUT_EMISSION":
            collision = False
            # Détection de collision
            if len(transmissions_en_cours) > 0:
                collision = True
                for autre_s in transmissions_en_cours:
                    transmissions_en_cours[autre_s] = True
                    
            transmissions_en_cours[s] = collision
            # Un service dure 1 unité de temps
            heapq.heappush(echeancier, (t + 1.0, "FIN_EMISSION", s))
            
        elif evt[1] == "FIN_EMISSION":
            a_eu_collision = transmissions_en_cours.pop(s)
            
            if a_eu_collision:
                # ECHEC
                attente = np.random.exponential((2**etats[s]) * tau)
                etats[s] += 1 
                heapq.heappush(echeancier, (t + attente, "DEBUT_EMISSION", s))
            else:
                # SUCCES
                n_success += 1
                queues[s] -= 1
                n_paquets_systeme -= 1
                etats[s] = 1 
                
                if queues[s] > 0:
                    attente = np.random.exponential((2**etats[s]) * tau)
                    heapq.heappush(echeancier, (t + attente, "DEBUT_EMISSION", s))
                    
    # on retourne les statistiques mesurées
    total_entres = n_success + n_lost + n_paquets_systeme
    taux_perte = n_lost / total_entres if total_entres > 0 else 0
    debit_final = n_success / t
    
    return historique_debit, historique_moyen, taux_perte, debit_final

# (La partie avec le if __name__ == "__main__": pour les graphiques reste exactement la même qu'avant)


# ==========================================
# EXÉCUTION ET GÉNÉRATION DES GRAPHIQUES
# ==========================================
if __name__ == "__main__":
    print(f"--- DÉBUT DE LA SIMULATION (TEMPS_MAX = {TEMPS_MAX}) ---")

    # ---------------------------------------------------------
    # PARTIE 1 : Évolution temporelle (Convergence)
    # ---------------------------------------------------------
    print("\n1. Simulation temporelle en cours (enregistrement brut intégral)...")
    N_fixe, K_fixe, lam_fixe, tau_fixe = 5, 10, 0.1, 1.0
    hist_d, hist_m, perte, debit_limite = simulateur_mac(N_fixe, K_fixe, lam_fixe, tau_fixe)
    
    print(f"-> Nombre de points enregistrés dans la liste : {len(hist_d)}")
    print(f"-> Taux de paquets perdus observé : {perte*100:.2f} %")
    
    temps_d, val_d = zip(*hist_d)
    temps_m, val_m = zip(*hist_m)

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(temps_d, val_d, label="Débit instantané n(t)/t")
    plt.axhline(y=debit_limite, color='r', linestyle='--', label=f"Limite d = {debit_limite:.4f}")
    plt.title(f"Convergence du débit (N={N_fixe}, λ={lam_fixe})")
    plt.xlabel("Temps")
    plt.ylabel("Débit")
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(temps_m, val_m, color="orange")
    plt.title("Nombre moyen de clients dans le système")
    plt.xlabel("Temps")
    plt.ylabel("Moyenne (L)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # ---------------------------------------------------------
    # PARTIE 2 : Impact du taux d'arrivée (Variation de Lambda)
    # ---------------------------------------------------------
    print("\n2. Calcul de l'impact de Lambda en cours...")
    valeurs_lambda = np.linspace(0.05, 0.6, 10)
    debits_lambda = []
    
    for l in valeurs_lambda:
        _, _, _, d = simulateur_mac(N_fixe, K_fixe, l, tau_fixe)
        debits_lambda.append(d)

    plt.figure(figsize=(8, 5))
    plt.plot(valeurs_lambda, debits_lambda, marker='o', color='green')
    plt.title(f"Débit d(N,K,λ,τ) en fonction de la charge λ (N={N_fixe})")
    plt.xlabel("Taux d'arrivée par station (λ)")
    plt.ylabel("Débit du système")
    plt.grid(True)
    plt.show()

    # ---------------------------------------------------------
    # PARTIE 2B : Convergence pour différentes valeurs de Lambda
    # ---------------------------------------------------------
    print("\n2B. Génération des courbes de convergence pour différents λ...")
    lambdas_etude = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for idx, lam_etude in enumerate(lambdas_etude):
        hist_d_lam, hist_m_lam, perte_lam, debit_lam = simulateur_mac(N_fixe, K_fixe, lam_etude, tau_fixe)
        temps_d_lam, val_d_lam = zip(*hist_d_lam)
        
        axes[idx].plot(temps_d_lam, val_d_lam, linewidth=2, color='blue')
        axes[idx].axhline(y=debit_lam, color='r', linestyle='--', label=f"d = {debit_lam:.4f}")
        axes[idx].set_title(f"λ = {lam_etude} | Perte = {perte_lam*100:.1f}%")
        axes[idx].set_xlabel("Temps")
        axes[idx].set_ylabel("Débit n(t)/t")
        axes[idx].grid(True, alpha=0.3)
        axes[idx].legend()
    
    # Masquer le 6ème subplot vide
    axes[5].axis('off')
    
    plt.suptitle("Impact de λ sur la convergence du débit (N=5, K=10, τ=1.0)", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()

    # ---------------------------------------------------------
    # PARTIE 3 : Impact de N et Intervalle de Confiance à 95%
    # ---------------------------------------------------------
    print("\n3. Recherche du N optimal (Intervalle de confiance 95%)...")
    lam_test = 0.2  
    valeurs_N = range(2, 12)
    nb_replications = 5  
    
    moyennes_debit_N = []
    intervalles_confiance = []
    
    meilleur_N = 0
    meilleur_debit = 0

    for n in valeurs_N:
        echantillons = []
        for _ in range(nb_replications):
            _, _, _, d = simulateur_mac(n, K_fixe, lam_test, tau_fixe)
            echantillons.append(d)
            
        moyenne = np.mean(echantillons)
        ecart_type = np.std(echantillons, ddof=1)
        marge_erreur = 1.96 * (ecart_type / math.sqrt(nb_replications))
        
        moyennes_debit_N.append(moyenne)
        intervalles_confiance.append(marge_erreur)
        
        if moyenne > meilleur_debit:
            meilleur_debit = moyenne
            meilleur_N = n
            
        print(f"  -> Pour N={n} : Débit moyen = {moyenne:.4f} ± {marge_erreur:.4f}")

    print(f"\n🏆 CONCLUSION : Le N optimal maximisant le débit est N = {meilleur_N}")
    
    plt.figure(figsize=(8, 5))
    plt.errorbar(valeurs_N, moyennes_debit_N, yerr=intervalles_confiance, marker='s', 
                 capsize=5, color='purple', ecolor='red')
    plt.title(f"Débit en fonction du nombre de stations N (λ={lam_test})")
    plt.xlabel("Nombre de stations (N)")
    plt.ylabel("Débit du système")
    plt.grid(True)
    plt.show()
    
    print("\n--- FIN DE LA SIMULATION ---")