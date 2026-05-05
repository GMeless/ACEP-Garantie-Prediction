"""
==============================================================
API FASTAPI - ACEP GARANTIE PRÉDICTION
Projet : Prédiction Garantie de Crédit - ACEP
==============================================================

Lancement :
    uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

Documentation auto :
    http://localhost:8000/docs   (Swagger)
    http://localhost:8000/redoc  (ReDoc)
==============================================================
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import pandas as pd
import numpy as np
import io
import logging
from pathlib import Path

# ---- Import du module partagé ----
import sys
sys.path.append(str(Path(__file__).parent.parent / "app"))

from preprocessing import ModelLoader, predict_single, predict_batch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION
# ============================================================

MODELS_DIR = Path(__file__).parent.parent / "models"

# ============================================================
# APPLICATION FASTAPI
# ============================================================

app = FastAPI(
    title="ACEP Garantie Prédiction API",
    description="""
    API de prédiction du montant de garantie de crédit pour l'institution ACEP.
    
    ## Fonctionnalités
    - **Prédiction unitaire** : estimez la garantie pour un client
    - **Prédiction batch** : traitez un fichier Excel complet
    - **Santé du service** : vérifiez que les modèles sont chargés
    
    ## Modèle
    XGBoost entraîné sur les données ACEP Burkina.
    Variable cible : LOG_MONTANT_GARANTIE → résultat converti en FCFA.
    """,
    version="1.0.0",
    contact={
        "name": "Projet M2 ISM Paris",
        "email": "contact@example.com"
    }
)

# ============================================================
# CHARGEMENT DU LOADER (singleton)
# ============================================================

_loader: Optional[ModelLoader] = None


def get_loader() -> ModelLoader:
    global _loader
    if _loader is None:
        _loader = ModelLoader(MODELS_DIR)
        _loader.check_all()
        logger.info("✅ Artefacts chargés avec succès.")
    return _loader


# ============================================================
# SCHÉMAS PYDANTIC
# ============================================================

class ClientInput(BaseModel):
    """Données d'entrée pour un client."""

    age_client: int = Field(
        ..., ge=0, le=100,
        description="Âge du client (0 pour les sociétés)",
        example=35
    )
    duree_credit: int = Field(
        ..., ge=1, le=120,
        description="Durée du crédit en mois",
        example=12
    )
    anciennete_client_jour_credit: int = Field(
        ..., ge=0,
        description="Ancienneté en jours au moment du crédit",
        example=365
    )
    montant_credit: float = Field(
        ..., gt=0,
        description="Montant du crédit en FCFA",
        example=1500000
    )
    libelle_garantie_clean: str = Field(
        ...,
        description="Libellé de la garantie (ex: MOTOCYCLE)",
        example="MOTOCYCLE"
    )
    genre_du_client: str = Field(
        ...,
        description="Genre : MASCULIN, FEMININ ou SOCIETE",
        example="MASCULIN"
    )
    type_emprunteur: str = Field(
        ...,
        description="Type d'emprunteur : TPE, PARTICULIER ou AUTRE",
        example="TPE"
    )
    proprietaire_de_la_garantie: str = Field(
        ...,
        description="Propriétaire de la garantie : OUI ou NON",
        example="OUI"
    )
    profession_groupe: str = Field(
        ...,
        description="Groupe de profession (ex: COMMERCANT)",
        example="COMMERCANT"
    )

    @validator("genre_du_client")
    def validate_genre(cls, v):
        allowed = {"MASCULIN", "FEMININ", "SOCIETE"}
        if v.upper() not in allowed:
            raise ValueError(f"genre_du_client doit être parmi {allowed}")
        return v.upper()

    @validator("type_emprunteur")
    def validate_type(cls, v):
        allowed = {"TPE", "PARTICULIER", "AUTRE"}
        if v.upper() not in allowed:
            raise ValueError(f"type_emprunteur doit être parmi {allowed}")
        return v.upper()

    @validator("proprietaire_de_la_garantie")
    def validate_proprietaire(cls, v):
        allowed = {"OUI", "NON"}
        if v.upper() not in allowed:
            raise ValueError(f"proprietaire_de_la_garantie doit être parmi {allowed}")
        return v.upper()


