# TD Data Lakehouse — Gestion de données massives

Pipeline complet à partir de 603 pages HTML LinkedIn et Glassdoor (offres d'emploi, fiches entreprises, avis d'employés) :
**HTML → data lake → PostgreSQL → dbt → Power BI**.

Le détail de l'analyse et des choix techniques est dans le [rapport](rapport/rapport.pdf).

## Lancer le projet

Prérequis : **Docker Desktop** lancé.

```bash
docker compose up -d --build
```

Cette commande reconstruit tout depuis les HTML de `2_datalake/0_SOURCE_WEB` :

1. `postgres_db` démarre la base ;
2. `ingestion` copie les HTML en landing zone, produit les métadonnées et les charge dans le schéma `raw` ;
3. `dbt` transforme les données, exécute les tests et construit le modèle décisionnel dans le schéma `marts`.

| Accès | Où |
|---|---|
| Base PostgreSQL | `localhost:5432`, identifiants dans `.env`, schéma `marts` |
| Documentation dbt (lignage, tests) | http://localhost:8080 |
| Tableaux de bord | `4_dataviz_pbi/Gestion de données massives.pbip` (Power BI Desktop) |

## Arborescence

```
├── 0_consignes/            sujets du TD
├── 1_ingestion/            phases 1 et 2 (Python) : copie, métadonnées, chargement raw
├── 2_datalake/             0_SOURCE_WEB, 1_LANDING_ZONE, 2_CURATED_ZONE
├── 3_dbt_transformation/   phase 3 (dbt) : staging → intermediate → marts
├── 4_dataviz_pbi/          phase 4 (Power BI)
├── rapport/                rapport final
└── docker-compose.yml
```

La landing zone et la curated zone ne sont pas versionnées : le pipeline les régénère.

## Équipe

| Membre | Rôle |
|---|---|
| Nicolas MENY | Ingestion (phases 1 et 2) |
| David TRUONG | Transformation, modélisation, conteneurisation (phase 3) |
| Ruth ABEBE NGUESSY | Data visualisation (phase 4) |
