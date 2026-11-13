# -*- coding: utf-8 -*-

#======================================================================================
#  Auteur: Eric KLOECKLE
#  Etablissement: Université Lumière Lyon 2 - Bron
#  Cursus: Master 2  BI&A : « Business Intelligence & Analytics » 
#  Domaine: « Gestion de données massives »
#  Cours: Enseignement TD Datalake-House
# 
#-------------------------------------------------------------------------------------- 
# 00-PHASE-1_Etude_de_la_Structure_type_des_Metadonnees_dans_un_Datalake_v0.01.py
#======================================================================================


########################################################################################
########################################################################################
#
# Outils 
#
########################################################################################
########################################################################################

#==============================================================================
#-- Afficher_une_ligne
#==============================================================================
def Afficher_une_ligne(caractere = "-", nombre_de_caractere=80):
    print(caractere*nombre_de_caractere)
    
    
#==============================================================================
#-- Sauter_une_ligne
#==============================================================================
def Sauter_une_ligne():
    print()


#==============================================================================
#-- Suppression du chaine_de_caractere "\n" (retour chariot) dans une chaine de chaine_de_caractere 
#   => Utilisation des "regular expression" - bibliotheque Python "re"
#==============================================================================
import re
def Supprimer_SautDeLigne(chaine_de_chaine_de_caractere):
    resultat = ""
    print(re.sub(r'(.*)\\n','' r'\1', str(chaine_de_chaine_de_caractere)))
    return(resultat)
    
    
    


########################################################################################
########################################################################################
#    
# Exemple: passage de "Liste" vers "Fichier CSV" et inversement
#
########################################################################################
########################################################################################

#==============================================================================
#==============================================================================
#  Passage d'une liste vers un CSV
#==============================================================================
#==============================================================================

#-- Chargement de la bibliotheque python pour la manipulation des fichiers CSV
import csv

#==============================================================================
# Création d'un jeux de test (factice) 
# pour générer un exemple de fichier de metadonnées technique
#==============================================================================
liste_lignes_metadonnee_technique_OUT =  [
                    ['OBJET_ID'   , 'COLONNE', 'VALEUR'],
                    ['16308' , 'date_heure_de_recuperation' , '2025-02-13 12:32:45'],
                    ['16308' , 'nom_du_fichier_source' , '13546-INFO-EMP-LINKEDIN-FR-1599984246.html'],
                    ['16308' , 'provenance_du_fichier_source' , 'C:\\TD_DATALAKE\\DATALAKE\\0_SOURCE_WEB\\'	],
                    ['16308' , 'nom_du_fichier_cible' , '13546-INFO-EMP-LINKEDIN-FR-1599984246.html'],
                    ['16308' , 'localisation_du_fichier_cible' , 'C:\\TD_DATALAKE\\DATALAKE\\1_LANDING_ZONE\\LINKEDIN\\EMP\\'],
                    ['16308' , 'type_du_fichier_source' , 'html'],
                    ['16308' , 'categorie_du_fichier_source' , 'INFO_EMPLOI'],
                    ['4216' , 'date_heure_de_recuperation' , '2022-11-25'],
                    ['4216' , 'nom_du_fichier_source' , '13552-INFO-SOC-GLASSDOOR-E2131167_P1.html '],
                    ['4216' , 'provenance_du_fichier_source' , 'C:\\TD_DATALAKE\\DATALAKE\\0_SOURCE_WEB\\'	],
                    ['4216' , 'nom_du_fichier_cible' , '13552-INFO-SOC-GLASSDOOR-E2131167_P1.html'],
                    ['4216' , 'localisation_du_fichier_cible' , 'C:\\TD_DATALAKE\\DATALAKE\\1_LANDING_ZONE\\GLASSDOOR\\SOC\\'],
                    ['4216' , 'type_du_fichier_source' , 'html'],
                    ['4216' , 'categorie_du_fichier_source' , 'INFO_SOCIETE']]
   
   
                    
#==============================================================================
# Création d'un jeux de test (factice) 
# pour générer un exemple de fichier de metadonnées descriptive
#==============================================================================
liste_lignes_metadonnee_descriptive_OUT =  [['OBJET_ID'   , 'COLONNE', 'VALEUR'],
                    ['16308' , 'nom_entreprise' , 'Business & décision'],
                    ['16308' , 'ville_entreprise','Lyon 7 eme'],
                    ['16308' , 'note_entreprise','3,2'],
                    ['4216' , 'nom_entreprise' , 'Sopra Group'],
                    ['4216' , 'ville_entreprise','Paris 15 ème'],
                    ['4216' , 'note_entreprise','2,5']]
   
   
