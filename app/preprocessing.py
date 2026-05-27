# =============================================================
# preprocessing.py — Prédiction Garanties de Crédit V2
# Approche agrégée par dossier — Mise à jour 2026
# Mémoire M2 ISM Paris — Microfinance
# =============================================================

import numpy as np
import pandas as pd
import joblib
import os
import re
import unicodedata
from rapidfuzz import process, fuzz, utils

# =============================================================
# CHEMINS
# =============================================================
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# =============================================================
# CHARGEMENT DES ARTEFACTS
# =============================================================
try:
    model            = joblib.load(os.path.join(MODELS_DIR, "xgboost_model.pkl"))
    scaler           = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
    feature_columns  = joblib.load(os.path.join(MODELS_DIR, "feature_columns.pkl"))
    freq_map         = joblib.load(os.path.join(MODELS_DIR, "garantie_freq_map.pkl"))
    colonnes_scaler  = joblib.load(os.path.join(MODELS_DIR, "colonnes_a_scaler.pkl"))
    fuzzy_references = joblib.load(os.path.join(MODELS_DIR, "fuzzy_references.pkl"))

    COLONNES_SCALER = list(scaler.feature_names_in_)

    print("✅ Artefacts V2 chargés avec succès")
    print(f"   → Modèle         : {type(model).__name__}")
    print(f"   → Colonnes total : {len(feature_columns)}")
    print(f"   → Scaler sur     : {COLONNES_SCALER}")
    print(f"   → Garanties      : {len(freq_map)} types connus")
    print(f"   → Fuzzy refs     : {len(fuzzy_references)} références")

except FileNotFoundError as e:
    raise FileNotFoundError(f"❌ Artefact manquant : {e}")


# =============================================================
# FUZZY MATCHING — Normalisation des libellés de garantie
# =============================================================

