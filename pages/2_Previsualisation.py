import streamlit as st
import sqlite3
from datetime import datetime
from components.pdf_generator import generate_pdf, build_facture_html


from components.sidebar import sidebar_navigation


# Appel du menu global
theme = sidebar_navigation()

# Appliquer le thème choisi
if theme == "Clair":
    st.markdown("""
        <style>
        body { background-color: #ffffff; color: #000000; }
        [data-testid="stSidebar"] { background-color: #f8f9fa; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        body { background-color: #1e1e1e; color: #ffffff; }
        [data-testid="stSidebar"] { background-color: #2c2c2c; }
        </style>
    """, unsafe_allow_html=True)




# Connexion et initialisation DB
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

st.title("📝 Prévisualisation")

modele = st.selectbox("Choisissez un modèle", ["Facture Professionnelle", "Reçu de Paiement"])

# -------------------------------
# FACTURE PROFESSIONNELLE
# -------------------------------
if modele == "Facture Professionnelle":
    client_name = st.text_input("Nom du client")
    client_phone = st.text_input("Téléphone du client")
    client_email = st.text_input("Email du client")

    st.markdown("### 🧾 Lignes de facture")

    if "facture_items" not in st.session_state:
        st.session_state.facture_items = []

    if st.button("➕ Ajouter une ligne"):
        st.session_state.facture_items.append({
            "description": "",
            "date": datetime.today().strftime("%d/%m/%Y"),
            "qty": 1,
            "price": 1000.0,
            "tva": 18
        })

    items = []
    for i, item in enumerate(st.session_state.facture_items):
        st.markdown(f"**Ligne {i+1}**")
        description = st.text_input(f"Description {i+1}", value=item["description"], key=f"desc_{i}")
        date = st.date_input(f"Date {i+1}", value=datetime.today(), key=f"date_{i}")
        qty = st.number_input(f"Quantité {i+1}", min_value=1, value=item["qty"], key=f"qty_{i}")
        price = st.number_input(f"Prix unitaire {i+1} (FCFA)", min_value=0.0, value=item["price"], key=f"price_{i}")
        tva = st.checkbox(f"Appliquer TVA 18% à la ligne {i+1}", value=True, key=f"tva_{i}")

        if st.button(f"🗑️ Supprimer la ligne {i+1}"):
            st.session_state.facture_items.pop(i)
            st.experimental_rerun()

        items.append({
            "description": description,
            "date": date.strftime("%d/%m/%Y"),
            "qty": qty,
            "price": price,
            "tva": 18 if tva else 0
        })

    data = {
        "client_name": client_name,
        "client_phone": client_phone,
        "client_email": client_email,
        "items": items
    }

    html_preview = build_facture_html(data, type_doc="Facture Professionnelle")
    montant = sum(item["qty"] * item["price"] for item in items)

# -------------------------------
# REÇU DE PAIEMENT
# -------------------------------
else:
    client_name = st.text_input("Nom du client")
    client_phone = st.text_input("Téléphone du client")
    client_email = st.text_input("Email du client")
    amount = st.number_input("Montant payé (FCFA)", min_value=0, value=0)
    objet = st.text_input("Objet du paiement", "Paiement de services médicaux")

    data = {
        "client_name": client_name,
        "client_phone": client_phone,
        "client_email": client_email,
        "amount": amount,
        "objet": objet
    }
    html_preview = build_facture_html(data, type_doc="Reçu de Paiement")
    montant = amount

# -------------------------------
# PRÉVISUALISATION
# -------------------------------
st.markdown("### 🔎 Aperçu")
st.markdown(html_preview, unsafe_allow_html=True)

# -------------------------------
# GÉNÉRATION PDF + SAUVEGARDE
# -------------------------------
if st.button("📄 Générer PDF"):
    filename = generate_pdf(html_preview, "document.pdf")
    if filename:
        st.success("✅ PDF généré avec succès")

        cursor.execute(
            "INSERT INTO factures (type, client, montant, objet, date) VALUES (?, ?, ?, ?, ?)",
            (modele, data["client_name"], montant, data.get("objet", ""), datetime.today().strftime("%Y-%m-%d"))
        )
        conn.commit()

        with open(filename, "rb") as f:
            st.download_button(
                label="⬇️ Télécharger le PDF",
                data=f,
                file_name=filename,
                mime="application/pdf"
            )
    else:
        st.error("❌ Erreur lors de la génération du PDF")
