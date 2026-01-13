import flet as ft
import random
import math
import time
import threading
from aco import AntColony


def main(page: ft.Page):
    # =====================
    # Configuration page
    # =====================
    page.title = "Algorithme de colonies de fourmis"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # =====================
    # Variables globales
    # =====================
    nodes = []
    distances = []
    pheromones = []
    best_path = []
    iteration = 0
    running = False
    stop_event = threading.Event()

    # =====================
    # Champs paramètres
    # =====================
    noeuds = ft.TextField(label="Nombre de nœuds", value="20")
    fourmis = ft.TextField(label="Nombre de fourmis", value="15")
    iterations_field = ft.TextField(label="Nombre d’itérations", value="100")
    best_field = ft.TextField(label="Meilleures fourmis", value="3")
    decay_field = ft.TextField(label="Décay", value="0.95")
    alpha_field = ft.TextField(label="Alpha", value="1")
    beta_field = ft.TextField(label="Beta", value="2")

    # =====================
    # Textes d’état
    # =====================
    iteration_text = ft.Text("Itération : 0")
    pheromone_text = ft.Text("Phéromones moyennes : ")
    path_text = ft.Text("Meilleur chemin : ")
    status_text = ft.Text("Prêt", color="green")

    # =====================
    # Zone graphe
    # =====================
    graph_container = ft.Container(
        width=620,
        height=520,
        border=ft.Border.all(2, ft.Colors.BLUE),
        border_radius=8,
        content=ft.Stack(width=600, height=500),
    )

    # =====================
    # Fonctions graphe
    # =====================
    def calculer_distances():
        n = len(nodes)
        M = []
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(0)
                else:
                    dx = nodes[i][0] - nodes[j][0]
                    dy = nodes[i][1] - nodes[j][1]
                    row.append(math.sqrt(dx * dx + dy * dy))
            M.append(row)
        return M

    def generer_nodes():
        nonlocal nodes, distances, pheromones
        try:
            n = int(noeuds.value)
        except ValueError:
            n = 20

        nodes = [(random.uniform(50, 550), random.uniform(50, 450)) for _ in range(n)]
        distances = calculer_distances()
        pheromones = [[1.0 for _ in range(n)] for _ in range(n)]
        dessiner_graphe()

    def create_line(x1, y1, x2, y2, color, thickness):
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx * dx + dy * dy)
        angle = math.atan2(dy, dx)
        return ft.Container(
            width=length,
            height=thickness,
            bgcolor=color,
            left=x1,
            top=y1 - thickness / 2,
            rotate=ft.Rotate(angle=angle, alignment=ft.alignment.Alignment(-1, 0)),
        )

    def dessiner_graphe():
        shapes = []

        # Phéromones
        if pheromones:
            max_ph = max(max(row) for row in pheromones)
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    if pheromones[i][j] > 0.1:
                        opacity = pheromones[i][j] / max_ph
                        thickness = max(1, opacity * 3)
                        shapes.append(
                            create_line(
                                nodes[i][0],
                                nodes[i][1],
                                nodes[j][0],
                                nodes[j][1],
                                ft.Colors.with_opacity(opacity, ft.Colors.BLUE),
                                thickness,
                            )
                        )

        # Meilleur chemin
        for i in range(len(best_path) - 1):
            a, b = best_path[i], best_path[i + 1]
            shapes.append(
                create_line(
                    nodes[a][0],
                    nodes[a][1],
                    nodes[b][0],
                    nodes[b][1],
                    "red",
                    3,
                )
            )

        # Nœuds
        for i, (x, y) in enumerate(nodes):
            shapes.append(
                ft.Container(
                    width=20,
                    height=20,
                    bgcolor="green",
                    border_radius=10,
                    left=x - 10,
                    top=y - 10,
                    content=ft.Text(str(i), size=10, color="white"),
                    alignment=ft.alignment.Alignment(0, 0),
                )
            )

        graph_container.content = ft.Stack(controls=shapes, width=600, height=500)
        page.update()

    # =====================
    # Callback ACO
    # =====================
    def update_callback(iter_num, current_best, current_pheromones):
        nonlocal iteration, best_path, pheromones

        iteration = iter_num
        pheromones = current_pheromones
        if (
            isinstance(current_best, tuple)
            and isinstance(current_best[0], list)
        ):
            best_path = current_best[0]
        else:
            best_path = []
            path_text.value = f"Meilleur chemin : {best_path} (L={current_best[1]:.2f})"

        iteration_text.value = f"Itération : {iteration}"
        avg = sum(sum(row) for row in pheromones) / (len(nodes) ** 2)
        pheromone_text.value = f"Phéromones moyennes : {avg:.4f}"
        dessiner_graphe()

    # =====================
    # Boutons contrôle
    # =====================
    def start_algorithm(e):
        nonlocal running
        if running:
            return

        running = True
        stop_event.clear()
        status_text.value = "En cours..."
        status_text.color = "orange"
        start_btn.disabled = True
        stop_btn.disabled = False
        page.update()

        threading.Thread(target=run_ants, daemon=True).start()

    def run_ants():
        nonlocal running
        colony = AntColony(
            distances,
            int(fourmis.value),
            int(best_field.value),
            int(iterations_field.value),
            float(decay_field.value),
            float(alpha_field.value),
            float(beta_field.value),
        )
        colony.run(update_callback, stop_event)

        running = False
        status_text.value = "Terminé"
        status_text.color = "green"
        start_btn.disabled = False
        stop_btn.disabled = True
        page.update()

    def stop_algorithm(e):
        stop_event.set()
        status_text.value = "Arrêté"
        status_text.color = "red"
        start_btn.disabled = False
        stop_btn.disabled = True
        page.update()

    btn_generer = ft.Button("Générer le graphe", on_click=lambda e: generer_nodes())
    start_btn = ft.Button("Démarrer", on_click=start_algorithm)
    stop_btn = ft.Button("Arrêter", on_click=stop_algorithm, disabled=True)

    # =====================
    # Layout
    # =====================
    params_panel = ft.Container(
        width=320,
        padding=15,
        border=ft.Border.all(1, ft.Colors.GREY_300),
        border_radius=8,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Text("Paramètres", size=20, weight="bold"),
                noeuds,
                fourmis,
                iterations_field,
                best_field,
                decay_field,
                alpha_field,
                beta_field,
                ft.Divider(),
                btn_generer,
                start_btn,
                stop_btn,
            ],
        ),
    )

    info_bar = ft.Container(
        padding=10,
        border=ft.Border.all(1, ft.Colors.GREY_300),
        border_radius=8,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[iteration_text, pheromone_text, path_text, status_text],
        ),
    )

    page.add(
        ft.Column(
            spacing=20,
            controls=[
                ft.Text("Algorithme de colonies de fourmis", size=26, weight="bold"),
                ft.Row(
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[params_panel, graph_container],
                ),
                info_bar,
            ],
        )
    )

    generer_nodes()


if __name__ == "__main__":
    ft.run(main)