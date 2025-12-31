import logging
from firebase_admin_setup import db, app
from firebase_admin import auth

def require_firebase():
    """Vérifie que Firebase Admin est bien initialisé."""
    if not app or not db:
        raise RuntimeError("Firebase Admin non initialisé")

def create_user(email: str, password: str, role: str = "user") -> str:
    """
    Crée un utilisateur dans Firebase Auth et stocke son rôle dans Firestore.
    Retourne l'UID de l'utilisateur.
    """
    require_firebase()
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({
            "email": email,
            "role": role
        })
        return user.uid
    except Exception as e:
        logging.error(f"Erreur lors de la création de l'utilisateur {email}: {e}")
        raise

def get_user_role(email: str) -> str | None:
    """
    Récupère le rôle d'un utilisateur à partir de son email.
    Retourne 'user' par défaut si aucun rôle n'est défini.
    """
    require_firebase()
    try:
        user = auth.get_user_by_email(email)
        doc = db.collection("users").document(user.uid).get()
        if doc.exists:
            return doc.to_dict().get("role", "user")
        return "user"
    except Exception as e:
        logging.warning(f"Erreur lors de la récupération du rôle pour {email}: {e}")
        return None

def is_admin(email: str) -> bool:
    """
    Vérifie si l'utilisateur est un administrateur.
    """
    role = get_user_role(email)
    return role == "admin"
