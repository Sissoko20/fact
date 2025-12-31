# components/sidebar.py
import streamlit as st

def sidebar_navigation():
    st.sidebar.image("assets/logo.png", width=100)
    st.sidebar.title("📌 Navigation")

    if st.sidebar.button("🏠 Accueil", key="home"):
        st.switch_page("home.py")
    if st.sidebar.button("🧾 Facture", key="facture"):
        st.switch_page("pages/2_Previsualisation.py")
    if st.sidebar.button("💰 Reçu", key="recu"):
        st.switch_page("pages/2_Previsualisation.py")
    if st.sidebar.button("📊 Dashboard", key="dashboard"):
        st.switch_page("pages/Data_analyse.py")
    if st.sidebar.button("👥 Gestion des utilisateurs", key="users"):
        st.switch_page("pages/Admin.py")

    # Ligne de séparation
    st.sidebar.markdown("---")

    # Bouton Déconnexion affiché uniquement si connecté
    if "authenticated" in st.session_state and st.session_state["authenticated"]:
        if st.sidebar.button("🚪 Déconnexion", key="logout"):
            st.session_state["authenticated"] = False
            st.session_state["role"] = None
            st.switch_page("app.py")
