import os, json, base64
import firebase_admin
from firebase_admin import credentials, firestore

def _from_streamlit_secrets():
    try:
        import streamlit as st
        if "firebase" in st.secrets:
            return credentials.Certificate(dict(st.secrets["firebase"]))
    except Exception:
        pass
    return None

def _from_env_json():
    raw = os.environ.get("SERVICE_ACCOUNT_JSON")
    if raw:
        try:
            return credentials.Certificate(json.loads(raw))
        except json.JSONDecodeError:
            pass
    return None

def _from_env_base64():
    b64 = os.environ.get("SERVICE_ACCOUNT_JSON_B64")
    if b64:
        try:
            decoded = base64.b64decode(b64).decode("utf-8")
            return credentials.Certificate(json.loads(decoded))
        except Exception:
            pass
    return None

def _from_file():
    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "serviceAccountKey.json")
    if os.path.exists(path):
        return credentials.Certificate(path)
    return None

def init_firebase():
    if firebase_admin._apps:
        return firebase_admin.get_app()

    for loader in (_from_streamlit_secrets, _from_env_json, _from_env_base64, _from_file):
        cred = loader()
        if cred:
            return firebase_admin.initialize_app(cred)

    try:
        return firebase_admin.initialize_app()
    except Exception:
        return None

app = init_firebase()
db = firestore.client() if app else None
