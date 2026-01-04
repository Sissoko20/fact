import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
from streamlit_option_menu import option_menu
from firebase_admin_setup import db
from components.sidebar import render_sidebar
# -------------------------------
# Configuration
# -------------------------------
st.set_page_config(page_title="Analyse des données", page_icon="📊", layout="wide")

# -------------------------------
# Vérification session persistante
# -------------------------------
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("⛔ Vous devez être connecté")
    st.switch_page("pages/Login.py")
    st.stop()

if st.session_state.get("role") != "admin":
    st.error("⛔ Accès réservé aux administrateurs")
    st.stop()

# Appel du composant sidebar 
selected = render_sidebar(default_index=0)
# -------------------------------
# Logique de navigation
# -------------------------------
if selected == "🏠 Tableau de bord":
    st.switch_page("app.py")
elif selected == "🧾 Factures":
    st.switch_page("pages/Previsualisation.py")
elif selected == "💰 Reçus":
    st.switch_page("pages/Previsualisation.py")
elif selected == "👥 Utilisateurs":
    st.switch_page("pages/Admin.py")
elif selected == "🔒 Déconnexion":
    st.session_state["authenticated"] = False
    st.info("✅ Déconnecté")
    st.switch_page("pages/Login.py")

# -------------------------------
# Contenu principal : Dashboard
# -------------------------------
st.title("📊 Dashboard - Analyse des factures")

# Charger les factures Firestore
factures_ref = db.collection("factures").stream()
rows = [doc.to_dict() | {"id": doc.id} for doc in factures_ref]
df = pd.DataFrame(rows)

st.dataframe(df)

# Aperçu global
st.subheader("📊 Aperçu global")
if not df.empty:
    total_factures = df[df["type"] == "Facture de doit"]["montant"].sum()
    total_recus = df[df["type"] == "Reçu de Paiement"]["montant"].sum()
    total_global = df["montant"].sum()
    nb_docs = len(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Factures totales", f"{total_factures:,.0f} FCFA")
    col2.metric("Reçus totaux", f"{total_recus:,.0f} FCFA")
    col3.metric("Montant Global", f"{total_global:,.0f} FCFA")
    col4.metric("Documents générés", nb_docs)
else:
    st.info("Aucune donnée disponible.")

# Historique
st.subheader("📑 Historique")
if not df.empty:
    type_filtre = st.selectbox("Filtrer par type :", ["Tous"] + df["type"].unique().tolist())
    if type_filtre != "Tous":
        df = df[df["type"] == type_filtre]
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Aucun historique disponible.")

# Visualisations
st.subheader("📈 Visualisations")
if not df.empty:
    chart_type = st.selectbox("Type de graphique :", ["Barres", "Camembert", "Courbe", "Histogramme"])
    col_x = st.selectbox("Colonne X :", df.columns)
    col_y = st.selectbox("Colonne Y :", df.columns)

    if st.button("Générer le graphique"):
        fig, ax = plt.subplots(figsize=(6,4))
        if chart_type == "Barres":
            df.groupby(col_x)[col_y].sum().plot(kind="bar", ax=ax)
        elif chart_type == "Camembert":
            df.groupby(col_x)[col_y].sum().plot(kind="pie", autopct='%1.1f%%', ax=ax)
        elif chart_type == "Courbe":
            df.groupby(col_x)[col_y].sum().plot(kind="line", ax=ax, marker="o")
        elif chart_type == "Histogramme":
            df[col_y].plot(kind="hist", ax=ax, bins=10)
        st.pyplot(fig)

# Comparaison Factures vs Reçus
st.subheader("⚖️ Comparaison Factures vs Reçus")
if not df.empty and "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"])
    min_date, max_date = df["date"].min(), df["date"].max()
    start_date = st.date_input("Date de début", min_date)
    end_date = st.date_input("Date de fin", max_date)

    df_periode = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]

    if not df_periode.empty:
        comparaison = df_periode.groupby("type")["montant"].sum()
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(comparaison)
        with col2:
            fig, ax = plt.subplots()
            comparaison.plot.pie(autopct='%1.1f%%', ax=ax)
            ax.set_ylabel("")
            st.pyplot(fig)
    else:
        st.warning("Aucune donnée dans cette période.")

# Evolution mensuelle
st.subheader("📅 Évolution mensuelle")
if not df.empty and "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"])
    df["mois"] = df["date"].dt.to_period("M").astype(str)
    evolution = df.groupby(["mois", "type"])["montant"].sum().unstack().fillna(0)
    st.line_chart(evolution)
    st.dataframe(evolution, use_container_width=True)

# CRUD
st.subheader("⚙️ Gestion de la base (Admin uniquement)")
facture_id = st.text_input("ID Firestore de la facture à supprimer")
if st.button("❌ Supprimer cette facture"):
    if facture_id:
        db.collection("factures").document(facture_id).delete()
        st.success(f"Facture {facture_id} supprimée")
        st.rerun()

if st.button("🗑️ Vider toutes les factures"):
    for doc in db.collection("factures").stream():
        db.collection("factures").document(doc.id).delete()
    st.warning("⚠️ Toutes les factures ont été supprimées")
    st.rerun()
