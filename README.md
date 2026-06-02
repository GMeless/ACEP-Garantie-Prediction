# 🏦 Prédiction du Montant Total des Garanties de Crédit

> ⚠️ **PROJET CONFIDENTIEL**  
> Toute modification, reproduction ou utilisation commerciale est strictement  
> interdite sans autorisation écrite de l'auteur.  
> 📧 Contact obligatoire avant toute utilisation : mgmeless@gmail.com

---

> **Mémoire de fin d'études — M2 Ingénierie Data — ISM Paris (2024)**  
> **Mise à jour modèle et déploiement — ISMD 26 (2026)**  
> Secteur : **Microfinance** | Données confidentielles — institution partenaire

---

## 🌐 Application en ligne

🚀 **Accéder à l'application :**  
👉 [https://garantie-credit-prediction.streamlit.app](https://garantie-credit-prediction.streamlit.app)

📂 **Code source GitHub :**  
👉 [https://github.com/GMeless/Garantie-Credit-Prediction](https://github.com/GMeless/Garantie-Credit-Prediction)

---

## 📋 Présentation

Ce projet développe un modèle de Machine Learning pour **prédire le montant total
des garanties** requis lors d'une demande de crédit dans une institution de microfinance.

L'objectif est d'aider les agents de crédit à évaluer si l'ensemble des biens proposés
en garantie couvre suffisamment le montant du crédit demandé, réduisant ainsi
la subjectivité dans la prise de décision.

---

## 🎯 Problématique

Dans une institution de microfinance, le montant total des garanties exigé peut varier
selon l'agent de crédit, le profil du client et les pratiques locales. Ce projet vise
à **standardiser et objectiver** cette décision grâce au Machine Learning, en s'appuyant
sur **184 810 observations** regroupées en **45 317 dossiers**.

---

## 🔄 Versions du projet

### Version 1 (2024) — Approche individuelle
Prédiction de la valeur marchande d'**un bien individuel** fourni en garantie.

### Version 2 (2026) — Approche agrégée par dossier ✅ ACTUELLE
Prédiction du **montant total des garanties** d'un dossier complet, avec indicateur
de couverture du crédit.

---

## 📊 Résultats des modèles

### Comparaison V1 vs V2

| Modèle | MAE V1 | MAE V2 | R² V1 | R² V2 |
|--------|--------|--------|-------|-------|
| Régression Linéaire | 0.625 | 0.446 | 0.325 | 0.530 |
| Arbre de Décision | 0.376 | 0.420 | 0.637 | 0.489 |
| Random Forest | 0.307 | 0.327 | 0.778 | 0.732 |
| **XGBoost ✅** | **0.286** | **0.303** | **0.812** | **0.773** |

> **V1** : 184 810 observations — variable cible : valeur d'un bien individuel  
> **V2** : 45 317 dossiers — variable cible : total des garanties par dossier  
> Le modèle **XGBoost V2** est retenu comme modèle final **(R² = 0.773)**

---

## 🗂️ Structure du Projet

```
Deploiement_Garantie_Credit/
│
├── app/
│   ├── streamlit_app.py         # Interface utilisateur Streamlit V2
│   └── preprocessing.py         # Pipeline de prétraitement V2
│
├── models/
│   ├── xgboost_model.pkl        # Modèle XGBoost V2 entraîné
│   ├── scaler.pkl               # StandardScaler (fitté sur X_train)
│   ├── feature_columns.pkl      # Liste ordonnée des 25 features
│   ├── garantie_freq_map.pkl    # Frequency encoding (237 types)
│   ├── colonnes_a_scaler.pkl    # Colonnes à standardiser
│   └── fuzzy_references.pkl     # Références Fuzzy Matching (94 refs)
│
├── scripts/
│   ├── save_artifacts.py        # Script de sauvegarde des artefacts
│   └── test_coherence.py        # Script de validation du modèle
│
├── data/                        # ⚠️ Non versionné – données confidentielles
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔧 Variables Utilisées — V2

### Variables numériques (standardisées)
| Variable | Description |
|----------|-------------|
| `AGE_CLIENT` | Âge du client (années) |
| `DUREE_CREDIT` | Durée du crédit (mois) |
| `ANCIENNETE_CLIENT_JOUR_CREDIT` | Ancienneté client au moment du crédit (jours) |
| `LOG_MONTANT_CREDIT` | Log du montant de crédit (après winsorisation) |
| `NB_GARANTIES` | Nombre de biens proposés en garantie ← **NOUVEAU V2** |

### Variables catégorielles (encodées)
| Variable | Encodage | Détail |
|----------|----------|--------|
| `GARANTIE_PRINCIPALE` | Frequency encoding | 237 types après Fuzzy Matching |
| `GENRE_DU_CLIENT` | One-hot | MASCULIN, SOCIETE |
| `TYPE_EMPRUNTEUR` | One-hot | TPE |
| `PROPRIETAIRE_DE_LA_GARANTIE` | One-hot | OUI |
| `PROFESSION_GROUPE` | One-hot | 15 catégories |

---

## 📐 Pipeline de Prétraitement V2

```
Données brutes (agent de crédit)
        ↓
Saisie de N biens en garantie (1 à 10)
        ↓
Fuzzy Matching → harmonisation des libellés
  ex: MOTOYCLE → MOTOCYCLETTE
  ex: FRIGIDAIRE → REFRIGERATEUR
  ex: TELE → TELEVISEUR
        ↓
Calcul ancienneté : (DATE_ACCORD - DATE_ADHESION) en jours
        ↓
log(MONTANT_CREDIT) → LOG_MONTANT_CREDIT
        ↓
NB_GARANTIES = nombre de biens proposés
        ↓
Frequency encoding → LIBELLE_GARANTIE_FREQ (garantie principale)
        ↓
One-hot encoding (GENRE, TYPE_EMPRUNTEUR, PROPRIETAIRE, PROFESSION)
        ↓
Alignement sur feature_columns.pkl (25 colonnes)
        ↓
StandardScaler.transform() [5 colonnes numériques]
        ↓
XGBoost.predict() → LOG_TOTAL_GARANTIES
        ↓
exp(LOG_TOTAL_GARANTIES) → Total garanties en FCFA
        ↓
Ratio = Total / Montant crédit × 100
→ Couverture suffisante si ratio ≥ 100%
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

→ Accessible sur : [http://localhost:8501](http://localhost:8501)

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
| Ratio médian réel | 108.7% du crédit |

---

## ✅ Tests de cohérence validés

| Test | V1 | V2 |
|------|----|----|
| Garantie croît avec le crédit | ✅ | ✅ |
| Hiérarchie par type de garantie | ✅ | ✅ |
| Ratio médian cohérent | 19.8% (par bien) | 108.7% (par dossier) |
| Couverture suffisante détectée | ❌ | ✅ |

---

## ⚠️ Données confidentielles

Les données brutes utilisées pour l'entraînement sont **strictement confidentielles**
et appartiennent exclusivement à l'institution de microfinance partenaire.  
Elles ne sont **pas incluses** dans ce dépôt public.

---

## 👤 Auteur

**GNAGNE MELESS M.**  
Master 2 Ingénierie Data — ISM Paris  
Promotion **ISMD 26** — Soutenance 2024 | Mise à jour 2026

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Meless%20M.%20Gnagne-blue?logo=linkedin)](https://www.linkedin.com/in/meless-m-gnagne-21261a196/)
[![Email](https://img.shields.io/badge/Email-mgmeless%40gmail.com-red?logo=gmail)](mailto:mgmeless@gmail.com)

---

## 📄 Licence

**Licence Propriétaire — Tous droits réservés © 2024-2026**

Usage académique uniquement.  
Toute reproduction, modification ou utilisation commerciale est **interdite**  
sans autorisation écrite préalable de l'auteur.

📧 Contact : mgmeless@gmail.com  
🔗 LinkedIn : [linkedin.com/in/meless-m-gnagne-21261a196](https://www.linkedin.com/in/meless-m-gnagne-21261a196/)
