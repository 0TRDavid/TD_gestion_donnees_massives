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