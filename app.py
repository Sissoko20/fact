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
# 👉 Bouton pour créer un compte
if st.button("🧾 Créer un compte"):
    st.switch_page("pages/Admin.py")
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
    st.image("assets/logo.png", width=150)
    st.title("Bienvenue sur MABOU-INSTRUMED Facturation")

    st.subheader("⚙️ Actions rapides")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🧾 Créer une facture")
        if st.button("➕ Nouvelle Facture"):
            selected = "🧾 Factures"

    with col2:
        st.markdown("### 💰 Créer un reçu")
        if st.button("➕ Nouveau Reçu"):
            selected = "💰 Reçus"

    with col3:
        st.markdown("### 👥 Gestion des utilisateurs")
        if st.button("🔑 Gérer les utilisateurs"):
            selected = "👥 Utilisateurs"

    st.markdown("---")
    st.caption("© 2025 MABOU-INSTRUMED - Système de gestion des factures et reçus médicaux")

elif selected == "🧾 Factures":
    st.title("Créer une facture")
    st.write("👉 Ici tu mets ton formulaire de facturation.")

elif selected == "💰 Reçus":
    st.title("Créer un reçu")
    st.write("👉 Ici tu mets ton formulaire de reçu.")

elif selected == "👥 Utilisateurs":
    st.title("Gestion des utilisateurs")
    st.write("👉 Ici tu mets ton interface Admin.")

elif selected == "🔒 Déconnexion":
    st.session_state["authenticated"] = False
    st.info("✅ Déconnecté")
    st.stop()
