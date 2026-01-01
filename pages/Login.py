import streamlit as st
from firebase_utils import get_user_role  # ta fonction Firestore

st.set_page_config(page_title="Connexion", layout="wide")

# Vérifier si déjà connecté via query params
params = st.query_params
if "auth" in params and params["auth"] == "true":
    st.session_state["authenticated"] = True
    st.session_state["role"] = params.get("role", "user")
    st.session_state["email"] = params.get("email", "")
    st.switch_page("app.py")
    st.stop()

# Initialiser session_state si vide
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["role"] = None
    st.session_state["email"] = None

st.title("🔑 Connexion")

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    submit = st.form_submit_button("Se connecter")

    if submit:
        role = get_user_role(email)  # 🔥 récupère le rôle depuis Firestore
        if role:
            st.session_state["authenticated"] = True
            st.session_state["role"] = role
            st.session_state["email"] = email

            # Sauvegarde dans l'URL (query params)
            st.query_params["auth"] = "true"
            st.query_params["role"] = role
            st.query_params["email"] = email

            st.success(f"✅ Connecté en tant que {role}")
            st.switch_page("app.py")
        else:
            st.error("❌ Utilisateur introuvable ou rôle non défini")

if st.button("🧾 Créer un compte"):
    st.switch_page("pages/Admin.py")
