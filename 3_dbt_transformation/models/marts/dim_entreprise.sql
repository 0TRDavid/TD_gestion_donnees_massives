-- models/marts/dim_entreprise.sql

with glassdoor as (
    select * from {{ ref('int_entreprises_glassdoor') }}
),

linkedin_seules as (
    select
        nom_normalise,
        max(nom_entreprise) as nom_entreprise,
        max(url_entreprise_linkedin) as url_entreprise_linkedin
    from {{ ref('int_offres_emploi') }}
    where nom_normalise not in (select nom_normalise from glassdoor)
    group by nom_normalise
)

select
    md5('GLASSDOOR-' || id_employeur_glassdoor) as entreprise_sk,
    'GLASSDOOR' as source_entreprise,
    true as a_fiche_glassdoor,
    id_employeur_glassdoor,
    nom_entreprise,
    nom_normalise,
    secteur_activite,
    secteur_glassdoor,
    industrie_glassdoor,
    type_entreprise,
    taille_entreprise,
    taille_entreprise_code,
    chiffre_affaires_tranche,
    statut_entreprise_code,
    siege_social,
    site_web,
    nom_pdg,
    annee_creation,
    note_globale,
    note_culture_valeurs,
    note_equilibre_vie_pro,
    note_equipe_dirigeante,
    note_opportunites_carriere,
    note_remuneration_avantages,
    taux_recommandation,
    taux_approbation_pdg,
    taux_perspective_positive,
    nb_avis_total,
    nb_salaires,
    nb_entretiens,
    nb_offres_emploi as nb_offres_glassdoor,
    entretien_difficulte_moyenne
from glassdoor

union all

select
    md5('LINKEDIN-' || nom_normalise) as entreprise_sk,
    'LINKEDIN' as source_entreprise,
    false as a_fiche_glassdoor,
    null::bigint as id_employeur_glassdoor,
    nom_entreprise,
    nom_normalise,
    -- Obligé de mettre les champs à nul car pas le même niveau de détail que Glassdoor
    null, null, null, null, null, null, null, null, null, null, null,
    null::int,
    null::numeric, null::numeric, null::numeric, null::numeric, null::numeric, null::numeric,
    null::numeric, null::numeric, null::numeric,
    null::int, null::int, null::int, null::int,
    null::numeric
from linkedin_seules
