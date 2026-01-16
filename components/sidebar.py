import streamlit as st
from streamlit_option_menu import option_menu

# Dictionnaire qui mappe chaque menu à une page cible
MENU_LINKS = {
    "🏠 Tableau de bord": "app.py",
    "Gerer mes factures": "pages/Data_analyse.py",
    "🧾 Factures": "pages/Previsualisation.py",
    "💰 Reçus": "pages/Previsualisation.py",
    "👥 Utilisateurs": "pages/Admin.py",
    "🔒 Déconnexion": "pages/Login.py",
}

def render_sidebar(default_index=0):
    """Affiche la barre latérale et retourne l'élément sélectionné."""
    with st.sidebar:
        st.image("assets/logo.png", width=120)
        selected = option_menu(
            "Navigation",
            list(MENU_LINKS.keys()),
            icons=["house", "bar-chart", "file-text", "cash", "people", "box-arrow-right"],
            menu_icon="cast",
            default_index=default_index,
        )
    return selected
