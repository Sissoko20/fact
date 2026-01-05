import streamlit as st
import sqlite3
from datetime import datetime, date
from streamlit_option_menu import option_menu
from components.pdf_generator import generate_pdf, build_facture_html
from firebase_admin_setup import db

# -------------------------------
# Vérification d'authentification
# -------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.warning("⚠️ Veuillez vous connecter d'abord.")
    st.switch_page("pages/Login.py")
    st.stop()

# -------------------------------
# Barre de navigation moderne
# -------------------------------
with st.sidebar:
    st.image("assets/logo.png", width=120)
    selected = option_menu(
        "Navigation",
        ["🏠 Tableau de bord", "🧾 Facture de doit", "💰 Reçus", "👥 Utilisateurs", "🔒 Déconnexion"],
        icons=["house", "file-text", "cash", "people", "box-arrow-right"],
        menu_icon="cast",
        default_index=1,
    )

# -------------------------------
# Redirections via menu
# -------------------------------
if selected == "🏠 Tableau de bord":
    st.switch_page("app.py")
elif selected == "👥 Utilisateurs":
    st.switch_page("pages/Admin.py")
elif selected == "🔒 Déconnexion":
    st.session_state["authenticated"] = False
    st.info("✅ Déconnecté")
    st.switch_page("pages/Login.py")

# -------------------------------
# Contenu principal : Facture / Reçu
# -------------------------------
st.title("📝 Prévisualisation")

modele = st.selectbox("Choisissez un modèle", ["Facture de doit", "Reçu de Paiement"])

# Connexion DB locale (facultatif si tu utilises Firestore)
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

filename = None  # pour gérer l'envoi par email après génération

# -------------------------------
# Facture de doit
# -------------------------------
if modele == "Facture de doit":
    client_name = st.text_input("Nom du client")
    client_phone = st.text_input("Téléphone du client")
    client_email = st.text_input("Email du client")

    st.markdown("### 🧾 Lignes de facture")
    if "facture_items" not in st.session_state:
        st.session_state.facture_items = []

    if st.button("➕ Ajouter une ligne"):
        st.session_state.facture_items.append({
            "description": "",
            "date": date.today().strftime("%d/%m/%Y"),
            "qty": 1,
            "price": 1000.0
        })

    items = []
    for i, item in enumerate(st.session_state.facture_items):
        st.markdown(f"**Ligne {i+1}**")
        description = st.text_area(f"Description {i+1}", value=item["description"], key=f"desc_{i}")
        ldate = st.date_input(f"Date {i+1}", value=date.today(), key=f"date_{i}")
        qty = st.number_input(f"Quantité {i+1}", min_value=1, value=item["qty"], key=f"qty_{i}")
        price = st.number_input(f"Prix unitaire {i+1} (FCFA)", min_value=0.0, value=item["price"], key=f"price_{i}")

        if st.button(f"🗑️ Supprimer la ligne {i+1}"):
            st.session_state.facture_items.pop(i)
            st.rerun()

        items.append({
            "description": description.strip(),
            "date": ldate.strftime("%d/%m/%Y"),
            "qty": int(qty),
            "price": float(price)
        })

    montant_total = sum(item["qty"] * item["price"] for item in items)
    avance = st.number_input("Avance payée (FCFA)", min_value=0.0, value=0.0, step=100.0)
    reliquat = max(montant_total - avance, 0.0)

    st.write(f"💰 Reliquat à payer : {reliquat:,.0f} FCFA".replace(",", " "))

    data = {
        "client_name": client_name.strip(),
        "client_phone": client_phone.strip(),
        "client_email": client_email.strip(),
        "items": items,
        "montant_total": montant_total,   # montant théorique
        "montant_paye": avance,           # montant réellement perçu
        "avance": avance,
        "reliquat": reliquat,
    }
    html_preview = build_facture_html(data, type_doc="Facture de doit")

# -------------------------------
# Reçu
# -------------------------------
else:
    client_name = st.text_input("Nom du client")
    client_phone = st.text_input("Téléphone du client")
    client_email = st.text_input("Email du client")
    montant_paye = st.number_input("Montant payé (FCFA)", min_value=0, value=0, step=100)
    objet = st.selectbox(
        "Objet du paiement",
        ["Achat de matériel médical", "Achat de vêtement", "Achat de chaussures", "Achat divers"]
    )

    data = {
        "client_name": client_name.strip(),
        "client_phone": client_phone.strip(),
        "client_email": client_email.strip(),
        "montant_paye": montant_paye,
        "objet": objet
    }
    html_preview = build_facture_html(data, type_doc="Reçu de Paiement")

# -------------------------------
# Génération PDF + Sauvegarde
# -------------------------------
if st.button("📄 Générer PDF"):
    filename = generate_pdf(html_preview, "document.pdf")
    if filename:
        st.success("✅ PDF généré avec succès")

        facture_doc = {
            "type": modele,
            "client_name": data.get("client_name", ""),
            "client_phone": data.get("client_phone", ""),
            "client_email": data.get("client_email", ""),
            "items": data.get("items", []),
            "objet": data.get("objet", ""),
            "montant_total": data.get("montant_total", 0.0),
            "montant_paye": data.get("montant_paye", 0.0),
            "avance": data.get("avance", 0.0),
            "reliquat": data.get("reliquat", 0.0),
            "date": datetime.today().strftime("%Y-%m-%d")
        }
        db.collection("factures").add(facture_doc)
        st.success("💾 Document enregistré dans Firestore")

        with open(filename, "rb") as f:
            st.download_button("⬇️ Télécharger le PDF", f, file_name=filename, mime="application/pdf")

conn.close()
