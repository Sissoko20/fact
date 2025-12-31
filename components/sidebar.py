import streamlit as st

def sidebar_navigation():
    with st.sidebar:
        st.markdown("## 🧭 Navigation")

        # Section Documents
        st.page_link("pages/Home.py", label="🏠 Accueil")
        st.page_link("pages/Previsualisation.py", label="🧾 Factures")
        st.page_link("pages/Previsualisation.py", label="💰 Reçus")

        st.markdown("---")

        # Section Analyse
        st.page_link("pages/Dashboard.py", label="📊 Dashboard")

        st.markdown("---")

        # Section Administration
        st.page_link("pages/Gestion.py", label="👥 Gestion utilisateurs")
        st.page_link("pages/Login.py", label="🔒 Déconnexion")

    # Tu peux retourner un paramètre si tu veux gérer un thème clair/sombre
    return "Sombre"
