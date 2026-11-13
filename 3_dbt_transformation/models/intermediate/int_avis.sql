-- ./models/intermediate/int_avis.sql
-- Une ligne par avis Glassdoor (grain : avis_id).
-- Un fichier AVIS contient plusieurs avis, un même avis peut apparaître sur deux pages (P1, P2)

with descriptif as (
    select *
    from {{ ref('stg_metadonnee_descriptive') }}
    where categorie = 'AVIS_SOCIETE'
),

employeur_par_page as (
    select
        objet_id,
        {{ vers_numerique('valeur') }}::bigint as id_employeur_glassdoor
    from descriptif
    where avis_id is null
      and attribut = 'id_employeur_glassdoor'
),

avis as (
    select d.*, e.id_employeur_glassdoor
    from descriptif d
    left join employeur_par_page e using (objet_id)
    where d.avis_id is not null
)

select
    avis_id,
    max(id_employeur_glassdoor)as id_employeur_glassdoor,
    {{ attribut('date_avis') }}::timestamptz as date_avis,
    {{ attribut('titre') }} as titre,

    -- notes sur 5
    {{ vers_note(attribut('note_globale')) }} as note_globale,
    {{ vers_note(attribut('note_culture_valeurs')) }} as note_culture_valeurs,
    {{ vers_note(attribut('note_equilibre_vie_pro')) }} as note_equilibre_vie_pro,
    {{ vers_note(attribut('note_equipe_dirigeante')) }} as note_equipe_dirigeante,
    {{ vers_note(attribut('note_opportunites_carriere')) }} as note_opportunites_carriere,
    {{ vers_note(attribut('note_remuneration_avantages')) }} as note_remuneration_avantages,

    -- indicateurs (Oui / Non -> booléen ; NULL si non renseigné)
    case {{ attribut('recommande_employeur') }}
        when 'Oui' then true when 'Non' then false end as recommande_employeur,
    case {{ attribut('avis_pdg') }}
        when 'Approuve' then true when 'N''approuve pas' then false end as approuve_pdg,
    {{ attribut('perspective_entreprise') }} as perspective_entreprise,

    -- auteur
    {{ attribut('statut_auteur') }} as statut_auteur,
    {{ attribut('statut_auteur') }} ilike '%actuel%' as est_employe_actuel,
    {{ attribut('poste_auteur') }} as poste_auteur,
    {{ attribut('ville_auteur') }} as ville_auteur,

    -- textes libres
    {{ attribut('contexte_emploi') }} as contexte_emploi,
    {{ attribut('avantages') }} as avantages,
    {{ attribut('inconvenients') }} as inconvenients,
    {{ attribut('conseils_direction') }} as conseils_direction
from avis
group by avis_id
