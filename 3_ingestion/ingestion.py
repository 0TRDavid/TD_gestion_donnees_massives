# -*- coding: utf-8 -*-
"""
PHASE 1 : Copie des fichiers HTML de 0_SOURCE_WEB vers 1_LANDING_ZONE
et création des métadonnées techniques et descriptives.

Structure des métadonnées : verticale (OBJET_ID ; COLONNE ; VALEUR)
"""

import os
import re
import shutil
import csv
from datetime import datetime
import hashlib # pour créer un identifiant unique basé sur le nom du fichier HTML
from extraction_metadonnees_descriptives import extraire_metadonnees_descriptives
# ============================================================
# 1. PARAMÈTRES À ADAPTER À TON ORDINATEUR
# ============================================================

REPERTOIRE_DATALAKE = os.getcwd()  # Répertoire racine

REPERTOIRE_SOURCE = os.path.join(REPERTOIRE_DATALAKE, "0_SOURCE_WEB")
REPERTOIRE_LANDING = os.path.join(REPERTOIRE_DATALAKE, "1_LANDING_ZONE")

REPERTOIRE_METADONNEES = os.path.join(
    REPERTOIRE_DATALAKE,
    "2_CURATED_ZONE",
    "METADONNEES"
)

FICHIER_METADONNEES_TECHNIQUES = os.path.join(
    REPERTOIRE_METADONNEES,
    "metadonnee_technique.csv"
)

FICHIER_METADONNEES_DESCRIPTIVES = os.path.join(
    REPERTOIRE_METADONNEES,
    "metadonnee_descriptive.csv"
)
FICHIER_HISTORIQUE_TRAITEMENT = os.path.join(
    REPERTOIRE_METADONNEES,
    "historique_traitement.csv"
)

# ============================================================
# 2. CRÉATION DES DOSSIERS SI BESOIN
# ============================================================

os.makedirs(REPERTOIRE_SOURCE, exist_ok=True)
os.makedirs(REPERTOIRE_LANDING, exist_ok=True)
os.makedirs(REPERTOIRE_METADONNEES, exist_ok=True)

# ============================================================
# 3. FONCTIONS
# ============================================================

def extraire_informations_nom_fichier(nom_fichier):
    """
    Exemple :
    13546-INFO-EMP-LINKEDIN-FR-1599984246.html

    Retourne :
    - identifiant : 13546
    - categorie : INFO_EMPLOI
    - site : LINKEDIN
    """

    nom_sans_extension = os.path.splitext(nom_fichier)[0]

    elements = nom_sans_extension.split("-")

    if len(elements) < 5:
        return None

    identifiant = hashlib.md5(nom_sans_extension.encode()).hexdigest() # identifiant unique basé sur le nom du fichier HTML
    type_information = elements[1] # Info si AVIS, 
    categorie = elements[2]
    site = elements[3]


    if type_information == "INFO" and categorie == "EMP":
        categorie_metier = "OFFRE_EMPLOI"
        categorie = "EMP"
    elif type_information == "INFO" and categorie == "SOC":
        categorie_metier = "INFO_SOCIETE"
        categorie = "SOC"
    elif type_information == "AVIS" and categorie == "SOC":
        categorie_metier = "AVIS_SOCIETE"
        categorie = "AVIS"
    else:
        categorie_metier = type_information + "_" + categorie

    return {
        "identifiant": identifiant,
        "type_information": categorie_metier,
        "site": site,
        "sous-dossier": categorie, # pour le sous dossier
    }


def copier_fichier_vers_landing_zone(chemin_fichier_source, informations):
    """
    Copie le fichier HTML vers :
    1_LANDING_ZONE / SITE / CATEGORIE
    """

    site = informations["site"]
    categorie = informations["sous-dossier"]

    repertoire_cible = os.path.join(
        REPERTOIRE_LANDING,
        site,
        categorie
    )

    os.makedirs(repertoire_cible, exist_ok=True)

    nom_fichier = os.path.basename(chemin_fichier_source)

    chemin_fichier_cible = os.path.join(
        repertoire_cible,
        nom_fichier
    )
    if os.path.exists(chemin_fichier_cible) and os.path.getmtime(chemin_fichier_cible) >= os.path.getmtime(chemin_fichier_source):
        print(f"Le fichier {nom_fichier} existe déjà dans la landing zone et est plus récent ou identique. Copie ignorée.")
        return chemin_fichier_cible, True  # Retourne le chemin cible et un indicateur que le fichier existait déjà
    else:
        shutil.copy2(chemin_fichier_source, chemin_fichier_cible)
        return chemin_fichier_cible, False  # Retourne le chemin cible et un indicateur que le fichier a été copié


def creer_metadonnees_techniques(
    objet_id,
    nom_fichier_source,
    chemin_fichier_source,
    nom_fichier_cible,
    chemin_fichier_cible,
    categorie_metier
):
    chemin_fichier_source = chemin_fichier_source.split("TD_gestion_donnees_massives\\")[1] # Normalisation du chemin 
    chemin_fichier_cible = chemin_fichier_cible.split("TD_gestion_donnees_massives\\")[1] # Normalisation du chemin
    date_heure_recuperation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    metadonnees = [
        [objet_id, "date_heure_de_recuperation", date_heure_recuperation],
        [objet_id, "nom_du_fichier_source", nom_fichier_source],
        [objet_id, "provenance_du_fichier_source", chemin_fichier_source],
        [objet_id, "nom_du_fichier_cible", nom_fichier_cible],
        [objet_id, "localisation_du_fichier_cible", chemin_fichier_cible],
        [objet_id, "type_du_fichier_source", "html"],
        [objet_id, "categorie_du_fichier_source", categorie_metier]
    ]

    return metadonnees


