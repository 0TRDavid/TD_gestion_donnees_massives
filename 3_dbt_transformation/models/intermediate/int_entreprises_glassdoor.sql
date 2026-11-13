-- ./models/intermediate/int_entreprise_glassdoor.sql
-- Une ligne par entreprise Glassdoor (grain : id_employeur_glassdoor).

with descriptif as (
    select * from {{ ref('stg_metadonnee_descriptive') }}
),

fiche_societe as (

    select
        prefixe,
        {{ vers_numerique(attribut('id_employeur_glassdoor')) }}::bigint as id_employeur_glassdoor,
        {{ attribut('nom_entreprise') }} as nom_entreprise,
        {{ attribut('secteur_activite') }} as secteur_activite,
        {{ attribut('secteur_glassdoor') }} as secteur_glassdoor,
        {{ attribut('industrie_glassdoor') }} as industrie_glassdoor,
        {{ attribut('type_entreprise') }} as type_entreprise,
        {{ attribut('taille_entreprise') }} as taille_entreprise,
        {{ attribut('taille_entreprise_code') }} as taille_entreprise_code,
        {{ attribut('chiffre_affaires_tranche') }} as chiffre_affaires_tranche,
        {{ attribut('statut_entreprise_code') }} as statut_entreprise_code,
        {{ attribut('siege_social') }} as siege_social,
        {{ attribut('site_web') }} as site_web,
        {{ attribut('nom_pdg') }} as nom_pdg,
        {{ vers_numerique(attribut('annee_creation')) }}::int as annee_creation,
        {{ vers_note(attribut('note_globale')) }} as note_globale,
        {{ vers_taux(attribut('taux_recommandation')) }} as taux_recommandation,
        {{ vers_taux(attribut('taux_approbation_pdg')) }} as taux_approbation_pdg,
        {{ vers_numerique(attribut('nb_avis_total')) }}::int as nb_avis_total,
        {{ vers_numerique(attribut('nb_salaires')) }}::int as nb_salaires,
        {{ vers_numerique(attribut('nb_entretiens')) }}::int as nb_entretiens,
        {{ vers_numerique(attribut('nb_offres_emploi')) }}::int as nb_offres_emploi,
        {{ vers_note(attribut('entretien_difficulte_moyenne')) }} as entretien_difficulte_moyenne,
        {{ attribut('url_canonique') }} as url_glassdoor
    from descriptif
    where categorie = 'INFO_SOCIETE'
    group by prefixe
),

stats_pages_avis as (
    select
        prefixe,
        {{ vers_note(attribut('note_culture_valeurs_globale')) }} as note_culture_valeurs,
        {{ vers_note(attribut('note_equilibre_vie_pro_globale')) }} as note_equilibre_vie_pro,
        {{ vers_note(attribut('note_equipe_dirigeante_globale')) }} as note_equipe_dirigeante,
        {{ vers_note(attribut('note_opportunites_carriere_globale')) }} as note_opportunites_carriere,
        {{ vers_note(attribut('note_remuneration_avantages_globale')) }} as note_remuneration_avantages,
        {{ vers_taux(attribut('taux_perspective_positive')) }} as taux_perspective_positive,
        {{ attribut('date_dernier_avis') }}::timestamp as date_dernier_avis
    from descriptif
    where categorie = 'AVIS_SOCIETE'
      and avis_id is null
    group by prefixe
)

select distinct on (s.id_employeur_glassdoor)
    s.id_employeur_glassdoor,
    s.prefixe,
    s.nom_entreprise,
    {{ normaliser_nom('s.nom_entreprise') }} as nom_normalise,
    s.secteur_activite,
    s.secteur_glassdoor,
    s.industrie_glassdoor,
    s.type_entreprise,
    s.taille_entreprise,
    s.taille_entreprise_code,
    s.chiffre_affaires_tranche,
    s.statut_entreprise_code,
    s.siege_social,
    s.site_web,
    s.nom_pdg,
    s.annee_creation,
    s.note_globale,
    a.note_culture_valeurs,
    a.note_equilibre_vie_pro,
    a.note_equipe_dirigeante,
    a.note_opportunites_carriere,
    a.note_remuneration_avantages,
    s.taux_recommandation,
    s.taux_approbation_pdg,
    a.taux_perspective_positive,
    s.nb_avis_total,
    s.nb_salaires,
    s.nb_entretiens,
    s.nb_offres_emploi,
    s.entretien_difficulte_moyenne,
    a.date_dernier_avis,
    s.url_glassdoor
from fiche_societe s
left join stats_pages_avis a using (prefixe)
order by s.id_employeur_glassdoor, s.prefixe
