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
    st.session_state["role"] = None
    st.session_state["email"] = None
    st.session_state["user_id"] = None

if not st.session_state["authenticated"]:
    st.warning("⚠️ Veuillez vous connecter d'abord.")
    st.switch_page("pages/Login.py")
    st.stop()

# 👉 Vérifie que l'identifiant utilisateur est bien présent
if not st.session_state.get("user_id"):
    st.error("⛔ Identifiant utilisateur manquant. Veuillez vous reconnecter.")
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

# Si une prévisualisation est demandée depuis une autre page (ex: Data_analyse)
preview_id = st.session_state.get("preview_invoice_id")
preview_pdf_flag = st.session_state.get("preview_generate_pdf", False)

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
# Si preview_id est présent, charger la facture depuis Firestore
# -------------------------------
invoice_from_db = None
if preview_id:
    try:
        doc = db.collection("factures").document(preview_id).get()
        if doc.exists:
            invoice_from_db = doc.to_dict()
            invoice_from_db["id"] = doc.id
        else:
            st.warning("La facture demandée pour prévisualisation est introuvable.")
            # nettoyer le flag pour éviter boucle
            st.session_state.pop("preview_invoice_id", None)
            st.session_state.pop("preview_generate_pdf", None)
            preview_id = None
            preview_pdf_flag = False
    except Exception as e:
        st.error("Erreur lors du chargement de la facture depuis la base.")
        preview_id = None
        preview_pdf_flag = False

# -------------------------------
# Modele : si preview vient d'une facture existante, on pré-remplit
# -------------------------------
if invoice_from_db:
    modele = invoice_from_db.get("type", "Facture de doit")
else:
    modele = st.selectbox("Choisissez un modèle", ["Facture de doit", "Reçu de Paiement"])

# -------------------------------
# Préparation des données (pré-remplissage si invoice_from_db)
# -------------------------------
# Initialiser items en session si nécessaire
if "facture_items" not in st.session_state:
    st.session_state.facture_items = []

if invoice_from_db and invoice_from_db.get("items"):
    # remplacer les items en session par ceux de la facture existante
    st.session_state.facture_items = invoice_from_db.get("items", [])

# -------------------------------
# Facture de doit
# -------------------------------
if modele == "Facture de doit":
    # Pré-remplir champs si invoice_from_db
    client_name = st.text_input(
        "Nom du client",
        value=invoice_from_db.get("client_name", "") if invoice_from_db else ""
    )
    client_phone = st.text_input(
        "Téléphone du client",
        value=invoice_from_db.get("client_phone", "") if invoice_from_db else ""
    )
    client_email = st.text_input(
        "Email du client",
        value=invoice_from_db.get("client_email", "") if invoice_from_db else ""
    )

    st.markdown("### 🧾 Lignes de facture")
    if st.button("➕ Ajouter une ligne"):
        st.session_state.facture_items.append({
            "description": "",
            "date": date.today().strftime("%d/%m/%Y"),
            "qty": 1,
            "price": 1000.0
        })

    items = []
    # afficher les lignes existantes (pré-remplies si invoice_from_db)
    for i, item in enumerate(st.session_state.facture_items):
        st.markdown(f"**Ligne {i+1}**")
        description = st.text_area(f"Description {i+1}", value=item.get("description", ""), key=f"desc_{i}")
        ldate = st.date_input(f"Date {i+1}", value=datetime.strptime(item.get("date", date.today().strftime("%d/%m/%Y")), "%d/%m/%Y").date() if item.get("date") else date.today(), key=f"date_{i}")
        qty = st.number_input(f"Quantité {i+1}", min_value=1, value=int(item.get("qty", 1)), key=f"qty_{i}")
        price = st.number_input(f"Prix unitaire {i+1} (FCFA)", min_value=0.0, value=float(item.get("price", 1000.0)), key=f"price_{i}")

        col1, col2 = st.columns([9,1])
        with col2:
            if st.button(f"🗑️", key=f"del_line_{i}"):
                st.session_state.facture_items.pop(i)
                st.experimental_rerun()

        items.append({
            "description": description.strip(),
            "date": ldate.strftime("%d/%m/%Y"),
            "qty": int(qty),
            "price": float(price)
        })

    montant_total = sum(item["qty"] * item["price"] for item in items)
    # si preview vient d'une facture existante, pré-remplir l'avance/montant_paye
    default_avance = invoice_from_db.get("montant_paye", 0.0) if invoice_from_db else 0.0
    avance = st.number_input("Avance payée (FCFA)", min_value=0.0, value=float(default_avance), step=100.0)
    reliquat = max(montant_total - avance, 0.0)

    st.write(f"💰 Reliquat à payer : {reliquat:,.0f} FCFA".replace(",", " "))

    data = {
        "client_name": client_name.strip(),
        "client_phone": client_phone.strip(),
        "client_email": client_email.strip(),
        "items": items,
        "montant_total": montant_total,
        "montant_paye": avance,
        "avance": avance,
        "reliquat": reliquat,
    }
    html_preview = build_facture_html(data, type_doc="Facture de doit")

