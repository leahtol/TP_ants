import flet as ft
import random
import math
import time
import threading
from aco import AntColony


def main(page: ft.Page):
    page.title="Algorithme de colonies de fourmis"
    page.theme_mode=ft.ThemeMode.LIGHT
    page.padding=20

     #Champs de saisie pour les paramètres
    nodes=[]
    distances = []
    pheromones = []
    best_path = []
    iteration = 0
    running = False
    stop_event = threading.Event()
    noeuds= ft.TextField(label='Nombre de noeuds', value='20', width=150)
    fourmis= ft.TextField(label='Nombre de fourmis', value='15', width=150)
    iterations= ft.TextField(label='Nombre de itérations', value='100', width=150)
    best_field = ft.TextField(label="Meilleures fourmis", value="3", width=150)
    decay_field = ft.TextField(label="Décay", value="0.95", width=150)
    alpha_field = ft.TextField(label="Alpha", value="1", width=150)
    beta_field = ft.TextField(label="Beta", value="2", width=150)
        
    
    #affichage graphe

    box= ft.Container(width=600, height=500, bgcolor='White', border=ft.Border.all(2,'blue'))
    titre= ft.Text("Paramètres de l'algorithme", size=24, weight="bold")
    status= ft.Text("Prêt à démarrer", size=16, color='green')
    iteration_text = ft.Text("Itération: 0", size=16)
    pheromone_text = ft.Text("Phéromones moyennes: ", size=14)
    path_text = ft.Text("Meilleur chemin: ", size=14)

    #noeuds

    def generer_nodes():
        nonlocal nodes, distances, pheromones
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
        n=len(nodes)
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
    
    distances = calculer_distances()
    pheromones = [[1.0 for _ in range(len(nodes))] for _ in range(len(nodes))]

    dessiner_graphe()
    # Bouton pour générer le graphe
    btn_generer = ft.Button(
        "Générer le Graphe",
        on_click=lambda e: generer_nodes()
    )
    page.add(ft.Column([titre, ft.Row([noeuds,fourmis,iterations]),btn_generer,ft.Divider(), status, box ]))
    generer_nodes()

    def create_line(x1, y1, x2, y2, color, thickness):
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        angle = math.atan2(dy, dx)

        return ft.Container(
            width=length,
            height=thickness,
            bgcolor=color,
            left=x1,
            top=y1 - thickness / 2,
            rotate=ft.Rotate(
                angle=angle,
                alignment=ft.alignment.Alignment(-1, 0)
            )
        )
    
    def draw_graph():

        # Liste de formes graphiques à afficher dans le Stack
        shapes = []
        
        if pheromones and len(pheromones) > 0:
            # Valeur maximale des phéromones (pour normalisation)
            max_pheromone = max(max(row) for row in pheromones) if pheromones else 1

            # Parcours de toutes les paires de nœuds
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    # Seuil minimal pour éviter l’encombrement visuel
                    if pheromones[i][j] > 0.1:
                        # Opacité proportionnelle à la quantité de phéromones
                        opacity = min(1, pheromones[i][j] / max_pheromone)

                        # Épaisseur proportionnelle aux phéromones
                        thickness = max(1, (pheromones[i][j] / max_pheromone) * 3)

                        # Création de la ligne entre les deux nœuds
                        line = create_line(
                            nodes[i][0], nodes[i][1],
                            nodes[j][0], nodes[j][1],
                            ft.Colors.with_opacity(opacity, ft.Colors.BLUE),
                            thickness
                        )
                        shapes.append(line)
        
        if best_path:
            for i in range(len(best_path) - 1):
                start_idx = best_path[i]
                end_idx = best_path[i + 1]

                # Vérification de sécurité
                if start_idx < len(nodes) and end_idx < len(nodes):
                    line = create_line(
                        nodes[start_idx][0], nodes[start_idx][1],
                        nodes[end_idx][0], nodes[end_idx][1],
                        "red",   # Couleur du meilleur chemin
                        3        # Épaisseur renforcée
                    )
                    shapes.append(line)
        
        # ==========================
        # Dessin des nœuds (villes)
        # ==========================
        for i, (x, y) in enumerate(nodes):
            shapes.append(
                ft.Container(
                    width=20,
                    height=20,
                    bgcolor="green",
                    border_radius=10,   # Cercle
                    left=x - 10,
                    top=y - 10,
                    content=ft.Text(str(i), size=10, color="white"),
                    alignment=ft.alignment.Alignment(0, 0)
                )
            )
        
        # Mise à jour du conteneur graphique
        graph_container.content = ft.Stack(controls=shapes, width=600, height=500)
        page.update()
    
    def update_callback(iter_num, current_best_path, current_pheromones):
        """
        Callback appelé par l’algorithme à chaque itération
        pour mettre à jour l’interface graphique.
        """
        nonlocal iteration, best_path, pheromones

        # Mise à jour des variables globales
        iteration = iter_num
        best_path = current_best_path[0] if current_best_path else []
        pheromones = current_pheromones

        async def update_ui():
            # Affichage du numéro d’itération
            iteration_text.value = f"Itération: {iteration}"

            # Affichage du meilleur chemin et de sa longueur
            if current_best_path:
                path_text.value = (
                    f"Meilleur chemin: {best_path} "
                    f"(longueur: {current_best_path[1]:.2f})"
                )

            # Calcul de la moyenne des phéromones
            avg = sum(sum(row) for row in pheromones) / (len(nodes) ** 2)
            pheromone_text.value = f"Phéromones moyennes: {avg:.4f}"

            # Redessiner le graphe
            dessiner_graphe()

        # Lancement asynchrone pour ne pas bloquer l’UI
        page.run_task(update_ui)

    def start_algorithm(e):
        nonlocal running
        # Empêche un double lancement
        if running:
            return

        running = True
        stop_event.clear()

        # Mise à jour de l’interface
        start_btn.disabled = True
        stop_btn.disabled = False
        status_text.value = "En cours d'exécution..."
        status_text.color = "orange"
        page.update()

    def run_ants():
        try:
            # Création de la colonie de fourmis
            colony = AntColony(
                distances,
                int(ants_field.value),
                int(best_field.value),
                int(iterations_field.value),
                float(decay_field.value),
                float(alpha_field.value),
                float(beta_field.value),
            )
        except ValueError:
            # Valeurs par défaut en cas d’erreur utilisateur
            colony = AntColony(distances, 15, 3, 100, 0.95, 1, 2)

        # Lancement de l’algorithme
        colony.run(update_callback, stop_event)

        async def finalize():
            """
            Finalize the Ant Colony Optimization algorithm
            Called when the algorithm has finished its execution
            """
            nonlocal running
            running = False
            # Enable the "Start" button and disable the "Stop" button
            start_btn.disabled = False
            stop_btn.disabled = True
            # Update the status text
            status_text.value = "Terminé"
            status_text.color = "green"

            page.update()

        page.run_task(finalize)

    # Thread pour exécution non bloquante
    threading.Thread(target=run_ants, daemon=True).start()

    def stop_algorithm(e):
    
        nonlocal running
        # Set the stop event to signal the algorithm to stop
        stop_event.set()
        # Disable the "Stop" button and enable the "Start" button
        start_btn.disabled = False
        stop_btn.disabled = True
        # Update the status text
        status_text.value = "Arrêté"
        status_text.color = "red"
        # Update the page
        page.update()


    def restart_graph(e):
        """
        Réinitialise complètement le graphe et l’interface.
        """
        nonlocal iteration, best_path, running

        running = False
        stop_event.set()

        # Réinitialisation des variables
        iteration = 0
        best_path = []

        # Réinitialisation de l’UI
        iteration_text.value = "Itération: 0"
        path_text.value = "Meilleur chemin: "
        pheromone_text.value = "Phéromones moyennes: "
        status_text.value = "Prêt"
        status_text.color = "green"

        # Disable the "Stop" button and enable the "Start" button
        start_btn.disabled = False
        stop_btn.disabled = True

        # Génération de nouveaux nœuds
        generer_nodes()




if __name__ == "__main__":
    ft.run(main)


