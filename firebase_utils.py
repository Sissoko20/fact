import firebase_admin
from firebase_admin import credentials, auth, firestore

# Initialiser Firebase Admin une seule fois
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def create_user(email, password, role="user"):
    # Créer l’utilisateur dans Firebase Auth
    user = auth.create_user(
        email=email,
        password=password
    )
    # Stocker le rôle dans Firestore
    db.collection("users").document(user.uid).set({
        "email": email,
        "role": role
    })
    return user.uid

def get_user_role(email):
    try:
        user = auth.get_user_by_email(email)
        doc = db.collection("users").document(user.uid).get()
        if doc.exists:
            return doc.to_dict().get("role", "user")
        return "user"
    except Exception:
        return None