# -------------------------------
# Reçu
# -------------------------------
else:
    client_name = st.text_input("Nom du client", value=invoice_from_db.get("client_name", "") if invoice_from_db else "")
    client_phone = st.text_input("Téléphone du client", value=invoice_from_db.get("client_phone", "") if invoice_from_db else "")
    client_email = st.text_input("Email du client", value=invoice_from_db.get("client_email", "") if invoice_from_db else "")
    montant_paye = st.number_input("Montant payé (FCFA)", min_value=0, value=int(invoice_from_db.get("montant_paye", 0)) if invoice_from_db else 0, step=100)
    objet = st.selectbox(
        "Objet du paiement",
        ["Achat de matériel médical", "Achat de vêtement", "Achat de chaussures", "Achat divers"],
        index=0 if not invoice_from_db else 0
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
# Si la page a été appelée en preview depuis Data_analyse et preview_generate_pdf est True
# on propose directement le téléchargement du PDF de la facture existante
# -------------------------------
if invoice_from_db and preview_pdf_flag:
    st.markdown("---")
    st.subheader("Prévisualisation automatique de la facture mise à jour")

    # Construire le HTML à partir des données de la facture existante
    # Si la facture stocke déjà un format complet (items, montants), on l'utilise
    invoice_data_for_pdf = {
        "client_name": invoice_from_db.get("client_name", ""),
        "client_phone": invoice_from_db.get("client_phone", ""),
        "client_email": invoice_from_db.get("client_email", ""),
        "items": invoice_from_db.get("items", []),
        "montant_total": invoice_from_db.get("montant_total", invoice_from_db.get("montant", 0.0)),
        "montant_paye": invoice_from_db.get("montant_paye", 0.0),
        "avance": invoice_from_db.get("avance", invoice_from_db.get("montant_paye", 0.0)),
        "reliquat": invoice_from_db.get("reliquat", 0.0),
    }
    html_preview_db = build_facture_html(invoice_data_for_pdf, type_doc=invoice_from_db.get("type", "Facture de doit"))

    if st.button("📄 Générer et télécharger le PDF de la facture mise à jour", key=f"download_preview_{invoice_from_db['id']}"):
        filename = generate_pdf(html_preview_db, f"facture_{invoice_from_db['id']}.pdf")
        if filename:
            st.success("✅ PDF généré avec succès")
            with open(filename, "rb") as f:
                st.download_button("⬇️ Télécharger le PDF", f, file_name=filename, mime="application/pdf", key=f"dl_{invoice_from_db['id']}")
            # nettoyer les flags de preview pour éviter régénération automatique
            st.session_state.pop("preview_invoice_id", None)
            st.session_state.pop("preview_generate_pdf", None)

    st.markdown("---")

# -------------------------------
# Génération PDF + Sauvegarde (nouvelle facture ou reçu)
# -------------------------------
# Si la facture provient d'une prévisualisation existante, on évite de créer un nouveau document en base.
if st.button("📄 Générer PDF"):
    filename = generate_pdf(html_preview, "document.pdf")
    if filename:
        st.success("✅ PDF généré avec succès")

        # Si preview_id existe, on met à jour la facture existante au lieu d'en créer une nouvelle
        if invoice_from_db:
            doc_ref = db.collection("factures").document(invoice_from_db["id"])
            # Mettre à jour les champs pertinents
            update_payload = {
                "client_name": data.get("client_name", ""),
                "client_phone": data.get("client_phone", ""),
                "client_email": data.get("client_email", ""),
                "items": data.get("items", []),
                "montant_total": data.get("montant_total", 0.0),
                "montant_paye": data.get("montant_paye", 0.0),
                "avance": data.get("avance", 0.0),
                "reliquat": data.get("reliquat", 0.0),
                "date": datetime.today().strftime("%Y-%m-%d"),
            }
            try:
                doc_ref.update(update_payload)
                st.success("💾 Facture mise à jour dans Firestore")
            except Exception:
                st.warning("⚠️ Impossible de mettre à jour la facture en base. Vérifiez la connexion.")

            # proposer le téléchargement
            with open(filename, "rb") as f:
                st.download_button("⬇️ Télécharger le PDF", f, file_name=filename, mime="application/pdf")
            # nettoyer flags preview
            st.session_state.pop("preview_invoice_id", None)
            st.session_state.pop("preview_generate_pdf", None)

        else:
            # Créer une nouvelle facture dans Firestore
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
                "date": datetime.today().strftime("%Y-%m-%d"),
                "user_id": st.session_state["user_id"],
                "role": st.session_state.get("role", "user")
            }

            try:
                db.collection("factures").add(facture_doc)
                st.success("💾 Document enregistré dans Firestore")
            except Exception:
                st.warning("⚠️ Impossible d'enregistrer la facture en base. Vérifiez la connexion.")

            with open(filename, "rb") as f:
                st.download_button("⬇️ Télécharger le PDF", f, file_name=filename, mime="application/pdf")

conn.close()
