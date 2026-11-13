-- ./models/marts/fct_offres.sql

with offres as (
    select * from {{ ref('int_offres_emploi') }}
),

glassdoor_par_nom as (
    select distinct on (nom_normalise)
        nom_normalise,
        id_employeur_glassdoor
    from {{ ref('int_entreprises_glassdoor') }}
    order by nom_normalise, nb_avis_total desc nulls last, id_employeur_glassdoor
)

select
    o.id_offre_linkedin,
    case
        when g.id_employeur_glassdoor is not null
            then md5('GLASSDOOR-' || g.id_employeur_glassdoor)
        else md5('LINKEDIN-' || o.nom_normalise)
    end as entreprise_sk,
    to_char(o.date_publication, 'YYYYMMDD')::int as date_publication_sk,
    to_char(o.date_expiration, 'YYYYMMDD')::int as date_expiration_sk,

    -- mesures
    1 as nb_offres,
    (o.date_expiration::date - o.date_publication::date) as duree_publication_jours,

    -- attributs propres à l'offre
    o.intitule_poste,
    o.niveau_hierarchique,
    o.type_emploi,
    o.fonction,
    o.secteurs,
    o.localisation,
    o.ville,
    o.code_postal,
    o.departement,
    o.pays,
    o.url_offre,
    o.description_offre
from offres o
left join glassdoor_par_nom g using (nom_normalise)
