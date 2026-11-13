import html
import json
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

SEPARATEUR_DECIMAL = ","      
SEPARATEUR_MULTI = " | "      

# ----------------------------------------------------------------------------
# Helpers génériques
# ----------------------------------------------------------------------------
def _texte(fragment_html, garder_sauts_ligne=True):
    """HTML -> texte brut : retire les balises, décode les entités, normalise les espaces.
    Retourne None si le résultat est vide (pas de chaîne vide dans la sortie)."""
    if fragment_html is None:
        return None
    t = re.sub(r"(?is)<(script|style)\b.*?</\1>", "", fragment_html)
    if garder_sauts_ligne:
        t = re.sub(r"(?i)<br\s*/?>|</(p|li|ul|ol|div|h[1-6])>", "\n", t)
        t = re.sub(r"(?i)<li[^>]*>", "- ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t).replace("\xa0", " ")
    lignes = [re.sub(r"[ \t\r\f\v]+", " ", l).strip() for l in t.split("\n")]
    t = "\n".join(l for l in lignes if l) if garder_sauts_ligne else " ".join(t.split())
    return t or None


def _decimal(valeur):
    """Nombre (str/float) -> chaîne avec séparateur décimal paramétré. None si non numérique."""
    if valeur is None:
        return None
    s = str(valeur).strip().replace(",", ".")
    try:
        float(s)
    except ValueError:
        return None
    return s.replace(".", SEPARATEUR_DECIMAL)


def _ajouter(sortie, vus, cle, valeur):
    """Ajoute [cle, valeur] si valeur non vide et si le couple n'est pas déjà présent (idempotence)."""
    if valeur is None:
        return
    valeur = str(valeur).strip()
    if not valeur or (cle, valeur) in vus:
        return
    vus.add((cle, valeur))
    sortie.append([cle, valeur])


def _objet_json(contenu, cle):
    """Extrait l'objet JSON `"cle":{...}` par comptage d'accolades (tolère les '}' dans les chaînes)."""
    debut = contenu.find('"%s":{' % cle)
    if debut < 0:
        return {}
    i = contenu.index("{", debut)
    profondeur, dans_chaine, echappe = 0, False, False
    for k in range(i, len(contenu)):
        c = contenu[k]
        if dans_chaine:
            if echappe:
                echappe = False
            elif c == "\\":
                echappe = True
            elif c == '"':
                dans_chaine = False
        elif c == '"':
            dans_chaine = True
        elif c == "{":
            profondeur += 1
        elif c == "}":
            profondeur -= 1
            if profondeur == 0:
                try:
                    return json.loads(contenu[i:k + 1])
                except json.JSONDecodeError:
                    return {}
    return {}


def _gdglobals_employeur(contenu):
    """Bloc `'employer' : { 'size' : "..", 'name':".." ... }` de window.gdGlobals (syntaxe JS à quotes simples)."""
    m = re.search(r"'employer'\s*:\s*\{(.*?)\}", contenu, re.S)
    if not m:
        return {}
    return {k: v for k, v in re.findall(r"'(\w+)'\s*:\s*\"([^\"]*)\"", m.group(1))}


def _url_canonique(contenu):
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', contenu, re.I)
    return html.unescape(m.group(1)) if m else None


# ----------------------------------------------------------------------------
# 1. OFFRE_EMPLOI (LinkedIn)
# ----------------------------------------------------------------------------
def _extraire_offre_emploi(contenu, sortie, vus):
    ajout = lambda c, v: _ajouter(sortie, vus, c, v)

    ld = {}
    for m in re.finditer(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', contenu, re.S | re.I):
        try:
            candidat = json.loads(m.group(1), strict=False)
        except json.JSONDecodeError:
            continue
        if isinstance(candidat, dict) and candidat.get("@type") == "JobPosting":
            ld = candidat
            break

    h1 = re.search(r'<h1[^>]*class="[^"]*topcard__title[^"]*"[^>]*>(.*?)</h1>', contenu, re.S | re.I)
    ajout("intitule_poste", _texte(h1.group(1), False) if h1 else _texte(ld.get("title"), False))

    org = ld.get("hiringOrganization") or {}
    lien_org = re.search(r'<a[^>]*class="[^"]*topcard__org-name-link[^"]*"[^>]*>(.*?)</a>', contenu, re.S | re.I)
    ajout("nom_entreprise", _texte(lien_org.group(1), False) if lien_org else _texte(org.get("name"), False))
    ajout("url_page_entreprise_linkedin", org.get("sameAs"))
    ajout("identifiant_offre_source", (ld.get("identifier") or {}).get("value"))

    url = _url_canonique(contenu)
    ajout("url_canonique", url)
    m_id = re.search(r"-(\d{6,})(?:\?|$)", url or "")
    ajout("id_offre_linkedin", m_id.group(1) if m_id else None)

    # Localisation : texte affiché + adresse structurée
    lieu = re.search(r'<span[^>]*class="[^"]*topcard__flavor--bullet[^"]*"[^>]*>([^<]+)</span>', contenu, re.I)
    ajout("localisation", _texte(lieu.group(1), False) if lieu else None)
    adr = (ld.get("jobLocation") or {}).get("address") or {}
    ajout("ville", adr.get("addressLocality"))
    ajout("region", adr.get("addressRegion"))
    ajout("code_postal", adr.get("postalCode"))
    ajout("pays", adr.get("addressCountry"))

    ajout("date_publication", ld.get("datePosted"))
    ajout("date_expiration", ld.get("validThrough"))
    anciennete = re.search(r'posted-time-ago__text[^>]*>(.*?)</span>', contenu, re.S | re.I)
    ajout("anciennete_publication_texte", _texte(anciennete.group(1), False) if anciennete else None)
    candidats = re.search(r'num-applicants__caption[^>]*>(.*?)</figcaption>', contenu, re.S | re.I)
    ajout("indicateur_candidats_texte", _texte(candidats.group(1), False) if candidats else None)

    ajout("type_contrat_schema_org", ld.get("employmentType"))
    ajout("secteur_activite_schema_org", _texte(ld.get("industry"), False))
    ajout("competences_declarees", _texte(ld.get("skills"), False))

    # Critères LinkedIn (niveau, type d'emploi, fonction, secteurs) : libellé -> valeurs multiples
    correspondance = {
        "niveau hiérarchique": "niveau_hierarchique",
        "type d’emploi": "type_emploi", "type d'emploi": "type_emploi",
        "fonction": "fonction",
        "secteurs": "secteurs",
    }
    for item in re.findall(r'<li[^>]*class="job-criteria__item"[^>]*>(.*?)</li>', contenu, re.S | re.I):
        lib = re.search(r'job-criteria__subheader[^>]*>(.*?)</h3>', item, re.S | re.I)
        vals = [_texte(v, False) for v in re.findall(r'job-criteria__text[^>]*>(.*?)</span>', item, re.S | re.I)]
        if lib:
            libelle = (_texte(lib.group(1), False) or "").lower()
            cle = correspondance.get(libelle, "critere_" + re.sub(r"\W+", "_", libelle).strip("_"))
            ajout(cle, SEPARATEUR_MULTI.join(v for v in vals if v))

    desc = re.search(r'<div[^>]*class="[^"]*description__text[^"]*"[^>]*>(.*?)</div>\s*</section>', contenu, re.S | re.I)
    ajout("description_offre", _texte(desc.group(1)) if desc else _texte(ld.get("description")))


# ----------------------------------------------------------------------------
# 2. INFO_SOCIETE (Glassdoor – page de présentation)
# ----------------------------------------------------------------------------
_LIBELLES_INFO_SOCIETE = {
    "site web": "site_web", "siège social": "siege_social", "taille": "taille_entreprise",
    "fondé en": "annee_creation", "type": "type_entreprise", "secteur": "secteur_activite",
    "revenu": "chiffre_affaires_tranche", "industrie": "industrie",
}


def _extraire_info_societe(contenu, sortie, vus):
    ajout = lambda c, v: _ajouter(sortie, vus, c, v)
    emp = _objet_json(contenu, "empDetails")
    notes = _objet_json(contenu, "eiRatingDetails")
    compteurs = _objet_json(contenu, "sectionCounts")
    gd = _gdglobals_employeur(contenu)

    titre = re.search(r"<title>\s*(?:Travailler chez\s+)?(.*?)\s*\|\s*Glassdoor", contenu, re.S | re.I)
    ajout("nom_entreprise", emp.get("employerName") or gd.get("name") or (_texte(titre.group(1), False) if titre else None))
    ajout("id_employeur_glassdoor", emp.get("employerId") or gd.get("id"))
    ajout("url_canonique", _url_canonique(contenu))

    # Bloc visible « Présentation » (libellés localisés)
    for lib, val in re.findall(r"<div class='infoEntity'><label>(.*?)</label><span class='value[^']*'>(.*?)</span></div>",
                               contenu, re.S):
        cle = _LIBELLES_INFO_SOCIETE.get((_texte(lib, False) or "").lower())
        if cle:
            ajout(cle, _texte(val, False))

    ajout("siege_social_detail", emp.get("hqCity"))
    ajout("annee_creation_json", emp.get("yearFounded"))
    ajout("statut_entreprise_code", emp.get("companyStatus"))
    ajout("type_entreprise_code", emp.get("companyType"))
    ajout("taille_entreprise_code", emp.get("employees"))
    ajout("chiffre_affaires_code", emp.get("annualRevenue"))
    ajout("secteur_glassdoor", gd.get("sector"))
    ajout("industrie_glassdoor", gd.get("industry"))
    ajout("taille_entreprise_gdglobals", gd.get("size"))
    ajout("description_entreprise", _texte(emp.get("companyDescription")))
    ajout("mission_entreprise", _texte(emp.get("companyMission")))

    # Notes agrégées
    ajout("note_globale", _decimal(notes.get("overallRating")))
    ajout("taux_recommandation", _decimal(notes.get("recommendToFriendRating")))
    ajout("nom_pdg", _texte(notes.get("ratedCeoName"), False))
    ajout("taux_approbation_pdg", _decimal(notes.get("ceoRating")))
    ajout("nb_notes_pdg", notes.get("ceoRatingsCount"))
    ajout("nb_avis_notes", notes.get("reviewCount"))

    # Volumétries par section
    for src, cle in [("reviewCount", "nb_avis_total"), ("interviewCount", "nb_entretiens"),
                     ("salaryCount", "nb_salaires"), ("jobCount", "nb_offres_emploi"),
                     ("benefitCount", "nb_avantages"), ("photoCount", "nb_photos"), ("awardCount", "nb_distinctions")]:
        ajout(cle, compteurs.get(src))

    # Distinction « Meilleurs Employeurs »
    m = re.search(r"Les distinctions Glassdoor</h3>(.{0,1500}?)<(?:hr|h2|h3)", contenu, re.S)
    if m:
        ajout("distinction_glassdoor", _texte(m.group(1), False))

    # Prix et distinctions (liste courte + liste complète dupliquées dans le HTML -> dédoublonnées)
    for nom, source, annee in re.findall(
            r"<div class='award'><span class='name'>(.*?)</span>,\s*<span class='awardSource'>(.*?)</span>,\s*"
            r"<span class='year'>(.*?)</span>", contenu, re.S):
        ajout("prix_distinction", " | ".join(filter(None, [_texte(nom, False), _texte(source, False), _texte(annee, False)])))

    # Notes par lieu
    for nom, note in re.findall(r"<li[^>]*><a href='/Lieu/[^']*'>(.*?)</a><span class='compactStars[^']*'>(.*?)</span></li>",
                                contenu, re.S):
        n = _decimal(_texte(re.sub(r"<i[^>]*></i>", "", note), False))
        ajout("note_lieu", "%s | %s" % (_texte(nom, False), n) if n else None)

    # Statistiques d'entretien (3 blocs : expérience, mode d'obtention, difficulté)
    for classe, prefixe in [("experience", "entretien_experience"), ("obtained", "entretien_obtention"),
                            ("difficulty", "entretien_difficulte")]:
        bloc = re.search(r'chartWrapper %s">(.*?)(?=<div class="cell chartWrapper|</div></div><!--|$)' % classe, contenu, re.S)
        if not bloc:
            continue
        nb = re.search(r"(\d[\d\s]*)\s*(?:Évaluations|Avis sur les entretiens)", _texte(bloc.group(1), False) or "")
        ajout(prefixe + "_nb_reponses", nb.group(1).replace(" ", "") if nb else None)
        for lib, pct in re.findall(r"<label class='[^']*pct'>(.*?)</label>.*?<span class='strong num[^']*'>(\d+)</span>",
                                   bloc.group(1), re.S):
            ajout(prefixe + "_pct", "%s | %s" % (_texte(lib, False), pct))
        moy = re.search(r'difficultyLabel[^>]*>\s*(\d[.,]\d)\s*</div>\s*([^<]*)', bloc.group(1))
        if moy:
            ajout(prefixe + "_moyenne", _decimal(moy.group(1)))
            ajout(prefixe + "_libelle", _texte(moy.group(2), False))


# ----------------------------------------------------------------------------
# 3. AVIS_SOCIETE (Glassdoor – liste d'avis, N pages possibles)
# ----------------------------------------------------------------------------
_SOUS_NOTES = {
    "équilibre travail/vie privée": "note_equilibre_vie_pro",
    "culture et valeurs": "note_culture_valeurs",
    "opportunités de carrière": "note_opportunites_carriere",
    "rémunération et avantages": "note_remuneration_avantages",
    "équipe dirigeante": "note_equipe_dirigeante",
}
_RUBRIQUES_TEXTE = {
    "avantages": "avantages",
    "inconvénients": "inconvenients",
    "conseils à la direction": "conseils_direction",
}
_RECOMMANDATIONS = {  # libellé Glassdoor -> (champ, valeur normalisée)
    "recommande": ("recommande_employeur", "Oui"),
    "ne recommande pas": ("recommande_employeur", "Non"),
    "point de vue positif": ("perspective_entreprise", "Positive"),
    "point de vue neutre": ("perspective_entreprise", "Neutre"),
    "point de vue négatif": ("perspective_entreprise", "Négative"),
    "approuve le pdg": ("avis_pdg", "Approuve"),
    "n'approuve pas le pdg": ("avis_pdg", "N'approuve pas"),
    "pas d'avis sur le pdg": ("avis_pdg", "Sans avis"),
}


def _date_iso(chaine):
    """'Thu Dec 12 2019 15:39:27 GMT-0800 (PST)' -> '2019-12-12T15:39:27-08:00'."""
    m = re.search(r"(\w{3} \d{1,2} \d{4} \d{2}:\d{2}:\d{2}) GMT([+-]\d{4})", chaine or "")
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1) + m.group(2), "%b %d %Y %H:%M:%S%z").isoformat()
    except ValueError:
        return None


