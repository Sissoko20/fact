import streamlit as st
from firebase_admin_setup import db   # ton module qui initialise Firebase
from components.sidebar import render_sidebar

# -------------------------------
# Configuration de la page
# -------------------------------
st.set_page_config(page_title="Gestion des utilisateurs", page_icon="👥", layout="wide")

# -------------------------------
# Vérification d'authentification et rôle
# -------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Si non connecté → redirection
if not st.session_state["authenticated"]:
    st.warning("⚠️ Veuillez vous connecter d'abord.")
    st.switch_page("pages/Login.py")
    st.stop()

# Si connecté mais pas admin → redirection
if st.session_state.get("role") != "admin":
    st.error("⛔ Accès réservé aux administrateurs")
    st.switch_page("pages/Login.py")
    st.stop()

# -------------------------------
# Barre latérale
# -------------------------------
selected = render_sidebar(default_index=3)  # Admin actif

# -------------------------------
# Redirections via menu
# -------------------------------
if selected == "🏠 Tableau de bord":
    st.switch_page("app.py")
elif selected == "🧾 Factures":
    st.switch_page("pages/Previsualisation.py")
elif selected == "💰 Reçus":
    st.switch_page("pages/Previsualisation.py")
elif selected == "🔒 Déconnexion":
    st.session_state["authenticated"] = False
    st.info("✅ Déconnecté")
    st.switch_page("pages/Login.py")

# -------------------------------
# Contenu principal : Gestion des utilisateurs
# -------------------------------
st.title("👥 Gestion des utilisateurs")

# --- Formulaire d'inscription ---
st.subheader("🧾 Créer un nouvel utilisateur")
with st.form("signup_form"):
    email = st.text_input("Email")
    password = st.text_input("Mot de passe", type="password")
    role = st.selectbox("Rôle", ["user", "admin"])
    submit = st.form_submit_button("Créer le compte")

    if submit:
        if email and password:
            user_doc = {
                "email": email,
                "password": password,   # ⚠️ à hasher en production
                "role": role
            }
            db.collection("users").add(user_doc)
            st.success(f"✅ Utilisateur {email} créé avec rôle {role}")
        else:
            st.error("❌ Email et mot de passe requis")

# --- Liste des utilisateurs avec modification de rôle ---
st.subheader("📋 Liste des utilisateurs")
users = db.collection("users").stream()

for user in users:
    u = user.to_dict()
    user_id = user.id
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        st.write(f"📧 {u.get('email')}")
    with col2:
        st.write(f"Rôle actuel : {u.get('role')}")
    with col3:
        new_role = st.selectbox(
            f"Changer rôle ({u.get('email')})",
            ["user", "admin"],
            index=0 if u.get("role") == "user" else 1,
            key=f"role_{user_id}"
        )
        if st.button(f"✅ Appliquer ({u.get('email')})", key=f"apply_{user_id}"):
            db.collection("users").document(user_id).update({"role": new_role})
            st.success(f"🔄 Rôle de {u.get('email')} mis à jour en {new_role}")
            st.experimental_rerun()
