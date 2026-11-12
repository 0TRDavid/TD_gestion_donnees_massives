#!/usr/bin/env bash
# ============================================================
# Pipeline de gestion de données massives
# Compatible Linux / macOS / Windows (Git Bash ou WSL)
# Option : -y / --yes  -> remplace les seeds sans confirmation
# ============================================================

set -eo pipefail

# ============================================================
# 1. PARAMÈTRES DU PROJET
# ============================================================

REPERTOIRE_PROJET="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

REPERTOIRE_VENV="$REPERTOIRE_PROJET/.venv"

REPERTOIRE_DATALAKE="$REPERTOIRE_PROJET"         # pour le script Python, le datalake est le répertoire racine du projet
REPERTOIRE_SOURCE_HTML="$REPERTOIRE_DATALAKE/0_SOURCE_WEB"
REPERTOIRE_INGESTION="$REPERTOIRE_PROJET/3_ingestion"
SCRIPT_INGESTION="ingestion.py"
SCRIPT_EXPORT_DBT="export_dbt.py"

REPERTOIRE_DBT="$REPERTOIRE_PROJET/dbt_transformation"
REPERTOIRE_SEEDS="$REPERTOIRE_DBT/seeds"
SEEDS_ATTENDUS=("metadonnee_technique.csv" "metadonnee_descriptive.csv")
REPERTOIRE_METADONNEES="$REPERTOIRE_DATALAKE/2_CURATED_ZONE/METADONNEES" 


FICHIER_ENV="$REPERTOIRE_PROJET/.env"
FICHIER_COMPOSE="$REPERTOIRE_PROJET/docker-compose.yml"

SERVICE_POSTGRES="${SERVICE_POSTGRES:-postgres}"                
VARIABLES_DBT_REQUISES=("POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB")

CONFIRMATION_AUTO=0
for argument in "$@"; do
    case "$argument" in
        -y|--yes) CONFIRMATION_AUTO=1 ;;
    esac
done

# Évite les erreurs d'encodage (cp1252) de Python sous Windows
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

# ============================================================
# 2. FONCTIONS
# ============================================================

afficher_titre() {
    echo ""
    echo "============================================================"
    echo "$1"
    echo "============================================================"
}

arreter() {
    echo "ERREUR : $1" >&2
    exit 1
}

verifier_fichier() { [ -f "$1" ] || arreter "fichier introuvable : $1"; }
verifier_dossier() { [ -d "$1" ] || arreter "dossier introuvable : $1"; }

verifier_seed_copie() {
    local seed="$1"
    local cible="$REPERTOIRE_SEEDS/$seed"
    local source="$REPERTOIRE_METADONNEES/$seed"

    [ -s "$cible" ] || arreter "$seed absent ou vide dans $REPERTOIRE_SEEDS."

    if [ -f "$source" ]; then
        cmp -s "$source" "$cible" \
            || arreter "$seed diffère de la source $source : copie incomplète, ou $SCRIPT_EXPORT_DBT transforme le fichier."
    else
        echo "ATTENTION : source $source introuvable, comparaison de contenu ignorée pour $seed."
    fi
}

# Choisit un interpréteur réellement fonctionnel (écarte le faux "python" du Microsoft Store)
detecter_python() {
    local candidat
    for candidat in "python3" "python" "py -3"; do
        # $candidat volontairement non quoté pour permettre "py -3"
        # shellcheck disable=SC2086
        if $candidat -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >/dev/null 2>&1; then
            # shellcheck disable=SC2206
            PYTHON_BOOT=($candidat)
            return 0
        fi
    done
    return 1
}

charger_variables_environnement() {
    if [ ! -f "$FICHIER_ENV" ]; then
        echo "ATTENTION : fichier .env introuvable : $FICHIER_ENV"
        return 0
    fi
    echo "Chargement des variables d'environnement depuis : $FICHIER_ENV"
    set -a
    # tr -d '\r' : neutralise les fins de ligne Windows (CRLF) qui corrompent les valeurs
    # shellcheck disable=SC1090
    source <(tr -d '\r' < "$FICHIER_ENV")
    set +a
}

verifier_variables_dbt() {
    local manquantes=() variable
    for variable in "${VARIABLES_DBT_REQUISES[@]}"; do
        [ -n "${!variable:-}" ] || manquantes+=("$variable")
    done
    if [ "${#manquantes[@]}" -gt 0 ]; then
        arreter "variables absentes ou vides dans $FICHIER_ENV : ${manquantes[*]}"
    fi
}

attendre_postgres() {
    if ! docker compose config --services | tr -d '\r' | grep -qx "$SERVICE_POSTGRES"; then
        echo "ATTENTION : service '$SERVICE_POSTGRES' absent du compose, attente PostgreSQL ignorée."
        echo "(définir SERVICE_POSTGRES=<nom du service> pour l'activer)"
        return 0
    fi
    echo "Attente de PostgreSQL (service : $SERVICE_POSTGRES)..."
    local essais=0
    until docker compose exec -T "$SERVICE_POSTGRES" pg_isready -U "${POSTGRES_USER:-postgres}" >/dev/null 2>&1; do
        essais=$((essais + 1))
        if [ "$essais" -ge 30 ]; then
            docker compose logs --tail 30 "$SERVICE_POSTGRES" || true
            arreter "PostgreSQL n'est pas prêt après 60 s."
        fi
        sleep 2
    done
    echo "PostgreSQL est prêt."
}

