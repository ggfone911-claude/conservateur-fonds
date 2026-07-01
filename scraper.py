#!/usr/bin/env python3
"""
scraper.py — Récupère les VL (valeurs liquidatives) sur Boursorama pour tous les fonds.
Génère vl_overrides.json avec { ISIN: { "vl": float, "ytd": float, "date": "YYYY-MM-DD" } }

Usage local  : python3 scraper.py
GitHub Action: python3 scraper.py  (même commande)
"""

import json
import re
import time
import datetime
import urllib.request
import urllib.error

# ── Liste des fonds à scraper ────────────────────────────────────────────────
# (ISIN, Boursorama ID)
FUNDS = [
    ("FR0013287315", "0P0001CB5C"),
    ("FR0011461334", "0P0000ZL7R"),
    ("FR0011461326", "0P0000ZL7Q"),
    ("LU1585265066", "0P0001KJDD"),
    ("LU1694790202", "0P0001CH1A"),
    ("FR0013505450", "0P0001KE62"),
    ("FR001400K2B5", "0P0001S8T9"),
    ("FR0010915314", "MP-805617"),
    ("FR0010564328", "MP-460761"),
    ("FR0007497813", "MP-305918"),
    ("LU1752460292", "0P0001EITS"),
    ("FR0013398294", "0P0001HS9U"),
    ("FR0013426657", "0P0001IFLQ"),
    ("FR0013398302", "0P0001HS9V"),
    ("FR0013398310", "0P0001HS9W"),
    ("FR001400PKZ3", "0P0001UGT4"),
    ("FR001400PL02", "0P0001UGT3"),
    ("LU0512124107", "0P0000P3DN"),
    ("FR0010135103", "MP-829413"),
    ("FR0010564336", "MP-495318"),
    ("FR0010057711", "MP-495316"),
    ("FR0007051040", "MP-804518"),
    ("FR0011199314", "0P0000VYE0"),
    ("FR0011199322", "0P0000VYE1"),
    ("FR0010489542", "MP-514618"),
    ("FR0010510370", "0P0000JZWQ"),
    ("FR0007439666", "0P00005VUH"),
    ("FR001400UAZ4", "0P0001XK54"),
    ("FR0013087152", "0P00019OMO"),
    ("FR0013108982", "0P00019OMN"),
    ("LU1694789451", "0P0001CH1D"),
    ("FR0007076930", "MP-805274"),
    ("FR001400U512", "0P0001UVBG"),
    ("FR0000989899", "MP-802731"),
    ("FR0010547869", "MP-928594"),
    ("FR0000978439", "MP-800357"),
    ("FR0010574434", "MP-828166"),
    ("FR0000427445", "MP-803445"),
    ("FR0010321810", "MP-805948"),
    ("FR0010106500", "MP-420630"),
    ("FR0000983819", "MP-805200"),
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
    ("FR0010149179", "MP-802605"),
    ("FR0010038257", "MP-806670"),
    ("FR0000930471", "MP-829178"),
    ("LU1490785091", "0P000195NQ"),
    ("LU0280435388", "MP-990541"),
    ("LU2809794220", "0P0001T914"),
    ("FR0000292278", "MP-829227"),
    ("FR0010649079", "MP-534378"),
    ("LU0115768185", "MP-356085"),
    ("LU1744646933", "0P0001DK5M"),
    ("LU1819480192", "0P0001DYQM"),
    ("LU0592698954", "0P0000TIYB"),
    ("LU0592699093", "0P0000TIYE"),
    ("LU2254337392", "0P0001LOB8"),
    ("FR0010148981", "MP-800128"),
    ("FR0010863688", "MP-664642"),
    ("LU1261432659", "0P00016FY4"),
    ("LU1902443420", "0P0001FLNU"),
    ("FR0010564229", "MP-460332"),
    ("FR0007499470", "MP-958966"),
    ("LU1103305709", "0P000172SH"),
    ("LU1244893696", "0P00016P7T"),
    ("LU1120766388", "0P00016ALF"),
    ("FR0000974149", "MP-803486"),
    ("LU0528228074", "0P0000VTJH"),
    ("LU1892829828", "0P0001EVSZ"),
    ("LU1653748860", "0P0001BOX5"),
    ("FR0012844140", "0P00016HZ8"),
    ("LU1160365091", "0P00016716"),
    ("LU0366534344", "MP-521217"),
    ("FR0000295230", "MP-829523"),
    ("LU0217139020", "MP-119337"),
    ("FR0010479931", "MP-806384"),
    ("FR0010097683", "MP-802713"),
    ("LU2147879543", "0P0001L9PD"),
    ("FR0011175652", "0P00015XU2"),
    ("FR0011184191", "0P00015XU4"),
    ("FR0010286013", "MP-805700"),
    ("FR0011253624", "0P00017T6E"),
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Patterns pour extraire le cours depuis la page Boursorama
_PRICE_PATTERNS = [
    # JSON structuré dans la page (le plus fiable)
    re.compile(r'"currentPrice"\s*:\s*([\d,\.]+)', re.IGNORECASE),
    re.compile(r'"last"\s*:\s*([\d,\.]+)', re.IGNORECASE),
    # Balise data-* ou attribut HTML
    re.compile(r'data-ist-last="([^"]+)"', re.IGNORECASE),
    re.compile(r'class="[^"]*c-instrument--last[^"]*"[^>]*>\s*([\d\s,\.]+)', re.IGNORECASE),
    # Regex générique sur le cours affiché
    re.compile(r'Cours\s*:\s*([\d\s,\.]+)', re.IGNORECASE),
    re.compile(r'Valeur\s+liquidative\s*[:\s]+([\d\s,\.]+)', re.IGNORECASE),
]

# Patterns pour le YTD
_YTD_PATTERNS = [
    # Table des performances Boursorama — ligne "FONDS", 1re colonne = "1er JANV."
    re.compile(r'FONDS\s*</th>\s*<td[^>]*>\s*([-+\d,\.]+)\s*%', re.IGNORECASE | re.DOTALL),
    # Anciens formats de secours
    re.compile(r'"ytdReturn"\s*:\s*"?([-\d\.]+)"?', re.IGNORECASE),
    re.compile(r'1\s+jan\.?\s*[-–]\s*auj\.?\s*[:\s]+([-\d,\.]+)\s*%', re.IGNORECASE),
    re.compile(r'Depuis\s+le\s+1er\s+jan\.?\s*[:\s]+([-\d,\.]+)\s*%', re.IGNORECASE),
]


def _clean_number(s: str) -> float | None:
    """Nettoie une chaîne numérique (espaces, virgules françaises) → float."""
    s = s.strip().replace('\xa0', '').replace(' ', '').replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return None


def fetch_vl(isin: str, bid: str) -> dict | None:
    """
    Récupère la VL et le YTD depuis Boursorama pour un fonds.
    Retourne {"vl": float, "ytd": float|None} ou None en cas d'échec.
    """
    url = f"https://www.boursorama.com/bourse/opcvm/cours/{bid}/"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  ✗ {isin} ({bid}): erreur réseau — {e}")
        return None

    # Extraction VL
    vl = None
    for pat in _PRICE_PATTERNS:
        m = pat.search(html)
        if m:
            v = _clean_number(m.group(1))
            if v and v > 0:
                vl = v
                break

    # Extraction YTD
    ytd = None
    for pat in _YTD_PATTERNS:
        m = pat.search(html)
        if m:
            v = _clean_number(m.group(1))
            if v is not None:
                ytd = v
                break

    if vl:
        return {"vl": vl, "ytd": ytd}
    else:
        print(f"  ✗ {isin} ({bid}): VL non trouvée dans la page")
        return None


def main():
    today = datetime.date.today().isoformat()
    results = {}
    ok = 0
    ko = 0

    print(f"Scraping Boursorama — {today} — {len(FUNDS)} fonds")
    print("─" * 60)

    for i, (isin, bid) in enumerate(FUNDS, 1):
        print(f"[{i:2}/{len(FUNDS)}] {isin} ({bid}) ...", end=" ", flush=True)
        data = fetch_vl(isin, bid)
        if data:
            results[isin] = {**data, "date": today}
            print(f"VL={data['vl']:.4f}  YTD={data['ytd']}%")
            ok += 1
        else:
            ko += 1
        # Pause polie pour ne pas surcharger Boursorama
        time.sleep(0.8)

    print("─" * 60)
    print(f"✅ {ok} fonds récupérés  |  ✗ {ko} échecs")

    # Sauvegarde
    out_path = "vl_overrides.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"💾 Sauvegardé → {out_path}")


if __name__ == "__main__":
    main()
