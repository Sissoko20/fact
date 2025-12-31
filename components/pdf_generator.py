from fpdf import FPDF
from datetime import datetime
import os

class PDF(FPDF):
    def header(self):
        # Logo
        if os.path.exists("assets/logo.png"):
            self.image("assets/logo.png", 10, 8, 25)
        # Titre
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "MABOU-INSTRUMED-SARL", ln=True, align="R")
        self.set_font("Arial", "", 9)
        self.cell(0, 5, "HAMDALLAYE ACI 2000 - IMMEUBLE MOUSSA ARAMA", ln=True, align="R")
        self.cell(0, 5, "Tél : +223 74 56 43 95 | Email : sidibeyakouba@ymail.com", ln=True, align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-20)
        self.set_font("Arial", "I", 8)
        self.multi_cell(0, 5,
            "MABOU-INSTRUMED-SARL | RCCM : Ma.Bko.2023.M11004 | NIF : 084148985H\n"
            "HAMDALLAYE ACI 2000 | Tél : +223 74 56 43 95 | Email : sidibeyakouba@ymail.com",
            align="C"
        )

def generate_pdf(data, type_doc="Facture Professionnelle", filename="document.pdf"):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    today = datetime.today().strftime("%d/%m/%Y")

    # ---------------- FACTURE ----------------
    if type_doc == "Facture Professionnelle":
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "FACTURE", ln=True, align="C")
        pdf.ln(5)

        # Client
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 10, f"Client : {data['client_name']}", ln=True)
        pdf.cell(0, 10, f"Tél : {data.get('client_phone','')}", ln=True)
        pdf.cell(0, 10, f"Email : {data.get('client_email','')}", ln=True)
        pdf.ln(5)

        # Tableau
        pdf.set_font("Arial", "B", 10)
        pdf.cell(60, 8, "Description", 1)
        pdf.cell(25, 8, "Date", 1, align="C")
        pdf.cell(20, 8, "Qté", 1, align="C")
        pdf.cell(30, 8, "Prix unitaire", 1, align="R")
        pdf.cell(20, 8, "TVA", 1, align="C")
        pdf.cell(35, 8, "Montant", 1, align="R")
        pdf.ln()

        total_ht = 0
        for item in data["items"]:
            montant = item["qty"] * item["price"]
            total_ht += montant
            pdf.set_font("Arial", "", 10)
            pdf.cell(60, 8, item["description"], 1)
            pdf.cell(25, 8, item["date"], 1, align="C")
            pdf.cell(20, 8, str(item["qty"]), 1, align="C")
            pdf.cell(30, 8, f"{item['price']:.2f}", 1, align="R")
            pdf.cell(20, 8, f"{item.get('tva',0)}%", 1, align="C")
            pdf.cell(35, 8, f"{montant:.2f}", 1, align="R")
            pdf.ln()

        tva_total = total_ht * 0.18
        total_ttc = total_ht + tva_total

        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, f"Total HT : {total_ht:.2f} FCFA", ln=True)
        pdf.cell(0, 8, f"TVA 18% : {tva_total:.2f} FCFA", ln=True)
        pdf.cell(0, 8, f"Total TTC : {total_ttc:.2f} FCFA", ln=True)

        pdf.ln(10)
        pdf.cell(0, 8, f"Fait à Bamako, le {today}", ln=True, align="R")
        if os.path.exists("assets/signature.png"):
            pdf.image("assets/signature.png", x=150, y=pdf.get_y(), w=50)

    # ---------------- REÇU ----------------
    elif type_doc == "Reçu de Paiement":
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "REÇU DE PAIEMENT", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 10, f"Client : {data['client_name']}", ln=True)
        pdf.cell(0, 10, f"Tél : {data.get('client_phone','')}", ln=True)
        pdf.cell(0, 10, f"Email : {data.get('client_email','')}", ln=True)
        pdf.ln(5)

        pdf.cell(0, 10, f"Objet : {data.get('objet','')}", ln=True)
        pdf.cell(0, 10, f"Montant payé : {data.get('amount',0):.2f} FCFA", ln=True)

        pdf.ln(10)
        pdf.cell(0, 8, f"Fait à Bamako, le {today}", ln=True, align="R")
        if os.path.exists("assets/signature.png"):
            pdf.image("assets/signature.png", x=150, y=pdf.get_y(), w=50)

    pdf.output(filename)
    return filename
