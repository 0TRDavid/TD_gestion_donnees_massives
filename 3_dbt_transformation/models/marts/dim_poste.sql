
with postes as (

    select distinct
        intitule_poste,
        niveau_hierarchique,
        type_emploi,
        fonction,
        secteurs

    from {{ ref('int_offres_emploi') }}

),

dimension as (

    select
        md5(
            jsonb_build_array(
                intitule_poste,
                niveau_hierarchique,
                type_emploi,
                fonction,
                secteurs
            )::text
        ) as poste_sk,

        intitule_poste,
        niveau_hierarchique,
        type_emploi,
        fonction,
        secteurs

    from postes

)

select *
from dimension
