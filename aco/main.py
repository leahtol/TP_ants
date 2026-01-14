import flet as ft
import random
import math
import time
import threading
from aco import AntColony

def main(page: ft.Page):
    """
    Main function for the Ant Colony Optimization algorithm page.
    
    Responsible for initializing the page elements, setting up the event handlers and running the algorithm.
    """
    page.title = "Algorithme de Colonie de Fourmis"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    
    # Variables pour le graphe
    nodes = []
    distances = []
    pheromones = []
    best_path = []
    iteration = 0
    running = False
    stop_event = threading.Event()
    
    # Contrôles UI - Paramètres d'entrée
    nodes_field = ft.TextField(label="Nombre de nœuds", value="10", width=150)
    ants_field = ft.TextField(label="Nombre de fourmis", value="30", width=150)
    best_field = ft.TextField(label="Meilleures fourmis", value="3", width=150)
    iterations_field = ft.TextField(label="Itérations", value="200", width=150)
    decay_field = ft.TextField(label="Décay", value="0.95", width=150)
    alpha_field = ft.TextField(label="Alpha", value="1", width=150)
    beta_field = ft.TextField(label="Beta", value="2", width=150)
    
    # Contrôles d'affichage
    graph_container = ft.Container(
        width=600,
        height=500,
        bgcolor="white",
        border=ft.Border.all(1, "black")
    )
    
    iteration_text = ft.Text("Itération: 0", size=16)
    pheromone_text = ft.Text("Phéromones: ", size=14)
    path_text = ft.Text("Meilleur chemin: ", size=14)
    status_text = ft.Text("Prêt", size=14, color="green")
    
    def generer_nodes():
        """
        Initialize the graph by generating a specified number of nodes and their corresponding distances and pheromones.
    
        The number of nodes is determined by the value of the nodes_field.
        If the value is not a valid integer, it defaults to 50.
    
        The nodes are randomly positioned within the bounds of the graph container.
        The distances and pheromones are then calculated based on the positions of the nodes.
        """
        nonlocal nodes, distances, pheromones
        try:
            num_nodes = int(nodes_field.value)
        except ValueError:
            num_nodes = 50
            
        nodes = []
        for _ in range(num_nodes):
            nodes.append((
                random.uniform(40, 560),
                random.uniform(40, 460)
            ))

        def calculer_distances():
            """Calcule la matrice des distances entre tous les nœuds"""
            distances = []
            for i in range(len(nodes)):
                row = []
                for j in range(len(nodes)):
                    if i == j:
                        row.append(0)
                    else:
                        # Distance euclidienne
                        dx = nodes[i][0] - nodes[j][0]
                        dy = nodes[i][1] - nodes[j][1]
                        distance = math.sqrt(dx * dx + dy * dy)
                        row.append(distance)
                distances.append(row)
            return distances
        
        distances = calculer_distances()
        
        # Initialiser la matrice des phéromones
        pheromones = [[1.0 for _ in range(len(nodes))] for _ in range(len(nodes))]
    
    def create_line(x1, y1, x2, y2, color, thickness):
        """Crée une ligne entre deux points en utilisant un Container avec rotation"""
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx*dx + dy*dy)
        angle = math.atan2(dy, dx)
        
        return ft.Container(
            width=length,
            height=thickness,
            bgcolor=color,
            left=x1,
            top=y1 - thickness/2,
            rotate=ft.Rotate(angle=angle, alignment=ft.alignment.Alignment(-1, 0))
        )
    
    def draw_graph():
        # Créer un conteneur avec Stack pour dessiner
        shapes = []
        
        # Dessiner les arêtes (phéromones)
        if pheromones and len(pheromones) > 0:
            max_pheromone = max(max(row) for row in pheromones) if pheromones else 1
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    if pheromones[i][j] > 0.1:  # Seuil minimal
                        opacity = min(1, pheromones[i][j] / max_pheromone)
                        thickness = max(1, (pheromones[i][j] / max_pheromone) * 3)

                        line = create_line(
                            nodes[i][0], nodes[i][1],
                            nodes[j][0], nodes[j][1],
                            ft.Colors.with_opacity(opacity, ft.Colors.BLUE),
                            thickness
                        )
                        shapes.append(line)
        
        # Dessiner le meilleur chemin
        if best_path:
            for i in range(len(best_path) - 1):
                start_idx = best_path[i]
                end_idx = best_path[i + 1]
                if start_idx < len(nodes) and end_idx < len(nodes):
                    line = create_line(
                        nodes[start_idx][0], nodes[start_idx][1],
                        nodes[end_idx][0], nodes[end_idx][1],
                        "red",
                        3
                    )
                    shapes.append(line)
        
        # Dessiner les nœuds
        for i, (x, y) in enumerate(nodes):
            shapes.append(
                ft.Container(
                    width=20,
                    height=20,
                    bgcolor="green",
                    border_radius=10,
                    left=x-10,
                    top=y-10,
                    content=ft.Text(str(i), size=10, color="white"),
                    alignment=ft.alignment.Alignment(0, 0)
                )
            )
        
        graph_container.content = ft.Stack(controls=shapes, width=600, height=500)
        page.update()
    
    def update_callback(iter_num, current_best_path, current_pheromones):
        """
        Called at the end of each iteration of the Ant Colony Optimization algorithm.
        
        Parameters
        ----------
        iter_num : int
            The current iteration number.
        current_best_path : tuple of int
            The best path found so far with its length as the second element.
        current_pheromones : list of lists of float
            The pheromones matrix after the current iteration.
        """
        nonlocal iteration, best_path, pheromones

        # Mettre à jour les variables
        iteration = iter_num
        best_path = current_best_path[0] if current_best_path else []
        pheromones = current_pheromones
        # Fonction pour mettre à jour l'UI dans le thread principal
        async def update_ui():
            iteration_text.value = f"Itération: {iteration}"
            if best_path:
                path_text.value = f"Meilleur chemin: {best_path} (longueur: {current_best_path[1]:.2f})"

            # Mettre à jour les informations sur les phéromones
            if pheromones and len(pheromones) > 0:
                avg_pheromone = sum(sum(row) for row in pheromones) / (len(nodes) * len(nodes))
                pheromone_text.value = f"Phéromones moyennes: {avg_pheromone:.4f}"

            draw_graph()

        # Exécuter la mise à jour dans le thread principal de Flet
        page.run_task(update_ui)

    def start_algorithm(e):
        """
        Démarre l'algorithme des fourmis.
        
        Met à jour l'état de l'application pour indiquer que l'algorithme est en cours d'exécution.
        Démare l'exécution de l'algorithme dans un thread.
        """
        nonlocal running, stop_event
        if not running:
            running = True
            stop_event.clear()
            start_btn.disabled = True
            stop_btn.disabled = False
            status_text.value = "En cours d'exécution..."
            status_text.color = "orange"
            page.update()
            
            def run_ants():
                """
                Démare l'algorithme des fourmis.
                
                L'algorithme des fourmis est un algorithme d'optimisation qui consiste à
                plusieurs fourmis qui partagent d'un point de départ et qui
                cherchent à trouver le chemin le plus court entre le point de
                départ et un point d'arrivée.
                
                Les paramètres de l'algorithme sont:
                - n_ants: le nombre de fourmis.
                - n_best: le nombre de fourmis qui sont pris en compte pour
                  mettre à jour les phéromones.
                - n_iterations: le nombre d'itérations.
                - decay: le facteur de décroissance des phéromones.
                - alpha: le poids de la phéromone lors de la prise de décision.
                - beta: le poids de la distance lors de la prise de décision.
                """
        
                try:
                    n_ants = int(ants_field.value)
                    n_best = int(best_field.value)
                    n_iterations = int(iterations_field.value)
                    decay = float(decay_field.value)
                    alpha = float(alpha_field.value)
                    beta = float(beta_field.value)
                except ValueError:
                    # Valeurs par défaut en cas d'erreur
                    n_ants = 30
                    n_best = 3
                    n_iterations = 200
                    decay = 0.95
                    alpha = 1
                    beta = 2
                
                colony = AntColony(
                    distances,
                    n_fourmis=n_ants,
                    n_meilleurs=n_best,
                    n_iterations=n_iterations,
                    decroissance=decay,
                    alpha=alpha,
                    beta=beta
                )
                colony.run(update_callback, stop_event)
                # Finaliser dans le thread principal
                async def finalize():
                    """
                    Finalize the Ant Colony Optimization algorithm.

                    Called when the algorithm has finished its execution.

                    Sets the running flag to False, enables the "Start" button, disables the "Stop" button, and updates the status text to "Terminé".
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
            
            # Créer un thread pour exécuter l'algorithme des fourmis en arrière-plan de l'interface utilisateur
            thread = threading.Thread(target=run_ants)
            # Démarrer le thread en tant que daemon pour qu'il se termine avec l'application
            thread.daemon = True
            # Démarrer le thread
            thread.start()
    
    def stop_algorithm(e):
        """
        Stop the Ant Colony Optimization algorithm.
    
        Called when the "Stop" button is clicked.
    
        Sets the stop event, disables the "Stop" button, enables the "Start" button, and updates the status text to "Arrêté".
        """
        nonlocal running
        running = False
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
        Restart the graph and reset all the parameters to their default values.
        Called when the "Nouveau Graphe" button is clicked.
        """
        nonlocal best_path, iteration, running
        running = False
        stop_event.set()
        generer_nodes()
        best_path = []
        iteration = 0
        iteration_text.value = "Itération: 0"
        path_text.value = "Meilleur chemin: "
        pheromone_text.value = "Phéromones: "
        status_text.value = "Prêt"
        status_text.color = "green"
        start_btn.disabled = False
        stop_btn.disabled = True
        draw_graph()
    
    # Initialisation
    generer_nodes()
    
    # Boutons
    start_btn = ft.Button("Démarrer", on_click=start_algorithm)
    stop_btn = ft.Button("Arrêter", on_click=stop_algorithm, disabled=True)
    restart_btn = ft.Button("Nouveau Graphe", on_click=restart_graph)
    
    # Layout avec paramètres
    page.add(
        ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Paramètres de l'algorithme:", size=16),
                    nodes_field,
                    ants_field,
                    best_field,
                    iterations_field,
                ]),
                ft.Column([
                    ft.Text("", size=16),  # Espaceur
                    decay_field,
                    alpha_field,
                    beta_field,
                ]),
                ft.Column([
                    ft.Text("Contrôles:", size=16),
                    ft.Row([start_btn, stop_btn]),
                    restart_btn,
                    status_text
                ])
            ]),
            ft.Divider(),
            iteration_text,
            pheromone_text,
            path_text,
            graph_container
        ])
    )
    
    draw_graph()

if __name__ == "__main__":
    ft.run(main)