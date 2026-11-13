# -*- coding: utf-8 -*-

#======================================================================================
#  Auteur: Eric KLOECKLE
#  Etablissement: Université Lumière Lyon 2 - Bron
#  Cursus: Master 2  BI&A : « Business Intelligence & Analytics » 
#  Domaine: « Gestion de données massives »
#  Cours: Enseignement TD Datalake-House
# 
#-------------------------------------------------------------------------------------- 
# 01-PHASE-1_Recuperation_des_objets_HTML_source_vers_la_LANDINGZONE_avec_leurs_Metadonnes-Techniques_v0.01.py
#======================================================================================


###############################################################################
###############################################################################
#
# TRT01
#
#------------------------------------------------------------------------------
#- Comment recuperer la date/time systeme
#
###############################################################################
###############################################################################
from datetime import datetime
def Get_datetime():
    Result = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return(Result)

print(Get_datetime())   



###############################################################################
###############################################################################
#
# TRT02
#
#------------------------------------------------------------------------------
#- Comment parcourir un dossier et stocker dans une liste, les noms de fichiers 
#   filtrés selon des critères choisis
#
###############################################################################
###############################################################################

#-- Importation des bibliotheques necessaires
import os, fnmatch

#-- Initialisation des variables
liste_des_fichiers_html_tmp = []
liste_des_fichiers_html = []


#-- Utiliser dans le code comme sparateur d'arborescence des dossier soit "/" soit "\\" 
#   mais jamais "\"
repertoire_des_fichiers_html_source = "C:/TD_DATALAKE/DATALAKE/0_SOURCE_WEB"


#-- Recupere dans une liste temporaire, les noms longs  des fichiers dans le path
liste_des_fichiers_html_tmp = os.listdir(repertoire_des_fichiers_html_source)

#-- Parametrage permettant de ne filtrer que les fichiers concernés parmis tous 
#   les noms de fichiers de la liste
filtre_de_selection = "*INFO-EMP*.html"

#-- Parcourt tous les fichiers trouvés contenus dans la liste temporaire 
#   et ajoute ceux correspondant au filtre dans la liste definitive 
for nom_du_fichier_html_tmp in liste_des_fichiers_html_tmp :  
    #-- On n'ajoute que les fichiers concernés
    if fnmatch.fnmatch(nom_du_fichier_html_tmp, filtre_de_selection)==True:
        liste_des_fichiers_html.append(nom_du_fichier_html_tmp)

#-- Affichage à l'écran du nom des fichiers fichiers contenus 
#   dans la liste définitive
for nom_du_fichier in liste_des_fichiers_html : print(nom_du_fichier)



###############################################################################
###############################################################################
#
# TRT03
#
#------------------------------------------------------------------------------
#-- Comment preparer les informations et les lignes à enregistrer dans votre 
#   fichier de metadonnees techniques
#
###############################################################################
###############################################################################

#-- Importation des bibliotheques necessaires
import csv


#-- Verification visuelle que la liste des fichiers à recopier est correcte
for nom_du_fichier in liste_des_fichiers_html : print(nom_du_fichier)


#-- Initialisation des variables

liste_des_lignes_a_ecrire = []
#-- Creation de la 1ere ligne particulière du fichier (entete)
entete_fichier_csv = ["ID_OBJET","COLONNE","VALEUR"]
liste_des_lignes_a_ecrire.append(entete_fichier_csv)

print(liste_des_lignes_a_ecrire)

ID_Object = 0

