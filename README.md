
# TD Data Lakehouse — Gestion de données massives

Pipeline complet à partir de pages HTML LinkedIn et Glassdoor (offres d'emploi, fiches entreprises, avis d'employés) :
**Collecte → Ingestion → Extraction → Transformation → Analyse**.

## Démarrage rapide

Prérequis : **Docker Desktop** lancé.

```bash
docker compose up -d --build
```

Cette commande reconstruit tout le pipeline à partir des fichiers HTML de `0_SOURCE_WEB` :

1. `postgres_db` démarre la base PostgreSQL ;
2. `ingestion` copie les HTML en landing zone, produit les métadonnées en curated zone et les charge dans le schéma `raw` ;
3. `dbt` transforme les données et exécute les tests, jusqu'au modèle décisionnel dans le schéma `marts`.

Connexion à la base (Power BI ou autre client SQL) : `localhost:5432`, base, utilisateur et mot de passe définis dans `.env`, schéma `marts`.
Doc automatique de DBT généré et servi sur le lien : http://localhost:8080

## Arborescence

```
TD_gestion_donnees_massives/
├── 0_consignes/                  sujets et scripts d'exemple
├── 1_ingestion/                  phases 1 et 2 (Python)
│   ├── config.py                 chemins du projet
│   ├── ingestion.py              copie SOURCE → LANDING + métadonnées techniques et descriptives
│   ├── extraction_metadonnees_descriptives.py
│   ├── charger_raw.py            chargement des métadonnées dans PostgreSQL (schéma raw)
│   └── Dockerfile
├── 2_datalake/                   zones du datalake
│   ├── 0_SOURCE_WEB/             HTML sources (jamais modifiés)
│   ├── 1_LANDING_ZONE/           copie à l'identique, rangée par site et type (non versionné)
│   │   ├── GLASSDOOR/AVIS/
│   │   ├── GLASSDOOR/SOC/
│   │   └── LINKEDIN/EMP/
│   └── 2_CURATED_ZONE/METADONNEES/   métadonnées techniques et descriptives (non versionné)
├── 3_dbt_transformation/         phase 3 (dbt) = 3_PRODUCTION_ZONE
│   ├── macros/                   pivot et typage du format vertical
│   ├── models/staging/
│   ├── models/intermediate/
│   ├── models/marts/
│   └── Dockerfile
├── docker-compose.yml
└── .env
```

| Phase | Consigne | Réalisation |
|---|---|---|
| 1 — Ingestion | HTML → LANDING ZONE + métadonnées techniques | `1_ingestion/ingestion.py` |
| 2 — Extraction | métadonnées descriptives → CURATED ZONE | `1_ingestion/extraction_metadonnees_descriptives.py` |
| 3 — ETL / Data Warehouse | modèle décisionnel | `1_ingestion/charger_raw.py` + `3_dbt_transformation/` |
| 4 — Reporting | tableaux de bord BI | Power BI connecté au schéma `marts` |

## Architecture

```
0_SOURCE_WEB (HTML)
      │  copie non destructive
      ▼
1_LANDING_ZONE ──► métadonnées techniques ──┐
      │  extraction (parsing HTML)          │   2_CURATED_ZONE/METADONNEES
      ▼                                     │   (CSV, format vertical)
métadonnées descriptives ───────────────────┘
      │  charger_raw.py (COPY)
      ▼
PostgreSQL
  raw           tables chargées telles quelles
  staging       rattachement au fichier, nettoyage du texte
  intermediate  pivot du format vertical, typage, dédoublonnage
  marts         modèle décisionnel → Power BI
```

## Choix techniques

### Arborescence

Les dossiers sont numérotés dans l'ordre du pipeline (consignes → ingestion → datalake → transformation) et chaque dossier a un seul rôle : le code est séparé des données. Les noms des zones (`0_SOURCE_WEB`, `1_LANDING_ZONE`, `2_CURATED_ZONE`) et les sous-dossiers par site et type sont ceux des consignes.

### Ingestion (phases 1 et 2)

- Les fichiers sources sont copiés sans modification ; un fichier déjà présent et plus récent en landing zone n'est pas recopié.
- Chaque fichier reçoit un identifiant stable (`OBJET_ID`, hash MD5 du nom de fichier).
- Les métadonnées techniques et descriptives sont écrites dans deux CSV de même structure verticale `OBJET_ID ; COLONNE ; VALEUR`, comme demandé.

### Chargement dans PostgreSQL

`charger_raw.py` charge les deux CSV dans le schéma `raw` avec un `COPY`, sans aucune transformation. Toutes les transformations sont ensuite faites dans la base.