#------------------------------------------------------------------------------
#-- Visualisation du contenu de la liste de ligne à enregistrer dans un fichier 
#------------------------------------------------------------------------------
Sauter_une_ligne()
Afficher_une_ligne('-', 80)
for myLineOut in liste_lignes_metadonnee_technique_OUT : print(myLineOut)
Afficher_une_ligne()


#==============================================================================
# Préparation et création des fichiers de métadonnées
#==============================================================================
repertoire_fichier_metadonnee_OUT = "C:/TD_DATALAKE/DATALAKE/2_CURATED_ZONE/METADONNEES"
nom_du_fichier_metadonnee_technique_OUT = "metadonnee_technique.csv"
nom_du_fichier_metadonnee_descriptive_OUT = "metadonnee_descriptive.csv"



#------------------------------------------------------------------------------
# Traitement de création du fichier de métadonnées technique 
#------------------------------------------------------------------------------
#-- Ouverture du fichier CSV métadonnées techniques en écriture
objet_fichier_csv_OUT = open(repertoire_fichier_metadonnee_OUT + '/' + nom_du_fichier_metadonnee_technique_OUT, "w", encoding="utf8", errors="ignore", newline='')

#-- Préparation de l'objet d'ecriture au format CSV
objet_WriterOut = csv.writer(objet_fichier_csv_OUT, delimiter=';', quotechar='"',  quoting=csv.QUOTE_ALL, lineterminator='\n')

#-- Ecriture des éléments de la liste dans le fichier 
objet_WriterOut.writerows(liste_lignes_metadonnee_technique_OUT)

#-- Fermeture du fichier 
objet_fichier_csv_OUT.close()


#------------------------------------------------------------------------------
# Traitement de création du fichier de métadonnées descriptives 
#------------------------------------------------------------------------------
#-- Ouverture du fichier CSV métadonnées descriptives en écriture
objet_fichier_csv_OUT = open(repertoire_fichier_metadonnee_OUT + '/' + nom_du_fichier_metadonnee_descriptive_OUT, "w", encoding="utf8", errors="ignore", newline='')

#-- Préparation de l'objet d'ecriture au format CSV
objet_Writer_OUT = csv.writer(objet_fichier_csv_OUT, delimiter=';', quotechar='"',  quoting=csv.QUOTE_ALL, lineterminator='\n')

#-- Ecriture des éléments de la liste dans le fichier 
objet_Writer_OUT.writerows(liste_lignes_metadonnee_descriptive_OUT)

#-- Fermeture du fichier 
objet_fichier_csv_OUT.close()

#==============================================================================




########################################################################################
########################################################################################
#
# Exemple: Passage des lignes d'un fichier CSV dans une liste
#
# ==> Récupération des lignes du fichier de métadonnées techniques
# 
########################################################################################
########################################################################################

#-- Chargement de la bibliotheque python pour la manipulation des fichiers CSV
import csv

#-- Initialisation des variables
liste_lignes_metadonnee_technique_IN = []

 
#-- Nom et Emplacement du fichier CSV de metadonnées techniques à importer
repertoire_fichier_metadonnee_IN = "C:/TD_DATALAKE/DATALAKE/2_CURATED_ZONE/METADONNEES"
nom_du_fichier_metadonnee_technique_IN = "metadonnee_technique.csv"


#-- Ouverture du fichier en lecture
objet_fichier_csv_IN = open(repertoire_fichier_metadonnee_IN + '/' + nom_du_fichier_metadonnee_technique_IN , "r", encoding="utf8", errors="ignore", newline='')

#-- Lecture du fichier CSV, segmentation des colonne, et stockage dans une liste 
objet_Reader_IN = csv.reader(objet_fichier_csv_IN, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n')

print(objet_Reader_IN)

#------------------------------------------------------------------------------
#-- Test de visualisation du contenu de la liste de ligne à enregistrer dans un fichier 
#------------------------------------------------------------------------------
Sauter_une_ligne()
Afficher_une_ligne('=', 80)
for ligne_IN in objet_Reader_IN :
    print(ligne_IN)
    print(str(ligne_IN[1]))
    if str(ligne_IN[1]) == 'categorie_du_fichier_source': 
        print('Le fichier à parser concerne le domaine : :', ligne_IN[2])
Afficher_une_ligne()

objet_fichier_csv_IN.close()

#==============================================================================
