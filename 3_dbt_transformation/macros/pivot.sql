-- Macros utilisées pour pivoter le format vertical (OBJET_ID ; COLONNE ; VALEUR) et typer les valeurs au moment du pivot.

-- Valeur texte d'un attribut
{% macro attribut(nom) -%}
    max(valeur) filter (where attribut = '{{ nom }}')
{%- endmacro %}

-- Texte -> numeric
{% macro vers_numerique(expression) -%}
    (case
        when {{ expression }} ~ '^-?[0-9]+([.,][0-9]+)?$'
        then replace({{ expression }}, ',', '.')::numeric
    end)
{%- endmacro %}

-- Note sur 5
{% macro vers_note(expression) -%}
    (case when {{ vers_numerique(expression) }} > 0 then {{ vers_numerique(expression) }} end)
{%- endmacro %}

-- Taux entre 0 et 1 : les valeurs négatives signifient "non renseigné"
{% macro vers_taux(expression) -%}
    (case when {{ vers_numerique(expression) }} >= 0 then {{ vers_numerique(expression) }} end)
{%- endmacro %}

-- Nom d'entreprise comparable entre sources : minuscules, sans ponctuation ni espaces
{% macro normaliser_nom(expression) -%}
    lower(regexp_replace({{ expression }}, '[^[:alnum:]]', '', 'g'))
{%- endmacro %}
