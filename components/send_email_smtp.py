import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_email_smtp(sender, password, recipient, subject, body, pdf_file):
    try:
        # Création du message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject

        # Corps du mail
        msg.attach(MIMEText(body, 'plain'))

        # Pièce jointe PDF
        with open(pdf_file, "rb") as f:
            attach = MIMEApplication(f.read(), _subtype="pdf")
            attach.add_header('Content-Disposition', 'attachment', filename=pdf_file)
            msg.attach(attach)

        # Connexion SMTP (exemple Gmail)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        st.error(f"❌ Erreur envoi email : {e}")
        return False
