import argparse
from pathlib import Path

def extraire_nom(fichier: str) -> str | None:
    stem = Path(fichier).stem  # enlève l'extension, ex. .html
    parties = stem.split("-")

    if len(parties) < 3:
        return None

    # 52102-link-avis-emp-edzdfe -> ["52102", "link", "avis", "emp", "edzdfe"]
    return "-".join(parties[1:-1])

def main():
    parser = argparse.ArgumentParser(
        description="Liste les noms distincts entre le premier et le dernier séparateur '-'"
    )
    parser.add_argument("dossier", type=Path, help="Dossier contenant les fichiers")
    args = parser.parse_args()

    if not args.dossier.is_dir():
        raise SystemExit(f"Le dossier n'existe pas : {args.dossier}")

    noms = set()

    for fichier in args.dossier.iterdir():
        if fichier.is_file():
            nom = extraire_nom(fichier.name)
            if nom:
                noms.add(nom)

    for nom in sorted(noms):
        print(nom)

if __name__ == "__main__":
    main()