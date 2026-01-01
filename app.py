import streamlit as st

st.set_page_config(page_title="Tableau de bord", page_icon="📊", layout="wide")

# Vérifier session via query params
params = st.query_params
if "auth" in params and params["auth"] == "true":
    st.session_state["authenticated"] = True
    st.session_state["role"] = params.get("role", "user")
    st.session_state["email"] = params.get("email", "")
else:
    st.session_state["authenticated"] = False
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

st.sidebar.markdown(f"👤 Connecté : {st.session_state['email']} ({st.session_state['role']})")

if st.sidebar.button("🔒 Déconnexion"):
    # Supprimer les query params
    st.query_params.clear()
    st.session_state["authenticated"] = False
    st.session_state["role"] = None
    st.session_state["email"] = None
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
