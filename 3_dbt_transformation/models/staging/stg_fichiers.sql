-- ./models/staging/stg_fichiers

with pivote as (
    select
        objet_id,
        max(trim(valeur)) filter (where colonne = 'nom_du_fichier_source') as nom_fichier,
        max(trim(valeur)) filter (where colonne = 'categorie_du_fichier_source') as categorie,
        max(trim(valeur)) filter (where colonne = 'type_du_fichier_source') as type_fichier,
        max(trim(valeur)) filter (where colonne = 'provenance_du_fichier_source') as chemin_source,
        max(trim(valeur)) filter (where colonne = 'localisation_du_fichier_cible') as chemin_landing,
        max(trim(valeur)) filter (where colonne = 'date_heure_de_recuperation') as date_recuperation
    from {{ source('raw', 'metadonnee_technique') }}
    group by objet_id
)

select
    objet_id,
    nom_fichier,
    categorie,
    split_part(nom_fichier, '-', 1)::int as prefixe,
    -- Traitement sur le nom de fichier pour récupérer la source
    case when nom_fichier like '%-GLASSDOOR-%' then 'GLASSDOOR'
         when nom_fichier like '%-LINKEDIN-%'  then 'LINKEDIN' 
    end as site_source,

    substring(nom_fichier from '_P([0-9]+)\.html$')::int as numero_page,
    type_fichier,
    chemin_source,
    chemin_landing,
    date_recuperation::timestamp as date_recuperation
from pivote
