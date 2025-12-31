import streamlit as st
from firebase_utils import create_user

st.set_page_config(page_title="Créer un compte", layout="wide")

# Appliquer le style global

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["role"] = None

if st.session_state["authenticated"]:
    st.switch_page("app.py")
    st.stop()

st.title("🧾 Créer un compte")

with st.form("signup_form"):
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    role = st.selectbox("Rôle", ["user", "admin"])
    submit = st.form_submit_button("Créer le compte")

    if submit:
        try:
            uid = create_user(email, password, role)
            st.session_state["authenticated"] = True
            st.session_state["role"] = role
            st.success(f"✅ Compte créé (UID: {uid}, rôle: {role})")
            st.switch_page("app.py")
        except Exception as e:
            st.error(f"❌ Erreur: {e}")

st.markdown("👉 Déjà inscrit ? [Se connecter](2_Login)")
