# =============================================================
# streamlit_app.py — Prédiction Garanties de Crédit V2
# Approche agrégée par dossier — Mise à jour 2026
# Mémoire M2 ISM Paris — Microfinance
# =============================================================

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from io import BytesIO

# =============================================================
# CONFIGURATION DE LA PAGE
# =============================================================
st.set_page_config(
    page_title="Prédiction Garanties — Microfinance",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================
# IMPORT DU MODULE DE PREPROCESSING
# =============================================================
APP_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(APP_DIR)
sys.path.insert(0, APP_DIR)

from preprocessing import (
    predire_dossier,
    predire_batch,
    GARANTIES_CONNUES,
    PROFESSIONS_CONNUES,
    GENRES,
    TYPES_EMPRUNTEUR,
    PROPRIETAIRE_OPTIONS,
)

# =============================================================
# CSS PERSONNALISÉ
# =============================================================
st.markdown("""
    <style>
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
        .result-card-danger {
            background: linear-gradient(135deg, #C0392B, #E74C3C);
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            margin-top: 20px;
        }
        .result-card-danger .label {
            color: #FADBD8;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .result-card-danger .montant {
            color: white;
            font-size: 2.4em;
            font-weight: bold;
            margin: 8px 0;
        }
        .result-card-danger .detail {
            color: #FADBD8;
            font-size: 0.85em;
        }
        .info-box {
            background: #EBF5FB;
            border-left: 4px solid #2ECC71;
            padding: 12px 16px;
            border-radius: 6px;
            margin: 10px 0;
            font-size: 0.9em;
        }
        .garantie-box {
            background: #F8F9FA;
            border: 1px solid #DEE2E6;
            border-radius: 8px;
            padding: 12px;
            margin: 6px 0;
        }
        .stButton > button {
            background: linear-gradient(135deg, #1A535C, #2ECC71);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            width: 100%;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# =============================================================
# HEADER
# =============================================================
st.markdown("""
    <div style="padding: 20px 0px 10px 0px;">
        <h1 style="color:#1A535C; margin:0;">
            🏦 Système de Prédiction des Garanties de Crédit
        
<p>Outil d'aide à la décision pour les agents de crédit en Microfinance </div>
""", unsafe_allow_html=True)

st.markdown("---")

# =============================================================
# ONGLETS
# =============================================================
onglet1, onglet2 = st.tabs([
    "📋  Prédiction — Dossier Client",
    "📊  Prédiction — Fichier Excel"
])

# ─────────────────────────────────────────────────────────────
# ONGLET 1 — PRÉDICTION DOSSIER COMPLET
# ─────────────────────────────────────────────────────────────
with onglet1:

    st.markdown("### 📋 Saisir les informations du dossier")
    st.markdown("""
        <div class="info-box">
            💡 Saisissez les informations du client et <strong>tous les biens
            proposés en garantie</strong>. Le modèle prédit le montant total
            de couverture et vérifie si le crédit est suffisamment garanti.
        </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # SECTION 1 — Informations client et crédit
    # ----------------------------------------------------------
    st.markdown("#### 👤 Informations client et crédit")
    col1, col2, col3 = st.columns(3)

    with col1:
        genre = st.selectbox("Genre du client", options=GENRES, index=0)
        if genre == "SOCIETE":
            st.info("ℹ️ Client Société — âge non applicable")
            age_client = 0
        else:
            age_client = st.number_input(
                "Âge du client (années)",
                min_value=18, max_value=100, value=28, step=1
            )
        profession = st.selectbox(
            "Profession",
            options=PROFESSIONS_CONNUES,
            index=PROFESSIONS_CONNUES.index("COMMERCANT")
        )

    with col2:
        type_emprunteur = st.selectbox(
            "Type d'emprunteur", options=TYPES_EMPRUNTEUR, index=0)
        montant_credit = st.number_input(
            "Montant du crédit (FCFA)",
            min_value=500_000, max_value=100_000_000,
            value=3_000_000, step=100_000, format="%d"
        )
        duree_credit = st.number_input(
            "Durée du crédit (mois)",
            min_value=1, max_value=60, value=12, step=1
        )

    with col3:
        date_accord = st.date_input(
            "Date d'accord du crédit",
            value=pd.Timestamp("2022-03-15"),
            format="DD/MM/YYYY"
        )
        date_adhesion = st.date_input(
            "Date d'adhésion du client",
            value=pd.Timestamp("2018-01-01"),
            format="DD/MM/YYYY"
        )

    st.markdown("---")

    # ----------------------------------------------------------
    # SECTION 2 — Garanties proposées
    # ----------------------------------------------------------
    st.markdown("#### 🏠 Biens proposés en garantie")
    st.markdown("""
        <div class="info-box">
            💡 Ajoutez tous les biens que le client propose en garantie.
            Minimum 1 bien requis.
        </div>
    """, unsafe_allow_html=True)

    nb_garanties = st.number_input(
        "Nombre de biens en garantie",
        min_value=1, max_value=10, value=1, step=1
    )

    garanties = []
    cols_garanties = st.columns(min(int(nb_garanties), 3))

    for i in range(int(nb_garanties)):
        col_idx = i % 3
        with cols_garanties[col_idx]:
            st.markdown(f"**Garantie {i+1}**")
            libelle = st.selectbox(
                f"Type de bien {i+1}",
                options=GARANTIES_CONNUES,
                index=GARANTIES_CONNUES.index("MOTOCYCLETTE")
                      if "MOTOCYCLETTE" in GARANTIES_CONNUES else 0,
                key=f"libelle_{i}"
            )
            proprio = st.selectbox(
                f"Propriétaire ?",
                options=PROPRIETAIRE_OPTIONS,
                index=0,
                key=f"proprio_{i}"
            )
            garanties.append({"libelle": libelle, "proprietaire": proprio})

    st.markdown("")

    # ----------------------------------------------------------
    # BOUTON PRÉDICTION
    # ----------------------------------------------------------
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        predict_btn = st.button("🔮  Calculer la couverture de garantie")

    # ----------------------------------------------------------
    # RÉSULTAT
    # ----------------------------------------------------------
    if predict_btn:
        if date_adhesion >= date_accord:
            st.error("❌ La date d'adhésion doit être antérieure à la date d'accord.")
        else:
            with st.spinner("Calcul en cours..."):
                try:
                    res = predire_dossier(
                        age_client         = age_client,
                        duree_credit       = duree_credit,
                        montant_credit     = float(montant_credit),
                        date_adhesion      = date_adhesion.strftime("%d/%m/%Y"),
                        date_accord_credit = date_accord.strftime("%d/%m/%Y"),
                        garanties          = garanties,
                        genre              = genre,
                        type_emprunteur    = type_emprunteur,
                        profession         = profession
                    )

                    total    = res["total_garanties_predit"]
                    ratio    = res["ratio_couverture"]
                    suffisant = res["couverture_suffisante"]
                    manque   = max(0, montant_credit - total)

                    # Carte résultat
                    if suffisant:
                        st.markdown(f"""
                            <div class="result-card">
                                <div class="label">✅ Couverture suffisante</div>
                                <div class="montant">{res['total_garanties_formate']}</div>
                                <div class="detail">
                                    Ratio de couverture : <strong>{ratio}%</strong>
                                    du crédit ({montant_credit:,.0f} FCFA)
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="result-card-danger">
                                <div class="label">⚠️ Couverture insuffisante</div>
                                <div class="montant">{res['total_garanties_formate']}</div>
                                <div class="detail">
                                    Ratio de couverture : <strong>{ratio}%</strong>
                                    — Il manque <strong>{manque:,.0f} FCFA</strong>
                                    pour couvrir 100% du crédit
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                    st.markdown("")

                    # Barre de progression
                    st.markdown("**Niveau de couverture :**")
                    progress_val = min(ratio / 100, 1.0)
                    st.progress(progress_val)
                    st.caption(f"{ratio}% de couverture — Seuil requis : 100%")

                    # Métriques
                    st.markdown("")
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Total garanti",   f"{total:,.0f} FCFA")
                    c2.metric("Montant crédit",  f"{montant_credit:,.0f} FCFA")
                    c3.metric("Ratio couverture", f"{ratio}%")
                    c4.metric("Nb garanties",    f"{res['nb_garanties']} biens")

                    # Détail des garanties nettoyées
                    st.markdown("")
                    st.markdown("**Garanties après harmonisation (Fuzzy Matching) :**")
                    df_gar = pd.DataFrame({
                        "N°"              : range(1, len(res["garanties_clean"]) + 1),
                        "Libellé saisi"   : [g["libelle"] for g in garanties],
                        "Libellé nettoyé" : res["garanties_clean"],
                        "Propriétaire"    : [g["proprietaire"] for g in garanties],
                    })
                    st.dataframe(df_gar, use_container_width=True, hide_index=True)

                    if suffisant:
                        st.success("✅ Dossier garanti — Le modèle XGBoost V2 (R²=0.773) valide la couverture.")
                    else:
                        st.warning(
                            f"⚠️ Couverture insuffisante de {ratio}%. "
                            f"Demander {manque:,.0f} FCFA de garanties supplémentaires."
                        )

                except Exception as e:
                    st.error(f"❌ Erreur : {e}")


# ─────────────────────────────────────────────────────────────
# ONGLET 2 — PRÉDICTION BATCH EXCEL
# ─────────────────────────────────────────────────────────────
with onglet2:

    st.markdown("### 📊 Prédiction en masse via fichier Excel")
    st.markdown("""
        <div class="info-box">
            💡 Uploadez un fichier Excel avec plusieurs dossiers clients.
            Chaque dossier peut avoir jusqu'à <strong>5 garanties</strong>
            (colonnes LIBELLE_GARANTIE_1 à LIBELLE_GARANTIE_5).
        </div>
    """, unsafe_allow_html=True)

    # Format attendu
    with st.expander("📌 Voir le format Excel attendu"):
        st.markdown("**Colonnes obligatoires :**")
        df_format = pd.DataFrame({
            "Colonne": [
                "AGE_CLIENT", "DUREE_CREDIT", "MONTANT_DU_CREDIT",
                "DATE_ADHESION_CLIENT", "DATE_ACCORD_DU_CREDIT",
                "LIBELLE_GARANTIE_1", "LIBELLE_GARANTIE_2",
                "LIBELLE_GARANTIE_3", "LIBELLE_GARANTIE_4",
                "LIBELLE_GARANTIE_5",
                "PROPRIETAIRE_DE_LA_GARANTIE",
                "GENRE_DU_CLIENT", "TYPE_EMPRUNTEUR",
                "PROFESSION_DU_CLIENT"
            ],
            "Format / Exemple": [
                "Entier (ex: 28)", "Mois (ex: 12)",
                "FCFA (ex: 3000000)",
                "JJ/MM/AAAA", "JJ/MM/AAAA",
                "Ex: MOTOCYCLETTE (obligatoire)",
                "Ex: SALON (optionnel)",
                "Ex: TELEVISEUR (optionnel)",
                "Ex: REFRIGERATEUR (optionnel)",
                "Ex: STOCK DE MARCHANDISE (optionnel)",
                "OUI / NON",
                "MASCULIN / FEMININ / SOCIETE",
                "TPE / AUTRE",
                "Ex: COMMERCANT"
            ]
        })
        st.dataframe(df_format, use_container_width=True, hide_index=True)

        # Fichier exemple
        exemple = pd.DataFrame([{
            "AGE_CLIENT"                   : 45,
            "DUREE_CREDIT"                 : 12,
            "MONTANT_DU_CREDIT"            : 3000000,
            "DATE_ADHESION_CLIENT"         : "01/01/2018",
            "DATE_ACCORD_DU_CREDIT"        : "15/03/2022",
            "LIBELLE_GARANTIE_1"           : "MOTOCYCLE",
            "LIBELLE_GARANTIE_2"           : "SALON",
            "LIBELLE_GARANTIE_3"           : "STOCK DE MARCHANDISE",
            "LIBELLE_GARANTIE_4"           : "",
            "LIBELLE_GARANTIE_5"           : "",
            "PROPRIETAIRE_DE_LA_GARANTIE"  : "OUI",
            "GENRE_DU_CLIENT"              : "MASCULIN",
            "TYPE_EMPRUNTEUR"              : "TPE",
            "PROFESSION_DU_CLIENT"         : "COMMERCANT"
        }, {
            "AGE_CLIENT"                   : 38,
            "DUREE_CREDIT"                 : 12,
            "MONTANT_DU_CREDIT"            : 1500000,
            "DATE_ADHESION_CLIENT"         : "05/06/2015",
            "DATE_ACCORD_DU_CREDIT"        : "10/01/2023",
            "LIBELLE_GARANTIE_1"           : "TELEVISEUR",
            "LIBELLE_GARANTIE_2"           : "REFRIGERATEUR",
            "LIBELLE_GARANTIE_3"           : "",
            "LIBELLE_GARANTIE_4"           : "",
            "LIBELLE_GARANTIE_5"           : "",
            "PROPRIETAIRE_DE_LA_GARANTIE"  : "OUI",
            "GENRE_DU_CLIENT"              : "FEMININ",
            "TYPE_EMPRUNTEUR"              : "TPE",
            "PROFESSION_DU_CLIENT"         : "COUTURIER"
        }])

        buffer = BytesIO()
        exemple.to_excel(buffer, index=False)
        st.download_button(
            label="⬇️ Télécharger fichier exemple",
            data=buffer.getvalue(),
            file_name="exemple_dossiers_garanties.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.markdown("")

    # Upload
    fichier = st.file_uploader(
        "📂 Choisir le fichier Excel",
        type=["xlsx", "xls"]
    )

    if fichier is not None:
        try:
            df_input = pd.read_excel(fichier)
            st.success(f"✅ Fichier chargé : {len(df_input)} dossier(s) détecté(s)")
            st.dataframe(df_input.head(3), use_container_width=True)

            if st.button("🔮  Lancer la prédiction pour tous les dossiers"):
                with st.spinner(f"Calcul pour {len(df_input)} dossier(s)..."):
                    try:
                        df_res = predire_batch(df_input)
                        st.success(f"✅ Prédictions terminées !")
                        st.dataframe(df_res, use_container_width=True)

                        buffer_res = BytesIO()
                        df_res.to_excel(buffer_res, index=False)
                        st.download_button(
                            label="⬇️ Télécharger les résultats Excel",
                            data=buffer_res.getvalue(),
                            file_name="resultats_garanties.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    except Exception as e:
                        st.error(f"❌ Erreur traitement : {e}")

        except Exception as e:
            st.error(f"❌ Impossible de lire le fichier : {e}")


# =============================================================
# SIDEBAR
# =============================================================
with st.sidebar:
    st.markdown("### 📊 Modèle V2 — Agrégé par dossier")
    st.markdown("""
    | Paramètre | V1 | V2 |
    |-----------|----|----|
    | Algorithme | XGBoost | XGBoost |
    | R² | 0.812 | 0.773 |
    | MAE | 0.286 | 0.303 |
    | RMSE | 0.397 | 0.479 |
    | Données | 184 810 lignes | 45 317 dossiers |
    | Variable cible | 1 bien | Total dossier |
    """)

    st.markdown("---")
    st.markdown("### 🔄 Nouveautés V2")
    st.markdown("""
    - ✅ Prédiction par **dossier complet**
    - ✅ Jusqu'à **10 garanties** par dossier
    - ✅ **Fuzzy Matching** automatique
    - ✅ Indicateur de **couverture** (≥ 100%)
    - ✅ Ratio médian Microfinance : **108.7%**
    """)

    st.markdown("---")
    st.markdown("### 📌 Variable principale")
    st.markdown("""
    **Type de garantie** (52% d'importance),
    suivi du **montant du crédit** (13%) et
    du **nombre de garanties** (nouvelle variable).
    """)

    st.markdown("---")
    st.markdown("### ℹ️ À propos")
    st.markdown("""
    **Mémoire M2 Ingénierie Data**
    ISM Paris — Microfinance

    *Mise à jour Avril 2026*
    """)