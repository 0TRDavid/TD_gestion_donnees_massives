#!/usr/bin/env bash

# ============================================================
# Pipeline de gestion de données massives
# - Création / activation de l'environnement virtuel
# - Installation des dépendances
# - Démarrage de Docker Compose
# - Ingestion des fichiers HTML
# - Export des métadonnées vers dbt
# - Chargement des seeds dans dbt
# ============================================================

set -e

# ============================================================
# 1. PARAMÈTRES DU PROJET
# ============================================================

REPERTOIRE_PROJET="$(cd "$(dirname "$0")" && pwd)"

REPERTOIRE_VENV="$REPERTOIRE_PROJET/.venv"
FICHIER_REQUIREMENTS="./requirements.txt"

REPERTOIRE_INGESTION="$REPERTOIRE_PROJET/3_ingestion"
SCRIPT_INGESTION="ingestion.py"
SCRIPT_EXPORT_DBT="export_dbt.py"

REPERTOIRE_DBT="$REPERTOIRE_PROJET/dbt_transformation"

FICHIER_ENV="$REPERTOIRE_PROJET/.env"
FICHIER_COMPOSE="$REPERTOIRE_PROJET/docker-compose.yml"

# ============================================================
# 2. FONCTIONS
# ============================================================

afficher_titre() {
    echo ""
    echo "============================================================"
    echo "$1"
    echo "============================================================"
}

verifier_fichier() {
    if [ ! -f "$1" ]; then
        echo "ERREUR : fichier introuvable : $1"
        exit 1
    fi
}

verifier_dossier() {
    if [ ! -d "$1" ]; then
        echo "ERREUR : dossier introuvable : $1"
        exit 1
    fi
}

charger_variables_environnement() {
    if [ ! -f "$FICHIER_ENV" ]; then
        echo "ATTENTION : fichier .env introuvable : $FICHIER_ENV"
        return
    fi

    echo "Chargement des variables d'environnement depuis : $FICHIER_ENV"

    set -a
    source "$FICHIER_ENV"
    set +a
}

# ============================================================
# 3. VÉRIFICATIONS PRÉALABLES
# ============================================================

afficher_titre "Vérification de l'environnement"

verifier_fichier "$FICHIER_REQUIREMENTS"
verifier_fichier "$FICHIER_COMPOSE"
verifier_dossier "$REPERTOIRE_DBT"

PYTHON_COMMAND=""

if command -v python >/dev/null 2>&1; then
    PYTHON_COMMAND="python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_COMMAND="python3"
elif command -v py >/dev/null 2>&1; then
    PYTHON_COMMAND="py -3"
else
    echo "ERREUR : Python n'est pas installé ou n'est pas dans le PATH."
    exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "ERREUR : Docker n'est pas installé ou n'est pas dans le PATH."
    exit 1
fi

if ! command -v dbt >/dev/null 2>&1; then
    echo "ATTENTION : dbt n'est pas encore disponible."
    echo "Il sera installé avec requirements.txt si celui-ci contient dbt."
fi

# ============================================================
# 4. CRÉATION ET ACTIVATION DU VENV
# ============================================================

afficher_titre "Environnement virtuel Python"

if [ ! -d "$REPERTOIRE_VENV" ]; then
    echo "Création de l'environnement virtuel : $REPERTOIRE_VENV"
    python -m venv "$REPERTOIRE_VENV"
    sleep 10
else
    echo "Environnement virtuel déjà présent : $REPERTOIRE_VENV"
fi


if [ -f "$REPERTOIRE_VENV/Scripts/python.exe" ]; then
    PYTHON_EXECUTABLE="$REPERTOIRE_VENV/Scripts/python.exe"
elif [ -f "$REPERTOIRE_VENV/bin/python" ]; then
    PYTHON_EXECUTABLE="$REPERTOIRE_VENV/bin/python"
else
    echo "ERREUR : exécutable Python introuvable dans le venv."
    exit 1
fi

echo "Python du venv : $PYTHON_EXECUTABLE"

echo "Mise à jour de pip"
"$PYTHON_EXECUTABLE" -m pip install --upgrade pip

echo "Installation des dépendances depuis : $FICHIER_REQUIREMENTS"
cd "$REPERTOIRE_PROJET"
"$PYTHON_EXECUTABLE" -m pip install -r "$FICHIER_REQUIREMENTS"

# ============================================================
# 5. CHARGEMENT DU FICHIER .ENV
# ============================================================

afficher_titre "Chargement des variables d'environnement"

charger_variables_environnement

# ============================================================
# 6. DÉMARRAGE DE DOCKER COMPOSE
# ============================================================

afficher_titre "Démarrage de Docker Compose"

cd "$REPERTOIRE_PROJET"

docker compose up -d

echo "Attente du démarrage des conteneurs..."
sleep 10

docker compose ps

# ============================================================
# 7. INGESTION DES DONNÉES
# ============================================================

afficher_titre "Ingestion des fichiers HTML"

cd "$REPERTOIRE_INGESTION"

"$PYTHON_EXECUTABLE" "$SCRIPT_INGESTION"

# ============================================================
# 8. EXPORT DES MÉTADONNÉES VERS DBT
# ============================================================

afficher_titre "Export des métadonnées vers dbt"

echo "Les fichiers CSV suivants vont être copiés dans dbt_transformation/seeds :"
echo "- metadonnee_technique.csv"
echo "- metadonnee_descriptive.csv"

read -p "Voulez-vous continuer et remplacer les seeds existants ? (o/n) : " reponse

if [ "$reponse" = "o" ] || [ "$reponse" = "O" ] || [ "$reponse" = "oui" ]; then
    "$PYTHON_EXECUTABLE" "$SCRIPT_EXPORT_DBT"
else
    echo "Export vers dbt annulé."
fi

# ============================================================
# 9. CHARGEMENT DES SEEDS DANS DBT
# ============================================================

afficher_titre "Chargement des seeds dans dbt"

cd "$REPERTOIRE_DBT"

if [ -f "$REPERTOIRE_VENV/Scripts/dbt.exe" ]; then
    DBT_COMMAND="$REPERTOIRE_VENV/Scripts/dbt.exe"
elif [ -f "$REPERTOIRE_VENV/bin/dbt" ]; then
    DBT_COMMAND="$REPERTOIRE_VENV/bin/dbt"
else
    DBT_COMMAND="dbt"
fi

"$DBT_COMMAND" seed --full-refresh



# ============================================================
# 10. FIN DU PIPELINE
# ============================================================

afficher_titre "Pipeline terminé avec succès"

echo "Les données ont été ingérées."
echo "Les métadonnées ont été exportées vers dbt."
echo "Les seeds ont été chargés dans la base de données."