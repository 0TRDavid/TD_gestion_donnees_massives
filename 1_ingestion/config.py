# -*- coding: utf-8 -*-
"""Chemins du projet."""

import os

REPERTOIRE_PROJET = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------
# Zones du datalake 
# ------------------------------------------------------------
REPERTOIRE_DATALAKE = os.environ.get("DATALAKE_DIR") or os.path.join(REPERTOIRE_PROJET, "2_datalake")

REPERTOIRE_SOURCE = os.path.join(REPERTOIRE_DATALAKE, "0_SOURCE_WEB")
REPERTOIRE_LANDING = os.path.join(REPERTOIRE_DATALAKE, "1_LANDING_ZONE")
REPERTOIRE_METADONNEES = os.path.join(REPERTOIRE_DATALAKE, "2_CURATED_ZONE", "METADONNEES")

FICHIER_METADONNEES_TECHNIQUES = os.path.join(REPERTOIRE_METADONNEES, "metadonnee_technique.csv")
FICHIER_METADONNEES_DESCRIPTIVES = os.path.join(REPERTOIRE_METADONNEES, "metadonnee_descriptive.csv")
FICHIER_HISTORIQUE_TRAITEMENT = os.path.join(REPERTOIRE_METADONNEES, "historique_traitement.csv")

# ------------------------------------------------------------
# dbt
# ------------------------------------------------------------
REPERTOIRE_DBT = os.path.join(REPERTOIRE_PROJET, "3_dbt_transformation")
REPERTOIRE_DBT_SEEDS = os.path.join(REPERTOIRE_DBT, "seeds")
