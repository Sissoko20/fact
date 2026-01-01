import streamlit as st
from xhtml2pdf import pisa
from datetime import datetime
from streamlit_pdf import pdf_viewer   # composant pour prévisualiser le PDF

def generate_pdf(html_content, filename="document.pdf"):
    with open(filename, "wb") as f:
        pisa_status = pisa.CreatePDF(html_content, dest=f)
    if pisa_status.err:
        return None
    return filename

def build_facture_html(data, type_doc="Facture"):
    logo_path = "assets/logo.png"
    signature_path = "assets/signature.png"
    today = datetime.today().strftime("%d/%m/%Y")

    css_style = """
    <style>
        body { font-family: Arial, sans-serif; font-size: 13px; line-height: 1.3; }
        h3 { text-align: center; color: #003366; margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; font-size: 12px; margin-top: 10px; }
        th { background-color: #f2f2f2; border: 1px solid #999; padding: 4px; text-align: center; }
        td { border: 1px solid #999; padding: 4px; }
        .footer { font-size: 11px; text-align: center; color: #555; margin-top: 20px; }
        .signature { display: flex; justify-content: flex-end; align-items: center; gap: 10px; margin-top: 20px; }
    </style>
    """

    footer_text = f"""
    <div class="footer">
    MABOU-INSTRUMED-SARL | RCCM : Ma.Bko.2023.M11004 | NIF : 084148985H | HAMDALLAYE ACI 2000  
    Tél : +223 74 56 43 95 | IMMEUBLE MOUSSA ARAMA | Email : sidibeyakouba@ymail.com
    </div>
    """

    if type_doc == "Facture Professionnelle":
        items_html = ""
        total_ht = 0
        for item in data["items"]:
            montant = item["qty"] * item["price"]
            total_ht += montant
            tva = item.get("tva", 0)
            items_html += f"""
            <tr>
                <td>{item['description']}</td>
                <td style="text-align:center;">{item['date']}</td>
                <td style="text-align:center;">{item['qty']}</td>
                <td style="text-align:right;">{item['price']:.2f} FCFA</td>
                <td style="text-align:center;">{tva}%</td>
                <td style="text-align:right;">{montant:.2f} FCFA</td>
            </tr>
            """

        tva_total = total_ht * 0.18
        total_ttc = total_ht + tva_total

        html = f"""
        {css_style}
        <div style="width:650px; padding:10px;">
            <div style="display:flex; justify-content:space-between;">
                <div>
                    <img src="{logo_path}" width="70"><br>
                    <b>MABOU-INSTRUMED-SARL</b><br>
                    HAMDALLAYE ACI 2000<br>
                    IMMEUBLE MOUSSA ARAMA<br>
                    RUE 384, PORTE 249<br>
                    Tél : +223 74 56 43 95<br>
                    Email : sidibeyakouba@ymail.com
                </div>
                <div style="text-align:right;">
                    <b>Client :</b> {data['client_name']}<br>
                    Tél : {data.get('client_phone','')}<br>
                    Email : {data.get('client_email','')}
                </div>
            </div>

            <hr>
            <h3>FACTURE</h3>

            <table>
                <thead>
                    <tr>
                        <th>Description</th><th>Date</th><th>Qté</th><th>Prix unitaire</th><th>TVA</th><th>Montant</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>

            <p><b>Total HT :</b> {total_ht:.2f} FCFA</p>
            <p><b>TVA 18% :</b> {tva_total:.2f} FCFA</p>
            <p><b>Total TTC :</b> {total_ttc:.2f} FCFA</p>

            <hr>
            <div class="signature">
                <p style="margin:0;">Fait à Bamako, le {today}</p>
                <img src="{signature_path}" width="220">
            </div>

            {footer_text}
        </div>
        """
        return html

    elif type_doc == "Reçu de Paiement":
        html = f"""
        {css_style}
        <div style="width:650px; padding:10px;">
            <div style="display:flex; justify-content:space-between;">
                <div>
                    <img src="{logo_path}" width="70"><br>
                    <b>MABOU-INSTRUMED-SARL</b><br>
                    HAMDALLAYE ACI 2000<br>
                    IMMEUBLE MOUSSA ARAMA<br>
                    RUE 384, PORTE 249<br>
                    Tél : +223 74 56 43 95<br>
                    Email : sidibeyakouba@ymail.com
                </div>
                <div style="text-align:right;">
                    <b>Client :</b> {data['client_name']}<br>
                    Tél : {data.get('client_phone','')}<br>
                    Email : {data.get('client_email','')}
                </div>
            </div>

            <hr>
            <h3>REÇU DE PAIEMENT</h3>

            <p><b>Objet :</b> {data.get('objet','')}</p>
            <p><b>Montant payé :</b> {data.get('amount',0):.2f} FCFA</p>

            <hr>
            <div class="signature">
                <p style="margin:0;">Fait à Bamako, le {today}</p>
                <img src="{signature_path}" width="220">
            </div>

            {footer_text}
        </div>
        """
        return html

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
html_content = build_facture_html(data, type_doc=doc_type)
pdf_file = generate_pdf(html_content, filename="document.pdf")

# Prévisualisation du PDF
if pdf_file:
    pdf_viewer(pdf_file)

    # Bouton de téléchargement
    with open(pdf_file, "rb") as f:
        st.download_button("📥 Télécharger le document", f, file_name=pdf_file, mime="application/pdf")
else:
    st.error("Erreur lors de la génération du PDF")
