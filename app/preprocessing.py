# =============================================================
# preprocessing.py — ACEP Garantie Prédiction
# Reproduit EXACTEMENT le pipeline du notebook d'entraînement
# Mémoire M2 ISM Paris — ACEP Burkina
# =============================================================

import numpy as np
import pandas as pd
import joblib
import os

# =============================================================
# CHEMINS
# =============================================================
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# =============================================================
# CHARGEMENT DES ARTEFACTS
# =============================================================
try:
    model           = joblib.load(os.path.join(MODELS_DIR, "xgboost_model.pkl"))
    scaler          = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
    feature_columns = joblib.load(os.path.join(MODELS_DIR, "feature_columns.pkl"))
    freq_map        = joblib.load(os.path.join(MODELS_DIR, "garantie_freq_map.pkl"))

    # ✅ Colonnes réellement connues par le scaler (4 colonnes uniquement)
    COLONNES_SCALER = list(scaler.feature_names_in_)

    print("✅ Artefacts chargés avec succès")
    print(f"   → Modèle         : {type(model).__name__}")
    print(f"   → Colonnes total : {len(feature_columns)}")
    print(f"   → Scaler sur     : {COLONNES_SCALER}")
    print(f"   → Garanties      : {len(freq_map)} types connus")
    print(f"   → Type freq_map  : {type(freq_map).__name__}")

except FileNotFoundError as e:
    raise FileNotFoundError(f"❌ Artefact manquant : {e}")


# =============================================================
# FONCTIONS UTILITAIRES — compatibles dict ET pandas Series
# =============================================================
def _freq_get(libelle_clean: str) -> float:
    """
    Récupère la fréquence d'un libellé de garantie.
    Compatible que freq_map soit un dict ou une pandas Series.
    """
    if hasattr(freq_map, 'index'):
        # pandas Series
        return float(freq_map[libelle_clean]) if libelle_clean in freq_map.index else float(freq_map.min())
    else:
        # dictionnaire Python
        return float(freq_map.get(libelle_clean, min(freq_map.values())))


def _freq_keys() -> list:
    """
    Retourne la liste des libellés de garantie connus.
    Compatible que freq_map soit un dict ou une pandas Series.
    """
    if hasattr(freq_map, 'index'):
        return freq_map.index.tolist()
    else:
        return list(freq_map.keys())


# =============================================================
# LISTES POUR LE FORMULAIRE STREAMLIT
# =============================================================
GARANTIES_CONNUES = sorted(_freq_keys())

PROFESSIONS_CONNUES = [
    "AUTRE", "CHAUFFEUR", "COIFFEUSE", "COMMERCANT", "COUTURIER",
    "INSTITUTEUR", "MECANICIEN", "MENAGERE", "MENUISIER",
    "NON_DEFINI", "PROFESSEUR", "RESTAURATEUR", "SOUDEUR",
    "TAILLEUR", "TRANSPORTEUR"
]

GENRES               = ["MASCULIN", "FEMININ", "SOCIETE"]
TYPES_EMPRUNTEUR     = ["TPE", "AUTRE"]
PROPRIETAIRE_OPTIONS = ["OUI", "NON"]


