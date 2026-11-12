# TD_gestion_donnees_massives
Travail phase 1 :

py SCRIPT/verif_fichiers.py "0_SOURCE_WEB"


AVIS-SOC-GLASSDOOR                                                                                                                                                          
INFO-EMP-LINKEDIN-FR
INFO-SOC-GLASSDOOR

donc sous dossier : Glassdoor/avis et soc
                    Linkedin/emp


0_SOURCE_WEB
      ↓  copie brute du fichier
1_LANDING_ZONE\LINKEDIN\EMP\...
1_LANDING_ZONE\GLASSDOOR\SOC\...
      ↓  lecture du HTML + extraction des informations
2_CURATED_ZONE\METADONNEES\metadonnee_technique.csv
2_CURATED_ZONE\METADONNEES\metadonnee_descriptive.csv


ensuite on envoi les infos vers le dossier seed de dbt pour que DBT fasse l'ELT 



Etape 1 :

Lancement de la Pipeline : Ingestion des données sources vers la Landing Zone, création des métadonnées puis au choix, mise à jour des seeds DBT

Prérequis : Docker et python installés sur la machine

sur Windows avec PowerShell :  bash ./lancement_pipeline.sh 
Sur Linux : a toi de me dire David

