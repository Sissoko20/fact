# pages/Admin_dashboard.py

import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
from streamlit_option_menu import option_menu
from firebase_admin_setup import db

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Admin - Gestion factures", page_icon="🔧", layout="wide")

# -------------------------------
# Authentification (sécurisé)
# -------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.error("⛔ Vous devez être connecté")
    st.stop()

role = st.session_state.get("role", "user")
user_id = st.session_state.get("user_id")

if role != "admin":
    st.error("⛔ Accès réservé à l'administrateur")
    st.stop()

# -------------------------------
# Sidebar navigation (admin)
# -------------------------------
with st.sidebar:
    st.image("assets/logo.png", width=120)
    selected = option_menu(
        "Admin Navigation",
        ["📋 Gestion factures", "📊 Analyses", "👥 Utilisateurs", "🔒 Déconnexion"],
        icons=["file-text", "bar-chart", "people", "box-arrow-right"],
        default_index=0,
        key="admin_nav"
    )

    if selected == "🔒 Déconnexion":
        st.session_state.clear()
        st.success("✅ Déconnecté")
        st.experimental_rerun()

# -------------------------------
# Chargement : admin voit toutes les factures
# -------------------------------
factures_ref = db.collection("factures").stream()
rows = [doc.to_dict() | {"id": doc.id} for doc in factures_ref]
df = pd.DataFrame(rows)

