import streamlit as st
from firebase_utils import create_user, get_user_role

st.set_page_config(page_title="User Manager", layout="wide")

# Init session
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["role"] = None

# Si déjà connecté → bascule vers app
if st.session_state["authenticated"]:
    st.switch_page("app.py")
    st.stop()

st.title("👥 Gestion des utilisateurs")

st.subheader("🧾 Créer un compte")
with st.form("create_account"):
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
            if "EMAIL_EXISTS" in str(e):
                st.warning("⚠️ Cet email existe déjà. Essayez de vous connecter ci-dessous.")
            else:
                st.error(f"❌ Erreur: {e}")

st.subheader("🔑 Se connecter")
with st.form("login"):
    login_email = st.text_input("Email (connexion)")
    login_password = st.text_input("Mot de passe (connexion)", type="password")
    login_submit = st.form_submit_button("Se connecter")

    if login_submit:
        role = get_user_role(login_email)
        if role:
            st.session_state["authenticated"] = True
            st.session_state["role"] = role
            st.success(f"✅ Connecté en tant que {role}")
            st.switch_page("app.py")
        else:
            st.error("❌ Utilisateur introuvable")
