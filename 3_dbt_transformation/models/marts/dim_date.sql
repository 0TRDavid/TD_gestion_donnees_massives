-- ./models/marts/dim_date.sql

with jours as (
    select generate_series(
        '2009-01-01'::date,
        '2021-12-31'::date,
        interval '1 day'
    )::date as date_jour
)

select
    to_char(date_jour, 'YYYYMMDD')::int as date_sk,
    date_jour
from jours