def _extraire_avis_societe(contenu, sortie, vus):
    ajout = lambda c, v: _ajouter(sortie, vus, c, v)
    gd = _gdglobals_employeur(contenu)

    titre = re.search(r"<title>\s*Avis des salariés sur\s+(.*?)\s*\|", contenu, re.S | re.I)
    ajout("nom_entreprise", gd.get("name") or (_texte(titre.group(1), False) if titre else None))
    ajout("id_employeur_glassdoor", gd.get("id"))
    ajout("url_canonique", _url_canonique(contenu))

    # N° de page : déduit de l'URL canonique (_P2) ; absent = page 1. Évite de dépendre de infos_fichier.
    url = _url_canonique(contenu) or ""
    m_page = re.search(r"_P(\d+)\.htm", url)
    ajout("numero_page", m_page.group(1) if m_page else "1")

    # Attributs de l'entreprise (gdGlobals). NB : 'location' = siège de l'employeur, PAS la ville de l'auteur.
    ajout("secteur_glassdoor", gd.get("sector"))
    ajout("industrie_glassdoor", gd.get("industry"))
    ajout("taille_entreprise_gdglobals", gd.get("size"))
    ajout("siege_social", gd.get("location"))

    # Agrégats d'avis (état Apollo embarqué)
    for cle, regex in [("nb_pages_avis", r'"numberOfPages":(\d+)'), ("nb_avis_total", r'"allReviewsCount":(\d+)'),
                       ("nb_avis_notes", r'"ratedReviewsCount":(\d+)'),
                       ("date_dernier_avis", r'"lastReviewDateTime":"([^"]+)"')]:
        m = re.search(regex, contenu)
        ajout(cle, m.group(1) if m else None)
    m = re.search(r'ratings":(\{"overallRating":.*?"__typename":"EmployerRatings"\})', contenu)
    bloc_notes = m.group(1) if m else ""
    for cle, src in [("note_globale", "overallRating"), ("note_culture_valeurs_globale", "cultureAndValuesRating"),
                     ("note_opportunites_carriere_globale", "careerOpportunitiesRating"),
                     ("note_equilibre_vie_pro_globale", "workLifeBalanceRating"),
                     ("note_equipe_dirigeante_globale", "seniorManagementRating"),
                     ("note_remuneration_avantages_globale", "compensationAndBenefitsRating"),
                     ("taux_recommandation", "recommendToFriendRating"), ("taux_approbation_pdg", "ceoRating"),
                     ("taux_perspective_positive", "businessOutlookRating"), ("nb_notes_pdg", "ceoRatingsCount")]:
        mv = re.search(r'"%s":([0-9.]+)' % src, bloc_notes)
        ajout(cle, (mv.group(1) if cle.startswith("nb_") else _decimal(mv.group(1))) if mv else None)

    # Avis individuels : découpe par <li ... empReview ... id="empReview_N"> (la classe varie : « noBorder empReview cf »)
    flux = contenu[contenu.find('id="ReviewsFeed"'):] if 'id="ReviewsFeed"' in contenu else contenu
    motif = re.compile(r'<li class="[^"]*\bempReview\b[^"]*" id="empReview_(\d+)">(.*?)'
                       r'(?=<li class="[^"]*\bempReview\b|</ol>)', re.S)
    for id_avis, bloc in motif.findall(flux):
        p = "avis_%s__" % id_avis
        aj = lambda c, v, p=p: _ajouter(sortie, vus, p + c, v)

        m = re.search(r'<time[^>]*dateTime="([^"]+)"', bloc)
        aj("date_avis", _date_iso(m.group(1)) if m else None)
        m = re.search(r'class="reviewLink"[^>]*>(.*?)</a>', bloc, re.S)
        aj("titre", re.sub(r'^[«"\s]+|[»"\s]+$', "", _texte(m.group(1), False) or "") if m else None)
        m = re.search(r'<span class="value-title" title="([^"]+)"', bloc)
        aj("note_globale", _decimal(m.group(1)) if m else None)
        for lib, val in re.findall(r'<div class="minor">(.*?)</div><span class="gdBars[^"]*" title="([^"]+)"', bloc, re.S):
            cle = _SOUS_NOTES.get((_texte(lib, False) or "").lower())
            aj(cle or "note_" + re.sub(r"\W+", "_", (_texte(lib, False) or "").lower()).strip("_"), _decimal(val))

        m = re.search(r'class="authorJobTitle[^"]*"[^>]*>(.*?)</span>', bloc, re.S)
        auteur = _texte(m.group(1), False) if m else None
        if auteur:
            statut, _, poste = auteur.partition(" - ")
            aj("statut_auteur", statut)
            aj("poste_auteur", None if poste.strip().lower() == "employé anonyme" else poste)
        m = re.search(r'class="authorLocation"[^>]*>(.*?)</span>', bloc, re.S)
        aj("ville_auteur", _texte(m.group(1), False) if m else None)
        m = re.search(r'class="mainText[^"]*"[^>]*>(.*?)</p>', bloc, re.S)
        aj("contexte_emploi", _texte(m.group(1), False) if m else None)

        for lib in re.findall(r'<i class="sqLed[^"]*"></i><span>(.*?)</span>', bloc, re.S):
            cle_val = _RECOMMANDATIONS.get((_texte(lib, False) or "").lower())
            if cle_val:
                aj(*cle_val)
        m = re.search(r'helpfulCount[^>]*>(.*?)</div>', bloc, re.S)
        n = re.search(r"\((\d+)\)", _texte(m.group(1), False) or "") if m else None
        aj("nb_utile", n.group(1) if n else None)

        # Verbatims : deux gabarits HTML coexistent (P1 : <p class="strong">, P2 : <p class="strong mb-0 mt-xsm">)
        for lib, texte in re.findall(r'<p class="strong[^"]*">\s*(.*?)\s*</p>\s*<p[^>]*>(.*?)</p>', bloc, re.S):
            lib_n = (_texte(lib, False) or "").lower()
            aj(_RUBRIQUES_TEXTE.get(lib_n, "rubrique_" + re.sub(r"\W+", "_", lib_n).strip("_")), _texte(texte))


