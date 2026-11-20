"""Génère rapport.html puis rapport.pdf à partir de rapport.md.

Prérequis : pip install markdown ; Microsoft Edge ou Google Chrome installé.
Usage     : python rapport/generer_pdf.py

Une image absente (capture Power BI pas encore ajoutée dans captures/)
est remplacée par un cadre indiquant le fichier attendu.
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

import markdown

DOSSIER = Path(__file__).resolve().parent
SOURCE = DOSSIER / "rapport.md"
SORTIE_HTML = DOSSIER / "rapport.html"
SORTIE_PDF = DOSSIER / "rapport.pdf"

NAVIGATEURS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "msedge", "google-chrome", "chromium",
]

CSS = """
@page { size: A4; margin: 18mm 16mm 18mm 16mm;
        @bottom-right { content: counter(page); } }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.45;
       color: #1e293b; margin: 0; }
h1 { font-size: 18pt; color: #1e3a5f; border-bottom: 2px solid #1e3a5f; padding-bottom: 4px;
     margin: 16px 0 8px; break-after: avoid; }
h2 { font-size: 13pt; color: #1e3a5f; margin: 18px 0 6px; break-after: avoid; }
h3 { font-size: 11pt; color: #334155; margin: 14px 0 4px; break-after: avoid; }
p, li { text-align: justify; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 12px; font-size: 9pt;
        break-inside: auto; }
tr { break-inside: avoid; }
th { background: #1e3a5f; color: #fff; text-align: left; padding: 4px 6px; }
td { border-bottom: 1px solid #e2e8f0; padding: 4px 6px; vertical-align: top; }
tr:nth-child(even) td { background: #f8fafc; }
code { font-family: Consolas, monospace; font-size: 8.8pt; background: #f1f5f9;
       padding: 0 3px; border-radius: 3px; }
pre { background: #0f172a; color: #e2e8f0; padding: 8px 12px; border-radius: 6px;
      font-size: 8.5pt; line-height: 1.3; break-inside: avoid; }
pre code { background: none; color: inherit; padding: 0; }
figure { margin: 10px 0 14px; text-align: center; break-inside: avoid; }
figure img { max-width: 100%; max-height: 235mm; }
figcaption { font-size: 9pt; color: #64748b; font-style: italic; margin-top: 4px; }
.manquant { border: 2px dashed #94a3b8; border-radius: 8px; height: 95mm; display: flex;
            flex-direction: column; justify-content: center; align-items: center;
            color: #64748b; background: #f8fafc; }
.manquant b { font-size: 12pt; margin-bottom: 6px; }
.garde { height: 255mm; display: flex; flex-direction: column; justify-content: center;
         text-align: center; }
.garde .bandeau { background: #1e3a5f; color: #fff; padding: 36px 20px; border-radius: 10px; }
.garde .titre { font-size: 26pt; font-weight: bold; margin-bottom: 10px; }
.garde .sous-titre { font-size: 14pt; opacity: .9; }
.garde .infos { margin-top: 40px; font-size: 12pt; line-height: 2; }
.sommaire { break-before: page; }
.sommaire h2 { break-before: avoid; }
.sommaire ol { font-size: 11pt; line-height: 1.9; }
"""


def lire_entete(texte):
    entete = {}
    m = re.match(r"^---\n(.*?)\n---\n", texte, re.S)
    if m:
        for ligne in m.group(1).splitlines():
            cle, _, valeur = ligne.partition(":")
            entete[cle.strip()] = valeur.strip().strip('"')
        texte = texte[m.end():]
    return entete, texte


def figures(html):
    """<p><img></p> -> <figure> avec légende, ou cadre si le fichier n'existe pas."""
    def remplacer(m):
        alt, src = m.group(1), m.group(2)
        if (DOSSIER / src).exists():
            contenu = f'<img src="{src}" alt="{alt}">'
        else:
            contenu = (f'<div class="manquant"><b>Capture à insérer</b>'
                       f'<span>déposer le fichier <code>rapport/{src}</code></span></div>')
        return f"<figure>{contenu}<figcaption>{alt}</figcaption></figure>"
    return re.sub(r'<p><img alt="([^"]*)" src="([^"]*)"\s*/?></p>', remplacer, html)


def construire_html():
    entete, corps = lire_entete(SOURCE.read_text(encoding="utf-8"))
    titres = re.findall(r"^# (.+)$", corps, re.M)
    html_corps = markdown.markdown(corps, extensions=["tables", "fenced_code", "sane_lists"])
    html_corps = figures(html_corps)

    garde = f"""
<section class="garde"><div class="bandeau">
  <div class="sous-titre">{entete.get('sous_titre', '')}</div>
  <div class="titre">{entete.get('titre', '')}</div>
  <div class="sous-titre">{entete.get('groupe', '')}</div>
</div>
<div class="infos">{entete.get('auteurs', '')}<br>{entete.get('formation', '')} — {entete.get('date', '')}</div>
</section>"""
    sommaire = "<section class='sommaire'><h2>Sommaire</h2><ol style='list-style:none;padding:0'>" + \
        "".join(f"<li>{t}</li>" for t in titres) + "</ol></section>"

    SORTIE_HTML.write_text(
        f"<!doctype html><html lang='fr'><head><meta charset='utf-8'>"
        f"<title>{entete.get('titre', 'Rapport')}</title><style>{CSS}</style></head>"
        f"<body>{garde}{sommaire}{html_corps}</body></html>",
        encoding="utf-8",
    )


def imprimer_pdf():
    navigateur = next((n for n in NAVIGATEURS if os.path.exists(n) or shutil.which(n)), None)
    if navigateur is None:
        raise SystemExit("Edge ou Chrome introuvable : ouvrir rapport.html et l'imprimer en PDF.")
    subprocess.run([
        navigateur, "--headless", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={SORTIE_PDF}", SORTIE_HTML.as_uri(),
    ], check=True, capture_output=True)


if __name__ == "__main__":
    construire_html()
    imprimer_pdf()
    print(f"PDF généré : {SORTIE_PDF}")
