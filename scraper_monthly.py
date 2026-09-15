#!/usr/bin/env python3
"""
scraper_monthly.py — Récupère l'historique mensuel des VL depuis Boursorama.
Génère historical_monthly.json :
  {
    "last_updated": "YYYY-MM-DD",
    "data": {
      "FR0013287315": [
        {"date": "2024-06", "vl": 123.45},
        ...
        {"date": "2025-06", "vl": 130.00}
      ],
      ...
    }
  }

Stratégie :
  1. Visite la page du fonds pour établir les cookies de session Boursorama.
  2. Appelle GetTicksEOD avec Referer + X-Requested-With pour récupérer
     les cours journaliers sur 1825 jours (5 ans).
  3. Réduit à une valeur mensuelle (dernier cours du mois).
  4. Si l'API échoue pour un fonds, conserve les données déjà présentes dans
     historical_monthly.json (aucun écrasement des données existantes).

Déclenché via GitHub Actions une fois par mois (voir update_vl_monthly.yml).
"""

import json
import re
import time
import datetime
import gzip
import urllib.request
import urllib.error
import http.cookiejar

# ── Fonds à scraper (ISIN → Boursorama ID) ──────────────────────────────────
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
    ("FR0013367265", "0P0001F34F"),
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

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

HEADERS_HTML = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}

HEADERS_XHR = {
    "User-Agent": UA,
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "X-Requested-With": "XMLHttpRequest",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


def _decode_response(resp) -> str:
    """Lit et décompresse (gzip) si besoin le body de la réponse."""
    raw = resp.read()
    encoding = resp.headers.get("Content-Encoding", "")
    if encoding == "gzip":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="replace")


def fetch_historical(isin: str, bid: str) -> list | None:
    """
    Tente de récupérer l'historique de cours via GetTicksEOD.
    Retourne une liste triée de {"date": "YYYY-MM", "vl": float}
    ou None en cas d'échec.
    """
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cj),
        urllib.request.HTTPSHandler(),
    )

    base_url = f"https://www.boursorama.com/bourse/opcvm/cours/{bid}/"

    # ── Étape 1 : page du fonds → cookies de session ────────────────────────
    try:
        req = urllib.request.Request(base_url, headers=HEADERS_HTML)
        with opener.open(req, timeout=20) as resp:
            html = _decode_response(resp)
        n_cookies = sum(1 for _ in cj)
        print(f"      Page visitée ({len(html):,} chars, {n_cookies} cookie(s))")
    except Exception as e:
        print(f"      ✗ Page inaccessible : {e}")
        # On tente quand même l'API ci-dessous

    # ── Étape 2 : GetTicksEOD ───────────────────────────────────────────────
    api_url = (
        f"https://www.boursorama.com/bourse/action/graph/ws/GetTicksEOD"
        f"?symbol={bid}&length=1825&period=0&guid="
    )
    headers_xhr_with_ref = {**HEADERS_XHR, "Referer": base_url}

    try:
        req = urllib.request.Request(api_url, headers=headers_xhr_with_ref)
        with opener.open(req, timeout=20) as resp:
            raw = _decode_response(resp)

        print(f"      GetTicksEOD → {len(raw)} chars | aperçu : {raw[:120]!r}")

        if not raw.strip():
            print("      ✗ Réponse vide")
            return None

        data = json.loads(raw)
        return _parse_ticks(data)

    except json.JSONDecodeError as e:
        print(f"      ✗ JSON invalide : {e} | début : {raw[:200]!r}")
        return None
    except Exception as e:
        print(f"      ✗ GetTicksEOD erreur : {e}")
        return None


_EPOCH = datetime.date(1970, 1, 1)