def ecrire_fichier_csv(chemin_fichier_csv, liste_lignes):

    with open(
        chemin_fichier_csv,
        "w",
        encoding="utf-8",
        errors="ignore",
        newline=""
    ) as fichier_csv:

        writer = csv.writer(
            fichier_csv,
            delimiter=";",
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            lineterminator="\n"
        )

        writer.writerows(liste_lignes)

def ecrire_historique_traitement(fichier_historique, nb_fichiers_sources, nb_fichiers_copies, nb_fichiers_ignores):
    """
    Écrit un fichier d'historique du traitement.
    """
    taille_meta_tech = os.path.getsize(FICHIER_METADONNEES_TECHNIQUES) if os.path.exists(FICHIER_METADONNEES_TECHNIQUES) else 0
    taille_meta_desc = os.path.getsize(FICHIER_METADONNEES_DESCRIPTIVES) if os.path.exists(FICHIER_METADONNEES_DESCRIPTIVES) else 0
    date_heure_traitement = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(fichier_historique):
        with open(fichier_historique, "w", encoding="utf-8") as f:
            f.write("date_heure_traitement;nb_fichiers_sources;nb_fichiers_copies;nb_fichiers_ignores;taille_meta_tech;taille_meta_desc\n")
            f.write(f"{date_heure_traitement};{nb_fichiers_sources};{nb_fichiers_copies};{nb_fichiers_ignores};{taille_meta_tech};{taille_meta_desc}\n")
    else:
        with open(fichier_historique, "a", encoding="utf-8") as f:
            f.write(f"{date_heure_traitement};{nb_fichiers_sources};{nb_fichiers_copies};{nb_fichiers_ignores};{taille_meta_tech};{taille_meta_desc}\n")


# ============================================================
# 4. TRAITEMENT PRINCIPAL
# ============================================================

metadonnees_techniques = [
    ["OBJET_ID", "COLONNE", "VALEUR"]
]

metadonnees_descriptives = [
    ["OBJET_ID", "COLONNE", "VALEUR"]
]

print("Début du traitement")
print("Dossier source :", REPERTOIRE_SOURCE)
print("Dossier landing zone :", REPERTOIRE_LANDING)

fichiers_html = [
    nom_fichier
    for nom_fichier in os.listdir(REPERTOIRE_SOURCE)
    if nom_fichier.lower().endswith(".html")
]

print("Nombre de fichiers HTML trouvés :", len(fichiers_html))
nb_copies = 0
for nom_fichier in fichiers_html:

    informations = extraire_informations_nom_fichier(nom_fichier)

    if informations is None:
        print("Fichier ignoré, nom non conforme :", nom_fichier)
        continue

    chemin_fichier_source = os.path.join(
        REPERTOIRE_SOURCE,
        nom_fichier
    )

    chemin_fichier_cible, fichier_existant = copier_fichier_vers_landing_zone(
        chemin_fichier_source,
        informations
    )

    objet_id = informations["identifiant"]

    
    metadonnees_techniques.extend(
        creer_metadonnees_techniques(
            objet_id=objet_id,
            nom_fichier_source=nom_fichier,
            chemin_fichier_source=chemin_fichier_source,
            nom_fichier_cible=nom_fichier,
            chemin_fichier_cible=chemin_fichier_cible,
            categorie_metier=informations["type_information"]
        )
    )

    metadonnees_descriptives_fichier = extraire_metadonnees_descriptives(
        chemin_fichier_cible,extraire_informations_nom_fichier(nom_fichier)
    )

    for colonne, valeur in metadonnees_descriptives_fichier:
        metadonnees_descriptives.append(
            [objet_id, colonne, valeur]
        )

    if not fichier_existant:
        nb_copies += 1
        print("Fichier copié :", nom_fichier)
        print("Destination :", chemin_fichier_cible)

ecrire_fichier_csv(
    FICHIER_METADONNEES_TECHNIQUES,
    metadonnees_techniques
)

ecrire_fichier_csv(
    FICHIER_METADONNEES_DESCRIPTIVES,
    metadonnees_descriptives
)

print("Traitement terminé")
print("Métadonnées techniques :", FICHIER_METADONNEES_TECHNIQUES)
print("Métadonnées descriptives :", FICHIER_METADONNEES_DESCRIPTIVES)
print("Nombre de fichiers HTML Sources :", len(fichiers_html))
print("Nombre de fichiers copiés :", nb_copies)
print("Nombre de fichiers ignorés (existants et plus récents) :", len(fichiers_html) - nb_copies)


ecrire_historique_traitement(
    FICHIER_HISTORIQUE_TRAITEMENT,
    len(fichiers_html),
    nb_copies,
    len(fichiers_html) - nb_copies
)