def normalize_text(text):
    """Normalise un libellé de garantie brut."""
    if pd.isna(text) or text is None:
        return "NON_DEFINI"
    text = str(text).upper().strip()
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")

    corrections = {
        "MOTOCYCLE"             : "MOTOCYCLETTE",
        "VELOMOTEUR"            : "MOTOCYCLETTE",
        "REFRIGERRATEUR"        : "REFRIGERATEUR",
        "REFRIGERATEURS"        : "REFRIGERATEUR",
        "CONGELATEURS"          : "CONGELATEUR",
        "TELEVISEURS"           : "TELEVISEUR",
        "FAUTEUIL"              : "FAUTEUILS",
        "CHAISE"                : "CHAISES",
        "TABLES"                : "TABLE",
        "VOITURES"              : "VOITURE",
        "CAMIONS"               : "CAMION",
        "ORDINATEURS"           : "ORDINATEUR",
        "MACHINES A COUDRES"    : "MACHINE A COUDRE",
        "MACHINE A COUDRES"     : "MACHINE A COUDRE",
        "STOCK DE MARCHANDISES" : "STOCK DE MARCHANDISE",
    }
    text = corrections.get(text, text)
    text = re.sub(r"[^A-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fuzzy_clean(libelle: str) -> str:
    """Applique le Fuzzy Matching sur un libellé de garantie."""
    norm = normalize_text(libelle)
    if norm == "NON_DEFINI":
        return norm
    resultat = process.extractOne(
        norm,
        fuzzy_references,
        scorer=fuzz.token_sort_ratio,
        processor=utils.default_process,
        score_cutoff=75
    )
    return resultat[0] if resultat else norm


# =============================================================
# LISTES POUR LE FORMULAIRE STREAMLIT
# =============================================================

def _freq_keys():
    if hasattr(freq_map, 'index'):
        return freq_map.index.tolist()
    return list(freq_map.keys())

def _freq_get(libelle_clean: str) -> float:
    if hasattr(freq_map, 'index'):
        return float(freq_map[libelle_clean]) if libelle_clean in freq_map.index else float(freq_map.min())
    return float(freq_map.get(libelle_clean, min(freq_map.values())))


GARANTIES_CONNUES = sorted(_freq_keys())

PROFESSIONS_CONNUES = [
    "AUTRE", "CHAUFFEUR", "COIFFEUSE", "COMMERCANT", "COUTURIER",
    "INSTITUTEUR", "MECANICIEN", "MENAGERE", "MENUISIER",
    "NON_DEFINI", "PROFESSEUR", "RESTAURATEUR", "SOUDEUR",
    "TAILLEUR", "TRANSPORTEUR"
]

GENRES                = ["MASCULIN", "FEMININ", "SOCIETE"]
TYPES_EMPRUNTEUR      = ["TPE", "AUTRE"]
PROPRIETAIRE_OPTIONS  = ["OUI", "NON"]


# =============================================================
# FONCTION PRINCIPALE — Prédiction pour UN DOSSIER COMPLET
# =============================================================

def predire_dossier(
    age_client:            int,
    duree_credit:          int,
    montant_credit:        float,
    date_adhesion:         str,
    date_accord_credit:    str,
    garanties:             list,   # liste de dicts {"libelle": str, "proprietaire": str}
    genre:                 str,
    type_emprunteur:       str,
    profession:            str
) -> dict:
    """
    Prédit le TOTAL des garanties pour un dossier complet.

    Parameters:
        garanties : liste de biens proposés en garantie
                    ex: [{"libelle": "MOTOCYCLETTE", "proprietaire": "OUI"},
                         {"libelle": "SALON", "proprietaire": "OUI"}]

    Returns:
        dict avec total prédit, ratio couverture, détails
    """

    # ----------------------------------------------------------
    # Étape 1 : Ancienneté en jours
    # ----------------------------------------------------------
    date_adh    = pd.to_datetime(date_adhesion,      dayfirst=True)
    date_accord = pd.to_datetime(date_accord_credit, dayfirst=True)
    anciennete  = (date_accord - date_adh).days

    # ----------------------------------------------------------
    # Étape 2 : Log du montant crédit
    # ----------------------------------------------------------
    log_montant = np.log(montant_credit)

    # ----------------------------------------------------------
    # Étape 3 : Nombre de garanties
    # ----------------------------------------------------------
    nb_garanties = len(garanties)

    # ----------------------------------------------------------
    # Étape 4 : Garantie principale (la plus fréquente dans les données)
    # Fuzzy Matching sur chaque garantie saisie
    # ----------------------------------------------------------
    garanties_clean = [fuzzy_clean(g["libelle"]) for g in garanties]

    # La garantie principale = première de la liste
    garantie_principale = garanties_clean[0] if garanties_clean else "NON_DEFINI"
    freq_val = _freq_get(garantie_principale)

    # Propriétaire = OUI si au moins une garantie appartient au client
    proprietaires = [g.get("proprietaire", "NON") for g in garanties]
    proprietaire_oui = 1 if any(p.upper() == "OUI" for p in proprietaires) else 0

    # ----------------------------------------------------------
    # Étape 5 : One-hot encoding
    # ----------------------------------------------------------
    genre_upper = genre.strip().upper()
    prof_upper  = profession.strip().upper()

    prof_dict = {
        f"PROFESSION_GROUPE_{p}": (1 if prof_upper == p else 0)
        for p in PROFESSIONS_CONNUES
    }

    donnees = {
        "AGE_CLIENT"                      : age_client,
        "DUREE_CREDIT"                    : duree_credit,
        "ANCIENNETE_CLIENT_JOUR_CREDIT"   : anciennete,
        "LOG_MONTANT_CREDIT"              : log_montant,
        "LIBELLE_GARANTIE_FREQ"           : freq_val,
        "NB_GARANTIES"                    : nb_garanties,
        "GENRE_DU_CLIENT_MASCULIN"        : 1 if genre_upper == "MASCULIN" else 0,
        "GENRE_DU_CLIENT_SOCIETE"         : 1 if genre_upper == "SOCIETE"  else 0,
        "TYPE_EMPRUNTEUR_TPE"             : 1 if type_emprunteur.strip().upper() == "TPE" else 0,
        "PROPRIETAIRE_DE_LA_GARANTIE_OUI" : proprietaire_oui,
    }
    donnees.update(prof_dict)

    df = pd.DataFrame([donnees])

    # ----------------------------------------------------------
    # Étape 6 : Standardisation
    # ----------------------------------------------------------
    df_scaler = pd.DataFrame(
        scaler.transform(df[COLONNES_SCALER]),
        columns=COLONNES_SCALER,
        index=df.index
    )
    df[COLONNES_SCALER] = df_scaler

    # ----------------------------------------------------------
    # Étape 7 : Alignement colonnes
    # ----------------------------------------------------------
    df = df.reindex(columns=feature_columns, fill_value=0)

    # ----------------------------------------------------------
    # Étape 8 : Prédiction → TOTAL des garanties
    # ----------------------------------------------------------
    pred_log     = model.predict(df)[0]
    total_predit = float(np.exp(pred_log))
    ratio        = (total_predit / montant_credit) * 100

    return {
        "total_garanties_predit"  : round(total_predit, 0),
        "total_garanties_formate" : f"{total_predit:,.0f} FCFA".replace(",", " "),
        "montant_credit"          : montant_credit,
        "ratio_couverture"        : round(ratio, 1),
        "couverture_suffisante"   : ratio >= 100,
        "anciennete_calculee"     : anciennete,
        "nb_garanties"            : nb_garanties,
        "garantie_principale"     : garantie_principale,
        "garanties_clean"         : garanties_clean,
    }


# =============================================================
# FONCTION BATCH — Prédiction via fichier Excel
# =============================================================

def predire_batch(df_excel: pd.DataFrame) -> pd.DataFrame:
    """
    Colonnes attendues dans le fichier Excel :
        AGE_CLIENT, DUREE_CREDIT, MONTANT_DU_CREDIT,
        DATE_ADHESION_CLIENT, DATE_ACCORD_DU_CREDIT,
        LIBELLE_GARANTIE_1 (obligatoire),
        LIBELLE_GARANTIE_2, LIBELLE_GARANTIE_3 ... (optionnels),
        PROPRIETAIRE_DE_LA_GARANTIE,
        GENRE_DU_CLIENT, TYPE_EMPRUNTEUR, PROFESSION_DU_CLIENT
    """
    resultats = []

    for idx, row in df_excel.iterrows():
        try:
            # Construire la liste des garanties
            garanties = []
            for i in range(1, 11):
                col = f"LIBELLE_GARANTIE_{i}"
                if col in row and pd.notna(row[col]) and str(row[col]).strip():
                    garanties.append({
                        "libelle"       : str(row[col]),
                        "proprietaire"  : str(row.get("PROPRIETAIRE_DE_LA_GARANTIE", "OUI"))
                    })

            if not garanties:
                garanties = [{"libelle": "NON_DEFINI", "proprietaire": "NON"}]

            res = predire_dossier(
                age_client         = int(row["AGE_CLIENT"]),
                duree_credit       = int(row["DUREE_CREDIT"]),
                montant_credit     = float(row["MONTANT_DU_CREDIT"]),
                date_adhesion      = str(row["DATE_ADHESION_CLIENT"]),
                date_accord_credit = str(row["DATE_ACCORD_DU_CREDIT"]),
                garanties          = garanties,
                genre              = str(row["GENRE_DU_CLIENT"]),
                type_emprunteur    = str(row["TYPE_EMPRUNTEUR"]),
                profession         = str(row["PROFESSION_DU_CLIENT"])
            )

            resultats.append({
                "TOTAL_GARANTIES_PREDIT (FCFA)" : res["total_garanties_predit"],
                "RATIO_COUVERTURE (%)"           : res["ratio_couverture"],
                "COUVERTURE_SUFFISANTE"          : "✅ OUI" if res["couverture_suffisante"] else "⚠️ NON",
                "NB_GARANTIES"                   : res["nb_garanties"],
                "GARANTIE_PRINCIPALE"            : res["garantie_principale"],
            })

        except Exception as e:
            print(f"⚠️ Erreur ligne {idx} : {e}")
            resultats.append({
                "TOTAL_GARANTIES_PREDIT (FCFA)" : None,
                "RATIO_COUVERTURE (%)"           : None,
                "COUVERTURE_SUFFISANTE"          : "❌ ERREUR",
                "NB_GARANTIES"                   : None,
                "GARANTIE_PRINCIPALE"            : None,
            })

    df_res = pd.DataFrame(resultats)
    return pd.concat([df_excel.reset_index(drop=True), df_res], axis=1)


# =============================================================
# TEST RAPIDE
# =============================================================
if __name__ == "__main__":
    print("\n--- TEST PRÉDICTION DOSSIER COMPLET ---")

    res = predire_dossier(
        age_client         = 45,
        duree_credit       = 12,
        montant_credit     = 3_000_000,
        date_adhesion      = "01/01/2018",
        date_accord_credit = "15/03/2022",
        garanties          = [
            {"libelle": "MOTOCYCLE",            "proprietaire": "OUI"},
            {"libelle": "SALON",                "proprietaire": "OUI"},
            {"libelle": "STOCK DE MARCHANDISE", "proprietaire": "OUI"},
        ],
        genre              = "MASCULIN",
        type_emprunteur    = "TPE",
        profession         = "COMMERCANT"
    )

    print(f"✅ Total garanties prédit  : {res['total_garanties_formate']}")
    print(f"   Montant crédit         : {res['montant_credit']:,.0f} FCFA")
    print(f"   Ratio de couverture    : {res['ratio_couverture']}%")
    print(f"   Couverture suffisante  : {'✅ OUI' if res['couverture_suffisante'] else '⚠️ NON'}")
    print(f"   Nb garanties           : {res['nb_garanties']}")
    print(f"   Garanties nettoyées    : {res['garanties_clean']}")
    print(f"   Ancienneté             : {res['anciennete_calculee']} jours")