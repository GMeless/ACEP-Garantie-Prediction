# =============================================================
# streamlit_app.py — Interface ACEP Garantie
# Application de prédiction du montant des garanties de crédit
# Mémoire M2 ISM Paris — ACEP Burkina
# =============================================================

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from io import BytesIO

# =============================================================
# CONFIGURATION DE LA PAGE (doit être le 1er appel Streamlit)
# =============================================================
st.set_page_config(
    page_title="ACEP — Prédiction Garanties",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================
# IMPORT DU MODULE DE PREPROCESSING
# Ce fichier est dans app/, on ajoute app/ au path Python
# =============================================================
APP_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(APP_DIR)
sys.path.insert(0, APP_DIR)

from preprocessing import (
    predire_un_client,
    predire_batch,
    GARANTIES_CONNUES,
    PROFESSIONS_CONNUES,
    GENRES,
    TYPES_EMPRUNTEUR,
    PROPRIETAIRE_OPTIONS,
)

# =============================================================
# CSS PERSONNALISÉ — Style professionnel ACEP
# =============================================================
st.markdown("""
    <style>
        /* Couleurs ACEP */
        :root {
            --acep-vert:    #2ECC71;
            --acep-bleu:    #1A535C;
            --acep-gris:    #F4F6F7;
        }

        /* Header principal */
        .header-box {
            background: linear-gradient(135deg, #1A535C, #2ECC71);
            padding: 20px 30px;
            border-radius: 12px;
            margin-bottom: 25px;
            text-align: center;
        }
        .header-box h1 {
            color: white;
            font-size: 1.8em;
            margin: 0;
        }
        .header-box p {
            color: #e8f8f5;
            margin: 5px 0 0 0;
            font-size: 0.95em;
        }

        /* Carte résultat */
        .result-card {
            background: linear-gradient(135deg, #1A535C, #117A65);
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            margin-top: 20px;
        }
        .result-card .label {
            color: #A9DFBF;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .result-card .montant {
            color: white;
            font-size: 2.4em;
            font-weight: bold;
            margin: 8px 0;
        }
        .result-card .detail {
            color: #D5F5E3;
            font-size: 0.85em;
        }

        /* Info box */
        .info-box {
            background: #EBF5FB;
            border-left: 4px solid #2ECC71;
            padding: 12px 16px;
            border-radius: 6px;
            margin: 10px 0;
            font-size: 0.9em;
        }

        /* Bouton principal */
        .stButton > button {
            background: linear-gradient(135deg, #1A535C, #2ECC71);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            width: 100%;
            cursor: pointer;
        }
        .stButton > button:hover {
            opacity: 0.9;
        }

        /* Masquer le footer Streamlit */
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


# =============================================================
# HEADER
# =============================================================
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo_acep.png")

col_logo, col_titre = st.columns([1, 4])
with col_logo:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)
with col_titre:
    st.markdown("""
        <div style="padding-top:10px;">
            <h1 style="color:#1A535C; margin:0;">Système de Prédiction des Garanties</h1>
            <p style="color:#555; margin:4px 0 0 0;">
                ACEP Burkina — Outil d'aide à la décision pour les agents de crédit
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")


# =============================================================
# ONGLETS PRINCIPAUX
# =============================================================
onglet1, onglet2 = st.tabs([
    "📋  Prédiction — 1 Client",
    "📊  Prédiction — Fichier Excel"
])


# ─────────────────────────────────────────────────────────────
# ONGLET 1 : PRÉDICTION UNITAIRE
# ─────────────────────────────────────────────────────────────
with onglet1:

    st.markdown("### 📋 Saisir les informations du client")
    st.markdown("""
        <div class="info-box">
            💡 Remplissez les champs ci-dessous. Le montant de garantie recommandé
            sera calculé automatiquement par le modèle XGBoost.
        </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # FORMULAIRE — 3 colonnes
    # ----------------------------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**👤 Informations client**")

        age_client = st.number_input(
            "Âge du client (années)",
            min_value=18, max_value=100, value=18, step=1
        )
        genre = st.selectbox(
            "Genre du client",
            options=GENRES,
            index=0
        )
        profession = st.selectbox(
            "Profession",
            options=PROFESSIONS_CONNUES,
            index=PROFESSIONS_CONNUES.index("COMMERCANT")
        )
        type_emprunteur = st.selectbox(
            "Type d'emprunteur",
            options=TYPES_EMPRUNTEUR,
            index=0
        )

    with col2:
        st.markdown("**💳 Informations crédit**")

        montant_credit = st.number_input(
            "Montant du crédit (FCFA)",
            min_value=50_000,
            max_value=100_000_000,
            value=1_000_000,
            step=50_000,
            format="%d"
        )
        duree_credit = st.number_input(
            "Durée du crédit (mois)",
            min_value=1, max_value=60, value=12, step=1
        )
        date_accord = st.date_input(
            "Date d'accord du crédit",
            value=pd.Timestamp("2022-03-15"),
            format="DD/MM/YYYY"
        )

    with col3:
        st.markdown("**🏠 Informations garantie**")

        libelle_garantie = st.selectbox(
            "Type de garantie",
            options=GARANTIES_CONNUES,
            index=GARANTIES_CONNUES.index("MOTOCYCLETTE") if "MOTOCYCLETTE" in GARANTIES_CONNUES else 0
        )
        proprietaire_garantie = st.selectbox(
            "Le client est propriétaire ?",
            options=PROPRIETAIRE_OPTIONS,
            index=0
        )
        date_adhesion = st.date_input(
            "Date d'adhésion du client",
            value=pd.Timestamp("2018-01-01"),
            format="DD/MM/YYYY"
        )

    st.markdown("")

    # ----------------------------------------------------------
    # BOUTON DE PRÉDICTION
    # ----------------------------------------------------------
    col_btn, col_vide = st.columns([1, 2])
    with col_btn:
        predict_btn = st.button("🔮  Calculer le montant de garantie")

    # ----------------------------------------------------------
    # RÉSULTAT
    # ----------------------------------------------------------
    if predict_btn:

        # Validation de base
        if date_adhesion >= date_accord:
            st.error("❌ La date d'adhésion doit être antérieure à la date d'accord du crédit.")
        else:
            with st.spinner("Calcul en cours..."):
                try:
                    resultat = predire_un_client(
                        age_client            = age_client,
                        duree_credit          = duree_credit,
                        montant_credit        = float(montant_credit),
                        date_adhesion         = date_adhesion.strftime("%d/%m/%Y"),
                        date_accord_credit    = date_accord.strftime("%d/%m/%Y"),
                        libelle_garantie      = libelle_garantie,
                        genre                 = genre,
                        type_emprunteur       = type_emprunteur,
                        proprietaire_garantie = proprietaire_garantie,
                        profession            = profession
                    )

                    montant = resultat["montant_garantie"]
                    ratio   = (montant / montant_credit) * 100

                    # Carte résultat
                    st.markdown(f"""
                        <div class="result-card">
                            <div class="label">Montant de garantie recommandé</div>
                            <div class="montant">{resultat['montant_garantie_formate']}</div>
                            <div class="detail">
                                Soit <strong>{ratio:.1f}%</strong> du montant du crédit
                                ({montant_credit:,.0f} FCFA)
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Détails supplémentaires
                    st.markdown("")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Ancienneté client", f"{resultat['anciennete_calculee']} jours")
                    c2.metric("Montant crédit",    f"{montant_credit:,.0f} FCFA")
                    c3.metric("Ratio garantie",    f"{ratio:.1f}%")

                    st.success("✅ Prédiction réalisée avec succès par le modèle XGBoost (R² = 0.81)")

                except Exception as e:
                    st.error(f"❌ Erreur lors de la prédiction : {e}")


# ─────────────────────────────────────────────────────────────
# ONGLET 2 : PRÉDICTION BATCH (EXCEL)
# ─────────────────────────────────────────────────────────────
with onglet2:

    st.markdown("### 📊 Prédiction en masse via fichier Excel")
    st.markdown("""
        <div class="info-box">
            💡 Uploadez un fichier Excel contenant plusieurs clients.
            L'application ajoutera automatiquement la colonne <strong>GARANTIE_PREDITE (FCFA)</strong>.
        </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # FORMAT ATTENDU
    # ----------------------------------------------------------
    with st.expander("📌 Voir le format Excel attendu"):
        st.markdown("Le fichier Excel doit contenir **exactement ces colonnes** :")
        colonnes_attendues = pd.DataFrame({
            "Colonne": [
                "AGE_CLIENT", "DUREE_CREDIT", "MONTANT_DU_CREDIT",
                "DATE_ADHESION_CLIENT", "DATE_ACCORD_DU_CREDIT",
                "LIBELLE_GARANTIE", "GENRE_DU_CLIENT",
                "TYPE_EMPRUNTEUR", "PROPRIETAIRE_DE_LA_GARANTIE",
                "PROFESSION_DU_CLIENT"
            ],
            "Format": [
                "Entier (ex: 25)", "Entier en mois (ex: 12)", "Entier en FCFA (ex: 1500000)",
                "JJ/MM/AAAA", "JJ/MM/AAAA",
                "Texte (ex: MOTOCYCLETTE)", "MASCULIN / FEMININ / SOCIETE",
                "TPE / AUTRE", "OUI / NON",
                "Texte (ex: COMMERCANT)"
            ]
        })
        st.dataframe(colonnes_attendues, use_container_width=True, hide_index=True)

        # Bouton pour télécharger un fichier exemple
        exemple = pd.DataFrame([{
            "AGE_CLIENT": 18,
            "DUREE_CREDIT": 12,
            "MONTANT_DU_CREDIT": 1500000,
            "DATE_ADHESION_CLIENT": "01/01/2018",
            "DATE_ACCORD_DU_CREDIT": "15/03/2022",
            "LIBELLE_GARANTIE": "MOTOCYCLETTE",
            "GENRE_DU_CLIENT": "MASCULIN",
            "TYPE_EMPRUNTEUR": "TPE",
            "PROPRIETAIRE_DE_LA_GARANTIE": "OUI",
            "PROFESSION_DU_CLIENT": "COMMERCANT"
        }, {
            "AGE_CLIENT": 42,
            "DUREE_CREDIT": 24,
            "MONTANT_DU_CREDIT": 3000000,
            "DATE_ADHESION_CLIENT": "05/06/2015",
            "DATE_ACCORD_DU_CREDIT": "10/01/2023",
            "LIBELLE_GARANTIE": "SALON",
            "GENRE_DU_CLIENT": "FEMININ",
            "TYPE_EMPRUNTEUR": "TPE",
            "PROPRIETAIRE_DE_LA_GARANTIE": "NON",
            "PROFESSION_DU_CLIENT": "COUTURIER"
        }])

        buffer = BytesIO()
        exemple.to_excel(buffer, index=False)
        st.download_button(
            label="⬇️ Télécharger un fichier exemple",
            data=buffer.getvalue(),
            file_name="exemple_clients_acep.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.markdown("")

    # ----------------------------------------------------------
    # UPLOAD DU FICHIER
    # ----------------------------------------------------------
    fichier = st.file_uploader(
        "📂 Choisir le fichier Excel",
        type=["xlsx", "xls"],
        help="Fichier Excel avec les colonnes indiquées ci-dessus"
    )

    if fichier is not None:
        try:
            df_input = pd.read_excel(fichier)
            st.success(f"✅ Fichier chargé : {len(df_input)} client(s) détecté(s)")
            st.dataframe(df_input.head(5), use_container_width=True)

            # Bouton de traitement
            if st.button("🔮  Lancer la prédiction pour tous les clients"):
                with st.spinner(f"Calcul en cours pour {len(df_input)} client(s)..."):
                    try:
                        df_resultat = predire_batch(df_input)

                        st.success(f"✅ Prédictions terminées pour {len(df_resultat)} client(s) !")
                        st.dataframe(df_resultat, use_container_width=True)

                        # Téléchargement des résultats
                        buffer_result = BytesIO()
                        df_resultat.to_excel(buffer_result, index=False)

                        st.download_button(
                            label="⬇️ Télécharger les résultats Excel",
                            data=buffer_result.getvalue(),
                            file_name="predictions_garanties_acep.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                    except Exception as e:
                        st.error(f"❌ Erreur lors du traitement : {e}")

        except Exception as e:
            st.error(f"❌ Impossible de lire le fichier : {e}")


# =============================================================
# SIDEBAR — Informations sur le modèle
# =============================================================
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=150)

    st.markdown("---")
    st.markdown("### 📊 Informations modèle")
    st.markdown("""
    | Paramètre | Valeur |
    |-----------|--------|
    | Algorithme | XGBoost |
    | R² | 0.812 |
    | MAE | 0.286 |
    | RMSE | 0.397 |
    | Données | 184 810 obs. |
    """)

    st.markdown("---")
    st.markdown("### 📌 Variable principale")
    st.markdown("""
    La variable la plus influente est le
    **type de garantie** (52% d'importance),
    suivie du **montant du crédit** (13%).
    """)

    st.markdown("---")
    st.markdown("### ℹ️ À propos")
    st.markdown("""
    Application développée dans le cadre du
    **Mémoire M2 — ISM Paris **

    Domaine : Microfinance / Data Science

    *ACEP Burkina — 2026 MAJ *
    """)