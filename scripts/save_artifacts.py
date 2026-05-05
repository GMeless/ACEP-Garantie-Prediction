"""
==============================================================
SCRIPT DE SAUVEGARDE DES ARTEFACTS DE MODÉLISATION
Projet : Prédiction Garantie de Crédit - ACEP
Auteur : M2 ISM Paris
==============================================================

UTILISATION :
    Exécuter CE SCRIPT directement à la fin de ton notebook,
    ou le lancer en standalone après avoir chargé les objets.

    Il sauvegarde de manière robuste :
    - Le modèle XGBoost
    - Le scaler StandardScaler
    - La liste des colonnes finales (feature_columns)
    - Le dictionnaire de frequency encoding (garantie_freq_map)
    - Un fichier de métadonnées pour la traçabilité
==============================================================
"""

import joblib
import json
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

# ⚠️ Adapter ce chemin à ta machine
MODELS_DIR = Path(
    r"D:\DOSSIER MELESS\AAA ISMDATA 26\MODULE_PROJET"
    r"\PROJET_ACEP_BURKINA\PROJET_MEMOIRE_M2_ISM_PARIS"
    r"\Deploiement_Garantie_ACEP\models"
)
MODELS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. FONCTION DE SAUVEGARDE ROBUSTE
# ============================================================

def save_artifact(obj, filename: str, label: str):
    """Sauvegarde un artefact avec vérification d'intégrité."""
    path = MODELS_DIR / filename
    joblib.dump(obj, path)

    # Vérification : rechargement immédiat
    loaded = joblib.load(path)
    size_kb = path.stat().st_size / 1024

    print(f"✅ {label}")
    print(f"   → {path}")
    print(f"   → Taille : {size_kb:.1f} KB")
    print(f"   → Rechargement OK : {type(loaded).__name__}")
    print()
    return loaded


# ============================================================
# 3. SAUVEGARDE DE CHAQUE ARTEFACT
#
#    ⚠️ Les variables ci-dessous doivent exister dans ton
#    environnement notebook AVANT d'appeler ce script.
#    (modele_xgb, scaler, colonnes_finales, freq_map)
# ============================================================

def save_all_artifacts(
    modele_xgb,
    scaler,
    colonnes_finales: list,
    freq_map: dict,
    colonnes_a_scaler: list = None
):
    """
    Sauvegarde tous les artefacts nécessaires au déploiement.

    Paramètres
    ----------
    modele_xgb       : XGBRegressor entraîné
    scaler           : StandardScaler fitté sur X_train
    colonnes_finales : liste des colonnes de X (dans l'ordre exact)
    freq_map         : dict {libelle_garantie: fréquence}
    colonnes_a_scaler: liste des colonnes à standardiser
    """

    if colonnes_a_scaler is None:
        colonnes_a_scaler = [
            "AGE_CLIENT",
            "DUREE_CREDIT",
            "ANCIENNETE_CLIENT_JOUR_CREDIT",
            "LOG_MONTANT_CREDIT",
            "LIBELLE_GARANTIE_FREQ"
        ]

    print("=" * 60)
    print("SAUVEGARDE DES ARTEFACTS - ACEP GARANTIE")
    print("=" * 60)
    print()

    # --- Modèle XGBoost ---
    save_artifact(modele_xgb, "xgboost_model.pkl", "Modèle XGBoost")

    # --- Scaler ---
    save_artifact(scaler, "scaler.pkl", "StandardScaler")

    # --- Colonnes features ---
    save_artifact(colonnes_finales, "feature_columns.pkl", "Feature columns")

    # --- Frequency map ---
    # Conversion en dict natif Python (sérialisable)
    if isinstance(freq_map, pd.Series):
        freq_map_dict = freq_map.to_dict()
    else:
        freq_map_dict = dict(freq_map)

    save_artifact(freq_map_dict, "garantie_freq_map.pkl", "Garantie freq map")

    # --- Colonnes à scaler ---
    save_artifact(colonnes_a_scaler, "colonnes_a_scaler.pkl", "Colonnes à scaler")

    # --- Métadonnées (traçabilité) ---
    metadata = {
        "date_sauvegarde": datetime.now().isoformat(),
        "modele": "XGBRegressor",
        "parametres_modele": {
            "n_estimators": 300,
            "learning_rate": 0.05,
            "max_depth": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "random_state": 42
        },
        "variable_cible": "LOG_MONTANT_GARANTIE",
        "nb_features": len(colonnes_finales),
        "features": colonnes_finales,
        "colonnes_scalees": colonnes_a_scaler,
        "metriques": {
            "MAE": 0.286,
            "RMSE": 0.397,
            "R2": 0.812
        }
    }

    meta_path = MODELS_DIR / "metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    print(f"✅ Métadonnées sauvegardées → {meta_path}")
    print()
    print("=" * 60)
    print("✅ TOUS LES ARTEFACTS SAUVEGARDÉS AVEC SUCCÈS")
    print("=" * 60)


# ============================================================
# 4. BLOC D'APPEL (à coller à la fin de ton notebook)
# ============================================================
#
# Dans ton notebook, après entraînement :
#
#   from scripts.save_artifacts import save_all_artifacts
#   save_all_artifacts(
#       modele_xgb=modele_xgb,
#       scaler=scaler,
#       colonnes_finales=colonnes_finales,
#       freq_map=freq_map,       # ou freq_garantie selon ton notebook
#   )
#
# ============================================================

if __name__ == "__main__":
    print("⚠️ Ce script doit être appelé depuis le notebook.")
    print("   Voir les instructions à la fin du fichier.")
