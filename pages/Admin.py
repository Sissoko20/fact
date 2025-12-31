import streamlit as st
from firebase_utils import create_user

st.set_page_config(page_title="Admin Dashboard", layout="wide")

# Vérifier si connecté et admin
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.switch_page("pages/2_Login.py")
    st.stop()

if st.session_state["role"] != "admin":
    st.error("❌ Accès réservé aux administrateurs.")
    st.switch_page("app.py")
    st.stop()

st.title("⚙️ Administration - Gestion des utilisateurs")

st.subheader("🧾 Créer un nouveau compte utilisateur")

with st.form("create_user_form"):
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    role = st.selectbox("Rôle", ["user", "admin"])
    submit = st.form_submit_button("Créer le compte")

    if submit:
        try:
            uid = create_user(email, password, role)
            st.success(f"✅ Compte créé avec UID: {uid} et rôle: {role}")
        except Exception as e:
            st.error(f"❌ Erreur lors de la création: {e}")

st.markdown("---")
st.info("ℹ️ Seul l'administrateur peut créer de nouveaux comptes.")