Les tables sont vidées (`TRUNCATE`) puis rechargées à chaque exécution plutôt que supprimées, car les vues dbt en dépendent : le pipeline peut être relancé autant de fois que nécessaire.

### Transformation avec dbt (ELT)

Plutôt qu'un ETL en Python produisant des CSV, la phase 3 est réalisée en SQL avec dbt, directement dans PostgreSQL :

- **les transformations sont testées** : 59 tests (unicité, valeurs non nulles, relations entre tables, valeurs autorisées) sont exécutés à chaque lancement et bloquent le pipeline en cas d'anomalie ;
- **tout est rejouable en une commande** : `docker compose up` reconstruit l'entrepôt complet depuis les HTML, sans étape manuelle.

Le projet suit trois couches :

| Couche | Rôle | Matérialisation |
|---|---|---|
| `staging` | rattache chaque donnée à son fichier (catégorie, préfixe), extrait l'identifiant des avis, décode les entités HTML. Les données restent au format vertical. | vues |
| `intermediate` | pivote le format vertical (une colonne par attribut), type les valeurs et dédoublonne : une table par type de document. | tables |
| `marts` | modèle décisionnel interrogé par Power BI. | tables |

Le typage se fait au moment du pivot et non en staging : dans le format vertical, la colonne `VALEUR` mélange textes, notes et dates, elle ne peut être typée qu'une fois chaque attribut dans sa propre colonne. Les macros de `macros/pivot.sql` gèrent la virgule décimale et les valeurs factices de Glassdoor (`0`, `-0,1`, `-1`) qui signifient « non renseigné ».

### Modèle décisionnel

Modèle en constellation : deux tables de faits partagent les mêmes dimensions.

```
            dim_date
            ▲      ▲
            │      │
     fct_avis      fct_offres
            │      │
            ▼      ▼
         dim_entreprise
```

| Table | Grain | Contenu |
|---|---|---|
| `fct_avis` | un avis Glassdoor | 6 notes sur 5, recommandation, approbation du PDG, statut de l'auteur, titre, avantages, inconvénients |
| `fct_offres` | une offre LinkedIn | nombre d'offres, durée de publication, intitulé, niveau, type de contrat, localisation |
| `dim_entreprise` | une entreprise | fiche Glassdoor (secteur, taille, notes globales…) ou entreprise vue uniquement sur LinkedIn |
| `dim_date` | un jour | clé `AAAAMMJJ` |

- Une offre LinkedIn est rattachée à une fiche Glassdoor par le nom de l'entreprise normalisé (minuscules, sans ponctuation). Les entreprises sans fiche Glassdoor sont ajoutées à `dim_entreprise` avec des attributs Glassdoor vides, pour ne perdre aucune offre.
- Les clés de substitution sont des hash MD5 (`md5('GLASSDOOR-' || id)`, `md5('LINKEDIN-' || nom)`) : elles sont identiques d'une exécution à l'autre et ne peuvent pas entrer en collision entre les deux sources.

### Conteneurisation

Chaque étape tourne dans son propre conteneur, et `docker compose` garantit l'ordre d'exécution :

- l'ingestion attend que PostgreSQL soit prêt (`healthcheck`) ;
- dbt ne démarre que si l'ingestion s'est terminée sans erreur (`service_completed_successfully`).

### Versionnement

Seuls le code et les fichiers sources (`0_SOURCE_WEB`) sont versionnés. La landing zone, la curated zone et les tables de la base sont régénérées à l'identique par le pipeline, il n'y a donc pas lieu de les stocker dans git.

Le fichier `.env` est volontairement versionné : il ne contient que les identifiants de la base PostgreSQL locale.

## Qualité des données

Problèmes rencontrés dans les sources et traités dans le pipeline :

- avis présents sur plusieurs pages, offres et entreprises récupérées plusieurs fois : dédoublonnés ;
- valeurs factices de Glassdoor pour « pas de note » : converties en `NULL` ;
- virgules décimales et entités HTML (`&amp;`) : nettoyées ;
- codes postaux placés dans le champ ville sur LinkedIn : corrigés ;
- une partie seulement des offres LinkedIn correspond à une fiche Glassdoor ;
- au plus deux pages d'avis par entreprise ont été récupérées.

## Répartition du travail

| Rôle | Périmètre | Membre |
|---|---|---|
| Ingestion | phases 1 et 2 : copie en landing zone, métadonnées techniques, extraction des métadonnées descriptives | _Nico_ |
| Transformation et modélisation | phase 3 : chargement raw, projet dbt, modèle décisionnel, conteneurisation | _David_ |
| Data Visualisation & Documentation | phase 4: création des vues, rédaction des livrables | _Route_ |