# 🏦 ACEP – Prédiction du Montant de Garantie de Crédit

> **Projet de fin d'études M2 Ingénierie Data – ISM Paris (2026)**  
> Institution partenaire : **ACEP Burkina Faso** (microfinance)

---

## 📋 Présentation

Ce projet développe un modèle de Machine Learning pour **prédire le montant de garantie** requis lors d'une demande de crédit dans une institution de microfinance.

L'objectif est d'aider les agents de crédit à disposer d'une estimation objective, cohérente et rapide du niveau de garantie à exiger d'un client.

---

## 🎯 Problématique

Dans une institution de microfinance, le montant de garantie exigé peut varier selon l'agent de crédit, le profil du client, et les pratiques locales. Ce projet vise à **standardiser et objectiver** cette décision grâce au Machine Learning.

---

## 📊 Résultats du Modèle

| Modèle             | MAE   | RMSE  | R²    |
|--------------------|-------|-------|-------|
| Régression Linéaire | 0.625 | 0.817 | 0.325 |
| Arbre de Décision  | 0.376 | 0.514 | 0.611 |
| Random Forest      | 0.307 | 0.432 | 0.735 |
| **XGBoost ✅**     | **0.286** | **0.397** | **0.812** |

> Le modèle XGBoost est retenu comme modèle final.  
> Variable cible : `LOG_MONTANT_GARANTIE` (log du montant de garantie en FCFA).

---

## 🗂️ Structure du Projet

```
Deploiement_Garantie_ACEP/
│
├── app/
│   ├── streamlit_app.py        # Interface utilisateur Streamlit
│   └── preprocessing.py        # Pipeline de prétraitement (partagé)
│
├── api/
│   └── main.py                 # API FastAPI (endpoints REST)
│
├── models/
│   ├── xgboost_model.pkl       # Modèle XGBoost entraîné
│   ├── scaler.pkl               # StandardScaler (fitté sur X_train)
│   ├── feature_columns.pkl      # Liste ordonnée des features
│   ├── garantie_freq_map.pkl    # Dictionnaire frequency encoding
│   ├── colonnes_a_scaler.pkl    # Colonnes à standardiser
│   └── metadata.json            # Méta-informations du modèle
│
├── scripts/
│   └── save_artifacts.py        # Script de sauvegarde des artefacts
│
├── data/                        # (non versionné – données sensibles)
│
├── requirements.txt
└── README.md
```

---

## 🔧 Variables Utilisées

### Variables numériques (standardisées)
- `AGE_CLIENT` – Âge du client
- `DUREE_CREDIT` – Durée du crédit (mois)
- `ANCIENNETE_CLIENT_JOUR_CREDIT` – Ancienneté client au moment du crédit (jours)
- `LOG_MONTANT_CREDIT` – Log du montant de crédit (après winsorisation)
- `LIBELLE_GARANTIE_FREQ` – Fréquence d'apparition du type de garantie

### Variables catégorielles (encodées)
- `GENRE_DU_CLIENT` → one-hot (MASCULIN, SOCIETE)
- `TYPE_EMPRUNTEUR` → one-hot (TPE)
- `PROPRIETAIRE_DE_LA_GARANTIE` → one-hot (OUI)
- `PROFESSION_GROUPE` → one-hot (15 catégories)

---

## 🚀 Installation et Lancement

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-user/acep-garantie-prediction.git
cd acep-garantie-prediction
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Générer les artefacts du modèle

Dans votre notebook, **après l'entraînement**, exécutez :

```python
from scripts.save_artifacts import save_all_artifacts

save_all_artifacts(
    modele_xgb=modele_xgb,
    scaler=scaler,
    colonnes_finales=colonnes_finales,
    freq_map=freq_garantie   # ou freq_map selon votre notebook
)
```

### 4. Lancer l'application Streamlit

```bash
streamlit run app/streamlit_app.py
```

→ Accessible sur : [http://localhost:8501](http://localhost:8501)

### 5. Lancer l'API FastAPI (optionnel)

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

→ Documentation interactive : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔌 API REST – Exemples

### Prédiction unitaire (POST /predict)

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age_client": 35,
    "duree_credit": 12,
    "anciennete_client_jour_credit": 365,
    "montant_credit": 1500000,
    "libelle_garantie_clean": "MOTOCYCLE",
    "genre_du_client": "MASCULIN",
    "type_emprunteur": "TPE",
    "proprietaire_de_la_garantie": "OUI",
    "profession_groupe": "COMMERCANT"
  }'
```

**Réponse :**
```json
{
  "montant_garantie_predit": 1234567.89,
  "montant_garantie_formate": "1,234,568 FCFA",
  "prediction_log": 14.026,
  "ratio_garantie_credit": 82.3,
  "interpretation": "✅ Garantie cohérente avec le profil client"
}
```

### Prédiction batch (POST /predict/batch)

```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -F "file=@clients.xlsx"
```

---

## ⚠️ Problèmes Courants et Solutions

### EOFError lors du chargement du scaler

**Cause** : Le fichier `scaler.pkl` a été sauvegardé incorrectement (fichier vide ou tronqué).

**Solution** :
1. Retournez dans votre notebook
2. Assurez-vous que le `scaler` est fitté **uniquement sur `X_train`**
3. Exécutez le script `save_artifacts.py` qui vérifie l'intégrité après sauvegarde

### FeatureNames mismatch

**Cause** : Les colonnes du fichier d'entrée ne correspondent pas à `feature_columns.pkl`.

**Solution** : Le module `preprocessing.py` aligne automatiquement les colonnes. Assurez-vous que `feature_columns.pkl` provient bien du même entraînement que `xgboost_model.pkl`.

---

## 📐 Pipeline de Prétraitement (Déploiement)

```
Données brutes
    ↓
log1p(MONTANT_CREDIT) → LOG_MONTANT_CREDIT
    ↓
Frequency encoding → LIBELLE_GARANTIE_FREQ
    ↓
One-hot encoding (GENRE, TYPE_EMPRUNTEUR, PROPRIETAIRE, PROFESSION_GROUPE)
    ↓
Conversion bool → int
    ↓
Alignement colonnes sur feature_columns.pkl
    ↓
StandardScaler.transform() [colonnes numériques]
    ↓
XGBoost.predict() → LOG_MONTANT_GARANTIE
    ↓
expm1() → Montant en FCFA
```

---

## 👤 Auteur

**[Votre Nom]**  
Master 2 Ingénierie Data – ISM Paris  
Promotion 2026  

---

## 📄 Licence

Usage académique uniquement. Données ACEP confidentielles – non incluses dans ce dépôt.
