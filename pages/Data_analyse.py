import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
from streamlit_option_menu import option_menu
from firebase_admin_setup import db

# -------------------------------
# Configuration générale
# -------------------------------
st.set_page_config(
    page_title="Analyse des données",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# Sécurité session
# -------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.error("⛔ Vous devez être connecté")
    st.switch_page("pages/Login.py")
    st.stop()

user_id = st.session_state.get("user_id")
role = st.session_state.get("role", "user")

# -------------------------------
# Sidebar navigation
# -------------------------------
with st.sidebar:
    st.image("assets/logo.png", width=120)
    selected = option_menu(
        "Navigation",
        [
            "🏠 Tableau de bord",
            "📊 Gerer vos factures",
            "🧾 Factures",
            "💰 Reçus",
            "👥 Utilisateurs",
            "🔒 Déconnexion"
        ],
        icons=["house", "bar-chart", "file-text", "cash", "people", "box-arrow-right"],
        default_index=1,
    )

# -------------------------------
# Navigation logique
# -------------------------------
if selected == "🏠 Tableau de bord":
    st.switch_page("app.py")

elif selected == "🧾 Factures":
    st.switch_page("pages/Previsualisation.py")

elif selected == "💰 Reçus":
    st.switch_page("pages/Previsualisation.py")

elif selected == "👥 Utilisateurs":
    if role == "admin":
        st.switch_page("pages/Admin.py")
    else:
        st.error("⛔ Accès réservé à l’administrateur")

elif selected == "🔒 Déconnexion":
    st.session_state.clear()
    st.success("✅ Déconnecté")
    st.switch_page("pages/Login.py")

# -------------------------------
# Titre principal
# -------------------------------
st.title("📊 Dashboard – Analyse des factures")

# -------------------------------
# Chargement des factures (USER UNIQUEMENT)
# -------------------------------
factures_ref = (
    db.collection("factures")
    .where("user_id", "==", user_id)
    .stream()
)

rows = [doc.to_dict() | {"id": doc.id} for doc in factures_ref]
df = pd.DataFrame(rows)

st.subheader("📄 Données chargées")
st.dataframe(df, use_container_width=True)

# -------------------------------
# Aperçu global
# -------------------------------
st.subheader("📊 Aperçu global")

required_cols = {"type", "montant"}

if not df.empty and required_cols.issubset(df.columns):
    df["montant"] = pd.to_numeric(df["montant"], errors="coerce").fillna(0)

    total_factures = df[df["type"] == "Facture de doit"]["montant"].sum()
    total_recus = df[df["type"] == "Reçu de Paiement"]["montant"].sum()
    total_global = df["montant"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💼 Factures", f"{total_factures:,.0f} FCFA")
    col2.metric("💰 Reçus", f"{total_recus:,.0f} FCFA")
    col3.metric("📊 Total", f"{total_global:,.0f} FCFA")
    col4.metric("📄 Documents", len(df))
else:
    st.info("Aucune donnée exploitable disponible")

# -------------------------------
# Historique filtré + Impayés
# -------------------------------
st.subheader("📑 Historique")

if not df.empty and "type" in df.columns:
    filtre = st.selectbox(
        "Filtrer par type",
        ["Tous"] + sorted(df["type"].unique()),
        key="filtre_type"   # ✅ clé unique
    )

    df_filtre = df if filtre == "Tous" else df[df["type"] == filtre]
    st.dataframe(df_filtre, use_container_width=True)

    # -------------------------------
# -------------------------------
# Liste des impayés en tableau + sélection
# -------------------------------
if {"reliquat", "montant_paye", "montant_total"}.issubset(df.columns):
    impayes = df[df["reliquat"] > 0]

    st.subheader("❌ Factures impayées")
    if impayes.empty:
        st.info("✅ Aucune facture impayée")
    else:
        # Tableau clair
        tableau_impayes = impayes[["id","client_name","client_phone","montant_total","montant_paye","reliquat"]]
        st.dataframe(tableau_impayes, use_container_width=True)

      # Sélection d'une facture par nom du client
facture_selectionnee = st.selectbox(
    "Sélectionnez une facture à solder",
    options=impayes["client_name"].tolist(),
    format_func=lambda x: f"{x} - Reliquat {impayes.loc[impayes['client_name']==x,'reliquat'].values[0]} CFA",
    key="facture_select"
)

if facture_selectionnee:
    # Récupérer la facture correspondante
    facture = impayes[impayes["client_name"] == facture_selectionnee].iloc[0]

    montant_paye_input = st.number_input(
        f"Montant payé (Reliquat: {facture['reliquat']} CFA)",
        min_value=0,
        max_value=int(facture["reliquat"]),
        step=100,
        key="montant_paye_input"
    )

    if st.button("Solder la facture sélectionnée"):
        nouveau_montant_paye = facture["montant_paye"] + montant_paye_input
        nouveau_reliquat = facture["montant_total"] - nouveau_montant_paye

        # ⚡ Mise à jour Firestore
        db.collection("factures").document(facture["id"]).update({
            "montant_paye": nouveau_montant_paye,
            "reliquat": max(nouveau_reliquat, 0),
            "status": "payée" if nouveau_reliquat == 0 else "partielle"
        })

        st.success(
            f"Facture {facture['id']} mise à jour ✅ "
            f"(Payé: {nouveau_montant_paye} CFA, Reliquat: {nouveau_reliquat} CFA)"
        )
        st.experimental_rerun()