class PredictionResponse(BaseModel):
    """Réponse de prédiction."""
    montant_garantie_predit: float = Field(description="Montant de garantie estimé (FCFA)")
    montant_garantie_formate: str = Field(description="Montant formaté (ex: 1 234 567 FCFA)")
    prediction_log: float = Field(description="Valeur log prédite (usage interne)")
    ratio_garantie_credit: float = Field(description="Ratio garantie / crédit (%)")
    interpretation: str = Field(description="Interprétation du ratio")


class BatchPredictionResponse(BaseModel):
    """Réponse de prédiction batch."""
    nb_lignes_traitees: int
    message: str
    apercu: List[dict]


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/", tags=["Général"])
def root():
    """Point d'entrée de l'API."""
    return {
        "service": "ACEP Garantie Prédiction API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "predict_batch": "/predict/batch",
            "docs": "/docs"
        }
    }


@app.get("/health", tags=["Santé"])
def health_check():
    """Vérifie que le service et les modèles sont opérationnels."""
    try:
        loader = get_loader()
        nb_features = len(loader.feature_columns)
        return {
            "status": "healthy",
            "model": "XGBoost",
            "nb_features": nb_features,
            "models_dir": str(MODELS_DIR)
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service indisponible : {str(e)}"
        )


@app.post("/predict", response_model=PredictionResponse, tags=["Prédiction"])
def predict(client: ClientInput):
    """
    Prédit le montant de garantie pour un seul client.
    
    Retourne le montant estimé en FCFA avec interprétation.
    """
    try:
        loader = get_loader()
        input_data = {
            "AGE_CLIENT": client.age_client,
            "DUREE_CREDIT": client.duree_credit,
            "ANCIENNETE_CLIENT_JOUR_CREDIT": client.anciennete_client_jour_credit,
            "MONTANT_CREDIT": client.montant_credit,
            "LIBELLE_GARANTIE_CLEAN": client.libelle_garantie_clean,
            "GENRE_DU_CLIENT": client.genre_du_client,
            "TYPE_EMPRUNTEUR": client.type_emprunteur,
            "PROPRIETAIRE_DE_LA_GARANTIE": client.proprietaire_de_la_garantie,
            "PROFESSION_GROUPE": client.profession_groupe,
        }

        result = predict_single(input_data, loader)
        montant = result["montant_garantie_predit"]
        ratio = (montant / client.montant_credit) * 100

        if ratio < 80:
            interpretation = "⚠️ Garantie insuffisante (< 80% du crédit)"
        elif ratio > 150:
            interpretation = "ℹ️ Garantie élevée (> 150% du crédit)"
        else:
            interpretation = "✅ Garantie cohérente avec le profil client"

        return PredictionResponse(
            montant_garantie_predit=montant,
            montant_garantie_formate=result["montant_garantie_formate"],
            prediction_log=result["prediction_log"],
            ratio_garantie_credit=round(ratio, 2),
            interpretation=interpretation
        )

    except Exception as e:
        logger.error(f"Erreur prédiction : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch", tags=["Prédiction"])
async def predict_batch_endpoint(file: UploadFile = File(...)):
    """
    Prédit le montant de garantie pour un fichier Excel batch.
    
    Retourne le fichier Excel enrichi avec la colonne **GARANTIE_PREDITE**.
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Format invalide. Seuls les fichiers .xlsx et .xls sont acceptés."
        )

    try:
        contents = await file.read()
        df_input = pd.read_excel(io.BytesIO(contents))

        if len(df_input) == 0:
            raise HTTPException(status_code=400, detail="Le fichier est vide.")
        if len(df_input) > 10000:
            raise HTTPException(
                status_code=400,
                detail="Limite de 10 000 lignes par requête batch."
            )

        loader = get_loader()
        df_result = predict_batch(df_input, loader)

        # Retour du fichier Excel
        output = io.BytesIO()
        df_result.to_excel(output, index=False)
        output.seek(0)

        filename = file.filename.replace(".xlsx", "_predictions.xlsx")

        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur batch : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/info", tags=["Modèle"])
def model_info():
    """Retourne les informations du modèle en production."""
    import json
    meta_path = MODELS_DIR / "metadata.json"
    if meta_path.exists():
        with open(meta_path, encoding="utf-8") as f:
            return json.load(f)
    return {
        "modele": "XGBoost",
        "version": "1.0.0",
        "metriques": {"MAE": 0.286, "RMSE": 0.397, "R2": 0.812}
    }