# ============================================================
# 3. VÉRIFICATIONS PRÉALABLES
# ============================================================

afficher_titre "Vérification de l'environnement"

verifier_fichier "requirements.txt"
verifier_fichier "$FICHIER_COMPOSE"
verifier_dossier "$REPERTOIRE_INGESTION"
verifier_dossier "$REPERTOIRE_DBT"

detecter_python || arreter "Python >= 3.9 introuvable dans le PATH (essayé : python3, python, py -3)."
echo "Python détecté : ${PYTHON_BOOT[*]}"

command -v docker >/dev/null 2>&1 || arreter "Docker n'est pas installé ou n'est pas dans le PATH."
docker info >/dev/null 2>&1 || arreter "Le démon Docker ne répond pas (Docker Desktop est-il lancé ?)."

# ============================================================
# 4. ENVIRONNEMENT VIRTUEL
# ============================================================

afficher_titre "Environnement virtuel Python"

if [ ! -d "$REPERTOIRE_VENV" ]; then
    echo "Création de l'environnement virtuel : $REPERTOIRE_VENV"
    "${PYTHON_BOOT[@]}" -m venv "$REPERTOIRE_VENV"
else
    echo "Environnement virtuel déjà présent : $REPERTOIRE_VENV"
fi

if [ -f "$REPERTOIRE_VENV/Scripts/python.exe" ]; then      # Windows
    PYTHON_EXECUTABLE="$REPERTOIRE_VENV/Scripts/python.exe"
elif [ -f "$REPERTOIRE_VENV/bin/python" ]; then            # Linux / macOS
    PYTHON_EXECUTABLE="$REPERTOIRE_VENV/bin/python"
else
    arreter "exécutable Python introuvable dans le venv (supprimer $REPERTOIRE_VENV et relancer)."
fi
echo "Python du venv : $PYTHON_EXECUTABLE"

"$PYTHON_EXECUTABLE" -m pip install --upgrade pip
echo "Installation des dépendances depuis : requirements.txt"
"$PYTHON_EXECUTABLE" -m pip install -r requirements.txt

# ============================================================
# 5. VARIABLES D'ENVIRONNEMENT
# ============================================================

afficher_titre "Chargement des variables d'environnement"

charger_variables_environnement
verifier_variables_dbt

# ============================================================
# 6. DOCKER COMPOSE
# ============================================================

afficher_titre "Démarrage de Docker Compose"

cd "$REPERTOIRE_PROJET"
docker compose up -d
attendre_postgres
docker compose ps

# ============================================================
# 7. INGESTION
# ============================================================

afficher_titre "Ingestion des fichiers HTML"

verifier_dossier "$REPERTOIRE_SOURCE_HTML"
NB_HTML="$(find "$REPERTOIRE_SOURCE_HTML" -type f \( -iname "*.html" -o -iname "*.htm" \) | wc -l | tr -d ' ')"
echo "Fichiers HTML présents dans $REPERTOIRE_SOURCE_HTML : $NB_HTML"
if [ "$NB_HTML" -eq 0 ]; then
    arreter "aucun fichier HTML en source : l'ingestion produirait des métadonnées vides."
fi

cd "$REPERTOIRE_DATALAKE"
"$PYTHON_EXECUTABLE" "3_ingestion/$SCRIPT_INGESTION"

# ============================================================
# 8. EXPORT DES MÉTADONNÉES VERS DBT
# ============================================================

afficher_titre "Export des métadonnées vers dbt"

echo "Les fichiers suivants seront copiés dans : $REPERTOIRE_SEEDS"
printf -- "- %s\n" "${SEEDS_ATTENDUS[@]}"

if [ "$CONFIRMATION_AUTO" -eq 1 ]; then
    reponse="o"
else
    read -r -p "Voulez-vous continuer et remplacer les seeds existants ? (o/n) : " reponse
fi

case "$reponse" in
    o|O|oui|OUI)
        "$PYTHON_EXECUTABLE" "3_ingestion/$SCRIPT_EXPORT_DBT"
        for seed in "${SEEDS_ATTENDUS[@]}"; do
            verifier_seed_copie "$seed"
        done
        ;;
    *)
        echo "Export vers dbt annulé : les seeds existants seront chargés tels quels."
        ;;
esac

# ============================================================
# 9. SEEDS DBT
# ============================================================

afficher_titre "Chargement des seeds dans dbt"

if [ -f "$REPERTOIRE_VENV/Scripts/dbt.exe" ]; then
    DBT_COMMAND="$REPERTOIRE_VENV/Scripts/dbt.exe"
elif [ -f "$REPERTOIRE_VENV/bin/dbt" ]; then
    DBT_COMMAND="$REPERTOIRE_VENV/bin/dbt"
else
    arreter "dbt introuvable dans le venv : vérifier qu'il figure dans requirements.txt."
fi

export DBT_PROFILES_DIR="$REPERTOIRE_DBT"
cd "$REPERTOIRE_DBT"

"$DBT_COMMAND" debug        # échoue tôt si profil ou connexion invalides
"$DBT_COMMAND" seed --full-refresh

# ============================================================
# 10. FIN
# ============================================================

afficher_titre "Pipeline terminé avec succès"
echo "Les données ont été ingérées."
echo "Les métadonnées ont été exportées vers dbt."
echo "Les seeds ont été chargés dans la base de données."