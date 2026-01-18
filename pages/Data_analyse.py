import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
from streamlit_option_menu import option_menu
from firebase_admin_setup import db
from datetime import datetime

# -------------------------------
# Configuration générale
# -------------------------------
st.set_page_config(
    page_title="Gerer vos factures",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# Sécurité session
# -------------------------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.error("⛔ Vous devez être connecté")
    st.switch_page("pages/Login.py")
    st.stop()

user_id = st.session_state.get("user_id")
role = st.session_state.get("role", "user")

# -------------------------------
# Sidebar navigation
# -------------------------------
with st.sidebar:
    st.image("assets/logo.png", width=120)
    selected = option_menu(
        "Navigation",
        [
            "🏠 Tableau de bord",
            "📊 Gerer vos factures",
            "🧾 Factures",
            "💰 Reçus",
            "👥 Utilisateurs",
            "🔒 Déconnexion"
        ],
        icons=["house", "bar-chart", "file-text", "cash", "people", "box-arrow-right"],
        default_index=1,
    )

# -------------------------------
# Navigation logique
# -------------------------------
if selected == "🏠 Tableau de bord":
    st.switch_page("app.py")
elif selected == "🧾 Factures":
    st.switch_page("pages/Previsualisation.py")
elif selected == "💰 Reçus":
    st.switch_page("pages/Previsualisation.py")
elif selected == "👥 Utilisateurs":
    if role == "admin":
        st.switch_page("pages/Admin.py")
    else:
        st.error("⛔ Accès réservé à l’administrateur")
elif selected == "🔒 Déconnexion":
    st.session_state.clear()
    st.success("✅ Déconnecté")
    st.switch_page("pages/Login.py")

# -------------------------------
# Titre principal
# -------------------------------
st.title("📊 Gérer vos factures")

# -------------------------------
# Chargement des factures (USER UNIQUEMENT)
# -------------------------------
factures_ref = (
    db.collection("factures")
    .where("user_id", "==", user_id)
    .stream()
)

rows = [doc.to_dict() | {"id": doc.id} for doc in factures_ref]
df = pd.DataFrame(rows)

st.subheader("📄 Données chargées")
st.dataframe(df, use_container_width=True)

# -------------------------------
# Aperçu global (vue utilisateur)
# -------------------------------
st.subheader("📊 Aperçu global")

# Colonnes attendues pour les métriques utilisateur
cols_needed = {"montant_total", "montant_paye", "reliquat", "status", "type"}

if df.empty:
    st.info("Aucune facture trouvée pour votre compte.")
else:
    # Normaliser les colonnes numériques si elles existent
    if "montant_total" in df.columns:
        df["montant_total"] = pd.to_numeric(df["montant_total"], errors="coerce").fillna(0)
    if "montant_paye" in df.columns:
        df["montant_paye"] = pd.to_numeric(df["montant_paye"], errors="coerce").fillna(0)
    if "reliquat" in df.columns:
        df["reliquat"] = pd.to_numeric(df["reliquat"], errors="coerce").fillna(0)

    # Calculs sécurisés (utiliser 0 si colonne manquante)
    nb_factures = int(df.shape[0])
    total_montant_paye = float(df["montant_paye"].sum()) if "montant_paye" in df.columns else 0.0
    total_montant_facture = float(df["montant_total"].sum()) if "montant_total" in df.columns else 0.0
    total_reliquat = float(df["reliquat"].sum()) if "reliquat" in df.columns else 0.0

    # Affichage des métriques
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🧾 Nombre de factures", f"{nb_factures}")
    col2.metric("💰 Total payé", f"{total_montant_paye:,.0f} FCFA")
    col3.metric("📄 Total facturé", f"{total_montant_facture:,.0f} FCFA")
    col4.metric("❌ Total reliquat", f"{total_reliquat:,.0f} FCFA")

    # Répartition des statuts si disponible
    if "status" in df.columns:
        st.markdown("#### Répartition des statuts")
        status_counts = df["status"].fillna("inconnu").value_counts().rename_axis("status").reset_index(name="count")
        st.dataframe(status_counts, use_container_width=True)
    else:
        st.info("Le champ 'status' n'est pas disponible pour vos factures.")

    # Optionnel : 5 dernières factures pour contexte
    st.markdown("#### Dernières factures")
    cols_show = ["id", "date", "type", "client_name", "montant_total", "montant_paye", "reliquat", "status"]
    cols_show = [c for c in cols_show if c in df.columns]
    st.dataframe(df.sort_values(by="date", ascending=False).head(5)[cols_show].reset_index(drop=True), use_container_width=True)

# Historique filtré + Impayés (sécurisé)
# -------------------------------
st.subheader("📑 Historique")

# Vérifier qu'il y a des données et la colonne "type"
if df.empty:
    st.info("Aucune facture trouvée pour votre compte.")
else:
    if "type" not in df.columns:
        st.info("Aucune donnée de type disponible dans l'historique.")
    else:
        filtre = st.selectbox(
            "Filtrer par type",
            ["Tous"] + sorted(df["type"].unique()),
            key="filtre_type"
        )

        df_filtre = df if filtre == "Tous" else df[df["type"] == filtre]
        st.dataframe(df_filtre, use_container_width=True)

# -------------------------------
# Liste des impayés en tableau + sélection (safe)
# -------------------------------
cols_needed = {"reliquat", "montant_paye", "montant_total", "client_name"}
if not cols_needed.issubset(df.columns):
    st.info("Les colonnes nécessaires pour afficher les impayés sont manquantes.")
else:
    # Définir impayes ici, même si l'utilisateur n'a aucune facture
    impayes = df[df["reliquat"] > 0].copy()

    st.subheader("❌ Factures impayées")
    if impayes.empty:
        st.info("✅ Vous n'avez aucune facture impayée pour le moment.")
    else:
        # Afficher tableau clair
        tableau_impayes = impayes[["id","date", "client_name", "client_phone", "montant_total", "montant_paye", "reliquat"]]
        st.dataframe(tableau_impayes.reset_index(drop=True), use_container_width=True)

        # Préparer options lisibles pour la sélection
        def option_label(i):
            r = impayes.iloc[i]
            phone = r.get("client_phone", "")
            date = r.get("date", "")
            return f"{r['client_name']} — {phone} — {date} — Reliquat {int(r['reliquat'])} CFA"

        options = [option_label(i) for i in range(len(impayes))]
        # Sélecteur sûr (options non vides)
        selected_option = st.selectbox(
            "Sélectionnez une facture à solder",
            options=options,
            key="facture_select_user"
        )

        if selected_option:
            # retrouver la ligne sélectionnée par index
            idx = options.index(selected_option)
            facture = impayes.iloc[idx]

            montant_paye_input = st.number_input(
                f"Montant payé (Reliquat: {int(facture['reliquat'])} CFA)",
                min_value=0,
                max_value=int(facture["reliquat"]),
                step=100,
                key=f"montant_paye_input_{facture['id']}"
            )

            # -------------------------------
            # Bouton Solder (dans le même scope que facture)
            # -------------------------------
            if st.button("Solder la facture sélectionnée", key=f"solder_selected_{facture['id']}"):
                # calculer ici même
                nouveau_montant_paye = float(facture.get("montant_paye", 0)) + float(montant_paye_input)
                nouveau_reliquat = float(facture.get("montant_total", 0)) - nouveau_montant_paye
                nouveau_reliquat = max(nouveau_reliquat, 0)

                # mise à jour Firestore
                doc_ref = db.collection("factures").document(facture["id"])
                doc_ref.update({
                    "montant_paye": nouveau_montant_paye,
                    "reliquat": nouveau_reliquat,
                    "status": "payée" if nouveau_reliquat == 0 else "partielle"
                })

                # Enregistrer le paiement dans une sous-collection 'paiements'
                paiement_data = {
                    "montant": float(montant_paye_input),
                    "date": datetime.utcnow().isoformat(),
                    "user_id": user_id,
                    "mode": "manuel_user"
                }
                try:
                    doc_ref.collection("paiements").add(paiement_data)
                except Exception:
                    # si l'API Firestore diffère, on ignore l'erreur d'ajout de paiement mais la facture est mise à jour
                    pass

                # Préparer la prévisualisation / génération PDF dans la page Previsualisation
                st.session_state["preview_invoice_id"] = facture["id"]
                st.session_state["preview_generate_pdf"] = True

                # afficher le message de succès ici (variables définies)
                st.success(
                    f"Facture {facture['id']} mise à jour ✅ "
                    f"(Payé: {int(nouveau_montant_paye)} CFA, Reliquat: {int(nouveau_reliquat)} CFA)"
                )

                # tentative de rerun ou redirection vers la page de prévisualisation
                try:
                    # si disponible, relancer proprement
                    st.experimental_rerun()
                except Exception:
                    # fallback : naviguer vers la page de prévisualisation
                    try:
                        st.switch_page("pages/Previsualisation.py")
                    except Exception:
                        # dernier fallback : forcer un flag et stopper pour rafraîchir l'UI
                        st.session_state["_needs_refresh"] = not st.session_state.get("_needs_refresh", False)
                        st.stop()