# =============================================================
# FONCTION 1 : Prédiction pour UN SEUL CLIENT
# =============================================================
def predire_un_client(
    age_client:            int,
    duree_credit:          int,
    montant_credit:        float,
    date_adhesion:         str,    # "JJ/MM/AAAA"
    date_accord_credit:    str,    # "JJ/MM/AAAA"
    libelle_garantie:      str,
    genre:                 str,
    type_emprunteur:       str,
    proprietaire_garantie: str,
    profession:            str
) -> dict:
    """
    Prend les données brutes d'un client,
    applique le pipeline complet,
    retourne le montant de garantie prédit.
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
    # Étape 3 : Frequency encoding du libellé de garantie
    # ✅ Utilise _freq_get() — compatible dict ET Series
    # ----------------------------------------------------------
    libelle_clean = libelle_garantie.strip().upper()
    freq_val      = _freq_get(libelle_clean)

    # ----------------------------------------------------------
    # Étape 4 : One-hot encoding
    # ----------------------------------------------------------
    genre_upper = genre.strip().upper()
    prof_upper  = profession.strip().upper()

    prof_dict = {
        f"PROFESSION_GROUPE_{p}": (1 if prof_upper == p else 0)
        for p in PROFESSIONS_CONNUES
    }

    donnees = {
        "AGE_CLIENT":                      age_client,
        "DUREE_CREDIT":                    duree_credit,
        "ANCIENNETE_CLIENT_JOUR_CREDIT":   anciennete,
        "LOG_MONTANT_CREDIT":              log_montant,
        "LIBELLE_GARANTIE_FREQ":           freq_val,
        "GENRE_DU_CLIENT_MASCULIN":        1 if genre_upper == "MASCULIN" else 0,
        "GENRE_DU_CLIENT_SOCIETE":         1 if genre_upper == "SOCIETE"  else 0,
        "TYPE_EMPRUNTEUR_TPE":             1 if type_emprunteur.strip().upper() == "TPE" else 0,
        "PROPRIETAIRE_DE_LA_GARANTIE_OUI": 1 if proprietaire_garantie.strip().upper() == "OUI" else 0,
    }
    donnees.update(prof_dict)

    df = pd.DataFrame([donnees])

    # ----------------------------------------------------------
    # Étape 5 : Standardisation (4 colonnes que le scaler connaît)
    # ✅ Reconstruction DataFrame pour éviter le UserWarning sklearn
    # ----------------------------------------------------------
    df_scaler = pd.DataFrame(
        scaler.transform(df[COLONNES_SCALER]),
        columns=COLONNES_SCALER,
        index=df.index
    )
    df[COLONNES_SCALER] = df_scaler

    # ----------------------------------------------------------
    # Étape 6 : Alignement colonnes (ordre exact du modèle)
    # ----------------------------------------------------------
    df = df.reindex(columns=feature_columns, fill_value=0)

    # ----------------------------------------------------------
    # Étape 7 : Prédiction + retour à l'échelle réelle
    # ----------------------------------------------------------
    pred_log = model.predict(df)[0]
    montant  = float(np.exp(pred_log))

    return {
        "montant_garantie":         round(montant, 0),
        "montant_garantie_formate": f"{montant:,.0f} FCFA".replace(",", " "),
        "anciennete_calculee":      anciennete,
    }


# =============================================================
# FONCTION 2 : Prédiction BATCH (fichier Excel)
# =============================================================
def predire_batch(df_excel: pd.DataFrame) -> pd.DataFrame:
    """
    Prend un DataFrame issu d'un fichier Excel,
    retourne le même DataFrame avec la colonne GARANTIE_PREDITE ajoutée.

    Colonnes attendues dans le fichier Excel :
        AGE_CLIENT, DUREE_CREDIT, MONTANT_DU_CREDIT,
        DATE_ADHESION_CLIENT, DATE_ACCORD_DU_CREDIT,
        LIBELLE_GARANTIE, GENRE_DU_CLIENT,
        TYPE_EMPRUNTEUR, PROPRIETAIRE_DE_LA_GARANTIE,
        PROFESSION_DU_CLIENT
    """
    montants_predits = []

    for idx, row in df_excel.iterrows():
        try:
            res = predire_un_client(
                age_client            = int(row["AGE_CLIENT"]),
                duree_credit          = int(row["DUREE_CREDIT"]),
                montant_credit        = float(row["MONTANT_DU_CREDIT"]),
                date_adhesion         = str(row["DATE_ADHESION_CLIENT"]),
                date_accord_credit    = str(row["DATE_ACCORD_DU_CREDIT"]),
                libelle_garantie      = str(row["LIBELLE_GARANTIE"]),
                genre                 = str(row["GENRE_DU_CLIENT"]),
                type_emprunteur       = str(row["TYPE_EMPRUNTEUR"]),
                proprietaire_garantie = str(row["PROPRIETAIRE_DE_LA_GARANTIE"]),
                profession            = str(row["PROFESSION_DU_CLIENT"])
            )
            montants_predits.append(res["montant_garantie"])

        except Exception as e:
            print(f"⚠️ Erreur ligne {idx} : {e}")
            montants_predits.append(None)

    df_resultat = df_excel.copy()
    df_resultat["GARANTIE_PREDITE (FCFA)"] = montants_predits
    return df_resultat


# =============================================================
# TEST RAPIDE — lancer avec : python app/preprocessing.py
# =============================================================
if __name__ == "__main__":
    print("\n--- TEST DE PRÉDICTION ---")
    res = predire_un_client(
        age_client            = 45,
        duree_credit          = 12,
        montant_credit        = 1_500_000,
        date_adhesion         = "01/01/2018",
        date_accord_credit    = "15/03/2022",
        libelle_garantie      = "MOTOCYCLETTE",
        genre                 = "MASCULIN",
        type_emprunteur       = "TPE",
        proprietaire_garantie = "OUI",
        profession            = "COMMERCANT"
    )
    print(f"✅ Montant prédit    : {res['montant_garantie_formate']}")
    print(f"   Ancienneté       : {res['anciennete_calculee']} jours")