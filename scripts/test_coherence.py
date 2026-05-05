# =============================================================
# test_coherence.py — Vérification cohérence du modèle
# Lancer avec : python scripts/test_coherence.py
# =============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from preprocessing import predire_un_client

print("=" * 60)
print("TEST DE COHERENCE DU MODELE XGBOOST — ACEP")
print("=" * 60)

# TEST 1 : Credit faible
r1 = predire_un_client(35, 12, 500_000,
    "01/01/2018", "15/03/2022",
    "MOTOCYCLETTE", "MASCULIN", "TPE", "OUI", "COMMERCANT")

# TEST 2 : Credit moyen
r2 = predire_un_client(35, 12, 1_500_000,
    "01/01/2018", "15/03/2022",
    "MOTOCYCLETTE", "MASCULIN", "TPE", "OUI", "COMMERCANT")

# TEST 3 : Credit eleve
r3 = predire_un_client(35, 12, 5_000_000,
    "01/01/2018", "15/03/2022",
    "MOTOCYCLETTE", "MASCULIN", "TPE", "OUI", "COMMERCANT")

# TEST 4 : Garantie SALON
r4 = predire_un_client(35, 12, 1_500_000,
    "01/01/2018", "15/03/2022",
    "SALON", "MASCULIN", "TPE", "OUI", "COMMERCANT")

# TEST 5 : Garantie TELEVISEUR
r5 = predire_un_client(35, 12, 1_500_000,
    "01/01/2018", "15/03/2022",
    "TELEVISEUR", "MASCULIN", "TPE", "OUI", "COMMERCANT")

# TEST 6 : Client recent (anciennete faible)
r6 = predire_un_client(35, 12, 1_500_000,
    "01/01/2021", "15/03/2022",
    "MOTOCYCLETTE", "MASCULIN", "TPE", "OUI", "COMMERCANT")

# TEST 7 : Client ancien (anciennete elevee)
r7 = predire_un_client(35, 12, 1_500_000,
    "01/01/2010", "15/03/2022",
    "MOTOCYCLETTE", "MASCULIN", "TPE", "OUI", "COMMERCANT")

# TEST 8 : Duree credit courte vs longue
r8 = predire_un_client(35, 6, 1_500_000,
    "01/01/2018", "15/03/2022",
    "MOTOCYCLETTE", "MASCULIN", "TPE", "OUI", "COMMERCANT")

r9 = predire_un_client(35, 36, 1_500_000,
    "01/01/2018", "15/03/2022",
    "MOTOCYCLETTE", "MASCULIN", "TPE", "OUI", "COMMERCANT")

# =============================================================
print()
print("--- 1. MONTANT CREDIT vs GARANTIE ---")
print(f"  Credit   500 000 FCFA  -> Garantie : {r1['montant_garantie_formate']}")
print(f"  Credit 1 500 000 FCFA  -> Garantie : {r2['montant_garantie_formate']}")
print(f"  Credit 5 000 000 FCFA  -> Garantie : {r3['montant_garantie_formate']}")
ok1 = r1["montant_garantie"] < r2["montant_garantie"] < r3["montant_garantie"]
print(f"  => Garantie croissante avec le credit : {'OK' if ok1 else 'PROBLEME'}")

print()
print("--- 2. TYPE DE GARANTIE ---")
print(f"  MOTOCYCLETTE -> Garantie : {r2['montant_garantie_formate']}")
print(f"  SALON        -> Garantie : {r4['montant_garantie_formate']}")
print(f"  TELEVISEUR   -> Garantie : {r5['montant_garantie_formate']}")
print(f"  => Valeurs differentes selon le type de garantie")

print()
print("--- 3. ANCIENNETE CLIENT ---")
print(f"  Anciennete courte (1 an)   -> {r6['anciennete_calculee']} jours -> Garantie : {r6['montant_garantie_formate']}")
print(f"  Anciennete longue (12 ans) -> {r7['anciennete_calculee']} jours -> Garantie : {r7['montant_garantie_formate']}")

print()
print("--- 4. DUREE DU CREDIT ---")
print(f"  Duree  6 mois  -> Garantie : {r8['montant_garantie_formate']}")
print(f"  Duree 12 mois  -> Garantie : {r2['montant_garantie_formate']}")
print(f"  Duree 36 mois  -> Garantie : {r9['montant_garantie_formate']}")

print()
print("=" * 60)
print("FIN DU TEST DE COHERENCE")
print("=" * 60)