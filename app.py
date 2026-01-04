import streamlit as st
from components.sidebar import render_sidebar, MENU_LINKS

st.set_page_config(page_title="Tableau de bord", page_icon="📊", layout="wide")

# Vérification d'authentification
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.warning("⚠️ Veuillez vous connecter d'abord.")
    st.switch_page("pages/Login.py")
    st.stop()

# Sidebar
selected = render_sidebar(default_index=0)

# Gestion des redirections
if selected == "🔒 Déconnexion":
    st.session_state["authenticated"] = False
    st.info("✅ Déconnecté")
    st.switch_page(MENU_LINKS[selected])
elif selected != "🏠 Tableau de bord":
    st.switch_page(MENU_LINKS[selected])

# 👉 Contenu principal du tableau de bord
if selected == "🏠 Tableau de bord":
    st.image("assets/logo.png", width=150)
    st.title("Bienvenue sur MABOU-INSTRUMED Facturation")

    st.subheader("⚙️ Actions rapides")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("### 🧾 Créer une facture")
        if st.button("➕ Nouvelle Facture"):
            st.switch_page("pages/Previsualisation.py")

    with col2:
        st.markdown("### 💰 Créer un reçu")
        if st.button("➕ Nouveau Reçu"):
            st.switch_page("pages/Previsualisation.py")

    with col3:
        st.markdown("### 👥 Gestion des utilisateurs")
        if st.button("🔑 Gérer les utilisateurs"):
            st.switch_page("pages/Admin.py")

    with col4:
        st.markdown("### 📊 Analyse des données")
        if st.button("🔑 Data Analyse"):
            st.switch_page("pages/Data_analyse.py")

    st.markdown("---")
    st.caption("© 2025 MABOU-INSTRUMED - Système de gestion des factures et reçus médicaux")
