import flet as ft

def main(page: ft.Page):
    page.title="Algorithme de colonies de fourmis"
    page.theme_mode=ft.ThemeMode.LIGHT
    page.padding=20

     #Champs de saisie pour les paramètres

    noeuds= ft.TextField(label='Nombre de noeuds', value='20', width=150)
    fourmis= ft.TextField(label='Nombre de fourmis', value='15', width=150)
    iterations= ft.TextField(label='Nombre de itérations', value='100', width=150)

    #affichage graphe

    box= ft.Container(width=600, height=00, bgcolor='lightblue', border=ft.border.all(2,'blue'))
    titre= ft.Text("Paramètres de l'algorithme", size=24, weight="bold")
    status= ft.Text("Prêt à démarrer", size=16, color='green')
    page.add(ft.Column([titre, ft.Row([noeuds,fourmis,iterations]),ft.Divider(), status, box ], expand=True))

if __name__ == "__main__":
    ft.app(target=main)