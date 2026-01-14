import random
import time
import threading

class AntColony:
    def __init__(self, distances, n_fourmis, n_meilleurs, n_iterations, decroissance, alpha : float=1, beta : float =2):
        """
        Initialise la colonie de fourmis.

        Paramètres :
        - distances : matrice des distances entre les villes
        - n_fourmis : nombre de fourmis par itération
        - n_meilleurs : nombre de meilleurs chemins qui déposent des phéromones
        - n_iterations : nombre d'itérations de l'algorithme
        - decay : taux d'évaporation des phéromones (entre 0 et 1)
        - alpha : importance des phéromones (α)
        - beta : importance de l'heuristique (β)
        """
        self.distances = distances
        self.pheromones = [[1.0 for _ in range(len(distances))] for _ in range(len(distances))]
        self.n_fourmis = n_fourmis
        self.n_meilleurs = n_meilleurs
        self.n_iterations = n_iterations
        self.decroissance = decroissance
        self.alpha = alpha
        self.beta = beta
        self.tous_indices = range(len(distances))
        self.meilleur_chemin = None
        self.meilleure_distance = float('inf')

    def run(self, callback_maj, evenement_arret):
        """
        Exécute l'algorithme d'optimisation par colonie de fourmis.

        Paramètres
        ----------
        callback_maj : callable
            Une fonction de callback à appeler après chaque itération.
            La fonction doit prendre trois paramètres : l'itération actuelle,
            le meilleur chemin trouvé jusqu'à présent, et la matrice des phéromones.
        evenement_arret : threading.Event
            Un événement à définir pour arrêter l'algorithme.

        Retourne
        -------
        None
        """
        for iteration in range(self.n_iterations):
            # Vérifier si l'arrêt a été demandé
            if evenement_arret.is_set():
                break
            
            # Générer tous les chemins
            tous_chemins = self.generer_tous_chemins()
            # Déposer les phéromones
            self.deposer_pheromones(tous_chemins)
            # Trouver le meilleur chemin
            self.meilleur_chemin = min(tous_chemins, key=lambda x: x[1])
            # Mettre à jour la meilleure distance
            if self.meilleur_chemin[1] < self.meilleure_distance:
                self.meilleure_distance = self.meilleur_chemin[1]
            # Décroissance des phéromones
            self.pheromones = [[p * self.decroissance for p in ligne] for ligne in self.pheromones]

            # Appeler le callback de mise à jour
            callback_maj(iteration, self.meilleur_chemin, self.pheromones)
            # Pause pour permettre la mise à jour de l'interface utilisateur
            time.sleep(0.2*len(self.distances)/10)

    def calculer_distance_chemin(self, chemin):
        """
        Calcule la distance totale d'un chemin.

        Paramètres
        ----------
        chemin : list
            Une liste d'indices représentant un chemin.

        Retourne
        -------
        int
            La distance totale du chemin.
        """
        total = 0
        for i in range(len(chemin) - 1):
            total += self.distances[chemin[i]][chemin[i+1]]
        return total

    def generer_tous_chemins(self):
        """
        Génère tous les chemins possibles en utilisant l'algorithme d'optimisation par colonie de fourmis.

        Retourne
        -------
        list
            Une liste de tuples, où chaque tuple contient un chemin et sa distance totale.
        """
        tous_chemins = []
        # Générer les chemins pour chaque fourmi
        for _ in range(self.n_fourmis):
            # Commencer par une ville aléatoire
            chemin = [random.randint(0, len(self.distances) - 1)]
            # Ajouter les autres villes
            while len(chemin) < len(self.distances):
                # Générer les probabilités de mouvement
                probabilites_mouvement = self.calculer_probabilites_mouvement(chemin)
                # Choisir la prochaine ville
                ville_suivante = self.choisir_ville_suivante(probabilites_mouvement)
                # Ajouter la ville choisie au chemin
                chemin.append(ville_suivante)
            # Calculer la distance totale du chemin
            tous_chemins.append((chemin, self.calculer_distance_chemin(chemin)))
        return tous_chemins

    def calculer_probabilites_mouvement(self, chemin):
        """
        Calcule la probabilité de se déplacer vers chaque ville étant donné le chemin actuel.

        Paramètres
        ----------
        chemin : list
            Une liste d'indices représentant un chemin.

        Retourne
        -------
        list
            Une liste de probabilités, où chaque probabilité est la probabilité de se déplacer vers chaque ville étant donné le chemin actuel.
        """
        actuelle = chemin[-1]
        probabilites = []
        # Pour chaque ville, calculer la probabilité de mouvement
        for ville in self.tous_indices:
            # Si la ville est dans le chemin, la probabilité est nulle
            if ville in chemin:
                probabilites.append(0)
            else:
                # Phéromone^alpha * (1/distance)^beta
                pheromone = self.pheromones[actuelle][ville] ** self.alpha
                heuristique = (1.0 / self.distances[actuelle][ville]) ** self.beta
                # Ajouter la probabilité au tableau
                probabilites.append(pheromone * heuristique)
        # Sommer les probabilités pour la normalisation
        total = sum(probabilites)
        # Retourner les probabilités normalisées
        return [p / total for p in probabilites] if total > 0 else [0] * len(probabilites)

    def choisir_ville_suivante(self, probabilites):
        """
        Choisit la prochaine ville en fonction des probabilités données.

        Paramètres
        ----------
        probabilites : list
            Une liste de probabilités, où chaque probabilité est la probabilité de se déplacer vers chaque ville.

        Retourne
        -------
        int
            L'indice de la ville choisie comme prochaine ville.
        """
        r = random.random()
        total = 0
        for i, p in enumerate(probabilites):
            total += p
            if total >= r:
                return i
        return len(probabilites) - 1

    def deposer_pheromones(self, tous_chemins):
        """
        Dépose des phéromones sur les n_meilleurs chemins.

        Paramètres
        ----------
        tous_chemins : list
            Une liste de tuples, où chaque tuple contient un chemin et sa distance totale.

        Retourne
        -------
        None
        """
        chemins_tries = sorted(tous_chemins, key=lambda x: x[1])
        for chemin, distance in chemins_tries[:self.n_meilleurs]:
            for i in range(len(chemin) - 1):
                self.pheromones[chemin[i]][chemin[i+1]] += 1.0 #/ distance
    

