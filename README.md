# TD Data Lakehouse — Gestion de données massives

Pipeline complet à partir de fichiers HTML LinkedIn / Glassdoor :
**Collecte → Ingestion → Extraction → Transformation → Analyse**.

## Arborescence

```
TD_gestion_donnees_massives/
├── DATALAKE/                     ← zones du datalake (arborescence des consignes)
│   ├── 0_SOURCE_WEB/             ← HTML source (ne jamais modifier)
│   ├── 1_LANDING_ZONE/           ← copie à l'identique des HTML
│   │   ├── GLASSDOOR/{AVIS,SOC}/
│   │   └── LINKEDIN/EMP/
│   └── 2_CURATED_ZONE/
│       └── METADONNEES/          ← metadonnee_technique.csv, metadonnee_descriptive.csv
│
├── ingestion/                    ← Phases 1 et 2 (Python)
│   ├── config.py                 ← tous les chemins du projet
│   ├── ingestion.py              ← copie SOURCE → LANDING + métadonnées
│   ├── extraction_metadonnees_descriptives.py
│   └── export_dbt.py             ← copie des métadonnées vers les seeds dbt
│
├── dbt_transformation/           ← Phase 3 (ELT dans PostgreSQL = 3_PRODUCTION_ZONE)
│   ├── seeds/                    ← généré, non versionné
│   └── models/
│       ├── staging/              ← nettoyage / typage
│       ├── intermediate/         ← pivot du format vertical
│       └── marts/                ← modèle décisionnel (étoile)
│
├── consignes/                    ← sujets et scripts d'exemple du prof
├── docker-compose.yml            ← PostgreSQL
├── lancement_pipeline.sh         ← lance tout le pipeline
├── requirements.txt
└── .env.example                  ← à copier en .env
```

| Phase | Consigne | Où |
|---|---|---|
| 1 — Ingestion | HTML → LANDING ZONE + métadonnées techniques | `ingestion/ingestion.py` |
| 2 — Extraction | métadonnées descriptives → CURATED ZONE | `ingestion/extraction_metadonnees_descriptives.py` |
| 3 — ETL / DWH | modèle décisionnel | `dbt_transformation/` |
| 4 — Reporting | tableaux de bord BI | à venir |

## Lancement

Prérequis : Docker Desktop lancé, Python ≥ 3.9, un shell bash.

```bash
cp .env.example .env
```

Linux / macOS / Git Bash :

```bash
./lancement_pipeline.sh
```

Windows PowerShell : ne pas utiliser `bash` seul (il lance WSL), passer par Git Bash :

```powershell
& "C:\Program Files\Git\bin\bash.exe" ./lancement_pipeline.sh
```

Option `-y` : remplace les seeds dbt sans demander confirmation.
