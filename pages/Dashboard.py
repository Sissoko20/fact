import streamlit as st
from components.sidebar import sidebar_navigation

st.set_page_config(page_title="Gestion de Factures", layout="wide")

# Vérifier si connecté
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("pages/2_Login.py")
    st.stop()

# Menu global
theme = sidebar_navigation()

# Thème clair/sombre
if theme == "Clair":
    st.markdown("""<style>body{background:#fff;color:#000}</style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style>body{background:#1e1e1e;color:#fff}</style>""", unsafe_allow_html=True)

# Contenu principal
st.image("assets/logo.png", width=150)
st.title("Bienvenue sur MABOU-INSTRUMED Facturation")

st.subheader("⚙️ Actions rapides")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🧾 Créer une facture")
    if st.button("➕ Nouvelle Facture"):
        st.switch_page("pages/4_Previsualisation.py")

with col2:
    st.markdown("### 💰 Créer un reçu")
    if st.button("➕ Nouveau Reçu"):
        st.switch_page("pages/4_Previsualisation.py")

with col3:
    st.markdown("### 👥 Gestion des utilisateurs")
    if st.button("🔑 Gérer les utilisateurs"):
        st.switch_page("pages/3_Signup.py")
