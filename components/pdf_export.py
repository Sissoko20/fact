import tempfile
from xhtml2pdf import pisa


def generate_pdf(html_content):
    """
    Génération PDF compatible Streamlit Cloud
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            status = pisa.CreatePDF(html_content, dest=tmp)
            if status.err:
                return None
            return tmp.name
    except Exception as e:
        print("PDF Error:", e)
        return None
