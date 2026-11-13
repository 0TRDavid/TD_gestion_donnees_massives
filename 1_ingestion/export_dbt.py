# -*- coding: utf-8 -*-
"""
Copie les fichiers de métadonnées de la CURATED ZONE vers les seeds dbt.
"""

import os
import shutil

from config import REPERTOIRE_METADONNEES, REPERTOIRE_DBT_SEEDS

fichiers_csv = [
    "metadonnee_technique.csv",
    "metadonnee_descriptive.csv",
]

os.makedirs(REPERTOIRE_DBT_SEEDS, exist_ok=True)

for nom_fichier in fichiers_csv:
    chemin_source = os.path.join(REPERTOIRE_METADONNEES, nom_fichier)
    chemin_cible = os.path.join(REPERTOIRE_DBT_SEEDS, nom_fichier)

    shutil.copy2(chemin_source, chemin_cible)
    print("CSV copié vers dbt :", chemin_cible)
