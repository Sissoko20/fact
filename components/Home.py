import streamlit as st
from components.sidebar import sidebar_navigation

# -------------------------------
# Configuration de la page
# -------------------------------
st.set_page_config(page_title="Gestion de Factures", layout="wide")

# -------------------------------
# Afficher la sidebar personnalisée
# -------------------------------

# -------------------------------
# Vérification d'authentification
# -------------------------------
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("pages/Login.py")
    st.stop()

# -------------------------------
# Contenu principal
# -------------------------------
st.image("assets/logo.png", width=150)
st.title("Bienvenue sur MABOU-INSTRUMED Facturation")

# -------------------------------
# Actions rapides
# -------------------------------
st.subheader("⚙️ Actions rapides")

col1, col2, col3 = st.columns(3)

# ---- Colonne 1 : Facture ----
with col1:
    st.markdown("### 🧾 Créer une facture")
    if st.button("➕ Nouvelle Facture"):
        st.switch_page("pages/Previsualisation.py")

# ---- Colonne 2 : Reçu ----
with col2:
    st.markdown("### 💰 Créer un reçu")
    if st.button("➕ Nouveau Reçu"):
        st.switch_page("pages/Previsualisation.py")

# ---- Colonne 3 : Gestion utilisateurs ----
with col3:
    st.markdown("### 👥 Gestion des utilisateurs")
    if st.button("🔑 Gérer les utilisateurs"):
        st.switch_page("pages/Signup.py")

# -------------------------------
# Footer / Informations
# -------------------------------
st.markdown("---")
st.caption("© 2025 MABOU-INSTRUMED - Système de gestion des factures et reçus médicaux")
