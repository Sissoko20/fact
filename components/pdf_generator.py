import streamlit as st
from fpdf import FPDF
from datetime import datetime
from streamlit_pdf import pdf_viewer   # composant pour prévisualiser le PDF

class PDFGenerator(FPDF):
    def header(self):
        # Logo à gauche
        self.image("assets/logo.png", 10, 8, 20)
        # Coordonnées société à droite
        self.set_font("Arial", "B", 12)
        self.cell(0, 5, "MABOU-INSTRUMED-SARL", ln=True, align="R")
        self.set_font("Arial", "", 9)
        self.cell(0, 5, "HAMDALLAYE ACI 2000 - IMMEUBLE MOUSSA ARAMA", ln=True, align="R")
        self.cell(0, 5, "RUE 384, PORTE 249 - Tél : +223 74 56 43 95", ln=True, align="R")
        self.cell(0, 5, "Email : sidibeyakouba@ymail.com", ln=True, align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-25)
        self.set_font("Arial", "I", 8)
        self.multi_cell(0, 5,
            "MABOU-INSTRUMED-SARL | RCCM : Ma.Bko.2023.M11004 | NIF : 084148985H | HAMDALLAYE ACI 2000\n"
            "Tél : +223 74 56 43 95 | IMMEUBLE MOUSSA ARAMA | Email : sidibeyakouba@ymail.com",
            align="C"
        )

def generate_pdf(data, type_doc="Facture Professionnelle", filename="document.pdf"):
    pdf = PDFGenerator()
    pdf.add_page()
    today = datetime.today().strftime("%d/%m/%Y")

    if type_doc == "Facture Professionnelle":
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "FACTURE", ln=True, align="C")
        pdf.ln(5)

        # Infos client
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, f"Client : {data['client_name']}", ln=True)
        pdf.cell(0, 6, f"Tél : {data.get('client_phone','')}", ln=True)
        pdf.cell(0, 6, f"Email : {data.get('client_email','')}", ln=True)
        pdf.ln(5)

        # Tableau
        pdf.set_font("Arial", "B", 10)
        pdf.cell(50, 8, "Description", 1)
        pdf.cell(30, 8, "Date", 1, align="C")
        pdf.cell(20, 8, "Qté", 1, align="C")
        pdf.cell(30, 8, "Prix unitaire", 1, align="R")
        pdf.cell(20, 8, "TVA", 1, align="C")
        pdf.cell(30, 8, "Montant", 1, ln=True, align="R")

        pdf.set_font("Arial", "", 10)
        total_ht = 0
        for item in data["items"]:
            montant = item["qty"] * item["price"]
            total_ht += montant
            tva = item.get("tva", 0)
            pdf.cell(50, 8, item["description"], 1)
            pdf.cell(30, 8, item["date"], 1, align="C")
            pdf.cell(20, 8, str(item["qty"]), 1, align="C")
            pdf.cell(30, 8, f"{item['price']:.2f} FCFA", 1, align="R")
            pdf.cell(20, 8, f"{tva}%", 1, align="C")
            pdf.cell(30, 8, f"{montant:.2f} FCFA", 1, ln=True, align="R")

        # Totaux
        tva_total = total_ht * 0.18
        total_ttc = total_ht + tva_total
        pdf.ln(5)
        pdf.cell(0, 6, f"Total HT : {total_ht:.2f} FCFA", ln=True)
        pdf.cell(0, 6, f"TVA 18% : {tva_total:.2f} FCFA", ln=True)
        pdf.cell(0, 6, f"Total TTC : {total_ttc:.2f} FCFA", ln=True)

        # Signature
        pdf.ln(10)
        pdf.cell(0, 6, f"Fait à Bamako, le {today}", ln=True, align="R")
        pdf.image("assets/signature.png", x=150, y=pdf.get_y(), w=40)

    elif type_doc == "Reçu de Paiement":
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "REÇU DE PAIEMENT", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, f"Client : {data['client_name']}", ln=True)
        pdf.cell(0, 6, f"Tél : {data.get('client_phone','')}", ln=True)
        pdf.cell(0, 6, f"Email : {data.get('client_email','')}", ln=True)
        pdf.ln(5)

        pdf.cell(0, 6, f"Objet : {data.get('objet','')}", ln=True)
        pdf.cell(0, 6, f"Montant payé : {data.get('amount',0):.2f} FCFA", ln=True)

        pdf.ln(10)
        pdf.cell(0, 6, f"Fait à Bamako, le {today}", ln=True, align="R")
        pdf.image("assets/signature.png", x=150, y=pdf.get_y(), w=40)

    pdf.output(filename)
    return filename

# ---------------- Exemple Streamlit ----------------
st.title("📄 Générateur de Facture / Reçu")

data = {
    "client_name": "Client Test",
    "client_phone": "70 00 00 00",
    "client_email": "client@example.com",
    "items": [
        {"description": "Consultation médicale", "date": "31/12/2025", "qty": 1, "price": 50000, "tva": 18},
        {"description": "Analyse laboratoire", "date": "31/12/2025", "qty": 2, "price": 15000, "tva": 18},
    ],
    "objet": "Paiement consultation",
    "amount": 80000
}

doc_type = st.selectbox("Choisir le type de document", ["Facture Professionnelle", "Reçu de Paiement"])
pdf_file = generate_pdf(data, type_doc=doc_type)

# Prévisualisation du PDF
pdf_viewer(pdf_file)

# Bouton de téléchargement
with open(pdf_file, "rb") as f:
    st.download_button("📥 Télécharger le document", f, file_name=pdf_file, mime="application/pdf")
