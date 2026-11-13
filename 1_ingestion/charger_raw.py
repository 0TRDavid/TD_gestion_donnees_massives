# -*- coding: utf-8 -*-
"""Charge les CSV de métadonnées dans le schéma raw de PostgreSQL."""

import os
import psycopg

from config import FICHIER_METADONNEES_TECHNIQUES, FICHIER_METADONNEES_DESCRIPTIVES

def charger_csv_dans_raw(chemin_csv, nom_table, schema="raw"):
    """Recharge entièrement raw.<nom_table> à partir d'un CSV OBJET_ID;COLONNE;VALEUR."""
    connexion = psycopg.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=os.environ.get("POSTGRES_PORT", "5432"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD"),
        dbname=os.environ.get("POSTGRES_DB"),
    )
    with connexion, connexion.cursor() as curseur:
        curseur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
        curseur.execute(f'DROP TABLE IF EXISTS "{schema}"."{nom_table}"')
        curseur.execute(f'''
            CREATE TABLE "{schema}"."{nom_table}" (
                objet_id   TEXT NOT NULL,
                colonne    TEXT NOT NULL,
                valeur     TEXT,
                charge_le  TIMESTAMP DEFAULT now()
            )
        ''')
        copie = (f'COPY "{schema}"."{nom_table}" (objet_id, colonne, valeur) '
                 "FROM STDIN WITH (FORMAT csv, DELIMITER ';', QUOTE '\"', HEADER true)")
        with open(chemin_csv, "rb") as fichier, curseur.copy(copie) as flux:
            while bloc := fichier.read(1024 * 1024):
                flux.write(bloc)
        curseur.execute(f'SELECT count(*) FROM "{schema}"."{nom_table}"')
        print(f"{schema}.{nom_table} : {curseur.fetchone()[0]} lignes chargées")
    connexion.close()

if __name__ == "__main__":
    charger_csv_dans_raw(FICHIER_METADONNEES_TECHNIQUES, "metadonnee_technique")
    charger_csv_dans_raw(FICHIER_METADONNEES_DESCRIPTIVES, "metadonnee_descriptive")