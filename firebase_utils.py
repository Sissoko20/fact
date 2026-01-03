import logging
from firebase_admin_setup import db, app
from firebase_admin import auth

def require_firebase():
    """Vérifie que Firebase Admin est bien initialisé."""
    if not app or not db:
        raise RuntimeError("Firebase Admin non initialisé")

def create_user(email: str, password: str, role: str = "user") -> str:
    """
    Crée un utilisateur dans Firebase Auth et stocke son rôle + mot de passe dans Firestore.
    Retourne l'UID de l'utilisateur.
    ⚠️ En production, ne jamais stocker le mot de passe en clair → utiliser bcrypt.
    """
    require_firebase()
    try:
        user = auth.create_user(email=email, password=password)
        db.collection("users").document(user.uid).set({
            "email": email,
            "password": password,   # ⚠️ à remplacer par un hash en prod
            "role": role
        })
        logging.info(f"Utilisateur {email} créé avec rôle {role}")
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

def verify_user(email: str, password: str) -> str | None:
    """
    Vérifie si un utilisateur existe avec email + mot de passe.
    Retourne son rôle si trouvé, sinon None.
    ⚠️ Firebase Admin SDK ne permet pas de vérifier directement le mot de passe.
    👉 Ici, on simule avec Firestore (non sécurisé).
    """
    require_firebase()
    try:
        users_ref = db.collection("users").where("email", "==", email).stream()
        for u in users_ref:
            data = u.to_dict()
            if data.get("password") == password:  # ⚠️ comparer un hash en prod
                return data.get("role", "user")
        return None
    except Exception as e:
        logging.error(f"Erreur lors de la vérification de l'utilisateur {email}: {e}")
        return None

def is_admin(email: str) -> bool:
    """
    Vérifie si l'utilisateur est un administrateur.
    """
    role = get_user_role(email)
    return role == "admin"
