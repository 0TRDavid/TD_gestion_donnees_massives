import os
import shutil

REPERTOIRE_CURATED = "2_CURATED_ZONE/METADONNEES"
REPERTOIRE_DBT_SEEDS = "dbt_transformation/seeds"

fichiers_csv = [
    "metadonnee_technique.csv",
    "metadonnee_descriptive.csv"
]

os.makedirs(REPERTOIRE_DBT_SEEDS, exist_ok=True)

for nom_fichier in fichiers_csv:
    chemin_source = os.path.join(REPERTOIRE_CURATED, nom_fichier)
    chemin_cible = os.path.join(REPERTOIRE_DBT_SEEDS, nom_fichier)

    shutil.copy2(chemin_source, chemin_cible)
    print("CSV copié vers dbt :", chemin_cible)