import streamlit as st

st.set_page_config(page_title="Accueil", layout="wide")

# Logo
st.image("assets/logo.png", width=150)

# Titre
st.title("Bienvenue sur MABOU-INSTRUMED Facturation")

# Description
st.markdown("""
### Simplifiez la gestion de vos factures et reçus  
Accédez à une plateforme moderne, sécurisée et adaptée à vos besoins.
""")

# Colonnes
col1, col2 = st.columns(2)

with col1:
    if st.button("🔑 Se connecter"):
        st.switch_page("pages/Login.py")  # ⚠️ Mets bien le nom exact du fichier
