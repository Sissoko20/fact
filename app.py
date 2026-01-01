import streamlit as st
import os

SESSION_FILE = "data/session.txt"

# -------------------------------
# Fonctions session persistante
# -------------------------------
def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            content = f.read().strip().split("|")
            if len(content) == 2 and content[0] == "authenticated":
                st.session_state["authenticated"] = True
                st.session_state["role"] = content[1]
            else:
                st.session_state["authenticated"] = False
    else:
        st.session_state["authenticated"] = False

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    st.session_state["authenticated"] = False
    st.session_state["role"] = None

# -------------------------------
# Configuration de la page
# -------------------------------
st.set_page_config(page_title="Tableau de bord", page_icon="📊", layout="wide")

# -------------------------------
# Vérification d'authentification
# -------------------------------
if "authenticated" not in st.session_state:
    load_session()

if not st.session_state.get("authenticated", False):
    st.switch_page("pages/Login.py")
    st.stop()

# -------------------------------
# Sidebar personnalisée
# -------------------------------
st.sidebar.image("assets/logo.png", width=100)
st.sidebar.markdown("### 📂 Navigation")
st.sidebar.page_link("app.py", label="🏠 Tableau de bord", icon="📊")
st.sidebar.page_link("pages/Previsualisation.py", label="🧾 Créer une facture / reçu")
st.sidebar.page_link("pages/Admin.py", label="👥 Gestion des utilisateurs")

if st.sidebar.button("🔒 Déconnexion"):
    clear_session()
    st.switch_page("pages/Login.py")

# -------------------------------
# Contenu principal
# -------------------------------
st.image("assets/logo.png", width=150)
st.title("Bienvenue sur MABOU-INSTRUMED Facturation")

st.subheader("⚙️ Actions rapides")
col1, col2, col3 = st.columns(3)

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

st.markdown("---")
st.caption("© 2025 MABOU-INSTRUMED - Système de gestion des factures et reçus médicaux")
