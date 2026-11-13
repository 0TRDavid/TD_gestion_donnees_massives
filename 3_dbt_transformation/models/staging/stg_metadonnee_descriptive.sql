-- models/staging/stg_metadonne_descriptive.sql

with fichiers as (
    select objet_id, categorie, prefixe
    from {{ ref('stg_fichiers') }}
),

nettoye as (
    select
        objet_id,
        substring(colonne from '^avis_([0-9]+)__')::bigint as avis_id,
        regexp_replace(colonne, '^avis_[0-9]+__', '') as attribut,
        -- traitement des balises HTML restées dans le texte extrait
        nullif(trim(
            replace(replace(replace(replace(replace(replace(valeur,
                '&amp;', '&'), '&quot;', '"'), '&#39;', ''''), '&#x27;', ''''),
                '&lt;', '<'), '&gt;', '>')
        ), '') as valeur
    from {{ source('raw', 'metadonnee_descriptive') }}
)

select
    n.objet_id,
    f.categorie,
    f.prefixe,
    n.avis_id,
    n.attribut,
    n.valeur
from nettoye n, fichiers f 
where n.objet_id = f.objet_id and n.valeur is not null
