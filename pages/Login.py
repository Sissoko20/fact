import streamlit as st
import os

SESSION_FILE = "data/session.txt"

def save_session(role, email):
    """Sauvegarde la session dans un fichier local"""
    with open(SESSION_FILE, "w") as f:
        f.write(f"authenticated|{role}|{email}")

def load_session():
    """Recharge la session depuis le fichier local"""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE) as f:
            content = f.read().strip().split("|")
            if len(content) >= 2 and content[0] == "authenticated":
                st.session_state["authenticated"] = True
                st.session_state["role"] = content[1]
                st.session_state["email"] = content[2] if len(content) > 2 else None
            else:
                st.session_state["authenticated"] = False
    else:
        st.session_state["authenticated"] = False

def clear_session():
    """Supprime la session"""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    st.session_state["authenticated"] = False
    st.session_state["role"] = None
    st.session_state["email"] = None

# -------------------------------
# Initialisation session
# -------------------------------
if "authenticated" not in st.session_state:
    load_session()

if st.session_state.get("authenticated", False):
    st.success(f"✅ Déjà connecté en tant que {st.session_state['role']} ({st.session_state.get('email')})")
    if st.button("🔒 Déconnexion"):
        clear_session()
        st.rerun()
else:
    st.title("🔑 Connexion")
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        # Exemple simple : admin / user
        if email == "admin@mabou.com" and password == "admin123":
            save_session("admin", email)
            st.session_state["authenticated"] = True
            st.session_state["role"] = "admin"
            st.session_state["email"] = email
            st.success("✅ Connecté comme administrateur")
            st.rerun()
        elif email == "user@mabou.com" and password == "user123":
            save_session("user", email)
            st.session_state["authenticated"] = True
            st.session_state["role"] = "user"
            st.session_state["email"] = email
            st.success("✅ Connecté comme utilisateur")
            st.rerun()
        else:
            st.error("❌ Email ou mot de passe invalide")
