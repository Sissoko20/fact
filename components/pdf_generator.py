from datetime import datetime
from components.pdf_utils import image_to_base64

def build_facture_html(data, type_doc="Facture"):
    logo_base64 = image_to_base64("assets/logo.png")
    signature_base64 = image_to_base64("assets/signature.png")
    today = datetime.today().strftime("%d/%m/%Y")

    logo_img = f"data:image/png;base64,{logo_base64}"
    signature_img = f"data:image/png;base64,{signature_base64}"

    css_style = """
    <style>
        body { font-family: Arial, sans-serif; font-size: 13px; }
        h3 { text-align: center; color: #003366; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #999; padding: 5px; }
        th { background: #f2f2f2; }
        .footer { font-size: 11px; text-align: center; margin-top: 20px; }
        .signature { display: flex; justify-content: space-between; margin-top: 30px; }
    </style>
    """

    footer = """
    <div class="footer">
    MABOU-INSTRUMED-SARL | RCCM : Ma.Bko.2023.M11004 | NIF : 084148985H <br>
    HAMDALLAYE ACI 2000 | Tél : +223 74 56 43 95
    </div>
    """

    if type_doc == "Facture Professionnelle":
        rows = ""
        total = 0
        for i in data["items"]:
            montant = i["qty"] * i["price"]
            total += montant
            rows += f"""
            <tr>
                <td>{i['description']}</td>
                <td>{i['date']}</td>
                <td>{i['qty']}</td>
                <td>{i['price']:.2f}</td>
                <td>{i['tva']}%</td>
                <td>{montant:.2f}</td>
            </tr>
            """

        tva = total * 0.18
        ttc = total + tva

        return f"""
        {css_style}
        <img src="{logo_img}" width="80">
        <h3>FACTURE</h3>

        <p><b>Client :</b> {data['client_name']}</p>

        <table>
            <tr>
                <th>Description</th><th>Date</th><th>Qté</th>
                <th>Prix</th><th>TVA</th><th>Montant</th>
            </tr>
            {rows}
        </table>

        <p><b>Total HT :</b> {total:.2f} FCFA</p>
        <p><b>TVA :</b> {tva:.2f} FCFA</p>
        <p><b>Total TTC :</b> {ttc:.2f} FCFA</p>

        <div class="signature">
            <span>Fait à Bamako, le {today}</span>
            <img src="{signature_img}" width="200">
        </div>

        {footer}
        """
