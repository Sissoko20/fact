import streamlit as st
import sqlite3
from datetime import datetime
from streamlit_option_menu import option_menu
from components.pdf_generator import generate_pdf, build_facture_html
from firebase_admin_setup import db   # ton module qui initialise Firebase
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

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
        default_index=1,  # 👉 Facture de doit actif
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

# Connexion DB
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

    data = {"client_name": client_name, "client_phone": client_phone, "client_email": client_email, "items": items}
    html_preview = build_facture_html(data, type_doc="Facture de doit")
    montant = sum(item["qty"] * item["price"] for item in items)

# -------------------------------
# Reçu
# -------------------------------
else:
    client_name = st.text_input("Nom du client")
    client_phone = st.text_input("Téléphone du client")
    client_email = st.text_input("Email du client")
    amount = st.number_input("Montant payé (FCFA)", min_value=0, value=0)
    objet = st.text_input("Objet du paiement", "Paiement de services médicaux")

    data = {"client_name": client_name, "client_phone": client_phone, "client_email": client_email,
            "amount": amount, "objet": objet}
    html_preview = build_facture_html(data, type_doc="Reçu de Paiement")
    montant = amount

# -------------------------------
# Génération PDF + Sauvegarde
# -------------------------------
if st.button("📄 Générer PDF"):
    filename = generate_pdf(html_preview, "document.pdf")
    if filename:
        st.success("✅ PDF généré avec succès")

        facture_doc = {
            "type": modele,
            "client_name": data["client_name"],
            "client_phone": data["client_phone"],
            "client_email": data["client_email"],
            "items": data.get("items", []),
            "objet": data.get("objet", ""),
            "montant": montant,
            "date": datetime.today().strftime("%Y-%m-%d")
        }
        db.collection("factures").add(facture_doc)
        st.success("💾 Facture enregistrée dans Firestore")

        with open(filename, "rb") as f:
            st.download_button("⬇️ Télécharger le PDF", f, file_name=filename, mime="application/pdf")

        # Bouton Imprimer
st.markdown(f"[🖨️ Imprimer la facture](document.pdf)", unsafe_allow_html=True)


        # Bouton Envoyer par SMTP
if st.button("📧 Envoyer par email (SMTP)"):
    subject = f"{modele} - {data['client_name']}"
    body = f"Bonjour {data['client_name']},\n\nVeuillez trouver ci-joint votre {modele}.\nMontant : {montant} FCFA.\n\nCordialement,\nMABOU-INSTRUMED"

    try:
        sender = "ton_email@gmail.com"
        password = "ton_mot_de_passe_app"  # mot de passe d’application Gmail
        recipient = data["client_email"]

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with open(filename, "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(attach)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

        st.success("✅ Email envoyé avec succès")
    except Exception as e:
        st.error(f"❌ Erreur envoi email : {e}")

conn.close()
