import flet as ft
import random
import math
import time

class AntColony:
    def __init__(self, distances, n_ants, n_best, n_iterations, decay, alpha=1, beta=2):
        self.distances = distances
        self.n_ants = n_ants
        self.n_best = n_best
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        self.meilleur_chemin= None
        self.meilleure_distance=math.inf

        n=len(self.distances)
        self.all_indices= range(n)
        self.pheromones = [[1.0 for j in range(n)] for i in range(n)]

    def calculer_distance_chemin(self, chemin):
        L=len(chemin)
        total=0
        for i in range(L-1):
            total += self.distances[chemin[i]][chemin[i+1]]
        return total
    

    def generer_tous_chemins(self):
        chemin=[random.randint(0, len(self.distances)-1)]
        while len(chemin)<len(self.distances):
            prochaines_probas = self.calculer_probabilites_mouvement(chemin)
            prochaine_ville = self.choisir_ville_suivante(prochaines_probas)
            chemin.append(prochaine_ville)
        
        return (chemin, self.calculer_distance_chemin(chemin))

    def calculer_probabilites_mouvement(self, chemin):
        derniere=chemin[-1]
        proba=[]
        for ville in self.all_indices:
            if ville in chemin:
                proba.append(0)
            else:
                pheromone= self.pheromones[derniere][ville] ** self.alpha
                heuristique = (1.0 / self.distances[derniere][ville]) ** self.beta
                proba.append(pheromone * heuristique)
        
        total = sum(proba)
        if total > 0:
            return [p / total for p in proba]
        else:
            return [0] * len(proba)
        
    def choisir_ville_suivante(self, probabilites):
        r = random.random()  # nombre aléatoire dans [0,1[
        cumul = 0.0
        for i, p in enumerate(probabilites):
            cumul += p
            if r <= cumul:
                return i
        
        return len(probabilites) - 1
            
    def deposer_pheromones(self, tous_chemins):
        L=sorted(tous_chemins)
        for chemin, distance in L[:self.n_best]:
            for i in range(len(chemin) - 1):
                ville1, ville2 = chemin[i], chemin[i+1]
                self.pheromones[ville1][ville2] += 1.0 / distance
    
    def evaporer_pheromones(self):
        n = len(self.pheromones)
        for i in range(n):
            for j in range(n):
                self.pheromones[i][j] *= self.decay
    
    def executer_iteration(self):
        
        # Générer les chemins pour toutes les fourmis
        tous_les_chemins = []
        for _ in range(self.n_ants):
            tous_les_chemins.append(self.generer_tous_chemins())
        
        # Trouver le meilleur chemin de cette itération
        meilleur_chemin_iteration = min(tous_les_chemins, key=lambda x: x[1])
        
        # Mettre à jour le meilleur chemin global
        if meilleur_chemin_iteration[1] < self.meilleure_distance:
            self.meilleur_chemin = meilleur_chemin_iteration[0]
            self.meilleure_distance = meilleur_chemin_iteration[1]
        
        # Déposer et évaporer les phéromones
        self.deposer_pheromones(tous_les_chemins)
        self.evaporer_pheromones()
        
        return meilleur_chemin_iteration

    def run(self, callback_maj, evenement_arret):
        
        for iteration in range(self.n_iterations):
            # Vérifier si l'arrêt a été demandé
            if evenement_arret.is_set():
                break
            
            # Exécuter une itération
            chemin_courant, distance_courante = self.executer_iteration()
            
            # Appeler le callback de mise à jour
            callback_maj(iteration,(chemin_courant, distance_courante),self.pheromones)
            
            # Petite pause pour permettre la mise à jour de l'interface
            time.sleep(0.1)

