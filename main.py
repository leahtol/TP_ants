import flet as ft
import random
import math

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

        n = len(distances)
        self.all_indices= range(n)
        pheromones = [[1.0 for j in range(n)] for i in range(n)]

    def calculer_distance_chemin(self, chemin):
        L=len(chemin)
        total=0
        for i in range(L-1):
            total += self.distances[chemin[i]][chemin[i+1]]
        return total
    

    def generer_tous_chemins(self):
        chemin=[random.randint(0, len(distances)-1)]
        while len(chemin)<len(self.distances):
            prochaines_probas = self.calculer_probabilites_mouvement(chemin)
            prochaine_ville = self.choisir_prochaine_ville(prochaines_probas)
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

def main(page: ft.Page):
    page.title="Algorithme de colonies de fourmis"
    page.theme_mode=ft.ThemeMode.LIGHT
    page.padding=20

     #Champs de saisie pour les paramètres
    nodes=[]
    noeuds= ft.TextField(label='Nombre de noeuds', value='20', width=150)
    fourmis= ft.TextField(label='Nombre de fourmis', value='15', width=150)
    iterations= ft.TextField(label='Nombre de itérations', value='100', width=150)
    
    
    #affichage graphe

    box= ft.Container(width=600, height=500, bgcolor='lightblue', border=ft.Border.all(2,'blue'))
    titre= ft.Text("Paramètres de l'algorithme", size=24, weight="bold")
    status= ft.Text("Prêt à démarrer", size=16, color='green')

    #noeuds
    def generer_nodes():
        nonlocal nodes
        try:
            num_nodes = int(noeuds.value)
        except ValueError:
            num_nodes = 20
        
        nodes = []
        for _ in range(num_nodes):
            x = random.uniform(50, 550)
            y = random.uniform(50, 450)
            nodes.append((x, y))
        
        distances = calculer_distances()
        print(f"{len(nodes)} nœuds générés")
        print(f"Distance entre nœud 0 et 1 : {distances[0][1]:.2f}")
        dessiner_graphe()
    
    def dessiner_graphe():
        shapes = []
        for i, (x, y) in enumerate(nodes):

            cercle = ft.Container(
                width=20,
                height=20,
                bgcolor="green",
                border_radius=10,
                left=x - 10,  # Centrer le cercle
                top=y - 10,
                content=ft.Text(str(i), size=10, color="white"),
                alignment=ft.alignment.Alignment(0, 0)
            )
            shapes.append(cercle)
        
    # Mettre à jour le conteneur avec un Stack (empilement)
        box.content = ft.Stack(
            controls=shapes,
            width=600,
            height=500
        )
        page.update()
    
    def calculer_distances():
        n=int(noeuds.value)
        M = [] 
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(0)
                else:
                    # Distance euclidienne
                    dx = nodes[i][0] - nodes[j][0]
                    dy = nodes[i][1] - nodes[j][1]
                    distance = math.sqrt(dx * dx + dy * dy)
                    row.append(distance)
            M.append(row)
        return M
    # Bouton pour générer le graphe
    btn_generer = ft.Button(
        "Générer le Graphe",
        on_click=lambda e: generer_nodes()
    )
    page.add(ft.Column([titre, ft.Row([noeuds,fourmis,iterations]),btn_generer,ft.Divider(), status, box ]))
    generer_nodes()

if __name__ == "__main__":
    ft.run(main)


