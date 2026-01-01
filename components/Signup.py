import streamlit as st
from firebase_utils import create_user

st.set_page_config(page_title="Inscription", layout="wide")

# Initialiser l'état de session si besoin
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["role"] = None
    st.session_state["email"] = None

# Si déjà connecté → redirection
if st.session_state["authenticated"]:
    st.switch_page("pages/Home.py")
    st.stop()

st.title("🧾 Créer un compte")

with st.form("signup_form"):
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    role = st.selectbox("Rôle", ["user", "admin"])  # tu peux limiter à "user" si besoin
    submit = st.form_submit_button("S'inscrire")

    if submit:
        try:
            uid = create_user(email, password, role)
            st.session_state["authenticated"] = True
            st.session_state["role"] = role
            st.session_state["email"] = email
            st.success(f"✅ Compte créé ({role}), UID: {uid}")
            st.switch_page("pages/Home.py")
        except Exception as e:
            st.error(f"❌ Erreur lors de la création du compte: {e}")

# 👉 Bouton retour vers Connexion
if st.button("🔑 Déjà un compte ? Se connecter"):
    st.switch_page("pages/Login.py")
