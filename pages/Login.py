import streamlit as st
from firebase_utils import get_user_role

st.set_page_config(page_title="Connexion", layout="wide")

# Initialiser l'état de session
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["role"] = None
    st.session_state["email"] = None

# Si déjà connecté → redirection
if st.session_state["authenticated"]:
    st.switch_page("app.py")
    st.stop()

st.title("🔑 Connexion")

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")  # champ placeholder
    submit = st.form_submit_button("Se connecter")

    if submit:
        role = get_user_role(email)  # 🔥 récupère le rôle depuis Firestore
        if role:
            st.session_state["authenticated"] = True
            st.session_state["role"] = role
            st.session_state["email"] = email
            st.success(f"✅ Connecté en tant que {role}")
            st.switch_page("app.py")
        else:
            st.error("❌ Utilisateur introuvable ou rôle non défini")

# 👉 Bouton pour créer un compte
if st.button("🧾 Créer un compte"):
    st.switch_page("pages/Admin.py")