#-- Exemple de boucle de traitment d'ecriture du fichier metadonnes techniques
for nom_du_fichier_html in liste_des_fichiers_html: 
    #-- Repertoire source
    repertoire_des_fichiers_html_source = "C:/TD_DATALAKE/DATALAKE/0_SOURCE_WEB"
    
    #!!! Attention, dans cet exemple,  on ne traite que les données EMP  !!!
    #==> A adapter et compléter le code pour gérer les 2 autres types de données SOC, AVI 
    #-- Repertoire cible 
    repertoire_des_fichiers_html_cible = "C:/TD_DATALAKE/DATALAKE/1_LANDING_ZONE/LINKEDIN/EMP"

    chemin_du_fichier_html_source = repertoire_des_fichiers_html_source + "/" + nom_du_fichier_html
    chemin_du_fichier_html_cible = repertoire_des_fichiers_html_cible + "/" + nom_du_fichier_html
    
    #-- Creation d'une ligne pour la date d'ingestion
    liste_des_lignes_lues = [str(ID_Object), "date_ingestion", Get_datetime()]
    liste_des_lignes_a_ecrire.append(liste_des_lignes_lues)
    
    #-- Creation d'une ligne pour l'emplacement d'où l'on a récupéré le fichier 
    liste_des_lignes_lues = [str(ID_Object), "path_name_file_source", chemin_du_fichier_html_source]
    liste_des_lignes_a_ecrire.append(liste_des_lignes_lues)
    
    #-- Creation d'une ligne pour l'emplacement où l'on a enregistré le fichier 
    liste_des_lignes_lues = [str(ID_Object), "path_name_file_cible", chemin_du_fichier_html_cible]
    liste_des_lignes_a_ecrire.append(liste_des_lignes_lues)

    #-- Creation d'une ligne pour le type d'objet source 
    liste_des_lignes_lues = [str(ID_Object), "type_objet_source", "INFO-EMP"]
    liste_des_lignes_a_ecrire.append(liste_des_lignes_lues)
    
    #-- Rajoutez d'autres métadonnées techniques si necessaire
    # ....    
    # ....

    ID_Object = ID_Object + 1

#-- Verifiation visuelle contenue de la liste des metadonnées à eregistrer
for ligne_a_ecrire in liste_des_lignes_a_ecrire : print(ligne_a_ecrire, "\n")




###############################################################################
###############################################################################
#
# TRT04
#
#------------------------------------------------------------------------------
#-- Ecriture directe de la liste le fichier CSV de metadonnees techniques
#    RQ: Ici la liste contiendra les lignes pour SOC, AVI et EMP qui seront 
#         enregistrées à ce moment dans leur totalité
# 
###############################################################################
###############################################################################

#------------------------------------------------------------------------------
#-- Definir le nom et l'emplacement où sera stocké votre fichier metadonnes techniques 
#------------------------------------------------------------------------------
repertoire_du_fichier_metadonnee_technique = "C:/TD_DATALAKE/DATALAKE/2_CURATED_ZONE/METADONNEES"
nom_du_fichier_metadonnee_technique = "metadonnee_technique.csv"
chemin_du_fichier_metadonnee_technique = repertoire_du_fichier_metadonnee_technique + "/" + nom_du_fichier_metadonnee_technique

#-- Verification visuelle  u nom de fichier métadonnées techniques
print(chemin_du_fichier_metadonnee_technique)

#-- Affichage pour controle des ligne contenues dans la liste  enregistrer dans le fichier 
for ligne_a_ecrire in liste_des_lignes_a_ecrire :  print(ligne_a_ecrire)

#-- Ouverture du fihier en append ("a" = ajout)
# objet_fichier_metadonnee_technique = open(myPathFileNameMetaDataOut, 'a', newline='', encoding="utf-8", errors="ignore")
objet_fichier_metadonnee_technique = open(chemin_du_fichier_metadonnee_technique, 'a', newline='')

#-- Ecriture en une seule commade de l'ensemble ds lignes contenues dans la liste que vous avez préparé
objet_WriterOut = csv.writer(objet_fichier_metadonnee_technique, delimiter=';', quotechar='"',  quoting=csv.QUOTE_ALL, lineterminator='\n')

objet_WriterOut.writerows(liste_des_lignes_a_ecrire)

#-- Fermeture du fihier
objet_fichier_metadonnee_technique.close()




###############################################################################
###############################################################################
# 
# TRT05
#
#------------------------------------------------------------------------------
#-- Comment Copier TOUS les fichiers de la liste d'un repertoire dans un autre repertoire
# 
###############################################################################
###############################################################################

#-- Importation des bibliotheques necessaires
import shutil

