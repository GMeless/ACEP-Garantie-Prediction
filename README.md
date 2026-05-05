# 🏦 ACEP – Prédiction du Montant de Garantie de Crédit

> ⚠️ **PROJET CONFIDENTIEL**  
> Toute modification, reproduction ou utilisation commerciale est strictement  
> interdite sans autorisation écrite de l'auteur.  
> 📧 Contact obligatoire avant toute utilisation : mgmeless@gmail.com

---

> **Mémoire de fin d'études — M2 Ingénierie Data — ISM Paris (2024)**  
> **Mise à jour déploiement — ISMD 26 (2026)**  
> Institution partenaire : **ACEP Burkina Faso** (microfinance)

---

## 🌐 Application en ligne

🚀 **Accéder à l'application :**  
👉 [https://acep-garantie-prediction.streamlit.app](https://acep-garantie-prediction.streamlit.app)

📂 **Code source GitHub :**  
👉 [https://github.com/GMeless/ACEP-Garantie-Prediction](https://github.com/GMeless/ACEP-Garantie-Prediction)

---

## 📋 Présentation

Ce projet développe un modèle de Machine Learning pour **prédire le montant de garantie**
requis lors d'une demande de crédit dans une institution de microfinance.

L'objectif est d'aider les agents de crédit à disposer d'une estimation objective,
cohérente et rapide du niveau de garantie à exiger d'un client, réduisant ainsi
la subjectivité dans la prise de décision.

---

## 🎯 Problématique

Dans une institution de microfinance comme ACEP Burkina Faso, le montant de garantie
exigé peut varier selon l'agent de crédit, le profil du client et les pratiques locales.
Ce projet vise à **standardiser et objectiver** cette décision grâce au Machine Learning,
en s'appuyant sur **184 810 observations historiques**.

---

## 📊 Résultats du Modèle

| Modèle              | MAE       | RMSE      | R²        |
|---------------------|-----------|-----------|-----------|
| Régression Linéaire | 0.625     | 0.817     | 0.325     |
| Arbre de Décision   | 0.376     | 0.514     | 0.611     |
| Random Forest       | 0.307     | 0.432     | 0.735     |
| **XGBoost ✅**      | **0.286** | **0.397** | **0.812** |

> Le modèle **XGBoost** est retenu comme modèle final **(R² = 0.812)**.  
> Variable cible : `LOG_MONTANT_GARANTIE` (logarithme du montant de garantie en FCFA).

---

## 🗂️ Structure du Projet

```
Deploiement_Garantie_ACEP/
│
├── app/
│   ├── streamlit_app.py         # Interface utilisateur Streamlit
│   └── preprocessing.py         # Pipeline de prétraitement
│
├── api/
│   └── main.py                  # API FastAPI (endpoints REST)
│
├── models/
│   ├── xgboost_model.pkl        # Modèle XGBoost entraîné
│   ├── scaler.pkl               # StandardScaler (fitté sur X_train)
│   ├── feature_columns.pkl      # Liste ordonnée des 24 features
│   ├── garantie_freq_map.pkl    # Frequency encoding (572 types)
│   ├── colonnes_a_scaler.pkl    # Colonnes à standardiser
│   └── metadata.json            # Méta-informations du modèle
│
├── scripts/
│   ├── save_artifacts.py        # Script de sauvegarde des artefacts
│   └── test_coherence.py        # Script de validation du modèle
│
├── assets/
│   └── logo_acep.png            # Logo ACEP
│
├── data/                        # ⚠️ Non versionné – données confidentielles
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🔧 Variables Utilisées

### Variables numériques (standardisées)
| Variable | Description |
|----------|-------------|
| `AGE_CLIENT` | Âge du client (années) |
| `DUREE_CREDIT` | Durée du crédit (mois) |
| `ANCIENNETE_CLIENT_JOUR_CREDIT` | Ancienneté client au moment du crédit (jours) |
| `LOG_MONTANT_CREDIT` | Log du montant de crédit (après winsorisation) |

### Variables catégorielles (encodées)
| Variable | Encodage | Détail |
|----------|----------|--------|
| `LIBELLE_GARANTIE` | Frequency encoding | 572 types de garantie |
| `GENRE_DU_CLIENT` | One-hot | MASCULIN, SOCIETE |
| `TYPE_EMPRUNTEUR` | One-hot | TPE |
| `PROPRIETAIRE_DE_LA_GARANTIE` | One-hot | OUI |
| `PROFESSION_GROUPE` | One-hot | 15 catégories |

---

## 📐 Pipeline de Prétraitement

```
Données brutes (agent de crédit)
        ↓
Calcul ancienneté : (DATE_ACCORD - DATE_ADHESION) en jours
        ↓
log(MONTANT_CREDIT) → LOG_MONTANT_CREDIT
        ↓
Frequency encoding → LIBELLE_GARANTIE_FREQ
        ↓
One-hot encoding (GENRE, TYPE_EMPRUNTEUR, PROPRIETAIRE, PROFESSION)
        ↓
Alignement sur feature_columns.pkl (24 colonnes dans l'ordre exact)
        ↓
StandardScaler.transform() [4 colonnes numériques]
        ↓
XGBoost.predict() → LOG_MONTANT_GARANTIE
        ↓
exp(LOG_MONTANT_GARANTIE) → Montant de garantie en FCFA
```

---

## 🚀 Installation et Lancement

### 1. Cloner le dépôt

```bash
git clone https://github.com/GMeless/ACEP-Garantie-Prediction.git
cd ACEP-Garantie-Prediction
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
```

---

## ✅ Tests de cohérence validés

```bash
python scripts/test_coherence.py
```

| Test | Résultat |
|------|----------|
| Garantie croît avec le crédit | ✅ Confirmé |
| Hiérarchie par type de garantie | ✅ CAMION > MOTO > SALON > TÉLÉ |
| Client fidèle = garantie ajustée | ✅ Logique métier ACEP |
| Ratio médian réel ACEP | ✅ 19.8% (base : 184 810 obs.) |

---

## ⚠️ Données confidentielles

Les données brutes utilisées pour l'entraînement sont **strictement confidentielles**
et appartiennent exclusivement à **ACEP Burkina Faso**.  
Elles ne sont **pas incluses** dans ce dépôt public.

---

## 👤 Auteur

**GNAGNE MELESS M.**  
Master 2 Ingénierie Data — ISM Paris  
Promotion **ISMD 26** — Soutenance 2024 | Mise à jour déploiement 2026

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