def _parse_ticks(data) -> list | None:
    """
    Convertit la réponse GetTicksEOD de Boursorama en liste mensuelle.

    Formats connus :
      • {"d": {"QuoteTab": [{"d":20258,"o":630.633,"c":630.633,...}], ...}}
        → format réel Boursorama (dates = jours depuis 1970-01-01)
      • {"d": [{"d":"2024-06-03","o":27.0,"c":27.05,...}]}
      • [{"Date":"2024-06-03","Value":27.05}, ...]
      • {"DataSet": {"Series": [...]}}
    """
    series = None

    if isinstance(data, list):
        series = data
    elif isinstance(data, dict):
        if "d" in data:
            d_val = data["d"]
            if isinstance(d_val, list):
                series = d_val
            elif isinstance(d_val, dict) and "QuoteTab" in d_val:
                # Format réel Boursorama : {"d": {"QuoteTab": [...], ...}}
                series = d_val["QuoteTab"]
        if series is None and "DataSet" in data:
            try:
                series = data["DataSet"]["Series"][0]["Value"]
            except (KeyError, IndexError, TypeError):
                pass

    if not series:
        print(f"      ✗ Structure inconnue : {str(data)[:300]}")
        return None

    # Réduit à la dernière valeur par mois
    monthly: dict[str, float] = {}
    for pt in series:
        if not isinstance(pt, dict):
            continue

        # Champ date
        raw_date = (
            pt.get("d") if pt.get("d") is not None else None
        )
        if raw_date is None:
            raw_date = pt.get("Date") or pt.get("date") or pt.get("t") or pt.get("T")

        # Champ valeur (close prioritaire, sinon open)
        raw_val = (
            pt.get("c") or pt.get("close")
            or pt.get("Value") or pt.get("value")
            or pt.get("o") or pt.get("open")
        )

        if raw_date is None or raw_val is None:
            continue

        # Normalise la date
        try:
            if isinstance(raw_date, int):
                # Boursorama : jours depuis 1970-01-01
                d = _EPOCH + datetime.timedelta(days=raw_date)
            else:
                date_str = str(raw_date).split("T")[0]
                d = datetime.date.fromisoformat(date_str)
        except (ValueError, OverflowError):
            continue

        try:
            val = float(raw_val)
        except (ValueError, TypeError):
            continue

        if val <= 0:
            continue

        month_key = d.strftime("%Y-%m")
        monthly[month_key] = val  # écrase → garde le dernier du mois

    if not monthly:
        print("      ✗ Aucun point valide extrait")
        return None

    result = [{"date": k, "vl": v} for k, v in sorted(monthly.items())]

    # Filtre des ticks aberrants : un point isolé qui vaut plus de 5x (ou moins
    # d'1/5) de TOUS ses voisins est une erreur de cotation, pas un mouvement.
    # (vu sur FR0010106500 : 47 948,79 € en septembre 2021 au lieu de ~487 €)
    cleaned = []
    for i, pt in enumerate(result):
        neighbours = [result[j]["vl"] for j in (i - 1, i + 1) if 0 <= j < len(result)]
        if neighbours and all(pt["vl"] / nb > 5 or nb / pt["vl"] > 5 for nb in neighbours):
            print(f"      ⚠ point aberrant ignoré : {pt['date']} = {pt['vl']}")
            continue
        cleaned.append(pt)
    result = cleaned
    if not result:
        return None

    print(f"      ✓ {len(result)} mois extraits ({result[0]['date']} → {result[-1]['date']})")
    return result


def main():
    today = datetime.date.today().isoformat()
    out_path = "historical_monthly.json"

    # Charge les données existantes
    try:
        with open(out_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        print(f"✔ Données existantes chargées ({len(existing.get('data', {}))} fonds)")
    except FileNotFoundError:
        existing = {}
    except Exception as e:
        print(f"⚠ Erreur lecture {out_path} : {e}")
        existing = {}

    stored = existing.get("data", {})

    print(f"\nScraping historique mensuel — {today} — {len(FUNDS)} fonds")
    print("─" * 60)

    ok = 0
    ko = 0
    skipped = 0

    for i, (isin, bid) in enumerate(FUNDS, 1):
        print(f"[{i:2}/{len(FUNDS)}] {isin} ({bid})")
        new_data = fetch_historical(isin, bid)

        if new_data and len(new_data) >= 3:
            stored[isin] = new_data
            ok += 1
        else:
            # Conserve les données précédentes si elles existent
            if isin in stored:
                print(f"      ⚠ Échec scraping — données existantes conservées")
                skipped += 1
            else:
                ko += 1

        time.sleep(1.2)  # Pause polie

    print("─" * 60)
    print(f"✅ {ok} mis à jour  |  ↩ {skipped} conservés  |  ✗ {ko} manquants")

    output = {
        "last_updated": today,
        "data": stored,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Sauvegardé → {out_path}")
    print(f"   {sum(len(v) for v in stored.values())} points mensuels au total")

    # Un run qui ne rafraîchit rien doit être visible dans GitHub Actions.
    if ok == 0:
        print("❌ ÉCHEC : aucun fonds mis à jour — l'API Boursorama ne répond plus")
        return 1
    if ok < len(FUNDS) * 0.5:
        print(f"❌ ÉCHEC : seulement {ok}/{len(FUNDS)} fonds mis à jour")
        return 1
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
