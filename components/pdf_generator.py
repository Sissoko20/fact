from xhtml2pdf import pisa
from datetime import datetime

def format_number(n):
    return f"{n:,.0f}".replace(",", ".")

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
        td.desc { max-width: 250px; word-wrap: break-word; }
        .footer { font-size: 11px; text-align: center; color: #555; margin-top: 20px; }
        .signature { display: flex; justify-content: flex-end; align-items: center; gap: 10px; margin-top: 20px; }
    </style>
    """

    footer_text = """
    <div class="footer">
    MABOU-INSTRUMED-SARL | RCCM : Ma.Bko.2023.M11004 | NIF : 084148985H | HAMDALLAYE ACI 2000  
    Tél : +223 74 56 43 95 | IMMEUBLE MOUSSA ARAMA | Email : sidibeyakouba@ymail.com
    </div>
    """

    # ---------------- FACTURE ----------------
    if type_doc == "Facture de doit":
        items_html = ""
        total_ht = 0
        for item in data["items"]:
            montant = item["qty"] * item["price"]
            total_ht += montant
            items_html += f"""
            <tr>
                <td class="desc">{item['description']}</td>
                <td style="text-align:center;">{item['date']}</td>
                <td style="text-align:center;">{item['qty']}</td>
                <td style="text-align:right;">{format_number(item['price'])} FCFA</td>
                <td style="text-align:right;">{format_number(montant)} FCFA</td>
            </tr>
            """

        montant_total = data.get("montant_total", total_ht)
        montant_paye = data.get("montant_paye", 0.0)
        reliquat = data.get("reliquat", montant_total - montant_paye)
        objet = data.get("objet", "")

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

            <p><b>Objet :</b> {objet}</p>

            <table>
                <thead>
                    <tr>
                        <th>Description</th><th>Date</th><th>Qté</th><th>Prix unitaire</th><th>Montant</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>

            <p><b>Montant total :</b> {format_number(montant_total)} FCFA</p>
            <p><b>Montant payé :</b> {format_number(montant_paye)} FCFA</p>
            <p><b>Reliquat :</b> {format_number(reliquat)} FCFA</p>

            <hr>
            <div class="signature">
                <p style="margin:0;">Fait à Bamako, le {today}</p>
                <img src="{signature_path}" width="220">
            </div>

            {footer_text}
        </div>
        """
        return html

    # ---------------- REÇU ----------------
    elif type_doc == "Reçu de Paiement":
        montant_paye = data.get("montant_paye", 0.0)
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
            <p><b>Montant payé :</b> {format_number(montant_paye)} FCFA</p>

            <hr>
            <div class="signature">
                <p style="margin:0;">Fait à Bamako, le {today}</p>
                <img src="{signature_path}" width="220">
            </div>

            {footer_text}
        </div>
        """
        return html