# ----------------------------------------------------------------------------
# Point d'entrée
# ----------------------------------------------------------------------------
_EXTRACTEURS = {
    "OFFRE_EMPLOI": _extraire_offre_emploi,
    "INFO_SOCIETE": _extraire_info_societe,
    "AVIS_SOCIETE": _extraire_avis_societe,
}


def extraire_metadonnees_descriptives(chemin_fichier_html, infos_fichier):
    """
    Extrait les métadonnées descriptives d'un fichier HTML selon infos_fichier["type_information"] :
    OFFRE_EMPLOI (LinkedIn), INFO_SOCIETE (Glassdoor – présentation), AVIS_SOCIETE (Glassdoor – avis).

    Retourne une liste de [clé, valeur] (valeurs en str, champs absents omis, couples dédoublonnés).
    Pour AVIS_SOCIETE, les champs d'un avis sont préfixés « avis_<id_glassdoor>__ » : l'identifiant natif
    rend la clé stable d'une extraction à l'autre, quelle que soit la page.
    """
    type_donnee = (infos_fichier or {}).get("type_information")
    metadonnees, vus = [], set()

    extracteur = _EXTRACTEURS.get(type_donnee)
    if extracteur is None:
        logger.warning("type_information inconnu ou absent : %r (%s)", type_donnee, chemin_fichier_html)
        return [["type_page", type_donnee]] if type_donnee else []

    try:
        with open(chemin_fichier_html, "r", encoding="utf-8", errors="replace") as fichier:
            contenu = fichier.read()
    except OSError as erreur:
        logger.error("Erreur de lecture de %s : %s", chemin_fichier_html, erreur)
        return []

    try:
        extracteur(contenu, metadonnees, vus)
    except Exception:  # un gabarit HTML inattendu ne doit pas interrompre tout le lot
        logger.exception("Échec d'extraction (%s) sur %s", type_donnee, chemin_fichier_html)

    _ajouter(metadonnees, vus, "type_page", type_donnee)
    return metadonnees