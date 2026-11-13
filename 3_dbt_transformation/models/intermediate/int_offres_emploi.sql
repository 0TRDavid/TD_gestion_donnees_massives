-- ./models/intermediate/int_offres_emploi.sql
-- Une ligne par offre LinkedIn (grain : id_offre_linkedin).

with offres as (
    select *
    from {{ ref('stg_metadonnee_descriptive') }}
    where categorie = 'OFFRE_EMPLOI'
),

pivote as (
    select
        {{ vers_numerique(attribut('id_offre_linkedin')) }}::bigint as id_offre_linkedin,
        {{ attribut('intitule_poste') }} as intitule_poste,
        {{ attribut('nom_entreprise') }} as nom_entreprise,
        {{ attribut('date_publication') }}::timestamptz as date_publication,
        {{ attribut('date_expiration') }}::timestamptz as date_expiration,
        {{ attribut('localisation') }} as localisation,
        {{ attribut('ville') }} as ville,
        {{ attribut('code_postal') }} as code_postal,
        {{ attribut('pays') }} as pays,
        {{ attribut('niveau_hierarchique') }} as niveau_hierarchique,
        {{ attribut('type_emploi') }} as type_emploi,
        {{ attribut('fonction') }} as fonction,
        {{ attribut('secteurs') }} as secteurs,
        {{ attribut('url_canonique') }} as url_offre,
        {{ attribut('url_page_entreprise_linkedin') }} as url_entreprise_linkedin,
        {{ attribut('description_offre') }} as description_offre
    from offres
    group by objet_id
)

select
    id_offre_linkedin,
    max(intitule_poste) as intitule_poste,
    max(nom_entreprise) as nom_entreprise,
    {{ normaliser_nom('max(nom_entreprise)') }} as nom_normalise,
    min(date_publication) as date_publication,
    max(date_expiration) as date_expiration,
    max(localisation) as localisation,
    max(case when ville ~ '^[0-9]+$' then null else ville end) as ville,
    max(substring(code_postal from '^[0-9]{5}')) as code_postal,
    max(left(substring(code_postal from '^[0-9]{5}'), 2)) as departement,
    max(pays) as pays,
    max(niveau_hierarchique) as niveau_hierarchique,
    max(type_emploi) as type_emploi,
    max(fonction) as fonction,
    max(secteurs) as secteurs,
    max(url_offre) as url_offre,
    max(url_entreprise_linkedin) as url_entreprise_linkedin,
    max(description_offre) as description_offre
from pivote
group by id_offre_linkedin