#-- Verification visuelle que la liste des fichiers à recopier est correcte
for nom_du_fichier in liste_des_fichiers_html : 
    print(nom_du_fichier)

#-- Initialisation des variables
#-- Preciser le repertoire source
repertoire_des_fichiers_html_source = "C:/TD_DATALAKE/DATALAKE/0_SOURCE_WEB"

#-- Preciser le repertoire cible : (Exemple ici, pour recopier les fichiers EMP a partir de la liste correspondante)
repertoire_des_fichiers_html_cible = "C:/TD_DATALAKE/DATALAKE/1_LANDING_ZONE/LINKEDIN/EMP"

#------------------------------------------------------------------------------
#-- !!! Ecrire ici l'entete dans le fichier de Metadonnes Techniques 
#       ==> Ne le faire qu'une seule fois à la 1ere creation du fichier)
#------------------------------------------------------------------------------

print("******** Debut de copie des fichiers ********")

#-- Boucle pour copier l'ensemble des fichiers contenus dans les listes des fichiers à recopier
#   ==> A compléter et adapter pour gérer pour les 3 listes SOC, AVI et EMP

for nom_du_fichier_html in liste_des_fichiers_html: 
    #-- Preparation et affectation dans des variables
    #    des chemins complets des fchiers source et cible
    chemin_du_fichier_html_source = repertoire_des_fichiers_html_source + "/" + nom_du_fichier_html
    chemin_du_fichier_html_cible = repertoire_des_fichiers_html_cible + "/" + nom_du_fichier_html
    
    print("Copie du fichier : ", "\t", chemin_du_fichier_html_source, " -- vers -->", chemin_du_fichier_html_cible, "\n")
    #-- Lancement de la commande de copie du fichier
    shutil.copy(chemin_du_fichier_html_source, chemin_du_fichier_html_cible)

    #---------------------------------------------------
    # Vous coderez ici une  partie enregistrement des METADONNEES TECHNIQUE :
    #
    #   - Recuperation de la date / Heure systeme
    #   - Preparation des lignes à enregistrer dans le fichier Metadonnees Techniques
    #   - Ouverture en append (ajout) du fichier et enregistrement des lignes formatees comme vu en cours
    #     et fourni dans vos ressources à dispositin sur le site u mooc
    #   - ...
    #   - fermeture du fichier Metadonnees Techniques
    #---------------------------------------------------    
    
    
    #---------------------------------------------------
    
print("******** Fin de copie des fichiers ********\n")





###############################################################################
###############################################################################
# 
#-- Exemple d'algorithme pour votre TD pour la phase d'ingestion 
#   des données SOURCE  vers la LANDING ZONE + Metadonnees Technique
# 
###############################################################################
###############################################################################

#- 1) Choix et Selection des objets source à ingérer dans votre DataLake
#
#- 2) Récupération (sans les altérer et à l'identique) des objets source vers la Landing Zone du Datalake
#
#- 3) Récupératon et stockage des métadonnées techniques obligatoire + celles que vous aurez ajouté au besoin  
#       dans un fichier au format CSV  et de type Id/Key/Value.
#
#- 4) Preparer l'entete du fichier et l'écrire seulement une fois au début du fihier de métadonnées techniques
#       Exemple d'entete :  "ID_OBJET";"COLONNE";"VALEUR"
#
#- 5) Parcourir le dossier SOURCE et stocker respectivement dans 3 listes distinctes , les noms de fichiers 
#       correspondant à chacun des 3 types de source d'information SOC, AVI et EMP.  
#       (Voir le code python fourni dans ce document => TRT02)
# 
#  6) Préparer la phase d'ingestion des objets et des données techniques 
#
#    -  Preparer et realiser la copie des 3 type de fichiers sources dans leurs repertoires respectifs en utilisant 
#         les listes précédement crées.
#         (Voir le code python fourni dans ce document => TRT05)
#
#    - Preparer les informations de metadonnées techniques et les lignes à enregistrer 
#         (Voir le code python fourni dans ce document => TRT03)
# 
#    - Enregistrer les informations de metadonnées techniques dans votre fichier
#         (Voir le code python fourni dans ce document => TRT04)
#