# Normaliser colonnes numériques si présentes
for col in ["montant", "montant_total", "montant_paye", "reliquat"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

st.title("🔧 Admin — Gestion complète des factures")

# -------------------------------
# Vue d'ensemble / métriques
# -------------------------------
st.subheader("📊 Aperçu global")
if not df.empty:
    total_factures = df[df.get("type") == "Facture de doit"]["montant"].sum() if "type" in df.columns else 0
    total_recus = df[df.get("type") == "Reçu de Paiement"]["montant"].sum() if "type" in df.columns else 0
    total_global = df["montant"].sum() if "montant" in df.columns else 0
    total_impayes = int((df["reliquat"] > 0).sum()) if "reliquat" in df.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💼 Factures (montant)", f"{total_factures:,.0f} FCFA")
    c2.metric("💰 Reçus (montant)", f"{total_recus:,.0f} FCFA")
    c3.metric("📊 Total (montant)", f"{total_global:,.0f} FCFA")
    c4.metric("❌ Factures impayées", f"{total_impayes}")
else:
    st.info("Aucune facture trouvée")

st.markdown("---")

# -------------------------------
# Table complète des factures (admin)
# -------------------------------
st.subheader("📋 Toutes les factures")
if df.empty:
    st.info("Aucune facture à afficher")
else:
    # Afficher un aperçu triable
    st.dataframe(df.reset_index(drop=True), use_container_width=True)

st.markdown("---")

# -------------------------------
# Gestion des impayés (admin)
# -------------------------------
st.subheader("❌ Gestion des factures impayées")

cols_needed = {"reliquat", "montant_paye", "montant_total", "client_name"}
if not cols_needed.issubset(df.columns):
    st.info("Les colonnes nécessaires (reliquat, montant_paye, montant_total, client_name) sont manquantes.")
else:
    impayes = df[df["reliquat"] > 0].copy()
    if impayes.empty:
        st.info("✅ Aucune facture impayée")
    else:
        # Tableau synthétique des impayés
        tableau_impayes = impayes[["id", "client_name", "client_phone", "montant_total", "montant_paye", "reliquat"]]
        st.dataframe(tableau_impayes.reset_index(drop=True), use_container_width=True)

        # Sélection lisible (client + téléphone + montant)
        def label(i):
            r = impayes.iloc[i]
            phone = r.get("client_phone", "")
            return f"{r['client_name']} — {phone} — Total {int(r['montant_total'])} FCFA — Reliquat {int(r['reliquat'])} FCFA"

        options = [label(i) for i in range(len(impayes))]
        option_to_index = {options[i]: i for i in range(len(options))}

        selected = st.selectbox("Sélectionnez une facture à solder", options=options, key="admin_select_impaye")
        if selected:
            idx = option_to_index[selected]
            facture = impayes.iloc[idx]

            st.markdown(f"**Facture sélectionnée :** {facture['id']} — **Client :** {facture['client_name']}")
            st.write(f"**Payé :** {int(facture['montant_paye'])} FCFA  •  **Total :** {int(facture['montant_total'])} FCFA  •  **Reliquat :** {int(facture['reliquat'])} FCFA")

            montant_paye_input = st.number_input(
                "Montant à enregistrer (FCFA)",
                min_value=0,
                max_value=int(facture["reliquat"]),
                step=100,
                key=f"admin_montant_paye_{facture['id']}"
            )

            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.button("Enregistrer paiement", key=f"admin_save_pay_{facture['id']}"):
                    nouveau_montant_paye = float(facture["montant_paye"]) + float(montant_paye_input)
                    nouveau_reliquat = float(facture["montant_total"]) - nouveau_montant_paye
                    nouveau_reliquat = max(nouveau_reliquat, 0)

                    db.collection("factures").document(facture["id"]).update({
                        "montant_paye": nouveau_montant_paye,
                        "reliquat": nouveau_reliquat,
                        "status": "payée" if nouveau_reliquat == 0 else "partielle"
                    })
                    st.success(f"Paiement enregistré. Nouveau reliquat : {int(nouveau_reliquat)} FCFA")
                    st.experimental_rerun()

            with col_b:
                if st.button("Solder complètement", key=f"admin_full_pay_{facture['id']}"):
                    db.collection("factures").document(facture["id"]).update({
                        "montant_paye": float(facture["montant_total"]),
                        "reliquat": 0,
                        "status": "payée"
                    })
                    st.success("Facture soldée ✅")
                    st.experimental_rerun()

st.markdown("---")

# -------------------------------
# Analyses (graphiques) — admin
# -------------------------------
if selected == "📊 Analyses" or st.sidebar.button("Voir analyses", key="admin_open_analyses"):
    st.subheader("📈 Analyses et visualisations")

    if df.empty or "montant" not in df.columns:
        st.info("Pas assez de données pour afficher des graphiques")
    else:
        chart_type = st.selectbox("Type de graphique", ["Barres", "Camembert", "Courbe", "Histogramme"], key="admin_chart_type")
        col_x = st.selectbox("Axe X", df.columns, key="admin_col_x")
        col_y = st.selectbox("Axe Y", df.columns, key="admin_col_y")

        if st.button("Générer le graphique", key="admin_generate_chart"):
            try:
                fig, ax = plt.subplots(figsize=(8, 4))
                if chart_type == "Barres":
                    df.groupby(col_x)[col_y].sum().plot(kind="bar", ax=ax)
                elif chart_type == "Camembert":
                    df.groupby(col_x)[col_y].sum().plot(kind="pie", autopct="%1.1f%%", ax=ax)
                    ax.set_ylabel("")
                elif chart_type == "Courbe":
                    df.groupby(col_x)[col_y].sum().plot(kind="line", marker="o", ax=ax)
                elif chart_type == "Histogramme":
                    df[col_y].plot(kind="hist", bins=10, ax=ax)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Erreur graphique : {e}")

st.markdown("---")

# -------------------------------
# CRUD global (admin)
# -------------------------------
st.subheader("⚙️ Actions administrateur")

with st.expander("Supprimer / modifier une facture"):
    facture_id = st.text_input("ID de la facture", key="admin_crud_id")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Supprimer cette facture", key="admin_delete_one"):
            if not facture_id:
                st.error("Renseignez l'ID de la facture")
            else:
                doc_ref = db.collection("factures").document(facture_id)
                doc = doc_ref.get()
                if not doc.exists:
                    st.error("Facture introuvable")
                else:
                    doc_ref.delete()
                    st.success("Facture supprimée")
                    st.experimental_rerun()

    with col2:
        if st.button("🗂️ Marquer comme payée (status)", key="admin_mark_paid"):
            if not facture_id:
                st.error("Renseignez l'ID de la facture")
            else:
                doc_ref = db.collection("factures").document(facture_id)
                doc = doc_ref.get()
                if not doc.exists:
                    st.error("Facture introuvable")
                else:
                    data = doc.to_dict()
                    montant_total = float(data.get("montant_total", 0))
                    doc_ref.update({
                        "montant_paye": montant_total,
                        "reliquat": 0,
                        "status": "payée"
                    })
                    st.success("Facture marquée comme payée")
                    st.experimental_rerun()

with st.expander("Supprimer toutes les factures"):
    if st.button("🗑️ Supprimer TOUTES les factures (IRRÉVERSIBLE)", key="admin_delete_all_confirm"):
        docs = db.collection("factures").stream()
        for d in docs:
            db.collection("factures").document(d.id).delete()
        st.warning("Toutes les factures ont été supprimées")
        st.experimental_rerun()
