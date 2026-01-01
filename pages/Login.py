import streamlit as st
import os

SESSION_FILE = "data/session.txt"

def save_session(role):
    with open(SESSION_FILE, "w") as f:
        f.write(f"authenticated|{role}")

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            content = f.read().strip().split("|")
            if len(content) == 2 and content[0] == "authenticated":
                st.session_state["authenticated"] = True
                st.session_state["role"] = content[1]
            else:
                st.session_state["authenticated"] = False
    else:
        st.session_state["authenticated"] = False

def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    st.session_state["authenticated"] = False
    st.session_state["role"] = None

# -------------------------------
# Initialisation session
# -------------------------------
if "authenticated" not in st.session_state:
    load_session()

if st.session_state.get("authenticated", False):
    st.success(f"✅ Déjà connecté en tant que {st.session_state['role']}")
    if st.button("🔒 Déconnexion"):
        clear_session()
        st.rerun()
else:
    st.title("🔑 Connexion")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        # Exemple simple : admin / user
        if username == "admin" and password == "admin123":
            save_session("admin")
            st.session_state["authenticated"] = True
            st.session_state["role"] = "admin"
            st.success("✅ Connecté comme administrateur")
            st.rerun()
        elif username == "user" and password == "user123":
            save_session("user")
            st.session_state["authenticated"] = True
            st.session_state["role"] = "user"
            st.success("✅ Connecté comme utilisateur")
            st.rerun()
        else:
            st.error("❌ Identifiants invalides")
