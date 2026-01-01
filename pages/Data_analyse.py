import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# -------------------------------
# Configuration de la page
# -------------------------------
st.set_page_config(page_title="Dashboard - Analyse", layout="wide")
st.title("📊 Dashboard - Analyse des factures et reçus")

# -------------------------------
# Vérification rôle administrateur
# -------------------------------
if "role" not in st.session_state or st.session_state["role"] != "admin":
    st.error("⛔ Accès réservé aux administrateurs")
    st.stop()

# -------------------------------
# Connexion DB + Initialisation
# -------------------------------
conn = sqlite3.connect("data/factures.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS factures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    client TEXT,
    montant REAL,
    objet TEXT,
    date TEXT
)
""")
conn.commit()

# Charger les données
df = pd.read_sql("SELECT * FROM factures ORDER BY date DESC", conn)

# -------------------------------
# Aperçu global
# -------------------------------
st.subheader("📊 Aperçu global")

if not df.empty:
    total_factures = df[df["type"] == "Facture Professionnelle"]["montant"].sum()
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

# -------------------------------
# Historique
# -------------------------------
st.subheader("📑 Historique")
if not df.empty:
    type_filtre = st.selectbox("Filtrer par type :", ["Tous"] + df["type"].unique().tolist())
    if type_filtre != "Tous":
        df = df[df["type"] == type_filtre]
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Aucun historique disponible.")

# -------------------------------
# Visualisations interactives
# -------------------------------
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

# -------------------------------
# Comparaison Factures vs Reçus
# -------------------------------
st.subheader("⚖️ Comparaison Factures vs Reçus")

if not df.empty:
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

        st.write("### 📊 Analyse rapide")
        for t, v in comparaison.items():
            st.write(f"**{t} :** {v:,.0f} FCFA")
    else:
        st.warning("Aucune donnée dans cette période.")

# -------------------------------
# Évolution mensuelle
# -------------------------------
st.subheader("📅 Évolution mensuelle")

if not df.empty:
    df["date"] = pd.to_datetime(df["date"])
    df["mois"] = df["date"].dt.to_period("M").astype(str)

    evolution = df.groupby(["mois", "type"])["montant"].sum().unstack().fillna(0)

    st.line_chart(evolution)
    st.write("### 📊 Analyse mensuelle")
    st.dataframe(evolution, use_container_width=True)

# -------------------------------
# CRUD - Gestion de la base
# -------------------------------
st.subheader("⚙️ Gestion de la base (Admin uniquement)")

# Initialiser la base
if st.button("🆕 Initialiser la base"):
    cursor.execute("DROP TABLE IF EXISTS factures")
    cursor.execute("""
    CREATE TABLE factures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        client TEXT,
        montant REAL,
        objet TEXT,
        date TEXT
    )
    """)
    conn.commit()
    st.success("✅ Base initialisée")
    st.experimental_rerun()   # 👈 relance après action

# Vider toutes les factures
if st.button("🗑️ Vider toutes les factures"):
    cursor.execute("DELETE FROM factures")
    conn.commit()
    st.warning("⚠️ Toutes les factures ont été supprimées")
    st.experimental_rerun()   # 👈 relance après action

# Supprimer une facture spécifique
facture_id = st.number_input("ID de la facture à supprimer", min_value=1, step=1)
if st.button("❌ Supprimer cette facture"):
    cursor.execute("DELETE FROM factures WHERE id = ?", (facture_id,))
    conn.commit()
    st.info(f"Facture ID {facture_id} supprimée")
    st.experimental_rerun()   # 👈 relance après action

# Modifier une facture
st.subheader("✏️ Modifier une facture")
edit_id = st.number_input("ID de la facture à modifier", min_value=1, step=1, key="edit_id")
new_client = st.text_input("Nouveau nom du client")
new_montant = st.number_input("Nouveau montant", min_value=0.0)

if st.button("💾 Mettre à jour"):
    cursor.execute("UPDATE factures SET client=?, montant=? WHERE id=?", (new_client, new_montant, edit_id))
    conn.commit()
    st.success(f"Facture ID {edit_id} mise à jour")
    st.experimental_rerun()   # 👈 relance après action
