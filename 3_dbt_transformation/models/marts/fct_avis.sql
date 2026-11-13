-- ./models/marts/fct_avis.sql

select
    a.avis_id,
    md5('GLASSDOOR-' || a.id_employeur_glassdoor) as entreprise_sk,
    to_char(a.date_avis, 'YYYYMMDD')::int as date_avis_sk,

    -- mesures
    a.note_globale,
    a.note_culture_valeurs,
    a.note_equilibre_vie_pro,
    a.note_equipe_dirigeante,
    a.note_opportunites_carriere,
    a.note_remuneration_avantages,
    a.recommande_employeur,
    a.approuve_pdg,
    1 as nb_avis,

    -- attributs propres à l'avis
    a.perspective_entreprise,
    a.statut_auteur,
    a.est_employe_actuel,
    a.poste_auteur,
    a.ville_auteur,
    a.titre,
    a.avantages,
    a.inconvenients,
    a.conseils_direction
from {{ ref('int_avis') }} a
