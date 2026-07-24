# 🏦 Prédiction du Montant Total des Garanties de Crédit

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-FF6B35?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Machine Learning](https://img.shields.io/badge/ML-Scikit--learn-orange?style=flat-square)
![R²=0.773](https://img.shields.io/badge/R%C2%B2-0.773-brightgreen?style=flat-square)

> ⚠️ **PROJET CONFIDENTIEL** — Modification ou usage commercial interdit sans autorisation

> **Mémoire M2 Ingénierie Data — ISM Paris (2024) | Mise à jour & Déploiement (2026)**

---

## 🚀 ACCÉDER À L'APPLICATION

### 👉 **[https://garantie-credit-prediction.streamlit.app](https://garantie-credit-prediction.streamlit.app)**

**Pas d'installation requise!** Utilisation immédiate de l'app interactive.

---

## 📊 Quick Stats

| Métrique | Valeur |
|----------|--------|
| **Observations** | 184,810 |
| **Dossiers** | 45,317 |
| **Modèle** | XGBoost |
| **R² Score** | **0.773** ⭐ |
| **MAE** | €1,247.80 |
| **Couverture médiane** | 108.7% ✅ |
| **Types de garantie** | 573 (après Fuzzy Match) |

---

## 📋 Présentation

Ce projet développe un modèle de Machine Learning pour **prédire le montant total des garanties** requis lors d'une demande de crédit dans une institution de microfinance.

L'objectif est d'aider les agents de crédit à évaluer si l'ensemble des biens proposés en garantie couvre suffisamment le montant du crédit demandé, réduisant ainsi la subjectivité dans la prise de décision.

---

## 🎯 Problématique

Dans une institution de microfinance, le montant total des garanties exigé peut varier selon l'agent de crédit, le profil du client et les pratiques locales. 

**Ce projet vise à:**
- 📊 **Standardiser** la décision de garantie via Machine Learning
- 🎯 **Objectiver** l'évaluation du risque crédit
- 📈 **Prédire** le montant total des garanties par dossier
- ✅ **Indicateur** de couverture suffisante (≥100%)

**Base:** 184,810 observations regroupées en 45,317 dossiers clients

---

## 🔄 Versions du projet

### Version 1 (2024) — Approche individuelle
Prédiction de la valeur marchande d'**un bien individuel** fourni en garantie.

### Version 2 (2026) — Approche agrégée par dossier ✅ **ACTUELLE**
Prédiction du **montant total des garanties** d'un dossier complet, avec indicateur de couverture du crédit.

---

## 📊 Résultats des modèles

### Comparaison V1 vs V2

| Modèle | MAE V1 | MAE V2 | R² V1 | R² V2 |
|--------|--------|--------|-------|-------|
| Régression Linéaire | 0.625 | 0.446 | 0.325 | 0.530 |
| Arbre de Décision | 0.376 | 0.420 | 0.637 | 0.489 |
| Random Forest | 0.307 | 0.327 | 0.778 | 0.732 |
| **XGBoost ✅** | **0.286** | **0.303** | **0.812** | **0.773** |

> **Le modèle XGBoost V2 est retenu comme modèle final (R² = 0.773)**

---

## 🌟 Fonctionnalités de l'Application

### ✅ App Web Interactive (Streamlit)

**1. Prédiction Unitaire**
- Saisie données client
- Jusqu'à 10 biens en garantie
- Prédiction instantanée du total
- Indicateur couverture (% du crédit)

**2. Prédiction en Masse**
- Import fichier Excel
- Batch processing (jusqu'à 1000 dossiers)
- Export résultats CSV

**3. Fuzzy Matching Automatique**
- Normalisation libellés de garantie
- Correction typos automatique (RapidFuzz)
- Confidence scores

**4. Analyse Comparative**
- V1 vs V2 dans la sidebar
- Historique prédictions
- Dashboard performance

---

## 🏗️ Pipeline de Prétraitement V2

```
Données brutes (agent de crédit)
    ↓
Saisie de N biens en garantie (1 à 10)
    ↓
Fuzzy Matching → harmonisation libellés
  ex: MOTOYCLE → MOTOCYCLETTE
  ex: FRIGIDAIRE → REFRIGERATEUR
    ↓
Calcul ancienneté: (DATE_ACCORD - DATE_ADHESION)
    ↓
log(MONTANT_CREDIT) → LOG_MONTANT_CREDIT
    ↓
NB_GARANTIES = nombre de biens proposés
    ↓
Frequency encoding → LIBELLE_GARANTIE_FREQ
    ↓
One-hot encoding (GENRE, TYPE_EMPRUNTEUR, etc.)
    ↓
Alignement sur 25 colonnes features
    ↓
StandardScaler.transform() [5 colonnes numériques]
    ↓
XGBoost.predict() → LOG_TOTAL_GARANTIES
    ↓
exp(LOG_TOTAL) → Total garanties en FCFA
    ↓
Ratio = Total / Montant crédit × 100
→ ✅ Couverture suffisante si ratio ≥ 100%
```

---

## 🔧 Variables Utilisées — V2

### Variables numériques (standardisées)

| Variable | Description |
|----------|-------------|
| `AGE_CLIENT` | Âge du client (années) |
| `DUREE_CREDIT` | Durée du crédit (mois) |
| `ANCIENNETE_CLIENT_JOUR_CREDIT` | Ancienneté client au crédit (jours) |
| `LOG_MONTANT_CREDIT` | Log du montant de crédit (winsorisé) |
| `NB_GARANTIES` | Nombre de biens proposés ← **NOUVEAU V2** |

### Variables catégorielles (encodées)

| Variable | Encodage | Détail |
|----------|----------|--------|
| `GARANTIE_PRINCIPALE` | Frequency | 237 types après Fuzzy |
| `GENRE_DU_CLIENT` | One-hot | MASCULIN, SOCIETE |
| `TYPE_EMPRUNTEUR` | One-hot | TPE |
| `PROPRIETAIRE_DE_LA_GARANTIE` | One-hot | OUI |
| `PROFESSION_GROUPE` | One-hot | 15 catégories |

---

## 🗂️ Structure du Projet

```
Garantie-Credit-Prediction/
│
├── app/
│   ├── streamlit_app.py         # Interface utilisateur Streamlit V2
│   └── preprocessing.py         # Pipeline de prétraitement V2
│
├── models/
│   ├── xgboost_model.pkl        # Modèle XGBoost V2 entraîné
│   ├── scaler.pkl               # StandardScaler (fitté)
│   ├── feature_columns.pkl      # Liste ordonnée des 25 features
│   ├── garantie_freq_map.pkl    # Frequency encoding (237 types)
│   ├── colonnes_a_scaler.pkl    # Colonnes à standardiser
│   └── fuzzy_references.pkl     # Références Fuzzy Matching
│
├── scripts/
│   ├── save_artifacts.py        # Sauvegarde des artefacts
│   └── test_coherence.py        # Validation du modèle
│
├── data/                        # ⚠️ Données confidentielles
├── requirements.txt
└── README.md
```

---

## 🚀 Installation et Lancement

### 1. Cloner le dépôt
```bash
git clone https://github.com/GMeless/Garantie-Credit-Prediction.git
cd Garantie-Credit-Prediction
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Lancer l'application Streamlit
```bash
streamlit run app/streamlit_app.py
```

→ Accessible sur : `http://localhost:8501`

---

## 📦 Dépendances

```
streamlit==1.56.0
xgboost==3.2.0
scikit-learn==1.8.0
joblib==1.5.3
pandas==3.0.2
numpy==2.4.4
openpyxl==3.1.5
xlrd==2.0.2
rapidfuzz==3.14.5
```

---

## ✅ Nouveautés V2

| Nouveauté | Description |
|-----------|-------------|
| Modèle agrégé | Prédit le total des garanties par dossier |
| NB_GARANTIES | Nouvelle variable explicative clé |
| Fuzzy Matching amélioré | 94 références, seuil 55% |
| Multi-garanties | Jusqu'à 10 biens par dossier |
| Indicateur couverture | ✅ Suffisante / ⚠️ Insuffisante |
| Ratio médian | 108.7% du crédit |
| App Streamlit | Déploiement en ligne |

---

## ✅ Tests de cohérence validés

| Test | V1 | V2 |
|------|----|----|
| Garantie croît avec le crédit | ✅ | ✅ |
| Hiérarchie par type de garantie | ✅ | ✅ |
| Ratio médian cohérent | ✅ | ✅ (108.7%) |
| Couverture suffisante détectée | ❌ | ✅ |

---

## 🔑 Key Insights

### 1. Fuzzy Matching = Clé du succès
- 573 libellés de garantie uniques (beaucoup de typos)
- RapidFuzz + seuil 80% = normalisation très efficace
- Réduction de 40% de "noisy" labels

### 2. Agrégation par dossier = Utilité business réelle
- V1 (individuel): R² = 0.812
- V2 (agrégé): R² = 0.773
- Trade-off justifié: meilleure utilité opérationnelle

### 3. XGBoost >> autres modèles
- Capture des non-linéarités
- R² = 0.773 (excellent!)
- Feature importance interprétable

### 4. Couverture médiane 108.7% = Bon signe
- 62% des dossiers bien couverts (≥100%)
- 38% sous-couverts = risque à monitorer

---

## ⚠️ Données confidentielles

Les données brutes utilisées pour l'entraînement sont **strictement confidentielles** et appartiennent exclusivement à l'institution de microfinance partenaire.  
Elles ne sont **pas incluses** dans ce dépôt public.

---

## 📝 Déploiement en Production (2026)

**Évolutions depuis mémoire:**
- ✅ Migration de Jupyter → Streamlit app
- ✅ Fuzzy matching automatisé
- ✅ Batch processing (Excel import/export)
- ✅ CI/CD pipeline (GitHub Actions)


**Next steps:**
- API REST (FastAPI)
- Database backend (PostgreSQL)
- Real-time monitoring dashboard
- Model retraining pipeline (monthly)

---

## 👤 Auteur

**GNAGNE MELESS M.**  
Master 2 Ingénierie Data — ISM Paris  
Promotion **ISMD 26** — Soutenance 2024 | Mise à jour 2026

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Meless%20M.%20Gnagne-blue?logo=linkedin)](https://www.linkedin.com/in/meless-m-gnagne-21261a196/)
[![Email](https://img.shields.io/badge/Email-mgmeless%40gmail.com-red?logo=gmail)](mailto:mgmeless@gmail.com)
[![GitHub](https://img.shields.io/badge/GitHub-GMeless-black?logo=github)](https://github.com/GMeless)

---

## 📄 Licence

**Licence Propriétaire — Tous droits réservés © 2024-2026**

Usage académique uniquement.  
Toute reproduction, modification ou utilisation commerciale est **interdite** sans autorisation écrite préalable de l'auteur.

📧 Contact : mgmeless@gmail.com  
🔗 LinkedIn : [linkedin.com/in/meless-m-gnagne-21261a196](https://www.linkedin.com/in/meless-m-gnagne-21261a196/)

---

**Status:** ✅ Production-ready (2026) | **Last Updated:** Avril 2026
