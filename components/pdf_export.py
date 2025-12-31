import os
import tempfile
import platform


def generate_pdf(html_content):
    """
    Génération PDF compatible :
    - Windows local  → xhtml2pdf
    - Linux / Cloud → WeasyPrint
    """

    system = platform.system()

    # -------------------------------------------------
    # WINDOWS → XHTML2PDF (pas de dépendances système)
    # -------------------------------------------------
    if system == "Windows":
        try:
            from xhtml2pdf import pisa

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                pisa_status = pisa.CreatePDF(html_content, dest=tmp)
                if pisa_status.err:
                    return None
                return tmp.name

        except Exception as e:
            print("Erreur XHTML2PDF :", e)
            return None

    # -------------------------------------------------
    # LINUX / STREAMLIT CLOUD → WEASYPRINT
    # -------------------------------------------------
    else:
        try:
            from weasyprint import HTML

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                HTML(string=html_content).write_pdf(tmp.name)
                return tmp.name

        except Exception as e:
            print("Erreur WeasyPrint :", e)
            return None
