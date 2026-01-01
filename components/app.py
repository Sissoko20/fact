import streamlit as st
from PIL import Image

# -------------------------------
# Configuration de la page
# -------------------------------
st.set_page_config(page_title="MABOU-INSTRUMED", page_icon="🧾", layout="wide")

# -------------------------------
# Logo + Titre
# -------------------------------
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("assets/logo.png", width=80)
with col_title:
    st.markdown("## MABOU-INSTRUMED Facturation")

st.markdown("---")

# -------------------------------
# Authentification
# -------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.switch_page("Login.py")
    st.stop()

# -------------------------------
# Menu de navigation pro
# -------------------------------
st.sidebar.image("assets/logo.png", width=100)
st.sidebar.markdown("### 📂 Navigation")
st.sidebar.page_link("app.py", label="🏠 Accueil", icon="🏠")
st.sidebar.page_link("pages/Previsualisation.py", label="🧾 Créer une facture / reçu")
st.sidebar.page_link("pages/Signup.py", label="👥 Gestion des utilisateurs")

# Bouton déconnexion
if st.sidebar.button("🔒 Déconnexion"):
    st.session_state["authenticated"] = False
    st.switch_page("Login.py")

# -------------------------------
# Contenu principal
# -------------------------------
st.markdown("### Bienvenue 👋")
st.write("Pour MABOU-Facturation de vos factures et reçus, sécurisée et adaptée à vos besoins.")
