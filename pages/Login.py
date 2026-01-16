import streamlit as st
from firebase_utils import verify_user

st.set_page_config(page_title="Connexion", layout="wide")

# Initialiser l'état de session
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["role"] = None
    st.session_state["email"] = None
    st.session_state["user_id"] = None

# Si déjà connecté → redirection
if st.session_state["authenticated"]:
    st.switch_page("app.py")
    st.stop()

st.title("🔑 Connexion")

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    submit = st.form_submit_button("Se connecter")

    if submit:
        # ⚡️ verify_user renvoie maintenant un dict {role, user_id, email}
        user_data = verify_user(email, password)

        if user_data:
            st.session_state["authenticated"] = True
            st.session_state["role"] = user_data["role"]
            st.session_state["email"] = user_data["email"]
            st.session_state["user_id"] = user_data["user_id"]

            st.success(f"✅ Connecté en tant que {user_data['role']}")
            st.switch_page("app.py")
        else:
            st.error("❌ Email ou mot de passe incorrect")
