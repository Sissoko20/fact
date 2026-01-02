import streamlit as st
from streamlit_option_menu import option_menu

# -------------------------------
# Configuration de la page
# -------------------------------
st.set_page_config(page_title="Tableau de bord", page_icon="📊", layout="wide")

# -------------------------------
# Vérification d'authentification
# -------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.warning("⚠️ Veuillez vous connecter d'abord.")
    st.switch_page("pages/Login.py")  # fonctionne si Login.py existe dans pages/
    st.stop()

# -------------------------------
# Barre de navigation moderne
# -------------------------------
with st.sidebar:
    st.image("assets/logo.png", width=120)
    selected = option_menu(
        "Navigation",
        ["🏠 Tableau de bord", "🧾 Factures", "💰 Reçus", "👥 Utilisateurs", "🔒 Déconnexion"],
        icons=["house", "file-text", "cash", "people", "box-arrow-right"],
        menu_icon="cast",
        default_index=0,
    )

# -------------------------------
# Logique de navigation
# -------------------------------
if selected == "🏠 Tableau de bord":
    # Pas besoin de switch_page ici, tu es déjà dans app.py
    st.image("assets/logo.png", width=150)
    st.title("Bienvenue sur MABOU-INSTRUMED Facturation")

    st.subheader("⚙️ Actions rapides")
    col1, col2, col3,col4 = st.columns(4)

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
        st.markdown("### 👥 Analyse mes donnees")
        if st.button("🔑 Data_analyse"):
            st.switch_page("pages/Data_analyse.py")

    st.markdown("---")
    st.caption("© 2025 MABOU-INSTRUMED - Système de gestion des factures et reçus médicaux")

elif selected == "🧾 Factures":
    st.switch_page("pages/Previsualisation.py")

elif selected == "💰 Reçus":
    st.switch_page("pages/Previsualisation.py")

elif selected == "👥 Data_analys":
    st.switch_page("pages/Data_analyse.py")
    
elif selected == "👥 Utilisateurs":
    st.switch_page("pages/Admin.py")


elif selected == "🔒 Déconnexion":
    st.session_state["authenticated"] = False
    st.info("✅ Déconnecté")
    st.switch_page("pages/Login.py")