if __name__ == "__main__":
    distances = [
        [0, 2, 9, 10],
        [1, 0, 6, 4],
        [15, 7, 0, 8],
        [6, 3, 12, 0]
    ]
    # Créer une instance de la colonie de fourmis
    colonie_fourmis = AntColony(distances, n_fourmis=3, n_meilleurs=5, n_iterations=100, decroissance=0.95, alpha=1, beta=2)
    
    def callback_maj(iteration, meilleur_chemin, pheromones):
        """
        Fonction de callback appeler après chaque itération.

        Paramètres
        ----------
        iteration : int
            L'itération actuelle.
        meilleur_chemin : tuple
            Le meilleur chemin trouvé jusqu'à présent.
        pheromones : list
            La matrice des phéromones.

        Retourne
        -------
        None
        """
        if iteration % 10 == 0:
            print(f"Itération {iteration}: Meilleur chemin {meilleur_chemin} avec distance {colonie_fourmis.meilleure_distance}")
            print("Matrice des phéromones:")
            for ligne in pheromones:
                print(ligne)

    # Créer un événement d'arrêt
    evenement_arret = threading.Event()
    # Exécuter l'algorithme dans le thread principal pour cet exemple
    colonie_fourmis.run(callback_maj, evenement_arret)
    # Meillere chemin trouvé
    print(f"Meilleur chemin trouvé : {colonie_fourmis.meilleur_chemin} avec une distance de {colonie_fourmis.meilleure_distance}")