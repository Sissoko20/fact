import datetime

def facture_standard(data):
    today = datetime.date.today().strftime("%d/%m/%Y")
    total = sum(item["qty"] * item["price"] for item in data["items"])
    return f"Facture du {today} - Client {data['client_name']} - Total {total} FCFA"

def recu_paiement(data):
    today = datetime.date.today().strftime("%d/%m/%Y")
    return f"Reçu du {today} - Client {data['client_name']} - Montant {data['amount']} FCFA"
