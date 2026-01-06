import flet as ft
import random
import math

class Student:
    def __init__(self, first_name: str, last_name: str):
        self.first_name=first_name
        self.last_name=last_name
        self.matiere={}
        pass


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


