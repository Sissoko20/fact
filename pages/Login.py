import streamlit as st

st.set_page_config(page_title="Connexion", layout="wide")

# Initialiser l'état de session
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["role"] = None
    st.session_state["email"] = None

# Si déjà connecté → redirection
if st.session_state["authenticated"]:
    st.switch_page("pages/Home.py")
    st.stop()

st.title("🔑 Connexion")

# Charger les rôles depuis secrets.toml
roles = st.secrets["roles"]

def get_role(email: str) -> str:
    if email in roles.get("admin", []):
        return "admin"
    elif email in roles.get("user", []):
        return "user"
    return "guest"

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")  # champ placeholder
    submit = st.form_submit_button("Se connecter")

    if submit:
        role = get_role(email)
        if role != "guest":
            st.session_state["authenticated"] = True
            st.session_state["role"] = role
            st.session_state["email"] = email
            st.success(f"✅ Connecté en tant que {role}")
            st.switch_page("pages/Home.py")
        else:
            st.error("❌ Utilisateur introuvable ou non autorisé")

# 👉 Bouton pour créer un compte
if st.button("🧾 Créer un compte"):
    st.switch_page("pages/Signup.py")
