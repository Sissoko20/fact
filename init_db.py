import sqlite3
import os

# Vérifier que le dossier data existe
os.makedirs("data", exist_ok=True)

# Connexion à la base (créera data/factures.db si absent)
conn = sqlite3.connect("data/factures.db")
cursor = conn.cursor()

# Création de la table avec toutes les colonnes nécessaires
cursor.execute("""
CREATE TABLE IF NOT EXISTS factures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    client TEXT,
    montant REAL,
    objet TEXT,
    date TEXT
)
""")

conn.commit()
conn.close()

print("✅ Base de données factures.db créée avec succès dans le dossier data/")
