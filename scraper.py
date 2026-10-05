#!/usr/bin/env python3
"""
scraper.py — Releve quotidien Boursorama pour tous les fonds du site.

Produit DEUX fichiers :
  • bourso_perf.json  { last_updated, source, data: { ISIN: {bid, vl, date,
                        eom:{ytd,m1,m6,a1,a3,a5,a10}, gli:{...}} } }
  • vl_overrides.json { ISIN: {vl, ytd, ytd_gli, date} }

Les deux conventions Boursorama sont conservees :
  eom = onglet « A LA FIN DE MOIS »  (arrete a la derniere VL du mois precedent)
  gli = onglet « GLISSANTES »        (arrete a la derniere VL connue)

Le script REND UN CODE DE SORTIE NON NUL si le releve est vide, trop partiel,
ou si la VL la plus recente est trop ancienne. Le workflow ne doit donc PAS
utiliser continue-on-error : un echec silencieux a fige le site deux mois.

Usage : python3 scraper.py
"""

import datetime
import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.request

# ── Liste des fonds a relever (ISIN, identifiant Boursorama) ────────────────
FUNDS = [
    ("FR0013287315", "0P0001CB5C"),
    ("FR0011461334", "0P0000ZL7R"),
    ("FR0011461326", "0P0000ZL7Q"),
    ("LU1585265066", "0P0001KJDD"),
    ("LU1694790202", "0P0001CH1A"),
    ("FR0010564328", "MP-460761"),
    ("FR0007497813", "MP-305918"),
    ("FR001400PKZ3", "0P0001UGT4"),
    ("FR001400PL02", "0P0001UGT3"),
    ("LU0512124107", "0P0000P3DN"),
    ("LU0284394235", "MP-420353"),
    ("FR0010135103", "MP-829413"),
    ("FR0010564336", "MP-495318"),
    ("FR0010057711", "MP-495316"),
    ("FR0011199314", "0P0000VYE0"),
    ("FR0011199322", "0P0000VYE1"),
    ("FR0010489542", "MP-514618"),
    ("FR0010510370", "0P0000JZWQ"),
    ("FR0007439666", "0P00005VUH"),
    ("FR001400UAZ4", "0P0001XK54"),
    ("FR0013087152", "0P00019OMO"),
    ("FR0013108982", "0P00019OMN"),
    ("FR0007076930", "MP-805274"),
    ("FR0000989899", "MP-802731"),
    ("FR0010547869", "MP-928594"),
    ("FR0014008EH4", "0P0001P8TC"),
    ("FR0011606268", "0P00011IDZ"),
    ("FR0014008EI2", "0P0001P8TA"),
    ("FR0014008EJ0", "0P0001P8TB"),
    ("FR0010321802", "MP-800952"),
    ("FR0000989915", "MP-800743"),
    ("FR0010298596", "MP-807288"),
    ("FR0013256930", "0P0001HI3U"),
    ("FR0013256922", "0P0001HI3T"),
    ("LU0870553020", "0P0000XTFD"),
    ("FR0010038257", "MP-806670"),
    ("FR0000930471", "MP-829178"),
    ("LU1490785091", "0P000195NQ"),
    ("LU0592698954", "0P0000TIYB"),
    ("FR0010148981", "MP-800128"),
    ("FR0010863688", "MP-664642"),
    ("FR0010564229", "MP-460332"),
    ("FR0007499470", "MP-958966"),
    ("FR0000974149", "MP-803486"),
    ("FR0000295230", "MP-829523"),
    ("LU2147879543", "0P0001L9PD"),
    ("FR0011175652", "0P00015XU2"),
    ("FR0011184191", "0P00015XU4"),
    ("FR0011253624", "0P00017T6E"),
    ("LU2661119755", "0P0001RR16"),
    ("FR0010547067", "MP-804104"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
}

# Garde-fous : un run qui ne rapporte rien doit ECHOUER bruyamment.
MIN_OK_RATIO = 0.60          # part minimale de fonds a recuperer
MAX_VL_AGE_DAYS = 8          # age maximal tolere pour la VL la plus recente

_TAG_RE   = re.compile(r"<[^>]+>")
_TABLE_RE = re.compile(r"<table\b.*?</table>", re.I | re.S)
_THEAD_RE = re.compile(r"<thead\b.*?</thead>", re.I | re.S)
_TR_RE    = re.compile(r"<tr\b.*?</tr>", re.I | re.S)
_CELL_RE  = re.compile(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", re.I | re.S)
_VL_PATTERNS = [
    re.compile(r"c-instrument--last[^>]*>\s*([\d\s  ,\.]+)", re.I),
    re.compile(r'data-ist-last="([\d\s  ,\.]+)"', re.I),
    re.compile(r'"currentPrice"\s*:\s*"?([\d\.,]+)', re.I),
    re.compile(r'"last"\s*:\s*"?([\d\.,]+)', re.I),
]
_DATE_RE  = re.compile(r"DERNIER COURS CONNU AU\s*(\d{2}[/.]\d{2}[/.]\d{4})", re.I)

# Colonnes du tableau « PERFORMANCES DU FONDS ». Les deux onglets n'ont pas le
# meme nombre de colonnes (les glissantes ajoutent « 1 SEMAINE ») : on lit
# toujours les en-tetes, jamais une position fixe.
_COL_KEYS = [
    ("ytd", re.compile(r"1ER\s*JANV")),
    ("m1",  re.compile(r"^1\s*MOIS$")),
    ("m6",  re.compile(r"^6\s*MOIS$")),
    ("a1",  re.compile(r"^1\s*AN$")),
    ("a3",  re.compile(r"^3\s*ANS$")),
    ("a5",  re.compile(r"^5\s*ANS$")),
    ("a10", re.compile(r"^10\s*ANS$")),
]
_EMPTY_PERF = {k: None for k, _ in _COL_KEYS}


def _text(fragment):
    """Retire les balises et normalise les espaces (insecables compris)."""
    t = _TAG_RE.sub(" ", fragment)
    t = t.replace(" ", " ").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", t).strip()


def _clean_number(s):
    """'1 234,56 %' -> 1234.56  |  '-' / 'ND' / '' -> None"""
    if s is None:
        return None
    s = (s.replace(" ", "").replace(" ", "")
          .replace("%", "").replace(",", ".").strip())
    if s in ("", "-", "–", "ND", "N/A"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _perf_from_pairs(pairs):
    """[(libelle de periode, valeur)] -> {ytd, m1, m6, a1, a3, a5, a10}"""
    perf = {}
    for key, rx in _COL_KEYS:
        perf[key] = next((_clean_number(v) for lab, v in pairs if rx.search(lab)), None)
    return perf


def parse_perf_tables(html):
    """Renvoie les jeux de performances trouves, dans l'ordre du HTML.

    Boursorama a servi deux mises en page du tableau « PERFORMANCES DU FONDS » :

    • VERTICALE (depuis le 04-05/10/2026) : en-tetes FONDS / CATEGORIE / RANG*,
      puis une ligne par periode dont la premiere cellule est le libelle
      (<th scope=row>1er JANV.</th>) suivie de la valeur du fonds.
    • HORIZONTALE (jusqu'au 03/10/2026) : en-tetes = periodes, puis une ligne
      dont la premiere cellule est FONDS.

    Les deux sont reconnues. Le tableau « fonds partenaires » (en-tete LIBELLE,
    sans colonne ni ligne FONDS) est ignore dans les deux cas.
    """
    out = []
    for tbl in _TABLE_RE.findall(html):
        if not re.search(r"1ER\s*JANV", _text(tbl).upper()):
            continue
        thead = _THEAD_RE.search(tbl)
        head_src = thead.group(0) if thead else tbl
        heads = [_text(h).upper() for h in _CELL_RE.findall(head_src)]
        body = tbl[thead.end():] if thead else tbl
        rows = [[_text(c) for c in _CELL_RE.findall(tr)] for tr in _TR_RE.findall(body)]

        # 1) Mise en page verticale : une colonne « FONDS » dans l'en-tete
        if "FONDS" in heads:
            col = heads.index("FONDS")
            pairs = [(r[0].upper(), r[col]) for r in rows if len(r) > col]
            perf = _perf_from_pairs(pairs)
            if any(v is not None for v in perf.values()):
                out.append(perf)
            continue

        # 2) Mise en page horizontale : une ligne « FONDS »
        fonds_row = next((r for r in rows if r and r[0].upper() == "FONDS"), None)
        if fonds_row and any("1ER JANV" in h for h in heads):
            out.append(_perf_from_pairs(list(zip(heads, fonds_row))))
    return out


def parse_page(html):
    """VL, date de VL et les deux jeux de performances. None si VL illisible."""
    vl = None
    for pat in _VL_PATTERNS:
        m = pat.search(html)
        if m:
            v = _clean_number(m.group(1))
            if v and v > 0:
                vl = v
                break
    if not vl:
        return None
    dm = _DATE_RE.search(_text(html))
    vl_date = None
    if dm:
        d, mo, y = re.split(r"[/.]", dm.group(1))
        vl_date = "%s-%s-%s" % (y, mo, d)
    tables = parse_perf_tables(html)
    return {
        "vl": vl,
        "date": vl_date,
        "eom": tables[0] if len(tables) >= 1 else dict(_EMPTY_PERF),
        "gli": tables[1] if len(tables) >= 2 else dict(_EMPTY_PERF),
    }


def fetch_fund(isin, bid):
    url = "https://www.boursorama.com/bourse/opcvm/cours/%s/" % bid
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            html = raw.decode("utf-8", errors="replace")
    except Exception as e:
        print("  x %s (%s) : erreur reseau - %s" % (isin, bid, e))
        return None
    data = parse_page(html)
    if not data:
        print("  x %s (%s) : VL introuvable dans la page" % (isin, bid))
        return None
    data["bid"] = bid
    return data


def main():
    today = datetime.date.today()
    results = {}
    ok = ko = 0

    print("Scraping Boursorama - %s - %d fonds" % (today.isoformat(), len(FUNDS)))
    print("-" * 68)
    for i, (isin, bid) in enumerate(FUNDS, 1):
        print("[%2d/%d] %s (%s) ..." % (i, len(FUNDS), isin, bid), end=" ", flush=True)
        data = fetch_fund(isin, bid)
        if data:
            results[isin] = data
            print("VL=%s au %s | 1er janv=%s" % (data["vl"], data["date"], data["eom"]["ytd"]))
            ok += 1
        else:
            ko += 1
        time.sleep(0.8)
    print("-" * 68)
    print("OK %d fonds | echecs %d" % (ok, ko))

    # Un echec silencieux a fige le site pendant deux mois : on echoue fort.
    if not results:
        print("ECHEC : aucun fonds recupere - fichiers inchanges")
        return 1
    if ok < len(FUNDS) * MIN_OK_RATIO:
        print("ECHEC : %d/%d fonds seulement (seuil %.0f%%) - fichiers inchanges"
              % (ok, len(FUNDS), MIN_OK_RATIO * 100))
        return 1
    dates = sorted(d["date"] for d in results.values() if d.get("date"))
    if not dates:
        print("ECHEC : aucune date de VL lisible - fichiers inchanges")
        return 1
    newest = datetime.date.fromisoformat(dates[-1])
    age = (today - newest).days
    print("VL la plus recente : %s (%d jour(s))" % (newest.isoformat(), age))
    if age > MAX_VL_AGE_DAYS:
        print("ECHEC : la VL la plus recente a %d jours (> %d) - la source ne se met plus a jour"
              % (age, MAX_VL_AGE_DAYS))
        return 1

    # Le tableau de performances est rendu cote serveur, mais si Boursorama
    # sert un jour une variante sans ce tableau, mieux vaut echouer que
    # publier six colonnes de tirets a la place des chiffres precedents.
    with_perf = sum(1 for d in results.values() if d["eom"].get("a1") is not None)
    print("Performances 1 an lues sur %d/%d fonds" % (with_perf, len(results)))
    if with_perf < len(results) * 0.5:
        print("ECHEC : tableau de performances absent ou illisible - fichiers inchanges")
        return 1

    with open("bourso_perf.json", "w", encoding="utf-8") as f:
        json.dump({
            "last_updated": today.isoformat(),
            "source": "Boursorama - tableau PERFORMANCES DU FONDS "
                      "(onglets a la fin de mois et glissantes)",
            "data": results,
        }, f, ensure_ascii=False, indent=1)
    print("Sauvegarde -> bourso_perf.json (%d fonds)" % len(results))

    overrides = {}
    for isin, d in results.items():
        overrides[isin] = {"vl": d["vl"], "ytd": d["eom"]["ytd"],
                           "ytd_gli": d["gli"]["ytd"], "date": d["date"]}
    with open("vl_overrides.json", "w", encoding="utf-8") as f:
        json.dump(overrides, f, ensure_ascii=False, indent=1)
    print("Sauvegarde -> vl_overrides.json (%d fonds)" % len(overrides))
    return 0


if __name__ == "__main__":
    sys.exit(main())
