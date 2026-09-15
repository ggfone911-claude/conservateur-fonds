from __future__ import annotations
import json
import os
import datetime

# ─────────────────────────────────────────────────────────────────────────────
# VL overrides — chargées depuis vl_overrides.json si disponible (scraped live)
# ─────────────────────────────────────────────────────────────────────────────
_VL_OVERRIDES = {}
_VL_OVERRIDE_DATE = None
_vl_path = os.path.join(os.path.dirname(__file__), "vl_overrides.json")
if os.path.exists(_vl_path):
    try:
        with open(_vl_path, encoding="utf-8") as _f:
            _raw_overrides = json.load(_f)
        for _isin, _data in _raw_overrides.items():
            _VL_OVERRIDES[_isin] = _data
            _d = _data.get("date")
            if _d and (_VL_OVERRIDE_DATE is None or _d > _VL_OVERRIDE_DATE):
                _VL_OVERRIDE_DATE = _d
        print(f"📡 vl_overrides.json chargé — {len(_VL_OVERRIDES)} fonds (date: {_VL_OVERRIDE_DATE})")
    except Exception as _e:
        print(f"⚠️  Impossible de lire vl_overrides.json : {_e}")

# ─────────────────────────────────────────────────────────────────────────────
# Performances Boursorama — chargées depuis bourso_perf.json (scrapé quotidiennement)
# Format : { "last_updated": "...", "data": { ISIN: {"bid","vl","date",
#            "eom": {ytd,m1,m6,a1,a3,a5,a10}, "gli": {...}} } }
# Les deux conventions sont conservées : « à la fin de mois » et « glissantes ».
# ─────────────────────────────────────────────────────────────────────────────
_BP_DATA: dict = {}
_BP_LAST_UPDATED: str | None = None
_bp_path = os.path.join(os.path.dirname(__file__), "bourso_perf.json")
if os.path.exists(_bp_path):
    try:
        with open(_bp_path, encoding="utf-8") as _f:
            _bp_raw = json.load(_f)
        if isinstance(_bp_raw, dict) and "data" in _bp_raw:
            _BP_DATA = _bp_raw["data"]
            _BP_LAST_UPDATED = _bp_raw.get("last_updated")
            print(f"\U0001F4C8 bourso_perf.json chargé — {len(_BP_DATA)} fonds (màj: {_BP_LAST_UPDATED})")
        else:
            print("\u26A0\uFE0F  bourso_perf.json au format ancien (liste plate) — ignoré")
    except Exception as _e:
        print(f"\u26A0\uFE0F  Impossible de lire bourso_perf.json : {_e}")
else:
    print("\u26A0\uFE0F  bourso_perf.json absent — repli sur les performances figées dans le code")

# ─────────────────────────────────────────────────────────────────────────────
# Historical monthly VL — chargé depuis historical_monthly.json si disponible
# Format : { ISIN: [{"date":"YYYY-MM","vl":float}, ...] }
# ─────────────────────────────────────────────────────────────────────────────
_HIST_DATA: dict = {}
_HIST_LAST_UPDATED: str | None = None
_hist_path = os.path.join(os.path.dirname(__file__), "historical_monthly.json")
if os.path.exists(_hist_path):
    try:
        with open(_hist_path, encoding="utf-8") as _f:
            _hraw = json.load(_f)
        _HIST_DATA = _hraw.get("data", {})
        _HIST_LAST_UPDATED = _hraw.get("last_updated")
        _hist_pts = sum(len(v) for v in _HIST_DATA.values())
        print(f"📊 historical_monthly.json chargé — {len(_HIST_DATA)} fonds, {_hist_pts} points (màj: {_HIST_LAST_UPDATED})")
    except Exception as _e:
        print(f"⚠️  Impossible de lire historical_monthly.json : {_e}")

# ─────────────────────────────────────────────────────────────────────────────
# Helpers de formatage de date
# ─────────────────────────────────────────────────────────────────────────────
_MOIS_FR = ["janvier","février","mars","avril","mai","juin",
            "juillet","août","septembre","octobre","novembre","décembre"]

def _fmt_date_fr(iso: str | None) -> str:
    """'2026-06-24' → '24 juin 2026'  |  None → aujourd'hui"""
    if not iso:
        iso = datetime.date.today().isoformat()
    try:
        d = datetime.date.fromisoformat(iso)
        return f"{d.day} {_MOIS_FR[d.month - 1]} {d.year}"
    except ValueError:
        return iso

def _fmt_date_short(iso: str | None) -> str:
    """'2026-06-24' → '24/06/2026'  |  None → aujourd'hui"""
    if not iso:
        iso = datetime.date.today().isoformat()
    try:
        d = datetime.date.fromisoformat(iso)
        return f"{d.day:02d}/{d.month:02d}/{d.year}"
    except ValueError:
        return iso

# ─────────────────────────────────────────────────────────────────────────────
# Boursorama performance data collected 12/05/2026 (calculs au 12/06/2026)
# Format: { ISIN: { "bid": BoursoID, "ytd", "m1", "m6", "a1", "a3", "a5", "a10" } }
# ─────────────────────────────────────────────────────────────────────────────
def _p(s):
    parts = s.split(",")
    result = []
    for x in parts:
        x = x.strip()
        if x == "" or x == "None":
            result.append(None)
        else:
            try:
                result.append(float(x))
            except ValueError:
                result.append(None)
    while len(result) < 7:
        result.append(None)
    return result  # [ytd, m1, m6, a1, a3, a5, a10]

_RAW = [
    ("FR0013287315","0P0001CB5C","0.81,0.17,0.97,1.96,9.37,10.38,,"),
    ("FR0011461334","0P0000ZL7R","0.65,0.37,0.85,1.99,10.46,7.46,6.67,"),
    ("FR0011461326","0P0000ZL7Q","0.64,0.36,0.83,1.99,10.47,7.49,7.69,"),
    ("LU1585265066","0P0001KJDD","0.51,0.32,0.74,2.06,12.05,9.42,11.52,"),
    ("LU1694790202","0P0001CH1A","2.03,0.65,1.04,2.95,3.55,12.54,,"),
    ("FR0013505450","0P0001KE62","0.15,0.95,0.8,3.15,20.97,10.57,"),
    ("FR001400K2B5","0P0001S8T9","-0.25,1.19,-0.52,2.39,,,"),
    ("FR0010915314","MP-805617","0.52,0.93,0.37,1.85,12.97,-0.99,5.63,"),
    ("FR0010564328","MP-460761","0.47,0.86,0.3,1.39,12.18,4.44,9.71,"),
    ("FR0007497813","MP-305918","-0.39,0.96,-0.76,1.03,11.7,3.39,8.83"),
    ("LU1752460292","0P0001EITS","-0.23,1.05,-0.34,1.39,12.2,5.15,,"),
    ("FR0013398294","0P0001HS9U","0.87,0.34,0.98,2.27,16.45,9.94,,"),
    ("FR0013426657","0P0001IFLQ","0.68,0.24,0.93,2.37,13.38,11.31,,"),
    ("FR0013398302","0P0001HS9V","0.74,0.32,0.83,1.97,15.39,8.26,,"),
    ("FR0013398310","0P0001HS9W","0.42,0.56,0.61,2.13,15.5,8.08,"),
    ("FR001400PKZ3","0P0001UGT4","0.97,0.89,1.25,3.61,,,,"),
    ("FR001400PL02","0P0001UGT3","0.76,0.85,1.0,3.08,,,,"),
    ("LU0512124107","0P0000P3DN","10.83,3.92,11.44,13.87,32.52,16.55,23.67,"),
    ("FR0010135103","MP-829413","4.43,1.18,5.07,11.3,29.54,12.47,32.4,"),
    ("FR0010564336","MP-495318","2.58,1.16,3.32,9.16,22.4,13.49,27.18,"),
    ("FR0010057711","MP-495316","1.41,1.05,2.98,9.42,22.24,13.84,28.04"),
    ("LU0284394235","MP-420353","2.65,1.37,3.04,4.56,20.29,22.31,34.27"),
    ("FR0011199314","0P0000VYE0","1.92,0.56,1.63,7.14,23.99,7.8,31.18,"),
    ("FR0011199322","0P0000VYE1","1.36,1.39,2.19,8.71,21.02,10.85,28.39"),
    ("FR0010489542","MP-514618","2.6,2.0,2.77,4.91,21.15,13.35,26.91,"),
    ("FR0010510370","0P0000JZWQ","0.59,2.53,0.36,4.3,18.05,11.53,25.04"),
    ("FR0007439666","0P00005VUH","3.0,1.95,3.01,5.04,21.43,15.88,33.9,"),
    ("FR001400UAZ4","0P0001XK54",",2.8,,,,,"),
    ("FR0013087152","0P00019OMO","0.19,0.57,0.04,1.3,14.38,16.78,17.93,"),
    ("FR0013108982","0P00019OMN","-0.38,0.98,-0.84,1.22,14.46,16.99,18.63"),
    ("LU1694789451","0P0001CH1D","1.4,0.64,1.12,3.66,12.88,2.76,,"),
    ("FR0007076930","MP-805274","7.61,6.56,13.12,13.61,34.41,54.99,78.53"),
    ("FR001400U512","0P0001UVBG","5.89,3.83,8.32,10.48,,,,"),
    ("FR0000989899","MP-802731","3.73,3.76,7.25,6.87,7.1,2.86,54.54,"),
    ("FR0010547869","MP-928594","3.53,4.36,6.23,10.27,18.52,5.21,97.59,"),
    ("FR0000978439","MP-800357","4.2,6.37,7.56,9.59,13.52,4.3,54.91,"),
    ("FR0010574434","MP-828166","1.03,5.9,3.1,3.67,10.91,5.51,45.38,"),
    ("FR0000427445","MP-803445","-5.42,2.45,-1.02,10.9,-1.47,-15.22,40.17"),
    ("FR0010321810","MP-805948","10.15,3.75,12.06,8.88,16.08,-4.3,72.3,"),
    ("FR0010106500","MP-420630","12.76,9.04,16.28,15.92,38.27,18.52,114.13,"),
    ("FR0000983819","MP-805200","7.56,5.41,10.22,14.09,41.08,39.97,111.43,"),
    ("FR0014008EH4","0P0001P8TC","5.84,3.86,7.91,13.19,47.15,,,"),
    ("FR0011606268","0P00011IDZ","4.69,3.11,7.45,12.61,8.81,-12.49,63.1,"),
    ("FR0014008EI2","0P0001P8TA","5.26,3.75,7.24,12.27,44.54,,,"),
    ("FR0014008EJ0","0P0001P8TB","1.45,5.93,3.25,13.85,59.93,,"),
    ("FR0010321802","MP-800952","2.59,1.69,4.5,6.49,28.51,24.21,15.05,"),
    ("FR0000989915","MP-800743","2.63,0.74,0.66,-0.95,35.3,-15.27,6.8,"),
    ("FR0010298596","MP-807288","5.62,3.23,8.34,11.1,36.63,31.83,62.15,"),
    ("FR0013256930","0P0001HI3U","5.07,2.78,6.98,9.16,29.28,,,"),
    ("FR0013256922","0P0001HI3T","0.64,5.09,3.15,12.2,18.66,15.97,"),
    ("LU0870553020","0P0000XTFD","2.94,3.72,3.01,0.15,0.95,-0.27,66.62,"),
    ("FR0010149179","MP-802605","-0.49,0.13,-0.02,0.5,4.55,3.91,44.39,"),
    ("FR0010038257","MP-806670","-1.46,2.97,-0.96,-1.54,10.4,24.59,55.93,"),
    ("FR0000930471","MP-829178","-4.31,5.06,-4.94,0.03,4.45,24.16,55.44"),
    ("LU1490785091","0P000195NQ","1.25,4.63,2.34,-5.05,4.2,-7.4,,"),
    ("LU0280435388","MP-990541","38.08,10.64,36.2,67.47,78.55,90.93,273.47,"),
    ("LU2809794220","0P0001T914","20.14,22.94,16.46,80.73,,,"),
    ("FR0000292278","MP-829227","30.65,11.95,32.9,49.19,55.35,12.2,55.93,"),
    ("FR0010649079","MP-534378","21.28,4.55,23.28,27.49,40.59,46.24,124.13,"),
    ("LU0115768185","MP-356085","23.45,11.11,23.81,45.57,47.55,19.95,125.76,"),
    ("LU1744646933","0P0001DK5M","19.18,5.11,19.4,37.84,51.16,55.94,,"),
    ("LU1819480192","0P0001DYQM","27.3,16.7,24.37,47.31,122.88,60.75,,"),
    ("LU0592698954","0P0000TIYB","11.11,2.57,12.56,25.93,32.61,17.94,68.35,"),
    ("LU0592699093","0P0000TIYE","10.77,2.52,12.14,24.99,29.45,13.63,56.53,"),
    ("LU2254337392","0P0001LOB8","11.61,3.24,13.38,18.17,32.31,30.19,,"),
    ("FR0010148981","MP-800128","12.76,5.95,14.16,32.95,82.25,58.21,162.16,"),
    ("FR0010863688","MP-664642","7.79,2.43,8.53,3.09,22.06,10.79,92.69,"),
    ("LU1261432659","0P00016FY4","10.15,3.97,9.07,23.56,56.45,58.77,185.0,"),
    ("LU1902443420","0P0001FLNU","11.34,6.98,12.17,18.92,47.55,55.19,,"),
    ("FR0010564229","MP-460332","8.77,4.46,10.82,15.26,44.08,25.25,96.85,"),
    ("FR0007499470","MP-958966","3.35,7.7,3.41,19.3,41.81,39.12,95.15"),
    ("LU1103305709","0P000172SH","10.52,2.97,12.58,20.67,47.41,50.6,,"),
    ("LU1244893696","0P00016P7T","8.14,2.89,8.3,15.88,38.41,23.84,,"),
    ("LU1120766388","0P00016ALF","4.36,3.15,6.2,7.26,19.82,9.76,,"),
    ("FR0000974149","MP-803486","4.08,2.79,5.51,9.89,18.14,-2.69,39.87,"),
    ("LU0528228074","0P0000VTJH","5.71,3.97,6.15,17.21,31.78,18.09,106.19,"),
    ("LU1892829828","0P0001EVSZ","0.55,-3.95,-0.55,2.6,12.4,3.84,,"),
    ("LU1653748860","0P0001BOX5","-0.02,-1.58,-1.09,-10.17,-6.62,-12.86,,"),
    ("FR0013367265","0P0001F34F","-1.66,0.32,-2.0,7.37,29.05,18.64,,"),
    ("FR0012844140","0P00016HZ8","-2.73,2.31,-3.74,-1.27,4.44,1.71,38.63,"),
    ("LU1160365091","0P00016716","-9.49,0.16,-11.69,-12.59,-4.78,-3.6,,"),
    ("LU0366534344","MP-521217","-4.55,0.21,-6.93,-14.73,-16.78,-27.44,15.82,"),
    ("FR0000295230","MP-829523","-6.77,2.02,-6.63,-12.95,-9.19,1.64,78.33,"),
    ("LU0217139020","MP-119337","-4.59,5.35,-3.94,-1.99,8.06,13.08,121.82,"),
    ("FR0010479931","MP-806384","-13.11,-1.44,-15.45,-18.14,2.26,11.18,78.12,"),
    ("FR0010097683","MP-802713","2.86,2.98,2.82,10.28,20.34,16.39,33.82,"),
    ("LU2147879543","0P0001L9PD","1.52,1.69,1.91,4.99,19.22,13.45,30.14,"),
    ("FR0011175652","0P00015XU2","0.98,1.06,0.17,0.61,2.28,-21.26,-18.24,"),
    ("FR0011184191","0P00015XU4","-0.07,0.26,-1.18,-0.61,2.72,-21.18,-18.83"),
    ("FR0010286013","MP-805700","0.21,2.75,0.74,3.01,6.79,6.42,22.82,"),
    ("FR0011253624","0P00017T6E","-3.62,-0.22,-4.02,11.52,39.66,34.94,139.64,"),
]

BOURSO_DATA = {}
for isin, bid, perf_str in _RAW:
    p = _p(perf_str)
    BOURSO_DATA[isin] = {
        "bid": bid,
        "ytd_b": p[0],
        "m1":  p[1],
        "m6":  p[2],
        "a1":  p[3],
        "a3":  p[4],
        "a5":  p[5],
        "a10": p[6],
    }

def bourso_url(bid):
    return f"https://www.boursorama.com/bourse/opcvm/cours/{bid}/" if bid else None

# ─────────────────────────────────────────────────────────────────────────────
# Fund data — parts (D) supprimées + Tikehau 2027/2029 + Carmignac Tech Solutions
# ─────────────────────────────────────────────────────────────────────────────
CATEGORIES = [
  {"id":"monetaire","label":"Monétaire / Oblig. CT","color":"#3266ad","funds":[
    {"isin":"FR0013287315","name":"Palatine Monétaire Court Terme (R)","mgr":"Palatine AM","vl":642.78,"ytd":0.88,"srri":1},
    {"isin":"FR0011461326","name":"Conservateur Oblig. CT (C)","mgr":"Conservateur Gestion Valor","vl":112.46,"ytd":0.66,"srri":1},
    {"isin":"LU1585265066","name":"TF - Tikehau Short Duration (R)","mgr":"Tikehau IM","vl":133.20,"ytd":0.53,"srri":1},
  ]},
  {"id":"oblig_lt","label":"Obligataire LT","color":"#2a5298","funds":[
    {"isin":"LU1694790202","name":"DNCA INVEST Flex Inflation","mgr":"DNCA Finance","vl":117.11,"ytd":1.59,"srri":3},
    {"isin":"FR0010915314","name":"LF Obligations Carbon Impact C","mgr":"La Française AM Int.","vl":26.99,"ytd":0.45,"srri":3},
    {"isin":"FR0010564328","name":"Conservateur Oblig. MT (C)","mgr":"Conservateur Gestion Valor","vl":301.51,"ytd":0.28,"srri":3},
    {"isin":"LU1752460292","name":"Oddo Sustainable Credit Optn CR","mgr":"Oddo AM","vl":114.46,"ytd":-0.39,"srri":3},
    {"isin":"FR0013505450","name":"Tikehau 2027 (R-Acc-EUR)","mgr":"Tikehau IM","vl":123.44,"ytd":0.79,"srri":2},
    {"isin":"FR001400K2B5","name":"Tikehau 2029 (R-Acc-EUR)","mgr":"Tikehau IM","vl":115.10,"ytd":0.76,"srri":2},
  ]},
  {"id":"oblig_horizon","label":"Oblig. à Horizon","color":"#1a3a6b","funds":[
    {"isin":"FR0013398294","name":"Conservateur Horizon 2027 (I)","mgr":"Conservateur Gestion Valor","vl":11896.04,"ytd":0.93,"srri":2},
    {"isin":"FR0013426657","name":"Oddo BHF Global Target 2026 (CR)","mgr":"Oddo AM","vl":115.07,"ytd":0.77,"srri":2},
    {"isin":"FR0013398302","name":"Conservateur Horizon 2027 (C)","mgr":"Conservateur Gestion Valor","vl":1163.78,"ytd":0.79,"srri":2},
    {"isin":"FR001400PKZ3","name":"Conservateur Horizon 2031 (I)","mgr":"Conservateur Gestion Valor","vl":10628.80,"ytd":1.01,"srri":2},
    {"isin":"FR001400PL02","name":"Conservateur Horizon 2031 (C)","mgr":"Conservateur Gestion Valor","vl":1058.99,"ytd":0.78,"srri":2},
  ]},
  {"id":"mixtes_oblig","label":"Mixtes Obligataires","color":"#0d6efd","funds":[
    {"isin":"LU0512124107","name":"DNCA Invest - Convertibles (B)","mgr":"DNCA Finance","vl":191.32,"ytd":10.12,"srri":4},
    {"isin":"FR0010135103","name":"Carmignac Patrimoine (A)","mgr":"Carmignac Gestion","vl":819.36,"ytd":3.82,"srri":4},
    {"isin":"FR0010564336","name":"Conservateur Diversifié (C)","mgr":"Conservateur Gestion Valor","vl":212.52,"ytd":1.28,"srri":4},
    {"isin":"LU0284394235","name":"DNCA Invest - Eurose (A)","mgr":"DNCA Finance","vl":199.00,"ytd":2.65,"srri":3},
    {"isin":"FR0011199314","name":"Conservateur Immo-Or (C)","mgr":"Conservateur Gestion Valor","vl":123.86,"ytd":-1.10,"srri":4},
    {"isin":"FR0010489542","name":"Conservateur Diversifié Réactif (C)","mgr":"Conservateur Gestion Valor","vl":190.52,"ytd":2.75,"srri":4},
    {"isin":"FR0007439666","name":"Congrégation Investissement (C)","mgr":"Conservateur Gestion Valor","vl":10560.83,"ytd":3.50,"srri":4},
    {"isin":"FR001400UAZ4","name":"Congrégation Investissement (R)","mgr":"Conservateur Gestion Valor","vl":1050.39,"ytd":0.00,"srri":4},
    {"isin":"FR0013087152","name":"Conservateur Rendement Flexible (C)","mgr":"Conservateur Gestion Valor","vl":119.29,"ytd":0.12,"srri":4},
    {"isin":"LU1694789451","name":"DNCA Invest Alpha Bonds (A)","mgr":"DNCA Finance","vl":131.09,"ytd":None,"srri":3},
  ]},
  {"id":"actions_fr","label":"Actions Françaises","color":"#198754","funds":[
    {"isin":"FR0007076930","name":"Centifolia (C)","mgr":"DNCA Finance","vl":130.91,"ytd":9.46,"srri":6},
    {"isin":"FR001400U512","name":"Conservateur Investissement Proximité (C)","mgr":"Conservateur Gestion Valor","vl":111.50,"ytd":6.64,"srri":6},
    {"isin":"FR0000989899","name":"Oddo BHF Avenir (CR)","mgr":"Oddo AM","vl":4610.04,"ytd":0.83,"srri":6},
    {"isin":"FR0010547869","name":"SEXTANT PME-A","mgr":"Amiral Gestion","vl":311.29,"ytd":1.89,"srri":6},
    {"isin":"FR0000978439","name":"Palatine France Small Cap (I)","mgr":"Palatine AM","vl":870.44,"ytd":-0.12,"srri":6},
    {"isin":"FR0010574434","name":"Oddo BHF Génération (CR)","mgr":"Oddo AM","vl":1050.68,"ytd":0.25,"srri":6},
    {"isin":"FRBCP1260215","name":"LC Athena action Stellantis 11/2030","mgr":"","vl":776.40,"ytd":-20.63,"srri":7},
  ]},
  {"id":"actions_eu","label":"Actions Européennes","color":"#20c997","funds":[
    {"isin":"FR0010321810","name":"Echiquier Agenor Mid Cap Europe (A)","mgr":"Financière de l'Echiquier","vl":473.20,"ytd":10.01,"srri":6},
    {"isin":"FR0010106500","name":"Echiquier Excelsior A","mgr":"Financière de l'Echiquier","vl":550.10,"ytd":10.55,"srri":6},
    {"isin":"FR0000983819","name":"OFI Croiss Durable & Solidaire C","mgr":"OFI AM","vl":318.41,"ytd":9.80,"srri":6},
    {"isin":"FR0014008EH4","name":"Conservateur Actions Euro (I)","mgr":"Conservateur Gestion Valor","vl":171412.91,"ytd":7.91,"srri":6},
    {"isin":"FR0011606268","name":"Oddo BHF Active SMALL CAP (CR)","mgr":"Oddo AM","vl":240.73,"ytd":3.01,"srri":6},
    {"isin":"FR0014008EI2","name":"Conservateur Actions Euro (C)","mgr":"Conservateur Gestion Valor","vl":162.03,"ytd":7.25,"srri":6},
    {"isin":"FR0010321802","name":"Echiquier Agressor (A)","mgr":"Financière de l'Echiquier","vl":2145.00,"ytd":3.79,"srri":6},
    {"isin":"FR0000989915","name":"Oddo BHF Immobilier (CR)","mgr":"Oddo AM","vl":1699.03,"ytd":-0.03,"srri":5},
    {"isin":"FR0010298596","name":"Moneta Multi Caps (C)","mgr":"Moneta AM","vl":479.64,"ytd":5.80,"srri":6},
    {"isin":"FR0013256930","name":"Conservateur Actions Flexibles (C)","mgr":"Conservateur Gestion Valor","vl":138.76,"ytd":5.13,"srri":5},
    {"isin":"LU0870553020","name":"DNCA Invest SRI Europe Growth (A)","mgr":"DNCA Finance","vl":286.34,"ytd":3.67,"srri":6},
    {"isin":"FR0010149179","name":"Carmignac Absolute Return Europe (A)","mgr":"Carmignac Gestion","vl":419.89,"ytd":-0.02,"srri":5},
    {"isin":"FR0010038257","name":"Conservateur Emploi Durable (C)","mgr":"Palatine AM","vl":285.15,"ytd":-1.51,"srri":6},
    {"isin":"LU1490785091","name":"DNCA Invest SRI Norden Europe A","mgr":"DNCA Finance","vl":206.41,"ytd":1.11,"srri":6},
  ]},
  {"id":"actions_int","label":"Actions Internationales","color":"#fd7e14","funds":[
    {"isin":"LU0280435388","name":"Pictet - Clean Energy Transition (P)","mgr":"Pictet AM Europe","vl":242.71,"ytd":37.29,"srri":7},
    {"isin":"FR0000292278","name":"Magellan (C)","mgr":"Comgest AM","vl":27.92,"ytd":24.37,"srri":6},
    {"isin":"FR0010649079","name":"Palatine Planète (R)","mgr":"Palatine AM","vl":57.82,"ytd":23.52,"srri":6},
    {"isin":"LU0115768185","name":"FF - Sustainable Asia Equity Fund (E)","mgr":"Fidelity AM","vl":92.35,"ytd":25.08,"srri":6},
    {"isin":"LU1744646933","name":"LF IP Carbon Impact Global R","mgr":"La Française AM Int.","vl":208.40,"ytd":15.25,"srri":6},
    {"isin":"LU1819480192","name":"Echiquier Artificial Intelligence (B)","mgr":"Financière de l'Echiquier","vl":300.64,"ytd":24.11,"srri":7},
    {"isin":"LU0592698954","name":"Carmignac Portf. Emerging Patrimoine (A)","mgr":"Carmignac Gestion","vl":176.04,"ytd":11.30,"srri":6},
    {"isin":"LU0592699093","name":"Carmignac Portf. Emerging Patrimoine (E)","mgr":"Carmignac Gestion","vl":158.10,"ytd":10.92,"srri":6},
    {"isin":"LU2254337392","name":"DNCA INVEST - Beyond Climate (A)","mgr":"DNCA Finance","vl":133.80,"ytd":12.77,"srri":6},
    {"isin":"FR0010148981","name":"Carmignac Investissement (A)","mgr":"Carmignac Gestion","vl":2829.86,"ytd":10.55,"srri":6},
    {"isin":"FR0010863688","name":"Echiquier Positive Impact (A)","mgr":"Financière de l'Echiquier","vl":303.69,"ytd":7.81,"srri":6},
    {"isin":"LU1261432659","name":"FF - World Fund (A)","mgr":"Fidelity AM","vl":26.70,"ytd":10.19,"srri":6},
    {"isin":"LU1902443420","name":"CPR Invest Climate Action (A)","mgr":"CPR AM","vl":212.11,"ytd":10.70,"srri":6},
    {"isin":"FR0010564229","name":"Conservateur Actions Monde (C)","mgr":"Conservateur Gestion Valor","vl":552.20,"ytd":8.13,"srri":6},
    {"isin":"LU1103305709","name":"EdR Fund - Us Value (R)","mgr":"Edmond de Rothschild AM","vl":463.71,"ytd":10.55,"srri":6},
    {"isin":"LU1244893696","name":"EdR Fund - Big Data (A)","mgr":"Edmond de Rothschild AM","vl":359.98,"ytd":8.12,"srri":6},
    {"isin":"LU1120766388","name":"Candriam Equities L Biotechnology (C)","mgr":"Candriam Lux","vl":295.77,"ytd":4.44,"srri":7},
    {"isin":"FR0000974149","name":"Oddo BHF Avenir Europe (CR)","mgr":"Oddo AM","vl":711.53,"ytd":2.74,"srri":6},
    {"isin":"LU0528228074","name":"FF - Sustainable Demographics Fund (A)","mgr":"Fidelity AM","vl":32.61,"ytd":3.52,"srri":6},
    {"isin":"LU1892829828","name":"FF - Sustainable Water & Waste Fund (A)","mgr":"Fidelity AM","vl":14.78,"ytd":1.86,"srri":6},
    {"isin":"LU1653748860","name":"CPR Invest - Food For Generations (A)","mgr":"CPR AM","vl":121.33,"ytd":2.04,"srri":6},
    {"isin":"FR0012844140","name":"CPR Global Silver Age (E)","mgr":"CPR AM","vl":129.67,"ytd":-2.08,"srri":6},
    {"isin":"LU1160365091","name":"EdR Fund - China (A)","mgr":"Edmond de Rothschild AM","vl":303.84,"ytd":-10.26,"srri":7},
    {"isin":"LU0366534344","name":"Pictet - Nutrition (P)","mgr":"Pictet AM Europe","vl":206.20,"ytd":-2.49,"srri":6},
    {"isin":"FR0000295230","name":"Comgest Renaissance Europe (C)","mgr":"Comgest AM","vl":230.29,"ytd":-4.87,"srri":6},
    {"isin":"LU0217139020","name":"Pictet - Premium Brands (P)","mgr":"Pictet AM Europe","vl":281.75,"ytd":-2.99,"srri":5},
    {"isin":"FR0010479931","name":"EdR India (A)","mgr":"Edmond de Rothschild AM","vl":467.30,"ytd":-12.27,"srri":7},
  ]},
  {"id":"flexibles","label":"Flexibles","color":"#6f42c1","funds":[
    {"isin":"FR0010097683","name":"CPR Croissance Réactive (P)","mgr":"CPR AM","vl":577.70,"ytd":1.16,"srri":4},
    {"isin":"LU2147879543","name":"Tikehau International Cross Assets (R)","mgr":"Tikehau IM","vl":757.12,"ytd":0.79,"srri":4},
    {"isin":"FR0011175652","name":"Conservateur Reverso (C)","mgr":"Conservateur Gestion Valor","vl":77.25,"ytd":0.56,"srri":4},
    {"isin":"FR0010286013","name":"Sextant Grand Large (A)","mgr":"Amiral Gestion","vl":488.90,"ytd":-1.39,"srri":4},
    {"isin":"FR0011253624","name":"R-co Valor (C)","mgr":"Rothschild et Cie Gestion","vl":3817.19,"ytd":-4.94,"srri":5},
  ]},
]

# ── Indicateurs de risque depuis l'historique mensuel ────────────────────────
def _risk_metrics(isin):
    """Volatilité annualisée (%) et max drawdown (%) sur l'historique mensuel."""
    pts = _HIST_DATA.get(isin)
    if not pts:
        return None, None
    vls = [p["vl"] for p in sorted(pts, key=lambda x: x["date"]) if p.get("vl")]
    if len(vls) < 4:
        return None, None
    rets = [vls[i] / vls[i-1] - 1 for i in range(1, len(vls))]
    vol = None
    if len(rets) >= 5:
        m = sum(rets) / len(rets)
        var = sum((r - m) ** 2 for r in rets) / (len(rets) - 1)
        vol = round((var ** 0.5) * (12 ** 0.5) * 100, 2)
    peak, mdd = vls[0], 0.0
    for v in vls:
        if v > peak:
            peak = v
        dd = (v / peak - 1) * 100
        if dd < mdd:
            mdd = dd
    return vol, round(mdd, 2)

# Merge Boursorama data into each fund
for cat in CATEGORIES:
    for f in cat["funds"]:
        b  = BOURSO_DATA.get(f["isin"])
        bp = _BP_DATA.get(f["isin"])
        f["bid"] = (bp or {}).get("bid") or (b or {}).get("bid")
        _KEYS = ("ytd", "m1", "m6", "a1", "a3", "a5")
        if bp:
            # Source vivante : les deux conventions Boursorama
            f["perf_eom"] = {k: bp.get("eom", {}).get(k) for k in _KEYS}
            f["perf_gli"] = {k: bp.get("gli", {}).get(k) for k in _KEYS}
            if bp.get("date"):
                f["vl_date"] = bp["date"]
        elif b:
            # Repli : valeurs figées dans le code (une seule convention connue)
            _fallback = {"ytd": b.get("ytd_b"), "m1": b["m1"], "m6": b["m6"],
                         "a1": b["a1"], "a3": b["a3"], "a5": b["a5"]}
            f["perf_eom"] = dict(_fallback)
            f["perf_gli"] = dict(_fallback)
        else:
            f["perf_eom"] = {k: None for k in _KEYS}
            f["perf_gli"] = {k: None for k in _KEYS}
        # Jeu actif rendu côté serveur (bascule côté client ensuite)
        for _k in ("m1", "m6", "a1", "a3", "a5"):
            f[_k] = f["perf_eom"][_k]
        if f["perf_eom"].get("ytd") is not None:
            f["ytd"] = f["perf_eom"]["ytd"]
        # Écrase VL (et éventuellement YTD) avec les données scrapées en live
        ov = _VL_OVERRIDES.get(f["isin"])
        if ov:
            if ov.get("vl") and ov["vl"] > 0:
                f["vl"] = round(ov["vl"], 4)
            if ov.get("ytd") is not None:
                f["ytd"] = ov["ytd"]
        # Indicateurs de risque (volatilité annualisée + max drawdown 12 mois)
        f["vol"], f["mdd"] = _risk_metrics(f["isin"])

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def fmt(v, suffix="%", decimals=2):
    if v is None: return '<span class="na">—</span>'
    c = "pos" if v > 0 else ("neg" if v < 0 else "neu")
    return f'<span class="{c}">{v:+.{decimals}f}{suffix}</span>'

def fmt_vl(v):
    if v is None: return "—"
    if v >= 1000: return f"{v:,.2f} €".replace(",", " ")
    return f"{v:.2f} €"

def perf_td(f, key):
    """Cellule de performance portant les deux conventions Boursorama.
    data-e = à la fin de mois, data-g = glissantes ; le jeu affiché est
    reconstruit côté client par setPerfMode()."""
    e = (f.get("perf_eom") or {}).get(key)
    g = (f.get("perf_gli") or {}).get(key)
    if key == "ytd" and e is None:
        e = f.get("ytd")
    if key == "ytd" and g is None:
        g = f.get("ytd")
    av = e if e is not None else -9999
    de = "" if e is None else f"{e}"
    dg = "" if g is None else f"{g}"
    return (f'<td class="perf-cell" style="text-align:right" data-k="{key}" '
            f'data-e="{de}" data-g="{dg}" data-val="{av}">{fmt(e)}</td>')

def medal(rank):
    m = ["🥇","🥈","🥉"]
    return m[rank] if rank < 3 else f"{rank+1}"

# Palette de couleurs pour les lignes du graphique multi-périodes
LINE_PALETTE = [
    "#e6194b","#3cb44b","#4363d8","#f58231","#911eb4",
    "#42d4f4","#f032e6","#bfef45","#469990","#dcbeff",
    "#9A6324","#800000","#aaffc3","#808000","#ffd8b1",
    "#000075","#a9a9a9","#e6beff","#ffe119","#4169e1",
    "#c0392b","#16a085","#8e44ad","#f39c12","#2ecc71",
    "#1abc9c","#d35400","#7f8c8d","#2980b9","#27ae60",
]

# ─────────────────────────────────────────────────────────────────────────────
# HTML generation
# ─────────────────────────────────────────────────────────────────────────────
html_parts = []
html_parts.append("""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Le Conservateur - Analyse des Fonds</title>
<!-- Chart.js embarqué — fichier autonome, pas de CDN -->
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f4f8;color:#1a202c;font-size:14px}
header{background:linear-gradient(135deg,#1a3a6b,#3266ad);color:#fff;padding:24px 32px;box-shadow:0 2px 8px rgba(0,0,0,.2)}
header h1{font-size:22px;font-weight:700;letter-spacing:.3px}
header p{font-size:13px;opacity:.8;margin-top:4px}
.stats-bar{display:flex;gap:16px;padding:16px 32px;background:#fff;border-bottom:1px solid #e2e8f0;flex-wrap:wrap}
.stat{text-align:center;padding:8px 16px;background:#f7fafc;border-radius:8px;border:1px solid #e2e8f0}
.stat .val{font-size:20px;font-weight:700;color:#3266ad}
.stat .lbl{font-size:11px;color:#718096;margin-top:2px}
.tabs{display:flex;gap:0;padding:0 16px;background:#fff;border-bottom:2px solid #e2e8f0;overflow-x:auto;white-space:nowrap;scrollbar-width:thin}
.tab{padding:10px 12px;cursor:pointer;border-bottom:3px solid transparent;font-size:12px;font-weight:500;color:#4a5568;transition:all .2s;flex-shrink:0}
.tab:hover{color:#3266ad;background:#f7fafc}
.tab.active{color:#3266ad;border-bottom-color:#3266ad;font-weight:600}
.section{display:none;padding:24px 32px;overflow:hidden}
.section.active{display:block}
.cat-header{display:flex;align-items:center;gap:12px;margin-bottom:20px}
.cat-header h2{font-size:18px;font-weight:700;color:#1a202c}
.cat-header .badge{background:#e8f0fe;color:#3266ad;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600}
.top5{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-bottom:24px}
.fund-card{background:#fff;border-radius:10px;padding:14px;box-shadow:0 1px 4px rgba(0,0,0,.08);border-left:4px solid #3266ad;transition:transform .15s}
.fund-card:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.12)}
.fund-card .rank{font-size:18px;margin-bottom:6px}
.fund-card .fname{font-weight:600;font-size:13px;color:#1a202c;line-height:1.3;margin-bottom:4px}
.fund-card .fmgr{font-size:11px;color:#718096;margin-bottom:8px}
.fund-card .fytd{font-size:22px;font-weight:700}
.fund-card .fisin{font-size:10px;color:#a0aec0;margin-top:4px}
.chart-wrap{background:#fff;border-radius:10px;padding:16px;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08);overflow:hidden;min-width:0}
.chart-wrap canvas{max-width:100%;display:block}
.chart-wrap h3{font-size:14px;font-weight:600;color:#4a5568;margin-bottom:4px}
.chart-wrap .chart-sub{font-size:11px;color:#a0aec0;margin-bottom:12px}
.charts-row{display:grid;grid-template-columns:1fr;gap:16px;margin-bottom:24px}
.table-wrap{background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:24px;overflow-x:auto}
table{width:100%;border-collapse:collapse}
thead tr{background:#f7fafc}
th{padding:10px 12px;text-align:left;font-size:12px;font-weight:600;color:#4a5568;cursor:pointer;white-space:nowrap;user-select:none;border-bottom:1px solid #e2e8f0}
th:hover{background:#edf2f7;color:#1a202c}
th.sorted-asc::after{content:" ↑"}
th.sorted-desc::after{content:" ↓"}
td{padding:9px 12px;border-bottom:1px solid #f0f4f8;vertical-align:middle;white-space:nowrap}
tr:hover td{background:#f7fafc}
tr.top3 td:first-child{font-weight:700}
.pos{color:#22863a;font-weight:600}
.neg{color:#c0392b;font-weight:600}
.neu{color:#718096}
.na{color:#cbd5e0}
.fund-name{font-weight:500;white-space:normal;min-width:180px}
.isin-cell{font-family:monospace;font-size:11px;color:#a0aec0}
.bourso-link{font-size:12px;color:#3266ad;text-decoration:none;display:inline-flex;align-items:center;gap:3px}
.bourso-link:hover{text-decoration:underline}
.fund-name-link{color:inherit;text-decoration:none;border-bottom:1px dotted #3266ad}
.fund-name-link:hover{color:#3266ad;border-bottom-color:#3266ad}
.source-note{font-size:11px;color:#a0aec0;margin-bottom:8px}
.filter-bar{display:flex;gap:10px;padding:12px 32px;background:#fff;border-bottom:2px solid #e2e8f0;align-items:center;flex-wrap:wrap}
.view-tabs{display:flex;gap:6px;align-items:center;margin-left:auto}
.view-tab{padding:5px 14px;border:1.5px solid #e2e8f0;border-radius:20px;background:#fff;cursor:pointer;font-size:12px;font-weight:600;color:#4a5568;transition:all .15s;white-space:nowrap}
.view-tab:hover:not(.active){border-color:#3266ad;color:#3266ad}
.view-tab.active{background:#3266ad;color:#fff;border-color:#3266ad}
.filter-bar label{font-size:12px;font-weight:600;color:#4a5568;white-space:nowrap}
.search-input{border:1px solid #e2e8f0;border-radius:8px;padding:6px 14px;font-size:13px;width:220px;outline:none;color:#1a202c}
.search-input:focus{border-color:#3266ad;box-shadow:0 0 0 3px rgba(50,102,173,.12)}
.srri-btns{display:flex;gap:4px;align-items:center}
.srri-btn{width:30px;height:30px;border-radius:50%;border:2px solid transparent;font-size:12px;font-weight:700;color:#fff;cursor:pointer;transition:all .15s;opacity:.55}
.srri-btn:hover{opacity:.85;transform:scale(1.1)}
.srri-btn.active{opacity:1;border-color:#1a202c;transform:scale(1.15);box-shadow:0 2px 8px rgba(0,0,0,.2)}
.srri-1{background:#22c55e}.srri-2{background:#84cc16}.srri-3{background:#eab308}
.srri-4{background:#f59e0b}.srri-5{background:#f97316}.srri-6{background:#ef4444}.srri-7{background:#991b1b}
.srri-badge{display:inline-flex;align-items:center;justify-content:center;width:20px;height:20px;border-radius:50%;font-size:10px;font-weight:700;color:#fff;flex-shrink:0}
.clear-btn{padding:5px 12px;border:1px solid #e2e8f0;border-radius:6px;background:#f7fafc;color:#718096;font-size:12px;cursor:pointer;transition:all .15s}
.clear-btn:hover{background:#fee2e2;border-color:#ef4444;color:#ef4444}
.filter-results{display:none;padding:24px 32px}
.filter-results.active{display:block}
.filter-count{font-size:13px;color:#718096;margin-bottom:12px}
.period-btns{display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap}
.period-btn{padding:4px 12px;border:1px solid #e2e8f0;border-radius:20px;background:#f7fafc;color:#4a5568;font-size:12px;font-weight:500;cursor:pointer;transition:all .15s;outline:none}
.period-btn:hover{border-color:#3266ad;color:#3266ad;background:#eef3fb}
.period-btn.active{background:#3266ad;border-color:#3266ad;color:#fff;font-weight:600}
.perfmode-bar{display:flex;flex-wrap:wrap;align-items:center;gap:8px;padding:10px 24px 0}
.perfmode-label{font-size:12px;font-weight:600;color:#4a5568}
.perfmode-help{font-size:11px;color:#a0aec0;flex:1 1 220px;min-width:0}
@media(max-width:768px){.perfmode-bar{padding:10px 16px 0}}
@media(max-width:768px){.section{padding:16px}.tabs{padding:0 16px}.stats-bar{padding:12px 16px}}
.ptf-tabs{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap}
.ptf-tab{padding:8px 18px;border-radius:20px;border:1px solid #e2e8f0;background:#f7fafc;font-size:13px;font-weight:500;cursor:pointer;color:#4a5568;transition:all .15s}
.ptf-tab:hover{opacity:.85}
.ptf-tab.active.t-pru{background:#1a3a6b;color:#fff;border-color:transparent}
.ptf-tab.active.t-equ{background:#1D9E75;color:#fff;border-color:transparent}
.ptf-tab.active.t-dyn{background:#993C1D;color:#fff;border-color:transparent}
.ptf-panel{display:none}
.ptf-panel.active{display:block}
.ptf-header{border-radius:10px 10px 0 0;padding:16px 20px 14px}
.ptf-h-pru{background:#E6F1FB}
.ptf-h-equ{background:#E1F5EE}
.ptf-h-dyn{background:#FAECE7}
.ptf-title{font-size:17px;font-weight:700}
.ptf-t-pru{color:#0C447C}
.ptf-t-equ{color:#085041}
.ptf-t-dyn{color:#712B13}
.ptf-sub{font-size:12px;margin-top:3px}
.ptf-s-pru{color:#378ADD}
.ptf-s-equ{color:#1D9E75}
.ptf-s-dyn{color:#D85A30}
.ptf-kpis{display:flex;gap:10px;margin-top:12px;flex-wrap:wrap}
.ptf-kpi{flex:1;min-width:100px;background:#fff;border-radius:8px;border:1px solid #e2e8f0;padding:10px 14px}
.ptf-kpi-lbl{font-size:11px;color:#718096;margin-bottom:4px}
.ptf-kpi-val{font-size:18px;font-weight:700;color:#1a202c}
.ptf-kpi-val.pos{color:#22863a}
.ptf-pct-bar{display:flex;align-items:center;gap:6px}
.ptf-mini-bar{height:6px;border-radius:3px}
.ptf-bar-pru{background:#1a3a6b}
.ptf-bar-equ{background:#1D9E75}
.ptf-bar-dyn{background:#993C1D}
.ptf-bar-fe{background:#f59e0b}
.fe-controls{background:#fffdf0;border:1px solid #fde68a;border-radius:10px;padding:12px 18px;margin-bottom:16px}
.fe-ctrl-row{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.fe-ctrl-group{display:flex;align-items:center;gap:8px}
.fe-label{font-size:13px;font-weight:500;color:#78350f;white-space:nowrap}
.fe-taux-display{font-size:18px;font-weight:700;color:#92400e;min-width:58px}
.fe-enc-btn{padding:4px 10px;border-radius:6px;border:1px solid #f59e0b;background:#fff;font-size:12px;font-weight:500;color:#78350f;cursor:pointer;transition:background .15s}
.fe-enc-btn.active{background:#f59e0b;color:#fff;border-color:#f59e0b}
.fe-tranche-hint{font-size:11px;color:#a0aec0;font-style:italic}
.fe-slider{-webkit-appearance:none;appearance:none;width:150px;height:4px;border-radius:2px;outline:none;cursor:pointer;background:#fde68a}
.fe-slider::-webkit-slider-thumb{-webkit-appearance:none;width:16px;height:16px;border-radius:50%;background:#f59e0b;cursor:pointer;border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,.2)}
.fe-range-hint{font-size:11px;color:#a0aec0}
.fe-row>td{background:#fffdf0!important}
.fe-row .fund-name{font-weight:600;color:#78350f}
.ptf-bar-dop{background:#7c3aed}
.dop-row>td{background:#f5f3ff!important}
.dop-row .fund-name{font-weight:600;color:#5b21b6}
.dop-slider{-webkit-appearance:none;appearance:none;width:150px;height:4px;border-radius:2px;outline:none;cursor:pointer;background:#ddd6fe}
.dop-slider::-webkit-slider-thumb{-webkit-appearance:none;width:16px;height:16px;border-radius:50%;background:#7c3aed;cursor:pointer;border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,.2)}
.dop-lbl{font-size:13px;font-weight:500;color:#5b21b6;white-space:nowrap}
.chk-fund{width:15px;height:15px;cursor:pointer;accent-color:#4a90d9;flex-shrink:0}
.uc-row.deselected>td{opacity:0.35}
.uc-row.deselected .fund-name{text-decoration:line-through;color:#a0aec0}
.alloc-wrap{display:flex;align-items:center;gap:4px}
.manual-alloc{width:38px;font-size:11px;border:1px solid #e2e8f0;border-radius:3px;padding:1px 3px;text-align:center;color:#718096;background:transparent;-moz-appearance:textfield}
.manual-alloc::-webkit-outer-spin-button,.manual-alloc::-webkit-inner-spin-button{-webkit-appearance:none}
.manual-alloc:focus{border-color:#4a90d9;outline:none;background:#fff}
.manual-alloc.is-manual{border-color:#f59e0b!important;background:#fffdf0;color:#92400e;font-weight:700}
.manual-alloc.is-overflow{border-color:#ef4444!important;background:#fee2e2;color:#991b1b}
.ftype-badge{display:inline-block;font-size:10px;font-weight:600;padding:1px 5px;border-radius:3px;margin-left:5px;vertical-align:middle;opacity:0.85;letter-spacing:0.2px}
.ftype-1{border-left:3px solid #3b82f6!important}.ftype-badge-1{background:#dbeafe;color:#1d4ed8}
.ftype-2{border-left:3px solid #06b6d4!important}.ftype-badge-2{background:#cffafe;color:#0e7490}
.ftype-3{border-left:3px solid #10b981!important}.ftype-badge-3{background:#d1fae5;color:#065f46}
.ftype-4{border-left:3px solid #f59e0b!important}.ftype-badge-4{background:#fef3c7;color:#92400e}
.ftype-5{border-left:3px solid #f97316!important}.ftype-badge-5{background:#ffedd5;color:#9a3412}
.ftype-6{border-left:3px solid #ef4444!important}.ftype-badge-6{background:#fee2e2;color:#991b1b}
.ftype-7{border-left:3px solid #8b5cf6!important}.ftype-badge-7{background:#ede9fe;color:#5b21b6}
.ptf-bar-perso{background:#4a90d9}
.perso-tab-bar{display:flex;gap:6px;align-items:center;flex-wrap:wrap;padding:10px 0 14px}
.perso-tab-btn{padding:5px 14px;border:1.5px solid #e2e8f0;border-radius:20px;background:#fff;cursor:pointer;font-size:13px;font-weight:500;color:#4a5568;transition:all .15s}
.perso-tab-btn.active{background:#4a90d9;color:#fff;border-color:#4a90d9}
.perso-tab-btn:hover:not(.active){border-color:#4a90d9;color:#4a90d9}
.perso-tab-new{padding:5px 14px;border:1.5px dashed #cbd5e0;border-radius:20px;background:transparent;cursor:pointer;font-size:13px;color:#718096}
.perso-tab-new:hover{border-color:#4a90d9;color:#4a90d9}
.perso-panel{display:none}
.perso-panel.active{display:block}
.perso-actions-bar{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;align-items:center;padding:4px 0}
.perso-action-btn{padding:5px 12px;border:1px solid #e2e8f0;border-radius:6px;background:#f7fafc;cursor:pointer;font-size:12px;color:#4a5568;font-weight:500}
.perso-action-btn:hover{background:#edf2f7}
.perso-action-btn.primary{background:#ebf4ff;border-color:#bee3f8;color:#2b6cb0}
.perso-action-btn.primary:hover{background:#bee3f8}
.perso-action-btn.danger{background:#fff5f5;border-color:#fed7d7;color:#c53030}
.perso-action-btn.danger:hover{background:#fed7d7}
.perso-modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:1000;display:flex;align-items:center;justify-content:center}
.perso-modal-overlay.hidden{display:none}
.perso-modal-box{background:#fff;border-radius:12px;width:min(680px,95vw);max-height:82vh;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,.3)}
.perso-modal-header{padding:14px 18px;border-bottom:1px solid #e2e8f0;display:flex;align-items:center;gap:8px}
.perso-modal-header h3{margin:0;font-size:15px;flex:1}
.perso-modal-close{background:none;border:none;font-size:22px;cursor:pointer;color:#a0aec0;line-height:1}
.perso-modal-body{overflow-y:auto;padding:10px 14px;flex:1}
.perso-modal-footer{padding:10px 14px;border-top:1px solid #e2e8f0;display:flex;justify-content:flex-end;gap:8px}
.fs-cat-header{font-size:11px;font-weight:700;text-transform:uppercase;color:#a0aec0;letter-spacing:.7px;padding:10px 4px 4px;border-top:1px solid #f0f4f8;margin-top:4px}
.fs-cat-header:first-child{border-top:none;margin-top:0;padding-top:2px}
.fs-item{display:flex;align-items:center;gap:6px;padding:5px 8px;border-radius:6px;cursor:pointer;font-size:13px}
.fs-item:hover{background:#f7fafc}
.fs-item input{flex-shrink:0;width:15px;height:15px;accent-color:#4a90d9;cursor:pointer}
.fs-name{font-weight:500;flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.fs-ytd{font-size:12px;font-weight:600;white-space:nowrap;min-width:46px;text-align:right}
#fs-search-row{margin-bottom:8px;position:sticky;top:0;background:#fff;padding-bottom:4px;z-index:1}
.perso-empty{text-align:center;padding:32px;color:#a0aec0;font-style:italic;font-size:14px}
.perso-total-row>td{background:#eef3fb!important;font-weight:700;border-top:2px solid #3266ad}
.alloc-ok{color:#22863a}.alloc-warn{color:#d97706}.alloc-bad{color:#c0392b}
.sim-box{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px 20px;margin-top:20px;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.sim-title{font-size:15px;font-weight:700;color:#1a202c;margin-bottom:4px}
.sim-hint{font-size:12px;color:#718096;margin-bottom:12px}
.sim-row{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
.sim-row label{font-size:12px;font-weight:600;color:#4a5568}
.sim-row input{width:90px;border:1px solid #e2e8f0;border-radius:6px;padding:5px 8px;font-size:13px;text-align:right}
.sim-row input:focus{border-color:#3266ad;outline:none}
.sim-kpis{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px}
.sim-kpi{flex:1;min-width:130px;background:#f7fafc;border:1px solid #e2e8f0;border-radius:8px;padding:10px 14px}
.sim-kpi .lbl{font-size:11px;color:#718096;margin-bottom:3px}
.sim-kpi .val{font-size:18px;font-weight:700;color:#1a202c}
.sim-table{font-size:12px}
.sim-table td,.sim-table th{padding:5px 10px}
.sim-note{font-size:11px;color:#a0aec0;margin-top:8px;font-style:italic}
@media print{.no-print{display:none!important}}
.vision-bar{display:flex;gap:6px;align-items:center;margin-left:auto}
#sec_portefeuilles.vis-a1 table th:nth-child(6),#sec_portefeuilles.vis-a1 table td:nth-child(6){background:#fff8e1}
#sec_portefeuilles.vis-a3 table th:nth-child(7),#sec_portefeuilles.vis-a3 table td:nth-child(7){background:#fff8e1}
#sec_portefeuilles.vis-a5 table th:nth-child(8),#sec_portefeuilles.vis-a5 table td:nth-child(8){background:#fff8e1}
#sec_portefeuilles .sim-table th,#sec_portefeuilles .sim-table td{background:transparent!important}
</style>
</head>
<body>
""")

total = sum(len(c["funds"]) for c in CATEGORIES)
cats_str = str(len(CATEGORIES))
best = max((f for c in CATEGORIES for f in c["funds"] if f["ytd"] is not None), key=lambda x: x["ytd"])
worst = min((f for c in CATEGORIES for f in c["funds"] if f["ytd"] is not None), key=lambda x: x["ytd"])

html_parts.append(f"""<header>
<h1>📊 Le Conservateur — Analyse des Fonds</h1>
<p>VL &amp; YTD : Boursorama au {_fmt_date_fr(_VL_OVERRIDE_DATE)}</p>
</header>
<div class="stats-bar">
  <div class="stat"><div class="val">{total}</div><div class="lbl">Fonds analysés</div></div>
  <div class="stat"><div class="val">{cats_str}</div><div class="lbl">Catégories</div></div>
  <div class="stat"><div class="val pos">+{best['ytd']:.2f}%</div><div class="lbl">Meilleur YTD · {best['name']}</div></div>
  <div class="stat"><div class="val neg">{worst['ytd']:.2f}%</div><div class="lbl">Moins bon YTD · {worst['name']}</div></div>
</div>
""")

# ── Barre de filtres (recherche + SRRI) ──────────────────────────────────────
html_parts.append(f"""<div class="filter-bar">
  <label>🔍</label>
  <input class="search-input" id="searchInput" type="text" placeholder="Rechercher un fonds..." oninput="applyFilters()">
  <label style="margin-left:8px;font-size:12px;font-weight:600;color:#4a5568">Risque SRRI :</label>
  <div class="srri-btns">
    <button class="srri-btn srri-1" data-srri="1" onclick="toggleSRRI(1)" title="SRRI 1 — Très faible">1</button>
    <button class="srri-btn srri-2" data-srri="2" onclick="toggleSRRI(2)" title="SRRI 2 — Faible">2</button>
    <button class="srri-btn srri-3" data-srri="3" onclick="toggleSRRI(3)" title="SRRI 3 — Modéré bas">3</button>
    <button class="srri-btn srri-4" data-srri="4" onclick="toggleSRRI(4)" title="SRRI 4 — Modéré">4</button>
    <button class="srri-btn srri-5" data-srri="5" onclick="toggleSRRI(5)" title="SRRI 5 — Modéré haut">5</button>
    <button class="srri-btn srri-6" data-srri="6" onclick="toggleSRRI(6)" title="SRRI 6 — Élevé">6</button>
    <button class="srri-btn srri-7" data-srri="7" onclick="toggleSRRI(7)" title="SRRI 7 — Très élevé">7</button>
  </div>
  <button class="clear-btn" onclick="clearFilters()">✕ Effacer</button>
  <div class="view-tabs">
    <button class="view-tab" id="tab_portefeuilles" onclick="showTab('portefeuilles')">💼 Portefeuilles</button>
    <button class="view-tab" id="tab_perso" onclick="showTab('perso')">👤 Perso</button>
  </div>
</div>
""")

# ── Section résultats filtrés ────────────────────────────────────────────────
html_parts.append("""<div class="filter-results" id="filterResults">
  <div class="filter-count" id="filterCount"></div>
  <div class="table-wrap">
    <table id="tblFiltered">
      <thead><tr>
        <th onclick="sortTable('tblFiltered',0)">#</th>
        <th onclick="sortTable('tblFiltered',1)">Fonds</th>
        <th onclick="sortTable('tblFiltered',2)">Catégorie</th>
        <th style="text-align:center" onclick="sortTable('tblFiltered',3)">SRRI</th>
        <th style="text-align:right" onclick="sortTable('tblFiltered',4)">VL</th>
        <th style="text-align:right" onclick="sortTable('tblFiltered',5)">YTD</th>
        <th style="text-align:right" onclick="sortTable('tblFiltered',6)">1 Mois</th>
        <th style="text-align:right" onclick="sortTable('tblFiltered',7)">6 Mois</th>
        <th style="text-align:right" onclick="sortTable('tblFiltered',8)">1 An</th>
        <th style="text-align:right" onclick="sortTable('tblFiltered',9)">3 Ans</th>
        <th style="text-align:right" onclick="sortTable('tblFiltered',10)">5 Ans</th>
        <th style="text-align:right" onclick="sortTable('tblFiltered',11)" title="Volatilité annualisée 12 mois">Volat.</th>
        <th style="text-align:right" onclick="sortTable('tblFiltered',12)" title="Perte maximale 12 mois">Max DD</th>
      </tr></thead>
      <tbody id="filteredBody"></tbody>
    </table>
  </div>
</div>
""")

# ── Bascule de convention de performance ─────────────────────────────────────
html_parts.append(f'''<div class="perfmode-bar">
  <span class="perfmode-label">Performances&nbsp;:</span>
  <button class="period-btn active" data-pmode="eom" onclick="setPerfMode('eom')">À la fin de mois</button>
  <button class="period-btn" data-pmode="gli" onclick="setPerfMode('gli')">Glissantes</button>
  <span class="perfmode-help" id="perfmodeHelp">Arrêtées à la dernière VL du mois précédent — stables d'un jour à l'autre.</span>
</div>
''')

# ── Onglets ──────────────────────────────────────────────────────────────────
html_parts.append('<div class="tabs" id="mainTabs">\n')

for i, cat in enumerate(CATEGORIES):
    active = "active" if i == 0 else ""
    html_parts.append(f'  <div class="tab {active}" onclick="showTab(\'{cat["id"]}\')" id="tab_{cat["id"]}">{cat["label"]} <span style="font-size:11px;opacity:.7">({len(cat["funds"])})</span></div>\n')

html_parts.append("</div>\n")

# ── Collect all chart data for JS ──────────────────────────────────────────────
all_bar_charts = []   # [{id, labels, data, colors}]
all_line_charts = []  # [{id, datasets}]

for i, cat in enumerate(CATEGORIES):
    active = "active" if i == 0 else ""
    cid = cat["id"]
    funds_sorted = sorted(cat["funds"], key=lambda f: (f["ytd"] is None, -(f["ytd"] or -999)))
    top5 = funds_sorted[:5]
    color = cat["color"]

    # ── Données historiques mensuelles disponibles pour cette catégorie ? ──────
    _HIST_MONTHS = ["","Jan","Fév","Mar","Avr","Mai","Juin","Juil","Août","Sep","Oct","Nov","Déc"]
    hist_in_cat = {
        f["isin"]: _HIST_DATA[f["isin"]]
        for f in funds_sorted
        if f["isin"] in _HIST_DATA and len(_HIST_DATA[f["isin"]]) >= 3
    }
    use_hist = len(hist_in_cat) >= 2  # Minimum 2 fonds avec données historiques
    if use_hist:
        # Axe complet de la catégorie (jusqu'à 60 mois) — le découpage par
        # période et le rebasage sont faits côté client sur la fenêtre affichée.
        all_hist_dates = sorted({
            pt["date"]
            for months in hist_in_cat.values()
            for pt in months
        })[-61:]
    else:
        all_hist_dates = []

    html_parts.append(f'<div class="section {active}" id="sec_{cid}">\n')
    html_parts.append(f'<div class="cat-header"><h2>{cat["label"]}</h2><span class="badge">{len(cat["funds"])} fonds</span></div>\n')
    html_parts.append(f'<div class="source-note">📅 VL et performances relevées sur Boursorama le {_fmt_date_short(_BP_LAST_UPDATED or _VL_OVERRIDE_DATE)} (VL la plus récente : {_fmt_date_short(_VL_OVERRIDE_DATE)}) · historique mensuel des VL au {_fmt_date_short(_HIST_LAST_UPDATED)}</div>\n')

    # Top 5 cards
    html_parts.append('<div class="top5">\n')
    for rank, f in enumerate(top5):
        ytd_html = fmt(f["ytd"]) if f["ytd"] is not None else '<span class="na">NS</span>'
        bid = f.get("bid")
        link_html = f'<a href="{bourso_url(bid)}" target="_blank" class="bourso-link" title="Voir sur Boursorama">🔗</a>' if bid else ""
        html_parts.append(f'''<div class="fund-card" style="border-left-color:{color}">
  <div class="rank">{medal(rank)} {link_html}</div>
  <div class="fname">{f["name"]}</div>
  <div class="fmgr">{f["mgr"]}</div>
  <div class="fytd">{ytd_html}</div>
  <div class="fisin">{f["isin"]}</div>
</div>\n''')
    html_parts.append('</div>\n')

    # ── Two charts side by side ────────────────────────────────────────────────
    height_bar = "55" if len(funds_sorted) <= 6 else "90"
    html_parts.append('<div class="charts-row">\n')

    # Chart 1 : barres (période sélectionnable)
    html_parts.append(f'''<div class="chart-wrap">
<h3 id="bartitle_{cid}">Performance YTD</h3>
<div class="chart-sub">Relevé Boursorama du {_fmt_date_short(_BP_LAST_UPDATED or _VL_OVERRIDE_DATE)} · convention sélectionnée ci-dessus</div>
<div class="period-btns">
  <button class="period-btn active" data-cat="{cid}" data-bperiod="YTD" onclick="filterBarPeriod('{cid}','YTD')">YTD</button>
  <button class="period-btn" data-cat="{cid}" data-bperiod="1M" onclick="filterBarPeriod('{cid}','1M')">1 Mois</button>
  <button class="period-btn" data-cat="{cid}" data-bperiod="6M" onclick="filterBarPeriod('{cid}','6M')">6 Mois</button>
  <button class="period-btn" data-cat="{cid}" data-bperiod="1A" onclick="filterBarPeriod('{cid}','1A')">1 An</button>
  <button class="period-btn" data-cat="{cid}" data-bperiod="3A" onclick="filterBarPeriod('{cid}','3A')">3 Ans</button>
  <button class="period-btn" data-cat="{cid}" data-bperiod="5A" onclick="filterBarPeriod('{cid}','5A')">5 Ans</button>
</div>
<canvas id="bar_{cid}" height="{height_bar}"></canvas>
</div>
''')

    # Chart 2 : évolution de la VL sur l'historique réel
    _line_span = f"{all_hist_dates[0]} → {all_hist_dates[-1]}" if all_hist_dates else "—"
    _line_subtitle = (f"VL mensuelle Boursorama · {_line_span} — chaque courbe est rebasée à 0 %"
                      " à la première date de la période affichée")
    _line_buttons = f'''<div class="period-btns">
  <button class="period-btn" data-cat="{cid}" data-period="3M" onclick="filterLinePeriod('{cid}','3M')">3 Mois</button>
  <button class="period-btn" data-cat="{cid}" data-period="6M" onclick="filterLinePeriod('{cid}','6M')">6 Mois</button>
  <button class="period-btn active" data-cat="{cid}" data-period="1A" onclick="filterLinePeriod('{cid}','1A')">1 An</button>
  <button class="period-btn" data-cat="{cid}" data-period="3A" onclick="filterLinePeriod('{cid}','3A')">3 Ans</button>
  <button class="period-btn" data-cat="{cid}" data-period="5A" onclick="filterLinePeriod('{cid}','5A')">5 Ans</button>
</div>'''
    _line_title = "Évolution de la valeur liquidative"
    html_parts.append(f'''<div class="chart-wrap">
<h3>{_line_title}</h3>
<div class="chart-sub">{_line_subtitle}</div>
{_line_buttons}
<canvas id="line_{cid}" height="{height_bar}"></canvas>
<div class="chart-sub" id="linenote_{cid}" style="margin-top:10px;margin-bottom:0"></div>
</div>
''')

    html_parts.append('</div>\n')  # end charts-row

    # ── Préparer données JS ────────────────────────────────────────────────────
    # Bar chart — toutes périodes stockées, on switche dynamiquement
    bar_labels = [f["name"][:28] for f in funds_sorted]

    def bar_period(key, mode):
        src = "perf_eom" if mode == "eom" else "perf_gli"
        vals = []
        for f in funds_sorted:
            v = (f.get(src) or {}).get(key)
            if key == "ytd" and v is None:
                v = f.get("ytd")
            vals.append(v)
        cols = [color if (v is not None and v >= 0) else "#e53e3e" for v in vals]
        return {"data": vals, "colors": cols}

    def bar_set(mode):
        return {
            "YTD": bar_period("ytd", mode),
            "1M":  bar_period("m1",  mode),
            "6M":  bar_period("m6",  mode),
            "1A":  bar_period("a1",  mode),
            "3A":  bar_period("a3",  mode),
            "5A":  bar_period("a5",  mode),
        }

    all_bar_charts.append({
        "id": f"bar_{cid}",
        "labels": bar_labels,
        "color": color,
        "periods": bar_set("eom"),
        "periodsByMode": {"eom": bar_set("eom"), "gli": bar_set("gli")},
    })

    # Line chart — VL mensuelle brute ; le découpage par période et le rebasage
    # sont faits côté client, sur la fenêtre réellement affichée. Aucune série
    # multi-horizons n'est tracée sur un axe temporel : ce serait une fausse
    # chronologie (chaque horizon est une fenêtre de recul, pas un instant).
    line_datasets = []
    line_labels = [
        f"{_HIST_MONTHS[int(d.split('-')[1])]} {d.split('-')[0][-2:]}"
        for d in all_hist_dates
    ]
    for fi, f in enumerate(funds_sorted):
        isin = f["isin"]
        if isin not in hist_in_cat:
            continue
        monthly_dict = {pt["date"]: pt["vl"] for pt in hist_in_cat[isin]}
        pts = [monthly_dict.get(d) for d in all_hist_dates]
        if sum(1 for p in pts if p is not None) < 2:
            continue
        line_datasets.append({
            "label": f["name"][:35],
            "vl": pts,                      # VL brute alignée sur l'axe commun
            "data": pts,
            "fullData": pts,
            "borderColor": LINE_PALETTE[fi % len(LINE_PALETTE)],
            "borderWidth": 2,
            "pointRadius": 2,
        })
    all_line_charts.append({
        "id": f"line_{cid}",
        "mode": "vl",
        "labels": line_labels,
        "dates": all_hist_dates,
        "datasets": line_datasets,
    })

    # ── Table ──────────────────────────────────────────────────────────────────
    html_parts.append(f'''<div class="table-wrap">
<table id="tbl_{cid}">
<thead><tr>
  <th onclick="sortTable('tbl_{cid}',0)">#</th>
  <th onclick="sortTable('tbl_{cid}',1)">Fonds</th>
  <th onclick="sortTable('tbl_{cid}',2)" style="text-align:center">SRRI</th>
  <th onclick="sortTable('tbl_{cid}',3)" style="text-align:right">VL</th>
  <th onclick="sortTable('tbl_{cid}',4)" style="text-align:right" title="Depuis le 1er janvier — relevé Boursorama du {_fmt_date_short(_BP_LAST_UPDATED or _VL_OVERRIDE_DATE)}">YTD</th>
  <th onclick="sortTable('tbl_{cid}',5)" style="text-align:right" title="1 mois — relevé Boursorama du {_fmt_date_short(_BP_LAST_UPDATED or _VL_OVERRIDE_DATE)}">1 Mois</th>
  <th onclick="sortTable('tbl_{cid}',6)" style="text-align:right" title="6 mois — relevé Boursorama du {_fmt_date_short(_BP_LAST_UPDATED or _VL_OVERRIDE_DATE)}">6 Mois</th>
  <th onclick="sortTable('tbl_{cid}',7)" style="text-align:right" title="1 an — relevé Boursorama du {_fmt_date_short(_BP_LAST_UPDATED or _VL_OVERRIDE_DATE)}">1 An</th>
  <th onclick="sortTable('tbl_{cid}',8)" style="text-align:right" title="3 ans — relevé Boursorama du {_fmt_date_short(_BP_LAST_UPDATED or _VL_OVERRIDE_DATE)}">3 Ans</th>
  <th onclick="sortTable('tbl_{cid}',9)" style="text-align:right" title="5 ans — relevé Boursorama du {_fmt_date_short(_BP_LAST_UPDATED or _VL_OVERRIDE_DATE)}">5 Ans</th>
</tr></thead>
<tbody>
''')

    for rank, f in enumerate(funds_sorted):
        top3_cls = "top3" if rank < 3 else ""
        bid = f.get("bid")
        srri = f.get("srri", "—")
        bourso_cell = f'<a href="{bourso_url(bid)}" target="_blank" class="bourso-link">Voir →</a>' if bid else '<span class="na">—</span>'
        html_parts.append(f'''<tr class="{top3_cls}">
  <td data-val="{rank+1}">{medal(rank)}</td>
  <td class="fund-name" data-val="{f['name']}">{"<a href='" + bourso_url(bid) + "' target='_blank' class='fund-name-link'>" + f['name'] + "</a>" if bid else f["name"]}<br><span class="isin-cell">{f["isin"]}</span></td>
  <td style="text-align:center" data-val="{srri}"><span class="srri-badge srri-{srri}">{srri}</span></td>
  <td style="text-align:right" data-val="{f['vl'] or 0}">{fmt_vl(f["vl"])}</td>
  {perf_td(f, "ytd")}
  {perf_td(f, "m1")}
  {perf_td(f, "m6")}
  {perf_td(f, "a1")}
  {perf_td(f, "a3")}
  {perf_td(f, "a5")}
</tr>
''')
    html_parts.append('</tbody></table></div>\n')
    html_parts.append('</div>\n')  # end section

# ── Section Portefeuilles ──────────────────────────────────────────────────────
_SRRI_COLORS_PTF = {1:"#22c55e",2:"#84cc16",3:"#eab308",4:"#f59e0b",5:"#f97316",6:"#ef4444",7:"#991b1b"}

# Définition par ISIN + pondération — les perfs sont tirées automatiquement
# des données fonds (VL/YTD scrapés quotidiennement + perfs Boursorama).
# 15 lignes par profil.
_PORTFOLIOS_DEF = [
    {
        "id": "pru", "label": "Prudent", "emoji": "🔵",
        "range": "SRRI 1–3", "color_cls": "pru",
        "desc": "Horizon 3–5 ans · Préservation du capital · Rendement cible ~2–3%/an",
        "note": "20% SRRI1 (monétaire) · 45% SRRI2 (oblig. daté/horizon) · 35% SRRI3 (obligataire & diversifié prudent)",
        "funds": [
            ("FR0013287315", 8),   # Palatine Monétaire Court Terme (R)
            ("FR0011461326", 5),   # Conservateur Oblig. CT (C)
            ("LU1585265066", 7),   # TF - Tikehau Short Duration (R)
            ("FR001400PKZ3", 12),  # Conservateur Horizon 2031 (I)
            ("FR0013398294", 10),  # Conservateur Horizon 2027 (I)
            ("FR0013426657", 6),   # Oddo BHF Global Target 2026 (CR)
            ("FR0013505450", 6),   # Tikehau 2027
            ("FR001400K2B5", 6),   # Tikehau 2029
            ("FR0013398302", 5),   # Conservateur Horizon 2027 (C)
            ("LU0284394235", 10),  # DNCA Invest - Eurose (A)
            ("LU1694790202", 7),   # DNCA Invest Flex Inflation
            ("LU1694789451", 6),   # DNCA Invest Alpha Bonds (A)
            ("FR0010915314", 4),   # LF Obligations Carbon Impact C
            ("FR0010564328", 4),   # Conservateur Oblig. MT (C)
            ("LU1752460292", 4),   # Oddo Sustainable Credit Optn CR
        ]
    },
    {
        "id": "equ", "label": "Équilibré", "emoji": "🟢",
        "range": "SRRI 1–5", "color_cls": "equ",
        "desc": "Horizon 5–7 ans · Croissance modérée · Rendement cible ~7–9%/an",
        "note": "16% SRRI2–3 (ancre défensive) · 64% SRRI4 (diversifiés & flexibles) · 20% SRRI5 (actions flexibles)",
        "funds": [
            ("FR001400PKZ3", 4),   # Conservateur Horizon 2031 (I)
            ("LU0284394235", 8),   # DNCA Invest - Eurose (A)
            ("LU1694789451", 4),   # DNCA Invest Alpha Bonds (A)
            ("LU0512124107", 10),  # DNCA Invest - Convertibles (B)
            ("FR0010135103", 10),  # Carmignac Patrimoine (A)
            ("FR0010097683", 8),   # CPR Croissance Réactive (P)
            ("FR0010564336", 8),   # Conservateur Diversifié (C)
            ("FR0007439666", 8),   # Congrégation Investissement (C)
            ("FR0010489542", 6),   # Conservateur Diversifié Réactif (C)
            ("LU2147879543", 6),   # Tikehau International Cross Assets (R)
            ("FR0010286013", 4),   # Sextant Grand Large (A)
            ("FR0011199314", 4),   # Conservateur Immo-Or (C)
            ("FR0010149179", 4),   # Carmignac Absolute Return Europe (A)
            ("FR0011253624", 8),   # R-co Valor (C)
            ("FR0013256930", 8),   # Conservateur Actions Flexibles (C)
        ]
    },
    {
        "id": "dyn", "label": "Dynamique", "emoji": "🔴",
        "range": "SRRI 1–7", "color_cls": "dyn",
        "desc": "Horizon 7–10 ans · Croissance forte · Rendement cible ~15–20%/an",
        "note": "6% SRRI4 (ancre convertibles) · 79% SRRI6 (actions mondiales/thématiques) · 15% SRRI7 (croissance forte)",
        "funds": [
            ("LU0512124107", 6),   # DNCA Invest - Convertibles (B)
            ("FR0010148981", 10),  # Carmignac Investissement (A)
            ("LU1261432659", 10),  # FF - World Fund (A)
            ("FR0000292278", 8),   # Magellan (C)
            ("LU1819480192", 10),  # Echiquier Artificial Intelligence (B)
            ("LU0280435388", 5),   # Pictet - Clean Energy Transition (P)
            ("FR0010564229", 8),   # Conservateur Actions Monde (C)
            ("FR0000983819", 7),   # OFI Croiss Durable & Solidaire C
            ("FR0007076930", 5),   # Centifolia (C)
            ("LU1244893696", 4),   # EdR Fund - Big Data (A)
            ("FR0010649079", 7),   # Palatine Planète (R)
            ("LU0115768185", 6),   # FF - Sustainable Asia Equity Fund (E)
            ("FR0010106500", 5),   # Echiquier Excelsior A
            ("FR0010298596", 5),   # Moneta Multi Caps (C)
            ("LU1902443420", 4),   # CPR Invest Climate Action (A)
        ]
    },
]

# ── Construction des portefeuilles à partir des données fonds ──────────────
_FUND_BY_ISIN = {f["isin"]: f for cat in CATEGORIES for f in cat["funds"]}

def _esc_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _fmt_ptf_val(v):
    """float → '+2,06%' | None → '—' (format attendu par le rendu)"""
    if v is None:
        return "—"
    s = f"{v:+.2f}%".replace(".", ",")
    return s.replace("-", "−")

_PORTFOLIOS_DATA = []
for _pdef in _PORTFOLIOS_DEF:
    _funds = []
    _w_srri = 0.0
    _tot_w = 0
    for _isin, _pct in _pdef["funds"]:
        _fd = _FUND_BY_ISIN.get(_isin)
        if not _fd:
            print(f"⚠️  Portefeuille {_pdef['label']} : ISIN {_isin} introuvable — ignoré")
            continue
        _funds.append((
            len(_funds) + 1,
            _esc_html(_fd["name"]),
            _fd.get("srri") or 4,
            _fmt_ptf_val(_fd.get("ytd")),
            _fmt_ptf_val(_fd.get("a1")),
            _fmt_ptf_val(_fd.get("a3")),
            _fmt_ptf_val(_fd.get("a5")),
            _pct,
            _fd.get("vol"),
            _fd.get("mdd"),
        ))
        _w_srri += (_fd.get("srri") or 4) * _pct
        _tot_w += _pct
    if _tot_w != 100:
        print(f"⚠️  Portefeuille {_pdef['label']} : somme des pondérations = {_tot_w}% (≠ 100%)")
    _srri_moy = _w_srri / _tot_w if _tot_w else 0
    _PORTFOLIOS_DATA.append({
        **{k: _pdef[k] for k in ("id", "label", "emoji", "range", "color_cls", "desc", "note")},
        "kpis": [
            ("Perf. pondérée 1 An", "—", ""),
            ("Perf. annualisée", "—", ""),
            ("Volatilité 1 An (pond.)", "—", ""),
            ("SRRI moyen pond.", f"{_srri_moy:.1f}".replace(".", ","), ""),
            ("Fonds sélectionnés", str(len(_funds)), ""),
        ],
        "funds": _funds,
    })

# ── Tri des fonds UC par performance 1 an décroissante ────────────────────
def _a1_sort_key(fund_tuple):
    s = fund_tuple[4]  # a1 string, e.g. "+2,06%" or "−4,94%"
    if not s or s == "—":
        return float('-inf')
    try:
        return float(s.replace("+","").replace("\u2212","-").replace("−","-").replace(",",".").replace("%",""))
    except Exception:
        return float('-inf')

for _ptf in _PORTFOLIOS_DATA:
    _sorted = sorted(_ptf["funds"], key=_a1_sort_key, reverse=True)
    _ptf["funds"] = [(i+1,) + f[1:] for i, f in enumerate(_sorted)]

_FTYPE_LABELS = {1: "Monétaire", 2: "Oblig. Daté", 3: "Obligataire", 4: "Flexible", 5: "Mixte", 6: "Actions", 7: "Thématique"}

def _ptf_perf(v):
    if v == "—":
        return '<span class="na">—</span>'
    if v.startswith("+"):
        return f'<span class="pos">{v}</span>'
    return f'<span class="neg">{v}</span>'

def _parse_pct(s):
    """'+2,06%' → 2.06  |  '—' → None  |  '−4,94%' → -4.94"""
    if not s or s == "—":
        return None
    try:
        return float(s.strip()
                      .replace("+", "")
                      .replace("−", "-")   # unicode minus
                      .replace("−", "-")
                      .replace(",", ".")
                      .replace("%", ""))
    except Exception:
        return None

# Build PTF JS dataset (parsed floats for blended-perf calculations)
_ptf_js_dict = {}
for _ptf in _PORTFOLIOS_DATA:
    _funds_arr = []
    for _rank, _name, _srri, _ytd_s, _a1_s, _a3_s, _a5_s, _pct, _vol, _mdd in _ptf["funds"]:
        _funds_arr.append({
            "name": _name,
            "srri": _srri,
            "pct": _pct,
            "ytd": _parse_pct(_ytd_s),
            "a1":  _parse_pct(_a1_s),
            "a3":  _parse_pct(_a3_s),
            "a5":  _parse_pct(_a5_s),
            "vol": _vol,
            "mdd": _mdd,
        })
    _ptf_js_dict[_ptf["id"]] = {"cc": _ptf["color_cls"], "label": _ptf["label"], "funds": _funds_arr}
_PTF_DATA_JS = json.dumps(_ptf_js_dict, ensure_ascii=False)

html_parts.append('<div class="section vis-a1" id="sec_portefeuilles">\n')
html_parts.append('<div class="cat-header"><h2>💼 Portefeuilles Optimisés</h2><span class="badge">3 profils de risque</span>'
                  '<div class="vision-bar"><span style="font-size:12px;font-weight:600;color:#4a5568">Vision&nbsp;:</span>'
                  '<button class="period-btn active" id="visBtn-a1" onclick="setVision(\'a1\')">1 an</button>'
                  '<button class="period-btn" id="visBtn-a3" onclick="setVision(\'a3\')">3 ans (N−3)</button>'
                  '<button class="period-btn" id="visBtn-a5" onclick="setVision(\'a5\')">5 ans (N−5)</button></div></div>\n')
html_parts.append(f'<div class="source-note">📅 Construit sur la base des performances Boursorama au {_fmt_date_short(_HIST_LAST_UPDATED)} — Sélection et pondération optimisée de 15 fonds par profil SRRI · Perfs mises à jour automatiquement</div>\n')

# ── Fonds en Euros controls ────────────────────────────────────────────────
html_parts.append('''<div class="fe-controls">
  <div class="fe-ctrl-row">
    <span style="font-size:20px">🏦</span>
    <span class="fe-label" style="font-size:14px;font-weight:700">Fonds en Euros</span>
    <div class="fe-ctrl-group">
      <span class="fe-label">Encours&nbsp;:</span>
      <button class="fe-enc-btn active" id="feEncLow"  onclick="setEncours(false)">Moins de 150 k€</button>
      <button class="fe-enc-btn"        id="feEncHigh" onclick="setEncours(true)">150 k€ et plus</button>
    </div>
    <div class="fe-ctrl-group">
      <span class="fe-label">Allocation FE&nbsp;:</span>
      <input class="fe-slider" id="feSlider" type="range" min="20" max="49" value="30" oninput="updateFE()">
      <span class="fe-label"><span id="feAllocVal">30</span>&nbsp;%</span>
      <span class="fe-range-hint">(20–49 %)</span>
    </div>
    <div class="fe-ctrl-group">
      <span class="fe-label">Taux 2025&nbsp;:</span>
      <span class="fe-taux-display" id="feTauxDisplay">4,00&nbsp;%</span>
      <span class="fe-tranche-hint" id="feTranche">UC ≥ 70 %</span>
    </div>
  </div>
  <div class="fe-ctrl-row" style="margin-top:10px;padding-top:10px;border-top:1px solid #e9d5ff">
    <span style="font-size:20px">💎</span>
    <span class="dop-lbl" style="font-size:14px;font-weight:700">DOP</span>
    <div class="fe-ctrl-group">
      <span class="dop-lbl">Allocation DOP&nbsp;:</span>
      <input class="dop-slider" id="dopSlider" type="range" min="0" max="30" value="0" oninput="updateFE()">
      <span class="dop-lbl"><span id="dopAllocVal">0</span>&nbsp;%</span>
      <span class="fe-range-hint">(0–30 %)</span>
    </div>
    <div class="fe-ctrl-group">
      <span class="dop-lbl">Taux fixe&nbsp;:</span>
      <span style="font-size:18px;font-weight:700;color:#5b21b6">5,00&nbsp;%</span>
      <span class="fe-range-hint">/ an</span>
    </div>
  </div>
</div>\n''')

# Inner portfolio tabs
html_parts.append('<div class="ptf-tabs">\n')
for pi, ptf in enumerate(_PORTFOLIOS_DATA):
    _active_ptf = "active" if pi == 0 else ""
    html_parts.append(f'  <div class="ptf-tab {_active_ptf} t-{ptf["color_cls"]}" onclick="ptfShow(\'{ptf["id"]}\')">{ptf["emoji"]} {ptf["label"]} · {ptf["range"]}</div>\n')
html_parts.append('</div>\n')

for pi, ptf in enumerate(_PORTFOLIOS_DATA):
    _active_ptf = "active" if pi == 0 else ""
    cc = ptf["color_cls"]

    html_parts.append(f'<div class="ptf-panel {_active_ptf}" id="ptf_{ptf["id"]}">\n')
    html_parts.append(f'<div class="ptf-header ptf-h-{cc}">\n')
    html_parts.append(f'  <div class="ptf-title ptf-t-{cc}">{ptf["emoji"]} Portefeuille {ptf["label"]}</div>\n')
    html_parts.append(f'  <div class="ptf-sub ptf-s-{cc}">{ptf["desc"]}</div>\n')
    html_parts.append('  <div class="ptf-kpis">\n')
    _kpi_ids = {0: "main", 1: "ann", 2: "vol"}
    for ki, (lbl, val, cls) in enumerate(ptf["kpis"]):
        kid_attr = f' id="kpi-{_kpi_ids[ki]}-{ptf["id"]}"' if ki in _kpi_ids else ''
        klbl_attr = f' id="kpilbl-{_kpi_ids[ki]}-{ptf["id"]}"' if ki in (0, 1) else ''
        html_parts.append(f'    <div class="ptf-kpi"><div class="ptf-kpi-lbl"{klbl_attr}>{lbl}</div><div class="ptf-kpi-val {cls}"{kid_attr}>{val}</div></div>\n')
    html_parts.append(f'  <div style="margin-top:10px"><button class="perso-action-btn" onclick="printPortfolio(\'{ptf["id"]}\')">🖨️ Imprimer / PDF</button></div>\n')
    html_parts.append('  </div>\n</div>\n')

    html_parts.append('<div class="table-wrap" style="border-radius:0 0 10px 10px;margin-top:0">\n')
    html_parts.append('<table>\n<thead><tr>\n')
    html_parts.append('  <th style="width:24px"></th>\n')
    html_parts.append('  <th style="width:32px">#</th>\n  <th>Fonds</th>\n')
    html_parts.append('  <th style="text-align:center;width:48px">SRRI</th>\n')
    html_parts.append('  <th style="text-align:right;width:60px">YTD</th>\n')
    html_parts.append('  <th style="text-align:right;width:60px">1 An</th>\n')
    html_parts.append('  <th style="text-align:right;width:60px">3 Ans</th>\n')
    html_parts.append('  <th style="text-align:right;width:60px">5 Ans</th>\n')
    html_parts.append('  <th style="text-align:right;width:58px" title="Volatilité annualisée sur 12 mois">Volat.</th>\n')
    html_parts.append('  <th style="text-align:right;width:58px" title="Perte maximale sur 12 mois">Max DD</th>\n')
    html_parts.append('  <th style="width:110px">Allocation</th>\n')
    html_parts.append('</tr></thead>\n<tbody>\n')

    # ── Fonds en Euros row (first, dynamic) ───────────────────────────────────
    html_parts.append(f'''<tr class="fe-row">
  <td></td>
  <td style="font-size:13px;text-align:center">★</td>
  <td class="fund-name">🏦 Fonds en Euros</td>
  <td style="text-align:center"><span class="srri-badge" style="background:#22c55e">1</span></td>
  <td style="text-align:right" id="fe-ytd-{ptf["id"]}">—</td>
  <td style="text-align:right" id="fe-a1-{ptf["id"]}">—</td>
  <td style="text-align:right" id="fe-a3-{ptf["id"]}">—</td>
  <td style="text-align:right" id="fe-a5-{ptf["id"]}">—</td>
  <td style="text-align:right;color:#a0aec0">≈0</td>
  <td style="text-align:right;color:#a0aec0">0</td>
  <td id="fe-alloc-{ptf["id"]}"><div class="ptf-pct-bar"><div class="ptf-mini-bar ptf-bar-fe" style="width:84px"></div><span style="font-size:12px;font-weight:600;min-width:28px">30 %</span></div></td>
</tr>\n''')

    html_parts.append(f'''<tr class="dop-row">
  <td></td>
  <td style="font-size:13px;text-align:center">★</td>
  <td class="fund-name">💎 DOP</td>
  <td style="text-align:center"><span class="srri-badge" style="background:#7c3aed">2</span></td>
  <td style="text-align:right" id="dop-ytd-{ptf["id"]}">—</td>
  <td style="text-align:right" id="dop-a1-{ptf["id"]}">—</td>
  <td style="text-align:right" id="dop-a3-{ptf["id"]}">—</td>
  <td style="text-align:right" id="dop-a5-{ptf["id"]}">—</td>
  <td style="text-align:right;color:#a0aec0">≈0</td>
  <td style="text-align:right;color:#a0aec0">0</td>
  <td id="dop-alloc-{ptf["id"]}"><span style="color:#cbd5e0;font-size:12px;padding-left:4px">—</span></td>
</tr>\n''')

    for rank, name, srri, ytd, a1, a3, a5, pct, vol, mdd in ptf["funds"]:
        sc = _SRRI_COLORS_PTF.get(srri, "#94a3b8")
        bar_w = pct * 3
        _ytd_f = _parse_pct(ytd); _a1_f = _parse_pct(a1)
        _a3_f  = _parse_pct(a3);  _a5_f = _parse_pct(a5)
        def _dv(v): return str(v) if v is not None else "null"
        _ftype_lbl = _FTYPE_LABELS.get(srri, "")
        _vol_html = f'{vol:.1f}%'.replace(".", ",") if vol is not None else '<span class="na">—</span>'
        _mdd_html = (f'<span class="neg">{mdd:.1f}%</span>'.replace(".", ",") if mdd is not None and mdd < 0
                     else ('0,0%' if mdd is not None else '<span class="na">—</span>'))
        html_parts.append(f'''<tr class="uc-row ftype-{srri}" data-pct="{pct}" data-ytd="{_dv(_ytd_f)}" data-a1="{_dv(_a1_f)}" data-a3="{_dv(_a3_f)}" data-a5="{_dv(_a5_f)}">
  <td style="text-align:center;padding:0 4px"><input type="checkbox" class="chk-fund" id="chk-{cc}-{rank}" checked onchange="updateFE()"></td>
  <td style="font-size:11px;color:#a0aec0">{rank}</td>
  <td class="fund-name">{name}<span class="ftype-badge ftype-badge-{srri}">{_ftype_lbl}</span></td>
  <td style="text-align:center"><span class="srri-badge" style="background:{sc}">{srri}</span></td>
  <td style="text-align:right">{_ptf_perf(ytd)}</td>
  <td style="text-align:right">{_ptf_perf(a1)}</td>
  <td style="text-align:right">{_ptf_perf(a3)}</td>
  <td style="text-align:right">{_ptf_perf(a5)}</td>
  <td style="text-align:right;font-size:12px;color:#718096">{_vol_html}</td>
  <td style="text-align:right;font-size:12px">{_mdd_html}</td>
  <td id="alloc-{cc}-{rank}"><div class="alloc-wrap"><div class="ptf-pct-bar"><div class="ptf-mini-bar ptf-bar-{cc}" id="bar-{cc}-{rank}" style="width:{bar_w}px"></div><span id="pct-{cc}-{rank}" style="font-size:12px;font-weight:600;min-width:28px">{pct}&nbsp;%</span></div><input type="number" class="manual-alloc" id="minput-{cc}-{rank}" min="0" max="100" step="0.5" placeholder="%" oninput="updateFE()" title="Allocation manuelle — laisser vide pour auto"></div></td>
</tr>\n''')

    html_parts.append('</tbody></table></div>\n')
    html_parts.append(f'<p style="font-size:11px;color:#a0aec0;margin-top:8px;padding:0 4px">{ptf["note"]}. Performances passées cumulées, non garanties.</p>\n')
    html_parts.append('</div>\n')  # end ptf-panel

# ── Simulateur de projection (générique, réutilisé pour types & perso) ──────
def _sim_block(prefix, note):
    return f'''<div class="sim-box">
  <div class="sim-title">📈 Simulateur de projection</div>
  <div class="sim-hint" id="sim{prefix}-hint">{note}</div>
  <div class="sim-row">
    <label>Versement initial</label><input id="sim{prefix}-init" type="number" min="0" step="500" value="10000" oninput="simCompute('{prefix}')"><span style="font-size:12px">€</span>
    <label>Versement mensuel</label><input id="sim{prefix}-monthly" type="number" min="0" step="50" value="200" oninput="simCompute('{prefix}')"><span style="font-size:12px">€</span>
    <label>Horizon</label><input id="sim{prefix}-years" type="number" min="1" max="40" value="10" oninput="simCompute('{prefix}')"><span style="font-size:12px">ans</span>
    <label>Rendement annuel</label><input id="sim{prefix}-rate" type="number" step="0.1" value="5.0" oninput="simCompute('{prefix}')"><span style="font-size:12px">%</span>
    <button class="perso-action-btn primary" onclick="simUseActive('{prefix}')">↺ Utiliser le portefeuille affiché</button>
  </div>
  <div class="sim-kpis" id="sim{prefix}-kpis"></div>
  <div class="table-wrap" style="margin-bottom:0"><table class="sim-table" id="sim{prefix}-table"></table></div>
  <div class="sim-note">Projection théorique à rendement constant, hors frais et fiscalité. Les performances passées ne préjugent pas des performances futures.</div>
</div>\n'''

html_parts.append(_sim_block("T", "Basé sur le rendement pondéré du portefeuille type affiché (1 an, ou 3 ans annualisé)."))
html_parts.append('</div>\n')  # end sec_portefeuilles

# ── Section Portefeuille Perso ────────────────────────────────────────────────
html_parts.append('''<div class="section" id="sec_perso">
  <div class="perso-tab-bar" id="perso-tab-bar"></div>
  <div id="perso-panels"></div>
''')
html_parts.append(_sim_block("P", "Basé sur le rendement pondéré du portefeuille perso affiché."))
html_parts.append('''</div>

<div class="perso-modal-overlay hidden" id="perso-modal">
  <div class="perso-modal-box">
    <div class="perso-modal-header">
      <h3>🔍 Sélectionner les fonds</h3>
      <button class="perso-modal-close" onclick="PersoMgr.closeSelector()">✕</button>
    </div>
    <div class="perso-modal-body" id="perso-modal-funds"></div>
    <div class="perso-modal-footer">
      <button class="perso-action-btn" onclick="PersoMgr.closeSelector()">Annuler</button>
      <button class="perso-action-btn primary" onclick="PersoMgr.applySelector()">✓ Valider la sélection</button>
    </div>
  </div>
</div>
''')

# ── JavaScript ────────────────────────────────────────────────────────────────
bar_js  = json.dumps(all_bar_charts,  ensure_ascii=False)
line_js = json.dumps(all_line_charts, ensure_ascii=False)

# ── Données globales fonds (pour recherche + filtre SRRI) ─────────────────
all_funds_list = []
for cat in CATEGORIES:
    for f in cat["funds"]:
        all_funds_list.append({
            "isin": f["isin"], "name": f["name"], "mgr": f.get("mgr",""),
            "cat_label": cat["label"], "cat_id": cat["id"],
            "srri": f.get("srri"), "vl": f.get("vl"),
            "ytd": f.get("ytd"), "m1": f.get("m1"), "m6": f.get("m6"),
            "a1": f.get("a1"), "a3": f.get("a3"), "a5": f.get("a5"),
            "eom": f.get("perf_eom") or {}, "gli": f.get("perf_gli") or {},
            "bid": f.get("bid"), "vl_date": f.get("vl_date"),
            "vol": f.get("vol"), "mdd": f.get("mdd"),
        })
all_funds_js = json.dumps(all_funds_list, ensure_ascii=False)

# ── Moteur de graphiques Canvas pur (sans dépendance) ──────────────────────
html_parts.append("""<script>
/* =========================================================
   TinyChart — moteur Canvas autonome
   Supporte : hbar (barres horizontales) + line (courbes)
   ========================================================= */
(function(global){
'use strict';
const DPR = window.devicePixelRatio || 1;

function hex2rgba(hex, a) {
  hex = hex.replace('#','');
  if (hex.length === 3) hex = hex.split('').map(c=>c+c).join('');
  const r=parseInt(hex.slice(0,2),16), g=parseInt(hex.slice(2,4),16), b=parseInt(hex.slice(4,6),16);
  return 'rgba('+r+','+g+','+b+','+a+')';
}
function rRect(ctx, x, y, w, h, r) {
  if (ctx.roundRect) { ctx.roundRect(x,y,w,h,r); }
  else { ctx.rect(x,y,w,h); }
}
function niceTicks(mn, mx, n) {
  const range = mx - mn || 1;
  let step = Math.pow(10, Math.floor(Math.log10(range/n)));
  for (const f of [1,2,5,10]) { if (range/(step*f) <= n) { step*=f; break; } }
  const start = Math.ceil(mn/step)*step;
  const ticks = [];
  for (let v=start; v<=mx+step*0.01; v+=step) ticks.push(Math.round(v*10000)/10000);
  return ticks;
}
function pct(v) { return (v>=0?'+':'')+v.toFixed(2)+'%'; }

class TinyChart {
  constructor(canvas, cfg) {
    this.canvas  = canvas;
    this.ctx     = canvas.getContext('2d');
    this.type    = cfg.type;
    this.labels   = cfg.labels   || [];
    this.datasets = cfg.datasets || [];
    this.xWeights = cfg.xWeights || null;
    this._hov    = -1;
    this._hovX   = -1;
    canvas.addEventListener('mousemove', e=>this._onMove(e));
    canvas.addEventListener('mouseleave',()=>{ this._hov=-1; this._hovX=-1; this.render(); });
    this._resize();
  }
  _resize() {
    const p = this.canvas.parentElement;
    const W = p.clientWidth || 400;
    const n = this.type==='hbar' ? (this.datasets[0]?.data?.length||5) : 0;
    const H = this.type==='hbar' ? Math.max(160, n*28+60) : 300;
    this.canvas.style.width  = W+'px';
    this.canvas.style.height = H+'px';
    this.canvas.width  = Math.round(W*DPR);
    this.canvas.height = Math.round(H*DPR);
    this.ctx.setTransform(DPR,0,0,DPR,0,0);
    this.W=W; this.H=H;
    this.render();
  }
  setData(labels, datasets, xWeights) { this.labels=labels; this.datasets=datasets; this.xWeights=xWeights||null; this._resize(); }
  render() { this.type==='hbar' ? this._drawHBar() : this._drawLine(); }

  /* ── Horizontal Bar ──────────────────────────────────────── */
  _drawHBar() {
    const {ctx,W,H,labels} = this;
    const data   = this.datasets[0]?.data || [];
    const colors = this.datasets[0]?.backgroundColor || [];
    ctx.clearRect(0,0,W,H);
    const PL=190, PR=60, PT=16, PB=28;
    const cW=W-PL-PR, cH=H-PT-PB, n=data.length;
    if (!n) return;
    const barH = Math.max(6, Math.floor(cH/n*0.68));
    const step  = cH/n;
    const valid = data.filter(v=>v!=null&&!isNaN(v));
    if (!valid.length) return;
    const dmin=Math.min(0,...valid), dmax=Math.max(0,...valid);
    const range=dmax-dmin||1;
    const sc = v=>PL+((v-dmin)/range)*cW;
    const zero=sc(0);
    // grid + x ticks
    ctx.strokeStyle='#f0f4f8'; ctx.lineWidth=1;
    ctx.fillStyle='#718096'; ctx.font='10px system-ui'; ctx.textAlign='center';
    niceTicks(dmin,dmax,5).forEach(t=>{
      const x=sc(t);
      ctx.beginPath(); ctx.moveTo(x,PT); ctx.lineTo(x,H-PB); ctx.stroke();
      ctx.fillText((t>=0?'+':'')+t.toFixed(1)+'%', x, H-PB+14);
    });
    // zero
    ctx.strokeStyle='#94a3b8'; ctx.lineWidth=1.5;
    ctx.beginPath(); ctx.moveTo(zero,PT); ctx.lineTo(zero,H-PB); ctx.stroke();
    // bars
    data.forEach((v,i)=>{
      if (v==null||isNaN(v)) return;
      const y=PT+i*step+(step-barH)/2;
      const x0=v>=0?zero:sc(v);
      const bw=Math.max(2,Math.abs(sc(v)-zero));
      const col=colors[i]||'#3266ad';
      if (i===this._hov) {
        ctx.fillStyle=hex2rgba(col,0.12);
        ctx.fillRect(PL,y-2,cW,barH+4);
      }
      ctx.fillStyle=col;
      ctx.beginPath(); rRect(ctx,x0,y,bw,barH,3); ctx.fill();
      // value label
      const lbl=pct(v);
      ctx.fillStyle='#1a202c'; ctx.font='10px system-ui';
      if (v>=0){ ctx.textAlign='left';  ctx.fillText(lbl,x0+bw+4,y+barH/2+4); }
      else     { ctx.textAlign='right'; ctx.fillText(lbl,x0-4,   y+barH/2+4); }
      // fund label
      ctx.fillStyle = i===this._hov?'#3266ad':'#2d3748';
      ctx.font=(i===this._hov?'600 ':'')+'11px system-ui';
      ctx.textAlign='right';
      const nm=labels[i]||'';
      ctx.fillText(nm.length>27?nm.slice(0,26)+'…':nm, PL-8, y+barH/2+4);
    });
  }

  /* ── Line chart ──────────────────────────────────────────── */
  _drawLine() {
    const {ctx,W,H,labels,datasets} = this;
    ctx.clearRect(0,0,W,H);
    const n=labels.length, ds=datasets;
    if (!n||!ds.length) return;
    const legRows=Math.ceil(ds.length/3);
    const LEGH=legRows*20+10;
    // PR élargi : la dernière étiquette de l'axe X est centrée sur le dernier
    // point et doit tenir entièrement dans le canvas.
    const PL=50, PR=30, PT=14, PB=30+LEGH;
    const cW=W-PL-PR, cH=H-PT-PB;
    const allV=ds.flatMap(d=>(d.data||[]).filter(v=>v!=null&&!isNaN(v)));
    if (!allV.length) return;
    const dmin=Math.min(...allV), dmax=Math.max(...allV);
    const pad=(dmax-dmin||1)*0.08;
    const ymin=dmin-pad, ymax=dmax+pad, yr=ymax-ymin;
    // Axe X : positions proportionnelles au temps si xWeights disponible
    const W0=this.xWeights;
    const xP=i=>PL+(n===1?cW/2:(W0?W0[i]:i/(n-1))*cW);
    const yP=v=>PT+cH-((v-ymin)/yr)*cH;
    // y grid
    ctx.strokeStyle='#edf2f7'; ctx.lineWidth=1;
    ctx.fillStyle='#718096'; ctx.font='10px system-ui'; ctx.textAlign='right';
    niceTicks(ymin,ymax,8).forEach(t=>{
      const y=yP(t);
      if (y<PT||y>PT+cH) return;
      ctx.beginPath(); ctx.moveTo(PL,y); ctx.lineTo(PL+cW,y); ctx.stroke();
      ctx.fillText((t>=0?'+':'')+t.toFixed(1)+'%', PL-4, y+3);
    });
    // zero dashed
    if (ymin<0&&ymax>0) {
      ctx.strokeStyle='#94a3b8'; ctx.lineWidth=1.5; ctx.setLineDash([3,3]);
      ctx.beginPath(); ctx.moveTo(PL,yP(0)); ctx.lineTo(PL+cW,yP(0)); ctx.stroke();
      ctx.setLineDash([]);
    }
    // Espacement des libellés : au moins 46 px entre deux étiquettes, ancré
    // sur la dernière date pour qu'elle soit toujours affichée.
    const maxLbl=Math.max(2,Math.floor(cW/46));
    const lblStep=Math.max(1,Math.ceil(n/maxLbl));
    const showLbl=i=>(n-1-i)%lblStep===0;
    // x vertical grid lines (légères) — uniquement sous les libellés affichés
    ctx.strokeStyle='#edf2f7'; ctx.lineWidth=1; ctx.setLineDash([2,4]);
    for(let i=0;i<n;i++){
      if(!showLbl(i)) continue;
      ctx.beginPath(); ctx.moveTo(xP(i),PT); ctx.lineTo(xP(i),PT+cH); ctx.stroke();
    }
    ctx.setLineDash([]);
    // x labels
    ctx.fillStyle='#4a5568'; ctx.font='bold 11px system-ui'; ctx.textAlign='center';
    labels.forEach((l,i)=>{ if(showLbl(i)) ctx.fillText(l, xP(i), PT+cH+16); });
    // x axis
    ctx.strokeStyle='#e2e8f0'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(PL,PT+cH); ctx.lineTo(PL+cW,PT+cH); ctx.stroke();
    // hover column
    let hovXIdx=-1;
    if (this._hovX>=0) {
      let md=Infinity;
      for(let i=0;i<n;i++){ const d=Math.abs(xP(i)-this._hovX); if(d<md){md=d;hovXIdx=i;} }
      if (md>44) hovXIdx=-1;
      else {
        ctx.strokeStyle='#e2e8f0'; ctx.lineWidth=1; ctx.setLineDash([4,4]);
        ctx.beginPath(); ctx.moveTo(xP(hovXIdx),PT); ctx.lineTo(xP(hovXIdx),PT+cH); ctx.stroke();
        ctx.setLineDash([]);
      }
    }
    // ── Interpolation Catmull-Rom : calcule des valeurs intermédiaires ────────
    // Génère STEPS points entre chaque paire de données connues consécutives,
    // donnant une courbe continue et naturelle (pas juste des points reliés).
    const SMOOTH_STEPS = 12;
    function crVal(p0,p1,p2,p3,t) {
      return 0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t);
    }
    function buildInterpPts(rawData) {
      // Collecter tous les points connus avec leur position x canvas
      const kn=[];
      rawData.forEach((v,i)=>{ if(v!=null&&!isNaN(v)) kn.push({x:xP(i),v}); });
      if(kn.length<2) return kn.map(p=>({x:p.x,y:yP(p.v)}));
      const out=[];
      for(let i=0;i<kn.length-1;i++){
        const p0=kn[Math.max(0,i-1)];
        const p1=kn[i];
        const p2=kn[i+1];
        const p3=kn[Math.min(kn.length-1,i+2)];
        for(let s=0;s<SMOOTH_STEPS;s++){
          const t=s/SMOOTH_STEPS;
          const x=p1.x+(p2.x-p1.x)*t;
          const v=crVal(p0.v,p1.v,p2.v,p3.v,t);
          out.push({x,y:yP(v)});
        }
      }
      // Dernier point connu
      const last=kn[kn.length-1];
      out.push({x:last.x,y:yP(last.v)});
      return out;
    }
    // Tracer les lignes interpolées
    ds.forEach(d=>{
      ctx.strokeStyle=d.borderColor||'#3266ad'; ctx.lineWidth=d.borderWidth||2;
      ctx.lineJoin='round';
      const pts=buildInterpPts(d.data||[]);
      if(!pts.length) return;
      ctx.beginPath();
      ctx.moveTo(pts[0].x,pts[0].y);
      for(let k=1;k<pts.length;k++) ctx.lineTo(pts[k].x,pts[k].y);
      ctx.stroke();
    });
    // dots + valeurs sur chaque point
    ds.forEach(d=>{
      (d.data||[]).forEach((v,i)=>{
        if(v==null||isNaN(v)) return;
        const isHov=i===hovXIdx;
        const pr=(d.pointRadius==null)?4:d.pointRadius;
        if(pr<=0 && !isHov) return;   // séries denses : pas de pastilles
        const r=isHov?6:pr;
        ctx.beginPath(); ctx.arc(xP(i),yP(v),r,0,Math.PI*2);
        ctx.fillStyle='#fff'; ctx.fill();
        ctx.strokeStyle=d.borderColor||'#3266ad'; ctx.lineWidth=2; ctx.stroke();
        // Valeur affichée sur le point (sauf si trop de courbes → lisibilité)
        if ((ds.length<=6 && pr>0) || isHov) {
          const txt=(v>=0?'+':'')+v.toFixed(1)+'%';
          ctx.font=isHov?'bold 10px system-ui':'9px system-ui';
          ctx.fillStyle=d.borderColor||'#3266ad';
          ctx.textAlign='center';
          // Décaler vers le haut ou bas selon la position relative
          const yOff = yP(v) < PT+cH*0.5 ? r+10 : -(r+3);
          ctx.fillText(txt, xP(i), yP(v)+yOff);
        }
      });
    });
    // tooltip
    if (hovXIdx>=0) {
      const tips=ds.map(d=>({l:d.label,v:(d.data||[])[hovXIdx],c:d.borderColor}))
                   .filter(d=>d.v!=null&&!isNaN(d.v)).sort((a,b)=>b.v-a.v);
      if (tips.length) {
        const tx0=xP(hovXIdx), TP=8, LH=15, TW=210;
        const TH=TP*2+18+tips.length*LH;
        let tx=tx0+14; if(tx+TW>W-4) tx=tx0-TW-14;
        const ty=PT+6;
        ctx.fillStyle='rgba(255,255,255,0.97)'; ctx.shadowColor='rgba(0,0,0,0.1)'; ctx.shadowBlur=8;
        ctx.beginPath(); rRect(ctx,tx,ty,TW,TH,6); ctx.fill(); ctx.shadowBlur=0;
        ctx.strokeStyle='#e2e8f0'; ctx.lineWidth=1; ctx.stroke();
        ctx.fillStyle='#1a202c'; ctx.font='600 11px system-ui'; ctx.textAlign='left';
        ctx.fillText(labels[hovXIdx], tx+TP, ty+TP+11);
        tips.forEach((d,i)=>{
          const ly=ty+TP+18+i*LH+9;
          ctx.beginPath(); ctx.arc(tx+TP+4,ly-2,4,0,Math.PI*2);
          ctx.fillStyle=d.c; ctx.fill();
          ctx.fillStyle='#4a5568'; ctx.font='10px system-ui'; ctx.textAlign='left';
          const nm=d.l.length>20?d.l.slice(0,19)+'…':d.l;
          ctx.fillText(nm+' : '+pct(d.v), tx+TP+12, ly);
        });
      }
    }
    // legend
    const LY=H-LEGH+6;
    const iW=Math.floor(W/3);
    ds.forEach((d,i)=>{
      const col=i%3, row=Math.floor(i/3);
      const lx=col*iW+8, ly=LY+row*20+10;
      ctx.strokeStyle=d.borderColor||'#3266ad'; ctx.lineWidth=2;
      ctx.beginPath(); ctx.moveTo(lx,ly); ctx.lineTo(lx+16,ly); ctx.stroke();
      ctx.beginPath(); ctx.arc(lx+8,ly,3,0,Math.PI*2);
      ctx.fillStyle=d.borderColor; ctx.fill();
      ctx.fillStyle='#4a5568'; ctx.font='10px system-ui'; ctx.textAlign='left';
      const nm=d.label.length>22?d.label.slice(0,21)+'…':d.label;
      ctx.fillText(nm, lx+22, ly+3);
    });
  }

  _onMove(e) {
    const rect=this.canvas.getBoundingClientRect();
    const x=e.clientX-rect.left, y=e.clientY-rect.top;
    if (this.type==='hbar') {
      const n=this.datasets[0]?.data?.length||0;
      const step=(this.H-44)/n;
      const idx=Math.floor((y-16)/step);
      if(idx>=0&&idx<n&&idx!==this._hov){this._hov=idx;this.render();}
    } else {
      this._hovX=x; this.render();
    }
  }
}
global.TinyChart=TinyChart;
})(window);
</script>
""")

html_parts.append(f"""<script>
// ── Données globales pour filtres ─────────────────────────────────────────
const ALL_FUNDS = {all_funds_js};

// ── Filtre SRRI + Recherche ────────────────────────────────────────────────
let activeSRRI = null;

const SRRI_COLORS = {{'1':'#22c55e','2':'#84cc16','3':'#eab308','4':'f59e0b','5':'#f97316','6':'#ef4444','7':'#991b1b'}};

function srriColor(s) {{
  const map = {{'1':'#22c55e','2':'#84cc16','3':'#eab308','4':'#f59e0b','5':'#f97316','6':'#ef4444','7':'#991b1b'}};
  return map[String(s)] || '#94a3b8';
}}

function toggleSRRI(n) {{
  activeSRRI = (activeSRRI === n) ? null : n;
  document.querySelectorAll('.srri-btn').forEach(b => {{
    b.classList.toggle('active', parseInt(b.dataset.srri) === activeSRRI);
  }});
  applyFilters();
}}

function applyFilters() {{
  const q = document.getElementById('searchInput').value.trim().toLowerCase();
  const hasSRRI = activeSRRI !== null;
  const hasSearch = q.length > 0;

  if (!hasSRRI && !hasSearch) {{
    clearFilters();
    return;
  }}

  // Filtrer les fonds — recherche et SRRI sont indépendants :
  // si texte saisi → cherche dans TOUS les fonds (ignore SRRI)
  // si SRRI seulement → filtre par niveau de risque
  let results;
  if (hasSearch) {{
    results = ALL_FUNDS.filter(f =>
      f.name.toLowerCase().includes(q) || f.isin.toLowerCase().includes(q)
    );
  }} else {{
    results = ALL_FUNDS.filter(f => f.srri === activeSRRI);
  }}

  // Cacher les onglets, montrer les résultats
  document.getElementById('mainTabs').style.display = 'none';
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  const fr = document.getElementById('filterResults');
  fr.classList.add('active');

  // Compter et afficher
  const modeLabel = hasSearch ? ` · recherche "${'{q}'}"` : (hasSRRI ? ` · SRRI ${'{activeSRRI}'}` : '');
  document.getElementById('filterCount').innerHTML =
    `<strong>${'{results.length}'}</strong> fonds trouvés${'{modeLabel}'}`;

  const fmt = (v, dec=2) => v == null ? '<span class="na">—</span>'
    : `<span class="${'{v >= 0 ? "pos" : "neg"}'}">${'{v >= 0 ? "+" : ""}'}${{v.toFixed(dec)}}%</span>`;
  const fmtVL = v => v == null ? '—' : v >= 1000 ? v.toLocaleString('fr-FR',{{minimumFractionDigits:2}}) + ' €' : v.toFixed(2) + ' €';

  const tbody = document.getElementById('filteredBody');
  tbody.innerHTML = results.map((f, i) => {{
    const bid = f.bid;
    const sc = srriColor(f.srri);
    return `<tr>
      <td data-val="${'{i+1}'}">${'{i+1}'}</td>
      <td class="fund-name" data-val="${'{f.name}'}">${{bid ? `<a href="https://www.boursorama.com/bourse/opcvm/cours/${{bid}}/" target="_blank" class="fund-name-link">${{f.name}}</a>` : f.name}}<br><span class="isin-cell">${'{f.isin}'}</span></td>
      <td data-val="${'{f.cat_label}'}" style="font-size:11px;color:#718096">${'{f.cat_label}'}</td>
      <td style="text-align:center" data-val="${'{f.srri}'}">${{`<span class="srri-badge" style="background:${{sc}}">${{f.srri}}</span>`}}</td>
      <td style="text-align:right" data-val="${'{f.vl || 0}'}">${{fmtVL(f.vl)}}</td>
      <td style="text-align:right" data-val="${'{pv(f,"ytd") ?? -9999}'}">${{fmt(pv(f,'ytd'))}}</td>
      <td style="text-align:right" data-val="${'{pv(f,"m1") ?? -9999}'}">${{fmt(pv(f,'m1'))}}</td>
      <td style="text-align:right" data-val="${'{pv(f,"m6") ?? -9999}'}">${{fmt(pv(f,'m6'))}}</td>
      <td style="text-align:right" data-val="${'{pv(f,"a1") ?? -9999}'}">${{fmt(pv(f,'a1'))}}</td>
      <td style="text-align:right" data-val="${'{pv(f,"a3") ?? -9999}'}">${{fmt(pv(f,'a3'))}}</td>
      <td style="text-align:right" data-val="${'{pv(f,"a5") ?? -9999}'}">${{fmt(pv(f,'a5'))}}</td>
      <td style="text-align:right;color:#718096" data-val="${'{f.vol ?? -9999}'}">${{f.vol != null ? f.vol.toFixed(1).replace('.',',') + '%' : '<span class="na">—</span>'}}</td>
      <td style="text-align:right" data-val="${'{f.mdd ?? -9999}'}">${{f.mdd != null ? (f.mdd < 0 ? '<span class="neg">' + f.mdd.toFixed(1).replace('.',',') + '%</span>' : '0,0%') : '<span class="na">—</span>'}}</td>
    </tr>`;
  }}).join('');
}}

function clearFilters() {{
  activeSRRI = null;
  document.getElementById('searchInput').value = '';
  document.querySelectorAll('.srri-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('filterResults').classList.remove('active');
  document.getElementById('mainTabs').style.display = '';
  // Re-activer le premier onglet si aucun n'est actif
  const firstActive = document.querySelector('.section.active');
  if (!firstActive) {{
    const firstTab = document.querySelector('.tab');
    if (firstTab) firstTab.click();
  }}
}}

// ── Tab switching ──────────────────────────────────────────────────────────
function showTab(id) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.view-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  const tabEl = document.getElementById('tab_'+id);
  if (tabEl) tabEl.classList.add('active');
  document.getElementById('sec_'+id).classList.add('active');
  // Force redraw after layout recalc (ResizeObserver unreliable on display:none → block)
  requestAnimationFrame(() => {{
    if (barInstances[id])  barInstances[id]._resize();
    if (lineInstances[id]) lineInstances[id]._resize();
  }});
}}

// ── Table sort ─────────────────────────────────────────────────────────────
function sortTable(tableId, col) {{
  const tbl = document.getElementById(tableId);
  const tbody = tbl.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));
  const th = tbl.querySelectorAll('th')[col];
  const asc = !th.classList.contains('sorted-asc');
  tbl.querySelectorAll('th').forEach(t => t.classList.remove('sorted-asc','sorted-desc'));
  th.classList.add(asc ? 'sorted-asc' : 'sorted-desc');
  rows.sort((a,b) => {{
    const av = a.querySelectorAll('td')[col]?.dataset.val || '';
    const bv = b.querySelectorAll('td')[col]?.dataset.val || '';
    const an = parseFloat(av), bn = parseFloat(bv);
    if (!isNaN(an) && !isNaN(bn)) return asc ? an - bn : bn - an;
    return asc ? av.localeCompare(bv) : bv.localeCompare(av);
  }});
  rows.forEach(r => tbody.appendChild(r));
}}

// ── Bar charts (TinyChart) ─────────────────────────────────────────────────
const BAR_CHARTS = {bar_js};
const barInstances = {{}};

// ── Convention de performance active : 'eom' (à la fin de mois) | 'gli' (glissantes)
let PERF_MODE = 'eom';
const PERF_MODE_HELP = {{
  eom: "Arrêtées à la dernière VL du mois précédent — stables d'un jour à l'autre.",
  gli: "Arrêtées à la dernière VL connue — cohérentes avec la VL affichée, mais elles bougent chaque jour."
}};
function barPeriods(c) {{
  return (c.periodsByMode && c.periodsByMode[PERF_MODE]) || c.periods;
}}
// Valeur d'un fonds dans la convention active (ALL_FUNDS)
function pv(f, k) {{
  const src = (PERF_MODE === 'gli' ? f.gli : f.eom) || {{}};
  let v = src[k];
  if (v === undefined || v === null) v = (k === 'ytd' ? f.ytd : null);
  return (v === undefined) ? null : v;
}}

BAR_CHARTS.forEach(c => {{
  const canvas = document.getElementById(c.id);
  if (!canvas) return;
  const catId = c.id.replace('bar_','');
  const pd = barPeriods(c)['YTD'];
  barInstances[catId] = new TinyChart(canvas, {{
    type: 'hbar',
    labels: c.labels,
    datasets: [{{ data: pd.data, backgroundColor: pd.colors }}]
  }});
}});

const BAR_PERIOD_TITLES = {{'YTD':'YTD (au {_fmt_date_short(_VL_OVERRIDE_DATE)})','1M':'1 Mois','6M':'6 Mois','1A':'1 An','3A':'3 Ans','5A':'5 Ans'}};

function filterBarPeriod(catId, period) {{
  document.querySelectorAll('.period-btn[data-cat="'+catId+'"][data-bperiod]').forEach(b => {{
    b.classList.toggle('active', b.dataset.bperiod === period);
  }});
  const chart = barInstances[catId];
  if (!chart) return;
  const barDef = BAR_CHARTS.find(c => c.id === 'bar_'+catId);
  if (!barDef) return;
  const pd = barPeriods(barDef)[period];
  chart.setData(barDef.labels, [{{ data: pd.data, backgroundColor: pd.colors }}]);
  const el = document.getElementById('bartitle_'+catId);
  if (el) el.textContent = 'Performance ' + BAR_PERIOD_TITLES[period];
}}

function setPerfMode(mode) {{
  if (mode !== 'eom' && mode !== 'gli') return;
  PERF_MODE = mode;
  document.querySelectorAll('.period-btn[data-pmode]').forEach(b =>
    b.classList.toggle('active', b.dataset.pmode === mode));
  const help = document.getElementById('perfmodeHelp');
  if (help) help.textContent = PERF_MODE_HELP[mode];

  // Cellules de performance des tableaux par catégorie
  const attr = (mode === 'gli') ? 'g' : 'e';
  document.querySelectorAll('td.perf-cell[data-k]').forEach(td => {{
    const raw = td.dataset[attr];
    if (raw === undefined || raw === '') {{
      td.innerHTML = '<span class="na">—</span>';
      td.dataset.val = '-9999';
      return;
    }}
    const v = parseFloat(raw);
    td.dataset.val = String(v);
    const cls = v > 0 ? 'pos' : (v < 0 ? 'neg' : 'neu');
    td.innerHTML = '<span class="' + cls + '">' + (v >= 0 ? '+' : '') + v.toFixed(2) + '%</span>';
  }});

  // Graphiques en barres
  BAR_CHARTS.forEach(c => {{
    const catId = c.id.replace('bar_','');
    const inst = barInstances[catId];
    if (!inst) return;
    const btn = document.querySelector('.period-btn[data-cat="'+catId+'"][data-bperiod].active');
    const per = btn ? btn.dataset.bperiod : 'YTD';
    const pd = barPeriods(c)[per];
    if (pd) inst.setData(c.labels, [{{ data: pd.data, backgroundColor: pd.colors }}]);
  }});

  // Tableau de résultats (recherche / SRRI)
  const fr = document.getElementById('filterResults');
  if (fr && fr.classList.contains('active')) applyFilters();
}}

// ── Line charts (TinyChart) — évolution de la VL réelle ────────────────────
// Chaque courbe est rebasée à 0 % sur la PREMIÈRE date de la fenêtre affichée.
// Un fonds sans VL à cette date est exclu du graphique (et signalé), plutôt que
// rebasé sur sa propre date de départ : sinon les % ne sont pas comparables.
const LINE_CHARTS = {line_js};
const lineInstances = {{}};
const lineMeta      = {{}};

// Nombre de points mensuels affichés par période (n mois + le point de base)
const LINE_COUNT = {{'3M':4, '6M':7, '1A':13, '3A':37, '5A':61}};

function lineBuild(catId, period) {{
  const meta = lineMeta[catId];
  if (!meta) return null;
  const total = meta.labels.length;
  const n     = LINE_COUNT[period] || total;
  const start = Math.max(0, total - n);
  const labels = meta.labels.slice(start);
  const ds = [];
  let excluded = 0;
  meta.datasets.forEach(d => {{
    const win  = d.vl.slice(start);
    const base = win[0];
    if (base == null || base === 0) {{ excluded++; return; }}
    ds.push({{
      label:       d.label,
      data:        win.map(v => v == null ? null : Math.round((v / base - 1) * 10000) / 100),
      borderColor: d.borderColor,
      borderWidth: d.borderWidth || 2,
      pointRadius: labels.length > 24 ? 0 : 2
    }});
  }});
  return {{ labels: labels, ds: ds, excluded: excluded, from: meta.dates[start], to: meta.dates[total-1] }};
}}

function lineNote(catId, built, period) {{
  const el = document.getElementById('linenote_' + catId);
  if (!el || !built) return;
  const per = {{'3M':'3 mois','6M':'6 mois','1A':'1 an','3A':'3 ans','5A':'5 ans'}}[period] || period;
  let txt = built.ds.length + ' fonds sur ' + per + ' · base 0 % au ' + (built.from || '?');
  if (built.excluded > 0) {{
    txt += ' · ' + built.excluded + ' fonds non affiché' + (built.excluded > 1 ? 's' : '')
        + ' (pas de VL à cette date de départ)';
  }}
  el.textContent = txt;
}}

LINE_CHARTS.forEach(c => {{
  const canvas = document.getElementById(c.id);
  if (!canvas || !c.datasets.length) return;
  const catId = c.id.replace('line_','');
  lineMeta[catId] = {{
    labels:   c.labels || [],
    dates:    c.dates  || [],
    datasets: c.datasets.map(d => ({{
      label: d.label, vl: (d.vl || d.fullData || d.data || []).slice(),
      borderColor: d.borderColor, borderWidth: d.borderWidth || 2
    }}))
  }};
  const built = lineBuild(catId, '1A');
  lineInstances[catId] = new TinyChart(canvas, {{
    type: 'line', labels: built.labels, xWeights: null, datasets: built.ds
  }});
  lineNote(catId, built, '1A');
}});

function filterLinePeriod(catId, period) {{
  document.querySelectorAll('.period-btn[data-cat="'+catId+'"][data-period]').forEach(b => {{
    b.classList.toggle('active', b.dataset.period === period);
  }});
  const chart = lineInstances[catId];
  if (!chart) return;
  const built = lineBuild(catId, period);
  if (!built) return;
  chart.setData(built.labels, built.ds, null);
  lineNote(catId, built, period);
}}

// ── Portfolio tabs ────────────────────────────────────────────────────────────
function ptfShow(id) {{
  document.querySelectorAll('.ptf-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.ptf-panel').forEach(p => p.classList.remove('active'));
  const btn = document.querySelector('.ptf-tab.t-'+id);
  if (btn) btn.classList.add('active');
  const panel = document.getElementById('ptf_'+id);
  if (panel) panel.classList.add('active');
  if (typeof simSync === 'function') simSync('T');
}}

// ── Resize fenêtre (debounce 120ms — sans boucle) ─────────────────────────
let _rTimer;
window.addEventListener('resize', () => {{
  clearTimeout(_rTimer);
  _rTimer = setTimeout(() => {{
    const activeTab = document.querySelector('.tab.active');
    if (!activeTab) return;
    const id = activeTab.id.replace('tab_','');
    if (barInstances[id])  barInstances[id]._resize();
    if (lineInstances[id]) lineInstances[id]._resize();
  }}, 120);
}});

// ── Init : redessiner le premier onglet après layout complet ───────────────
window.addEventListener('load', () => {{
  const firstId = '{CATEGORIES[0]["id"]}';
  if (barInstances[firstId])  barInstances[firstId]._resize();
  if (lineInstances[firstId]) lineInstances[firstId]._resize();
  updateFE();
}});

// ── Fonds en Euros — recalcul dynamique ───────────────────────────────────
const _PTF_DATA = {_PTF_DATA_JS};

// Table taux Le Conservateur 2025 (source : communiqué presse 22/01/2026)
// Clé = UC% minimum, valeur = [taux_encours_bas, taux_encours_haut]
const _FE_RATES = [
  {{ ucMin: 70, rates: [4.00, 4.25] }},
  {{ ucMin: 60, rates: [3.75, 4.00] }},
  {{ ucMin: 50, rates: [3.25, 3.50] }},
  {{ ucMin: 40, rates: [2.00, 2.25] }},
  {{ ucMin:  0, rates: [1.10, 1.10] }},
];
const _FE_TRANCHE_LABELS = [
  {{ ucMin: 70, label: 'UC ≥ 70 %' }},
  {{ ucMin: 60, label: '60 % ≤ UC < 70 %' }},
  {{ ucMin: 50, label: '50 % ≤ UC < 60 %' }},
  {{ ucMin: 40, label: '40 % ≤ UC < 50 %' }},
  {{ ucMin:  0, label: 'UC < 40 %' }},
];

let _feHighEncours = false;

function setEncours(high) {{
  _feHighEncours = high;
  document.getElementById('feEncLow') ?.classList.toggle('active', !high);
  document.getElementById('feEncHigh')?.classList.toggle('active',  high);
  updateFE();
}}

function _getFERate(ucPct) {{
  const row = _FE_RATES.find(r => ucPct >= r.ucMin) || _FE_RATES[_FE_RATES.length - 1];
  return row.rates[_feHighEncours ? 1 : 0];
}}
function _getFETranche(ucPct) {{
  const row = _FE_TRANCHE_LABELS.find(r => ucPct >= r.ucMin) || _FE_TRANCHE_LABELS[_FE_TRANCHE_LABELS.length - 1];
  return row.label;
}}

function updateFE() {{
  const feAlloc  = parseInt(document.getElementById('feSlider')?.value)  || 30;
  const dopAlloc = parseInt(document.getElementById('dopSlider')?.value) || 0;
  const ucForRate = 100 - feAlloc;           // taux FE basé sur FE vs UC uniquement (DOP exclu)
  const ucPct     = 100 - feAlloc - dopAlloc; // allocation UC réelle pour les fonds
  const taux      = _getFERate(ucForRate);

  // Contrôles
  const dispEl = document.getElementById('feAllocVal');
  if (dispEl) dispEl.textContent = feAlloc;
  const dopDispEl = document.getElementById('dopAllocVal');
  if (dopDispEl) dopDispEl.textContent = dopAlloc;
  const tauxEl = document.getElementById('feTauxDisplay');
  if (tauxEl) tauxEl.textContent = taux.toFixed(2).replace('.', ',') + ' %';
  const trancheEl = document.getElementById('feTranche');
  if (trancheEl) trancheEl.textContent = _getFETranche(ucForRate);

  const ucScale  = ucPct / 100;
  const t        = taux / 100;
  const DOP_RATE = 5.0;
  const dopT     = DOP_RATE / 100;

  // YTD fraction
  const now   = new Date();
  const jan1  = new Date(now.getFullYear(), 0, 1);
  const ytdFr = (now - jan1) / (1000 * 60 * 60 * 24 * 365);

  const fePerfs = {{
    ytd: taux * ytdFr,
    a1:  taux,
    a3:  (Math.pow(1 + t,    3) - 1) * 100,
    a5:  (Math.pow(1 + t,    5) - 1) * 100
  }};
  const dopPerfs = {{
    ytd: DOP_RATE * ytdFr,  // intérêts simples
    a1:  DOP_RATE * 1,
    a3:  DOP_RATE * 3,
    a5:  DOP_RATE * 5
  }};

  const fmtFE = v =>
    v == null ? '<span class="na">—</span>' :
    '<span class="' + (v >= 0 ? 'pos' : 'neg') + '">'
      + (v >= 0 ? '+' : '') + v.toFixed(2).replace('.', ',') + '&nbsp;%</span>';

  const fmtKpi = v =>
    '<span class="' + (v >= 0 ? 'pos' : 'neg') + '">'
      + (v >= 0 ? '+' : '') + v.toFixed(1).replace('.', ',') + '&nbsp;%</span>';

  const mkBar = (pct, cls) =>
    '<div class="ptf-pct-bar"><div class="ptf-mini-bar ptf-bar-' + cls + '" style="width:' + Math.round(pct * 2.04) + 'px"></div>'
    + '<span style="font-size:12px;font-weight:600;min-width:28px">' + pct + '&nbsp;%</span></div>';

  const emptyBar = '<span style="color:#cbd5e0;font-size:12px;padding-left:4px">—</span>';

  Object.entries(_PTF_DATA).forEach(([pid, pd]) => {{

    // ── FE row
    ['ytd', 'a1', 'a3', 'a5'].forEach(k => {{
      const el = document.getElementById('fe-' + k + '-' + pid);
      if (el) el.innerHTML = fmtFE(fePerfs[k]);
    }});
    const feAllocEl = document.getElementById('fe-alloc-' + pid);
    if (feAllocEl) feAllocEl.innerHTML = mkBar(feAlloc, 'fe');

    // ── DOP row
    ['ytd', 'a1', 'a3', 'a5'].forEach(k => {{
      const el = document.getElementById('dop-' + k + '-' + pid);
      if (el) el.innerHTML = dopAlloc > 0 ? fmtFE(dopPerfs[k]) : '<span class="na">—</span>';
    }});
    const dopAllocEl = document.getElementById('dop-alloc-' + pid);
    if (dopAllocEl) dopAllocEl.innerHTML = dopAlloc > 0 ? mkBar(dopAlloc, 'dop') : emptyBar;

    // ── UC fund allocation — redistribution avec overrides manuels
    // Passe 1 : séparer manuels vs auto
    let manualSum = 0, autoInitPct = 0;
    const allocMeta = {{}};
    pd.funds.forEach((f, i) => {{
      const rank = i + 1;
      const chk  = document.getElementById('chk-' + pd.cc + '-' + rank);
      const sel  = chk ? chk.checked : true;
      const inp  = document.getElementById('minput-' + pd.cc + '-' + rank);
      const raw  = inp ? inp.value.trim() : '';
      const mv   = raw !== '' ? parseFloat(raw) : NaN;
      const isM  = sel && !isNaN(mv) && mv >= 0;
      allocMeta[rank] = {{ sel, isManual: isM, manVal: mv }};
      if (sel) {{ if (isM) manualSum += mv; else autoInitPct += f.pct; }}
    }});
    const autoSpace = Math.max(0, ucPct - manualSum);
    const overflow  = manualSum > ucPct;

    // Passe 2 : afficher barres + inputs
    const actualAllocs = {{}};
    pd.funds.forEach((f, i) => {{
      const rank  = i + 1;
      const {{ sel, isManual, manVal }} = allocMeta[rank];
      const chk   = document.getElementById('chk-' + pd.cc + '-' + rank);
      const rowEl = chk ? chk.closest('tr') : null;
      if (rowEl) rowEl.classList.toggle('deselected', !sel);
      const barEl = document.getElementById('bar-' + pd.cc + '-' + rank);
      const pctEl = document.getElementById('pct-' + pd.cc + '-' + rank);
      const inp   = document.getElementById('minput-' + pd.cc + '-' + rank);
      if (inp) {{
        inp.classList.toggle('is-manual',   !!(sel && isManual && !overflow));
        inp.classList.toggle('is-overflow', !!(sel && isManual && overflow));
      }}
      if (!sel) {{
        if (barEl) barEl.style.width = '0px';
        if (pctEl) pctEl.textContent = '—';
        actualAllocs[rank] = 0;
        return;
      }}
      const newPct = isManual ? manVal
        : (autoInitPct > 0 ? Math.round(f.pct / autoInitPct * autoSpace * 10) / 10 : 0);
      actualAllocs[rank] = newPct;
      if (barEl) barEl.style.width = Math.round(newPct * 3) + 'px';
      if (pctEl) pctEl.textContent = newPct.toFixed(1) + ' %';
    }});

    // ── KPI blended : FE + DOP + UC (pondéré par allocations réelles)
    const sums = {{ a1: [0,0], a3: [0,0], a5: [0,0], vol: [0,0] }};
    pd.funds.forEach((f, i) => {{
      const rank = i + 1;
      const chk  = document.getElementById('chk-' + pd.cc + '-' + rank);
      if (!chk || !chk.checked) return;
      const w = actualAllocs[rank] || 0;
      if (w <= 0) return;
      ['a1','a3','a5','vol'].forEach(k => {{
        if (f[k] != null) {{ sums[k][0] += w * f[k]; sums[k][1] += w; }}
      }});
    }});
    // Renormalisation : les fonds sans historique sur l'horizon sont exclus du calcul
    const blends = {{}};
    ['a1','a3','a5'].forEach(k => {{
      const ucAvg = sums[k][1] > 0 ? sums[k][0] / sums[k][1] : null;
      blends[k] = ucAvg != null
        ? feAlloc / 100 * fePerfs[k] + dopAlloc / 100 * dopPerfs[k] + ucScale * ucAvg
        : null;
    }});
    // Volatilité pondérée : FE et DOP ≈ 0 → contribution UC uniquement (approx. hors corrélations)
    const blend_vol = sums.vol[1] > 0 ? ucScale * (sums.vol[0] / sums.vol[1]) : null;

    // ── Vision 1 an / 3 ans / 5 ans ──────────────────────────────────────────
    const vis      = window._PTF_VISION || 'a1';
    const visYears = vis === 'a3' ? 3 : (vis === 'a5' ? 5 : 1);
    const visLbl   = vis === 'a3' ? '3 Ans' : (vis === 'a5' ? '5 Ans' : '1 An');
    const main = blends[vis];
    const ann  = main != null ? (Math.pow(1 + main / 100, 1 / visYears) - 1) * 100 : null;

    const lm = document.getElementById('kpilbl-main-' + pid);
    const la = document.getElementById('kpilbl-ann-' + pid);
    if (lm) lm.textContent = 'Perf. pondérée ' + visLbl + (visYears > 1 ? ' (cumulée)' : '');
    if (la) la.textContent = 'Annualisée (' + visLbl.toLowerCase() + ')';
    const km = document.getElementById('kpi-main-' + pid);
    const ka = document.getElementById('kpi-ann-' + pid);
    const kv = document.getElementById('kpi-vol-' + pid);
    if (km) km.innerHTML = main != null ? fmtKpi(main) : '<span class="na">—</span>';
    if (ka) ka.innerHTML = ann != null
      ? '<span class="' + (ann >= 0 ? 'pos' : 'neg') + '">' + (ann >= 0 ? '+' : '') + ann.toFixed(1).replace('.', ',') + '&nbsp;%/an</span>'
      : '<span class="na">—</span>';
    if (kv) kv.innerHTML = blend_vol != null
      ? blend_vol.toFixed(1).replace('.', ',') + '&nbsp;%'
      : '<span class="na">—</span>';

    // Mémorise les rendements pondérés pour le simulateur
    window._PTF_BLENDED = window._PTF_BLENDED || {{}};
    window._PTF_BLENDED[pid] = {{ a1: blends.a1, a3: blends.a3, a5: blends.a5 }};
  }});
  if (typeof simSync === 'function') simSync('T');
}}
</script>
</body>
</html>
""")

html_parts.append("""<script>
/* ===================================================================
   Utilitaires : impression / PDF + simulateur de projection
   =================================================================== */
function openPrintDoc(title, rows, tot) {
  const fmtP = v => v==null ? '—' : (v>=0?'+':'')+v.toFixed(2).replace('.',',')+' %';
  const today = new Date().toLocaleDateString('fr-FR');
  let trs = rows.map(r => '<tr>'
    +'<td>'+r.name+(r.isin?' <span class="isin">'+r.isin+'</span>':'')+(r.note?' <span class="isin">— '+r.note+'</span>':'')+'</td>'
    +'<td style="text-align:center">'+(r.srri||'—')+'</td>'
    +'<td class="r">'+fmtP(r.ytd)+'</td>'
    +'<td class="r">'+fmtP(r.a1)+'</td>'
    +'<td class="r">'+fmtP(r.a3)+'</td>'
    +'<td class="r">'+fmtP(r.a5)+'</td>'
    +'<td class="r">'+(r.vol!=null?r.vol.toFixed(1).replace('.',',')+' %':'—')+'</td>'
    +'<td class="r"><strong>'+(r.alloc!=null?r.alloc.toFixed(1).replace('.',',')+' %':'—')+'</strong></td>'
    +'</tr>').join('');
  if (tot && tot.a1 != null) {
    trs += '<tr class="tot"><td>Total portefeuille (pondéré)</td><td></td><td></td>'
      +'<td class="r">'+fmtP(tot.a1)+'</td><td class="r">'+fmtP(tot.a3)+'</td><td></td><td></td><td class="r">100 %</td></tr>';
  }
  const css = 'body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;color:#1a202c;padding:28px;font-size:12px}'
    +'h1{font-size:18px;color:#1a3a6b;margin-bottom:2px}'
    +'.sub{font-size:11px;color:#718096;margin-bottom:18px}'
    +'table{width:100%;border-collapse:collapse;margin-bottom:16px}'
    +'th{background:#f0f4f8;text-align:left;padding:7px 8px;font-size:11px;border-bottom:2px solid #3266ad}'
    +'td{padding:6px 8px;border-bottom:1px solid #e2e8f0}'
    +'.r{text-align:right}.isin{font-size:10px;color:#a0aec0}'
    +'.tot td{background:#eef3fb;font-weight:700;border-top:2px solid #3266ad}'
    +'.legal{font-size:10px;color:#718096;font-style:italic;margin-top:18px;border-top:1px solid #e2e8f0;padding-top:10px}';
  const html = '<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><title>'+title+'</title>'
    +'<style>'+css+'</style></head><body>'
    +'<h1>Le Conservateur — '+title+'</h1>'
    +'<div class="sub">Édité le '+today+' · Performances Boursorama · Volatilité et allocations indicatives</div>'
    +'<table><thead><tr><th>Fonds</th><th style="text-align:center">SRRI</th><th class="r">YTD</th><th class="r">1 An</th>'
    +'<th class="r">3 Ans</th><th class="r">5 Ans</th><th class="r">Volat. 1A</th><th class="r">Allocation</th></tr></thead>'
    +'<tbody>'+trs+'</tbody></table>'
    +'<div class="legal">Les performances passées ne préjugent pas des performances futures. '
    +'L\\'assureur ne s\\'engage que sur le nombre d\\'unités de compte et non sur leur valeur. '
    +'Document établi à titre informatif — ne constitue pas un conseil en investissement.</div>'
    +'<scr'+'ipt>window.onload=function(){window.print()}</scr'+'ipt></body></html>';
  const w = window.open('', '_blank');
  if (!w) { alert('Autorisez les pop-ups pour imprimer.'); return; }
  w.document.write(html);
  w.document.close();
}

function printPortfolio(pid) {
  const pd = _PTF_DATA[pid]; if (!pd) return;
  const feAlloc  = parseInt(document.getElementById('feSlider')?.value)  || 30;
  const dopAlloc = parseInt(document.getElementById('dopSlider')?.value) || 0;
  const taux = _getFERate(100 - feAlloc);
  const rows = [];
  rows.push({name:'Fonds en Euros', srri:1, ytd:null, a1:taux,
    a3:(Math.pow(1+taux/100,3)-1)*100, a5:(Math.pow(1+taux/100,5)-1)*100,
    alloc:feAlloc, note:'Taux 2025 : '+taux.toFixed(2).replace('.',',')+' %'});
  if (dopAlloc > 0) rows.push({name:'DOP (taux fixe 5,00 %/an)', srri:2, ytd:null, a1:5, a3:15, a5:25, alloc:dopAlloc});
  pd.funds.forEach((f, i) => {
    const rank = i + 1;
    const chk = document.getElementById('chk-'+pd.cc+'-'+rank);
    if (chk && !chk.checked) return;
    const pctEl = document.getElementById('pct-'+pd.cc+'-'+rank);
    let alloc = pctEl ? parseFloat(pctEl.textContent.replace(',','.')) : f.pct;
    if (isNaN(alloc)) alloc = null;
    rows.push({name:f.name, srri:f.srri, ytd:f.ytd, a1:f.a1, a3:f.a3, a5:f.a5, vol:f.vol, alloc:alloc});
  });
  const tot = (window._PTF_BLENDED||{})[pid] || {};
  openPrintDoc('Portefeuille type « '+pd.label+' »', rows, tot);
}

/* ── Vision 1 an / 3 ans / 5 ans ─────────────────────────────────── */
function setVision(vis) {
  window._PTF_VISION = vis;
  ['a1','a3','a5'].forEach(v => {
    const b = document.getElementById('visBtn-'+v);
    if (b) b.classList.toggle('active', v === vis);
  });
  const sec = document.getElementById('sec_portefeuilles');
  if (sec) { sec.classList.remove('vis-a1','vis-a3','vis-a5'); sec.classList.add('vis-'+vis); }
  if (typeof updateFE === 'function') updateFE();
}

/* ── Simulateur ─────────────────────────────────────────────────── */
function _activeBlended(prefix) {
  if (prefix === 'T') {
    const panel = document.querySelector('.ptf-panel.active');
    const pid = panel ? panel.id.replace('ptf_','') : null;
    return pid ? (window._PTF_BLENDED||{})[pid] : null;
  }
  const panel = document.querySelector('.perso-panel.active');
  const pid = panel ? panel.dataset.id : null;
  return pid ? (window._PERSO_BLENDED||{})[pid] : null;
}

function simCompute(prefix) {
  const g = id => document.getElementById('sim'+prefix+'-'+id);
  if (!g('init')) return;
  const init    = parseFloat(g('init').value)    || 0;
  const monthly = parseFloat(g('monthly').value) || 0;
  const years   = Math.max(1, Math.min(40, parseInt(g('years').value)||10));
  const rate    = parseFloat(g('rate').value)    || 0;
  const rm = Math.pow(1+rate/100, 1/12) - 1;
  let cap = init, invested = init;
  const yearRows = [];
  for (let m = 1; m <= years*12; m++) {
    cap = cap*(1+rm) + monthly; invested += monthly;
    if (m % 12 === 0) yearRows.push({y:m/12, cap, invested});
  }
  const fmtE = v => Math.round(v).toLocaleString('fr-FR') + ' €';
  const gains = cap - invested;
  g('kpis').innerHTML =
    '<div class="sim-kpi"><div class="lbl">Capital projeté ('+years+' ans)</div><div class="val">'+fmtE(cap)+'</div></div>'
    +'<div class="sim-kpi"><div class="lbl">Total versé</div><div class="val">'+fmtE(invested)+'</div></div>'
    +'<div class="sim-kpi"><div class="lbl">Gains théoriques</div><div class="val '+(gains>=0?'pos':'neg')+'">'+(gains>=0?'+':'−')+fmtE(Math.abs(gains))+'</div></div>';
  const step = years > 12 ? Math.ceil(years/12) : 1;
  let rows = '<thead><tr><th>Année</th><th style="text-align:right">Versé cumulé</th><th style="text-align:right">Capital projeté</th><th style="text-align:right">Gains</th></tr></thead><tbody>';
  yearRows.forEach(r => {
    if (r.y % step !== 0 && r.y !== years) return;
    const gn = r.cap - r.invested;
    rows += '<tr><td>'+r.y+'</td><td style="text-align:right">'+fmtE(r.invested)+'</td>'
      +'<td style="text-align:right"><strong>'+fmtE(r.cap)+'</strong></td>'
      +'<td style="text-align:right" class="'+(gn>=0?'pos':'neg')+'">'+(gn>=0?'+':'−')+fmtE(Math.abs(gn))+'</td></tr>';
  });
  g('table').innerHTML = rows + '</tbody>';
}

function _visionRate(b) {
  // Rendement annualisé selon la vision active, avec repli sur 1 an
  const vis = window._PTF_VISION || 'a1';
  const years = vis === 'a3' ? 3 : (vis === 'a5' ? 5 : 1);
  let v = b ? b[vis] : null, y = years, lbl = vis === 'a3' ? '3 ans' : (vis === 'a5' ? '5 ans' : '1 an');
  if (v == null && b && b.a1 != null) { v = b.a1; y = 1; lbl = '1 an'; }
  if (v == null) return null;
  return { rate: (Math.pow(1 + v/100, 1/y) - 1) * 100, lbl: lbl };
}

function simUseActive(prefix) {
  const r = _visionRate(_activeBlended(prefix));
  if (!r) { alert('Aucun portefeuille actif ou données insuffisantes.'); return; }
  document.getElementById('sim'+prefix+'-rate').value = r.rate.toFixed(1);
  simCompute(prefix);
}

function simSync(prefix) {
  const b = _activeBlended(prefix);
  const hint = document.getElementById('sim'+prefix+'-hint');
  const r = _visionRate(b);
  if (hint && r) {
    hint.textContent = 'Portefeuille affiché — vision '+r.lbl+' : '
      +(r.rate>=0?'+':'')+r.rate.toFixed(1).replace('.',',')+' %/an annualisé'
      +' — bouton « Utiliser le portefeuille affiché » pour reprendre ce taux.';
  }
  simCompute(prefix);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', ()=>{ simCompute('T'); simCompute('P'); });
} else { simCompute('T'); simCompute('P'); }
</script>""")

html_parts.append("""<script>
/* ===================================================================
   PersoMgr — Portefeuilles personnels avec persistance localStorage
   =================================================================== */
const PersoMgr = (function() {
  const SK = 'conservateur_perso_v1';
  const SC = {1:'#3b82f6',2:'#06b6d4',3:'#10b981',4:'#f59e0b',5:'#f97316',6:'#ef4444',7:'#8b5cf6'};
  const FT = {1:'Monétaire',2:'Oblig. Daté',3:'Obligataire',4:'Flexible',5:'Mixte',6:'Actions',7:'Thématique'};
  let state = {portfolios:[]};
  let active = null;
  let selTarget = null;

  function load() {
    try { const r = localStorage.getItem(SK); if (r) state = JSON.parse(r); } catch(e) {}
    if (!state.portfolios || !state.portfolios.length) state.portfolios = [mkNew('Mon Portefeuille 1')];
    if (!active || !state.portfolios.find(p=>p.id===active)) active = state.portfolios[0].id;
  }

  function save() {
    state.portfolios.forEach(p => {
      const fe = document.getElementById('pfe-slider-'+p.id);
      const dop = document.getElementById('pdop-slider-'+p.id);
      if (fe) p.feAlloc = parseInt(fe.value)||30;
      if (dop) p.dopAlloc = parseInt(dop.value)||0;
      p.funds.forEach(f => {
        const ik = isinKey(f.isin);
        const inp = document.getElementById('perso-inp-'+p.id+'-'+ik);
        if (inp) f.manualAlloc = inp.value.trim()!=='' ? parseFloat(inp.value) : null;
        const chk = document.getElementById('perso-chk-'+p.id+'-'+ik);
        if (chk) f.enabled = chk.checked;
      });
    });
    try { localStorage.setItem(SK, JSON.stringify(state)); } catch(e) {}
  }

  const genId   = () => 'p'+Date.now().toString(36)+Math.random().toString(36).slice(2,5);
  const isinKey = s => s.replace(/[^a-zA-Z0-9]/g,'_');
  const escH    = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  const getFund = isin => ALL_FUNDS.find(f=>f.isin===isin)||null;
  const fmtV    = v => v==null ? '<span style="color:#a0aec0">—</span>'
    : '<span class="'+(v>=0?'pos':'neg')+'">'+(v>=0?'+':'')+v.toFixed(2).replace('.',',')+'&nbsp;%</span>';

  function mkNew(label) {
    return {id:genId(), label, feAlloc:30, dopAlloc:0, highEncours:false, funds:[]};
  }

  // ── Actions ─────────────────────────────────────────────────────────────────
  function createNew() {
    const label = prompt('Nom du portefeuille :', 'Mon Portefeuille '+(state.portfolios.length+1));
    if (!label) return;
    const p = mkNew(label.trim());
    state.portfolios.push(p);
    active = p.id;
    save(); render();
    openSelector(p.id);
  }

  function duplicate(id) {
    const src = state.portfolios.find(p=>p.id===id); if (!src) return;
    const copy = JSON.parse(JSON.stringify(src));
    copy.id = genId(); copy.label = src.label+' (copie)';
    const idx = state.portfolios.findIndex(p=>p.id===id);
    state.portfolios.splice(idx+1, 0, copy);
    active = copy.id;
    save(); render();
  }

  function deletePortfolio(id) {
    if (state.portfolios.length<=1) { alert('Impossible de supprimer le dernier portefeuille.'); return; }
    if (!confirm('Supprimer ce portefeuille ?')) return;
    state.portfolios = state.portfolios.filter(p=>p.id!==id);
    if (active===id) active = state.portfolios[0].id;
    save(); render();
  }

  function rename(id) {
    const p = state.portfolios.find(x=>x.id===id); if (!p) return;
    const n = prompt('Renommer :', p.label);
    if (n && n.trim()) { p.label = n.trim(); save(); render(); }
  }

  function switchTo(id) {
    active = id;
    document.querySelectorAll('.perso-tab-btn').forEach(b => b.classList.toggle('active', b.dataset.id===id));
    document.querySelectorAll('.perso-panel').forEach(p => p.classList.toggle('active', p.dataset.id===id));
    if (typeof simSync === 'function') simSync('P');
  }

  // ── Render ───────────────────────────────────────────────────────────────────
  function render() { renderTabBar(); renderPanels(); switchTo(active); }

  function renderTabBar() {
    // Les onglets sont maintenant intégrés dans l'en-tête du tableau de chaque panel
    const bar = document.getElementById('perso-tab-bar');
    if (bar) bar.innerHTML = '';
  }

  function renderPanels() {
    const c = document.getElementById('perso-panels'); if (!c) return;
    c.innerHTML = state.portfolios.map(p => buildPanel(p)).join('');
    state.portfolios.forEach(p => updateAllocs(p.id));
  }

  function buildPanel(p) {
    const id = p.id;
    const feAlloc = p.feAlloc||30, dopAlloc = p.dopAlloc||0;
    const ucForRate = 100-feAlloc;
    const taux = _getFERate(ucForRate);

    const feCtrl = `
      <div class="fe-controls">
        <div class="fe-ctrl-row">
          <span class="fe-label">🏦 Fonds en Euros</span>
          <button class="fe-enc-btn ${!p.highEncours?'active':''}" onclick="PersoMgr.setEncours('${id}',false)">&lt; 150k€</button>
          <button class="fe-enc-btn ${p.highEncours?'active':''}" onclick="PersoMgr.setEncours('${id}',true)">≥ 150k€</button>
          <input type="range" class="fe-slider" id="pfe-slider-${id}" min="20" max="49" value="${feAlloc}"
            oninput="document.getElementById('pfe-val-${id}').textContent=this.value;PersoMgr.updateAllocs('${id}');PersoMgr.save()">
          <span id="pfe-val-${id}" style="font-size:14px;font-weight:600;min-width:28px;color:#78350f">${feAlloc}</span>%
          <span id="pfe-taux-${id}" class="fe-taux-display">${taux.toFixed(2).replace('.',',')} %</span>
          <span id="pfe-tranche-${id}" class="fe-tranche-hint">${_getFETranche(ucForRate)}</span>
        </div>
        <div class="fe-ctrl-row" style="border-top:1px solid #e9d5ff">
          <span class="dop-lbl">💎 DOP</span>
          <input type="range" class="dop-slider" id="pdop-slider-${id}" min="0" max="30" value="${dopAlloc}"
            oninput="document.getElementById('pdop-val-${id}').textContent=this.value;PersoMgr.updateAllocs('${id}');PersoMgr.save()">
          <span id="pdop-val-${id}" style="font-size:14px;font-weight:600;min-width:28px;color:#5b21b6">${dopAlloc}</span>%
          <span style="font-size:13px;color:#6d28d9;margin-left:8px">Taux fixe <strong>5,00 %</strong>/an</span>
        </div>
      </div>`;

    let tbody = '';
    if (!p.funds.length) {
      tbody = '<tr><td colspan="10" class="perso-empty">Aucun fonds sélectionné — cliquez sur "Modifier les fonds"</td></tr>';
    } else {
      tbody += `<tr class="fe-row">
        <td></td><td style="font-size:13px;text-align:center">★</td>
        <td class="fund-name">🏦 Fonds en Euros</td><td>SRRI 1</td>
        <td id="pfe-ytd-${id}">—</td><td id="pfe-a1-${id}">—</td><td id="pfe-a3-${id}">—</td><td id="pfe-a5-${id}">—</td>
        <td style="text-align:right;color:#a0aec0;font-size:12px">≈0</td>
        <td id="pfe-alloc-${id}"><div class="ptf-pct-bar"><div class="ptf-mini-bar ptf-bar-fe" style="width:${Math.round(feAlloc*2.04)}px"></div><span style="font-size:12px;font-weight:600">${feAlloc}&nbsp;%</span></div></td>
      </tr>`;
      tbody += `<tr class="dop-row">
        <td></td><td style="font-size:13px;text-align:center">★</td>
        <td class="fund-name">💎 DOP</td><td>SRRI 2</td>
        <td id="pdop-ytd-${id}">—</td><td id="pdop-a1-${id}">—</td><td id="pdop-a3-${id}">—</td><td id="pdop-a5-${id}">—</td>
        <td style="text-align:right;color:#a0aec0;font-size:12px">≈0</td>
        <td id="pdop-alloc-${id}"><span style="color:#cbd5e0;font-size:12px">—</span></td>
      </tr>`;
      p.funds.forEach((fi, idx) => {
        const fd = getFund(fi.isin); if (!fd) return;
        const srri=fd.srri||4, sc=SC[srri]||'#94a3b8', ftl=FT[srri]||'';
        const ik = isinKey(fi.isin);
        const chkd = fi.enabled===false ? '' : 'checked';
        const manV = fi.manualAlloc!=null ? fi.manualAlloc : '';
        tbody += `<tr class="uc-row ftype-${srri}" data-ytd="${fd.ytd??'null'}" data-a1="${fd.a1??'null'}" data-a3="${fd.a3??'null'}" data-a5="${fd.a5??'null'}">
          <td style="text-align:center;padding:0 4px"><input type="checkbox" class="chk-fund" id="perso-chk-${id}-${ik}" ${chkd} onchange="PersoMgr.updateAllocs('${id}');PersoMgr.save()"></td>
          <td style="font-size:11px;color:#a0aec0">${idx+1}</td>
          <td class="fund-name">${escH(fd.name)}<span class="ftype-badge ftype-badge-${srri}">${ftl}</span></td>
          <td style="text-align:center"><span class="srri-badge" style="background:${sc}">${srri}</span></td>
          <td style="text-align:right">${fmtV(fd.ytd)}</td>
          <td style="text-align:right">${fmtV(fd.a1)}</td>
          <td style="text-align:right">${fmtV(fd.a3)}</td>
          <td style="text-align:right">${fmtV(fd.a5)}</td>
          <td style="text-align:right;font-size:12px;color:#718096">${fd.vol!=null?fd.vol.toFixed(1).replace('.',',')+'%':'—'}</td>
          <td><div class="alloc-wrap">
            <div class="ptf-pct-bar">
              <div class="ptf-mini-bar ptf-bar-perso" id="perso-bar-${id}-${ik}" style="width:30px"></div>
              <span id="perso-pct-${id}-${ik}" style="font-size:12px;font-weight:600;min-width:28px">—</span>
            </div>
            <input type="number" class="manual-alloc" id="perso-inp-${id}-${ik}" min="0" max="100" step="0.5"
              placeholder="%" value="${manV}" oninput="PersoMgr.updateAllocs('${id}');PersoMgr.save()" title="Allocation manuelle">
          </div></td>
        </tr>`;
      });
      tbody += `<tr class="perso-total-row">
        <td></td><td style="text-align:center">Σ</td>
        <td class="fund-name">Total portefeuille</td>
        <td style="text-align:center" id="ptot-srri-${id}">—</td>
        <td style="text-align:right" id="ptot-ytd-${id}">—</td>
        <td style="text-align:right" id="ptot-a1-${id}">—</td>
        <td style="text-align:right" id="ptot-a3-${id}">—</td>
        <td style="text-align:right" id="ptot-a5-${id}">—</td>
        <td style="text-align:right;font-size:12px" id="ptot-vol-${id}">—</td>
        <td id="ptot-alloc-${id}">—</td>
      </tr>`;
    }

    // Onglets de portefeuille (tous les portefeuilles, celui-ci actif)
    const tabBtns = state.portfolios.map(px =>
      `<button class="perso-tab-btn${px.id===id?' active':''}" data-id="${px.id}" onclick="PersoMgr.switchTo('${px.id}')">${escH(px.label)}</button>`
    ).join('') + `<button class="perso-tab-new" onclick="PersoMgr.createNew()">＋</button>`;

    return `<div class="perso-panel" data-id="${id}">
      ${feCtrl}
      <div style="overflow-x:auto;margin-top:10px">
        <table class="fund-table" style="width:100%">
          <thead>
            <tr>
              <th rowspan="2" style="width:24px"></th>
              <th rowspan="2" style="font-size:11px">#</th>
              <th rowspan="2">Fonds</th>
              <th rowspan="2" style="text-align:center">SRRI</th>
              <th colspan="6" style="padding:4px 6px 4px 6px;border-bottom:1px solid #e2e8f0">
                <div style="display:flex;align-items:center;justify-content:space-between;gap:6px;flex-wrap:wrap">
                  <div style="display:flex;gap:4px;align-items:center;flex-wrap:wrap">
                    ${tabBtns}
                  </div>
                  <div style="display:flex;gap:4px;align-items:center;flex-wrap:wrap">
                    <button class="perso-action-btn" onclick="PersoMgr.rename('${id}')">✏️ Renommer</button>
                    <button class="perso-action-btn primary" onclick="PersoMgr.openSelector('${id}')">🔍 Modifier</button>
                    <button class="perso-action-btn" onclick="PersoMgr.duplicate('${id}')" title="Dupliquer">📋</button>
                    <button class="perso-action-btn" onclick="PersoMgr.exportJson('${id}')" title="Exporter en fichier JSON">💾</button>
                    <button class="perso-action-btn" onclick="PersoMgr.importJson()" title="Importer un fichier JSON">📥</button>
                    <button class="perso-action-btn" onclick="PersoMgr.shareLink('${id}')" title="Copier un lien de partage">🔗</button>
                    <button class="perso-action-btn" onclick="PersoMgr.printPerso('${id}')" title="Imprimer / PDF">🖨️</button>
                    <button class="perso-action-btn danger" onclick="PersoMgr.deletePortfolio('${id}')" title="Supprimer">🗑️</button>
                  </div>
                </div>
              </th>
            </tr>
            <tr>
              <th style="text-align:right;font-size:11px">YTD</th>
              <th style="text-align:right;font-size:11px">1 An</th>
              <th style="text-align:right;font-size:11px">3 Ans</th>
              <th style="text-align:right;font-size:11px">5 Ans</th>
              <th style="text-align:right;font-size:11px" title="Volatilité annualisée 12 mois">Volat.</th>
              <th style="font-size:11px">Allocation</th>
            </tr>
          </thead>
          <tbody>${tbody}</tbody>
        </table>
      </div>
    </div>`;
  }

  // ── Allocation update ────────────────────────────────────────────────────────
  function updateAllocs(pid) {
    const p = state.portfolios.find(x=>x.id===pid); if (!p) return;
    const feEl  = document.getElementById('pfe-slider-'+pid);
    const dopEl = document.getElementById('pdop-slider-'+pid);
    const feAlloc  = feEl  ? parseInt(feEl.value)||30  : p.feAlloc;
    const dopAlloc = dopEl ? parseInt(dopEl.value)||0  : p.dopAlloc;
    const ucForRate = 100-feAlloc, ucPct = 100-feAlloc-dopAlloc;
    const taux = _getFERate(ucForRate);
    const t=taux/100, DOP=5.0;
    const now=new Date(), jan1=new Date(now.getFullYear(),0,1);
    const ytdFr=(now-jan1)/(365*24*3600*1000);
    const feP={ytd:taux*ytdFr, a1:taux, a3:(Math.pow(1+t,3)-1)*100, a5:(Math.pow(1+t,5)-1)*100};
    const dopP={ytd:DOP*ytdFr, a1:DOP, a3:DOP*3, a5:DOP*5};
    const fmt=v=>v==null?'<span class="na">—</span>':'<span class="'+(v>=0?'pos':'neg')+'">'+(v>=0?'+':'')+v.toFixed(2).replace('.',',')+'&nbsp;%</span>';

    const tauxEl=document.getElementById('pfe-taux-'+pid); if(tauxEl) tauxEl.textContent=taux.toFixed(2).replace('.',',')+' %';
    const trEl=document.getElementById('pfe-tranche-'+pid); if(trEl) trEl.textContent=_getFETranche(ucForRate);
    ['ytd','a1','a3','a5'].forEach(k=>{const el=document.getElementById('pfe-'+k+'-'+pid);if(el)el.innerHTML=fmt(feP[k]);});
    const feAlEl=document.getElementById('pfe-alloc-'+pid);
    if(feAlEl) feAlEl.innerHTML='<div class="ptf-pct-bar"><div class="ptf-mini-bar ptf-bar-fe" style="width:'+Math.round(feAlloc*2.04)+'px"></div><span style="font-size:12px;font-weight:600">'+feAlloc+'&nbsp;%</span></div>';
    ['ytd','a1','a3','a5'].forEach(k=>{const el=document.getElementById('pdop-'+k+'-'+pid);if(el)el.innerHTML=dopAlloc>0?fmt(dopP[k]):'<span class="na">—</span>';});
    const dopAlEl=document.getElementById('pdop-alloc-'+pid);
    if(dopAlEl) dopAlEl.innerHTML=dopAlloc>0?'<div class="ptf-pct-bar"><div class="ptf-mini-bar ptf-bar-dop" style="width:'+Math.round(dopAlloc*2.04)+'px"></div><span style="font-size:12px;font-weight:600">'+dopAlloc+'&nbsp;%</span></div>':'<span style="color:#cbd5e0;font-size:12px">—</span>';

    if (!p.funds.length) return;
    let manSum=0, autoCnt=0;
    const meta={};
    p.funds.forEach(fi=>{
      const ik=isinKey(fi.isin);
      const chk=document.getElementById('perso-chk-'+pid+'-'+ik);
      const sel=chk?chk.checked:true;
      const inp=document.getElementById('perso-inp-'+pid+'-'+ik);
      const raw=inp?inp.value.trim():'';
      const mv=raw!==''?parseFloat(raw):NaN;
      const isM=sel&&!isNaN(mv)&&mv>=0;
      meta[ik]={sel,isM,mv};
      if(sel){if(isM)manSum+=mv; else autoCnt++;}
    });
    const autoSpace=Math.max(0,ucPct-manSum);
    const overflow=manSum>ucPct;
    const eachAuto=autoCnt>0?Math.round(autoSpace/autoCnt*10)/10:0;

    const sums={ytd:[0,0],a1:[0,0],a3:[0,0],a5:[0,0],vol:[0,0]};
    let ucAllocSum=0, srriW=feAlloc*1+dopAlloc*2;
    p.funds.forEach(fi=>{
      const ik=isinKey(fi.isin);
      const {sel,isM,mv}=meta[ik]||{};
      const chk=document.getElementById('perso-chk-'+pid+'-'+ik);
      const rowEl=chk?chk.closest('tr'):null;
      if(rowEl) rowEl.classList.toggle('deselected',!sel);
      const barEl=document.getElementById('perso-bar-'+pid+'-'+ik);
      const pctEl=document.getElementById('perso-pct-'+pid+'-'+ik);
      const inp=document.getElementById('perso-inp-'+pid+'-'+ik);
      if(inp){inp.classList.toggle('is-manual',!!(sel&&isM&&!overflow));inp.classList.toggle('is-overflow',!!(sel&&isM&&overflow));}
      if(!sel){if(barEl)barEl.style.width='0px';if(pctEl)pctEl.textContent='—';return;}
      const newPct=isM?mv:eachAuto;
      if(barEl) barEl.style.width=Math.round(newPct*3)+'px';
      if(pctEl) pctEl.textContent=newPct.toFixed(1)+' %';
      // Accumulation pour la ligne Total
      const fd=getFund(fi.isin);
      if(fd&&newPct>0){
        ucAllocSum+=newPct;
        srriW+=(fd.srri||4)*newPct;
        ['ytd','a1','a3','a5','vol'].forEach(k=>{
          if(fd[k]!=null){sums[k][0]+=newPct*fd[k];sums[k][1]+=newPct;}
        });
      }
    });

    // ── Ligne Total : perfs pondérées FE + DOP + UC ──────────────────────────
    const ucScale=ucPct/100;
    const tot={};
    ['ytd','a1','a3','a5'].forEach(k=>{
      const ucAvg=sums[k][1]>0?sums[k][0]/sums[k][1]:null;
      tot[k]=feAlloc/100*feP[k]+dopAlloc/100*dopP[k]+(ucAvg!=null?ucScale*ucAvg:0);
      const el=document.getElementById('ptot-'+k+'-'+pid);
      if(el) el.innerHTML=fmt(tot[k]);
    });
    const volAvg=sums.vol[1]>0?ucScale*(sums.vol[0]/sums.vol[1]):null;
    const volEl=document.getElementById('ptot-vol-'+pid);
    if(volEl) volEl.innerHTML=volAvg!=null?volAvg.toFixed(1).replace('.',',')+'&nbsp;%':'<span class="na">—</span>';
    const allocTotal=feAlloc+dopAlloc+ucAllocSum;
    const allocEl=document.getElementById('ptot-alloc-'+pid);
    if(allocEl){
      const cls=Math.abs(allocTotal-100)<0.5?'alloc-ok':(allocTotal>100?'alloc-bad':'alloc-warn');
      const icon=Math.abs(allocTotal-100)<0.5?'✓':'⚠';
      allocEl.innerHTML='<span class="'+cls+'" style="font-size:13px;font-weight:700">'+icon+' '+allocTotal.toFixed(1).replace('.',',')+'&nbsp;%</span>';
    }
    const srriEl=document.getElementById('ptot-srri-'+pid);
    if(srriEl){
      const base=feAlloc+dopAlloc+ucAllocSum;
      srriEl.innerHTML=base>0?'<span title="SRRI moyen pondéré">'+(srriW/base).toFixed(1).replace('.',',')+'</span>':'—';
    }
    // Mémorise pour le simulateur
    window._PERSO_BLENDED=window._PERSO_BLENDED||{};
    window._PERSO_BLENDED[pid]={a1:tot.a1,a3:tot.a3,a5:tot.a5};
    if(typeof simSync==='function') simSync('P');
  }

  function setEncours(id, high) {
    const p=state.portfolios.find(x=>x.id===id); if(p){p.highEncours=high; save();}
    const panel=document.querySelector('.perso-panel[data-id="'+id+'"]');
    if(panel) panel.querySelectorAll('.fe-enc-btn').forEach((b,i)=>b.classList.toggle('active',i===(high?1:0)));
    updateAllocs(id);
  }

  // ── Sélecteur de fonds ───────────────────────────────────────────────────────
  function openSelector(pid) {
    selTarget = pid;
    const p = state.portfolios.find(x=>x.id===pid); if (!p) return;
    const sel = new Set(p.funds.map(f=>f.isin));
    const cats = {};
    ALL_FUNDS.forEach(f=>{ if(!cats[f.cat_label]) cats[f.cat_label]=[]; cats[f.cat_label].push(f); });
    let html = '<div id="fs-search-row"><input type="text" id="fs-search" placeholder="Rechercher un fonds..." oninput="PersoMgr.filterSel()" style="width:100%;padding:8px 10px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;box-sizing:border-box"></div>';
    Object.entries(cats).forEach(([cat,funds])=>{
      html += '<div class="fs-cat-header">'+escH(cat)+' <span style="opacity:.6">('+funds.length+')</span></div>';
      funds.forEach(f=>{
        const chkd=sel.has(f.isin)?'checked':'';
        const srri=f.srri||4, sc=SC[srri]||'#94a3b8';
        const ytdTxt=f.ytd!=null?(f.ytd>=0?'+':'')+f.ytd.toFixed(2)+'%':'—';
        const ytdCls=f.ytd!=null&&f.ytd>=0?'pos':'neg';
        html += '<label class="fs-item" data-name="'+escH((f.name+(f.mgr||'')).toLowerCase())+'">'
          +'<input type="checkbox" class="fs-chk" data-isin="'+f.isin+'" '+chkd+'>'
          +'<span class="fs-name">'+escH(f.name)+'</span>'
          +'<span class="srri-badge" style="background:'+sc+';margin-left:4px;flex-shrink:0">'+srri+'</span>'
          +'<span style="font-size:11px;color:#a0aec0;margin-left:6px;flex-shrink:0;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+escH(f.mgr||'')+'</span>'
          +'<span class="fs-ytd '+ytdCls+'">'+ytdTxt+'</span>'
          +'</label>';
      });
    });
    document.getElementById('perso-modal-funds').innerHTML = html;
    document.getElementById('perso-modal').classList.remove('hidden');
    setTimeout(()=>document.getElementById('fs-search')?.focus(), 60);
  }

  function filterSel() {
    const q=(document.getElementById('fs-search')?.value||'').toLowerCase();
    document.querySelectorAll('.fs-item').forEach(el=>{
      el.style.display=(!q||el.dataset.name.includes(q))?'':'none';
    });
    // Show/hide cat headers based on visible items
    document.querySelectorAll('.fs-cat-header').forEach(h=>{
      let sib=h.nextElementSibling, visible=false;
      while(sib && !sib.classList.contains('fs-cat-header')){ if(sib.style.display!=='none') visible=true; sib=sib.nextElementSibling; }
      h.style.display=visible?'':'none';
    });
  }

  function closeSelector() {
    document.getElementById('perso-modal')?.classList.add('hidden');
    selTarget = null;
  }

  function applySelector() {
    if (!selTarget) return;
    const p = state.portfolios.find(x=>x.id===selTarget); if (!p) return;
    const existing={};
    p.funds.forEach(f=>{ existing[f.isin]={manualAlloc:f.manualAlloc, enabled:f.enabled}; });
    const checked = Array.from(document.querySelectorAll('.fs-chk:checked')).map(i=>i.dataset.isin);
    p.funds = checked.map(isin=>({ isin, manualAlloc:existing[isin]?.manualAlloc??null, enabled:existing[isin]?.enabled??true }));
    closeSelector(); save(); render();
  }

  // ── Export / Import / Partage ────────────────────────────────────────────
  function exportJson(id) {
    const p = state.portfolios.find(x=>x.id===id); if (!p) return;
    save();
    const payload = {version:1, exported:new Date().toISOString().slice(0,10),
      label:p.label, feAlloc:p.feAlloc, dopAlloc:p.dopAlloc, highEncours:p.highEncours, funds:p.funds};
    const blob = new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'portefeuille-'+p.label.replace(/[^a-zA-Z0-9]+/g,'-').toLowerCase()+'.json';
    a.click();
    setTimeout(()=>URL.revokeObjectURL(a.href), 500);
  }

  function importJson() {
    const inp = document.createElement('input');
    inp.type = 'file'; inp.accept = '.json,application/json';
    inp.onchange = () => {
      const f = inp.files[0]; if (!f) return;
      const r = new FileReader();
      r.onload = () => {
        try {
          const d = JSON.parse(r.result);
          if (!d || !Array.isArray(d.funds)) throw new Error('format');
          const p = mkNew(d.label || 'Portefeuille importé');
          p.feAlloc = parseInt(d.feAlloc)||30;
          p.dopAlloc = parseInt(d.dopAlloc)||0;
          p.highEncours = !!d.highEncours;
          p.funds = d.funds.filter(fi=>fi && typeof fi.isin==='string')
            .map(fi=>({isin:fi.isin, manualAlloc:fi.manualAlloc??null, enabled:fi.enabled!==false}));
          state.portfolios.push(p); active = p.id;
          save(); render();
        } catch(e) { alert('Fichier invalide — export JSON attendu.'); }
      };
      r.readAsText(f);
    };
    inp.click();
  }

  function shareLink(id) {
    const p = state.portfolios.find(x=>x.id===id); if (!p) return;
    save();
    const payload = {label:p.label, feAlloc:p.feAlloc, dopAlloc:p.dopAlloc, highEncours:p.highEncours, funds:p.funds};
    const data = btoa(unescape(encodeURIComponent(JSON.stringify(payload))));
    const url = location.origin + location.pathname + '#ptf=' + data;
    const done = () => alert('Lien copié !\\nEnvoyez-le : le portefeuille s\\'ajoutera automatiquement à l\\'ouverture de la page.');
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(done, ()=>prompt('Copiez ce lien :', url));
    } else { prompt('Copiez ce lien :', url); }
  }

  function checkHash() {
    const m = location.hash.match(/#ptf=(.+)/);
    if (!m) return false;
    try {
      const d = JSON.parse(decodeURIComponent(escape(atob(m[1]))));
      if (!d || !Array.isArray(d.funds)) return false;
      const p = mkNew((d.label || 'Portefeuille partagé') + ' (reçu)');
      p.feAlloc = parseInt(d.feAlloc)||30;
      p.dopAlloc = parseInt(d.dopAlloc)||0;
      p.highEncours = !!d.highEncours;
      p.funds = d.funds.filter(fi=>fi && typeof fi.isin==='string')
        .map(fi=>({isin:fi.isin, manualAlloc:fi.manualAlloc??null, enabled:fi.enabled!==false}));
      state.portfolios.push(p); active = p.id;
      history.replaceState(null, '', location.pathname + location.search);
      save();
      return true;
    } catch(e) { return false; }
  }

  // ── Impression / PDF ─────────────────────────────────────────────────────
  function printPerso(id) {
    const p = state.portfolios.find(x=>x.id===id); if (!p) return;
    save();
    const feAlloc = p.feAlloc||30, dopAlloc = p.dopAlloc||0;
    const taux = _getFERate(100-feAlloc);
    const rows = [];
    rows.push({name:'Fonds en Euros', srri:1, ytd:null, a1:taux, a3:(Math.pow(1+taux/100,3)-1)*100, a5:(Math.pow(1+taux/100,5)-1)*100, alloc:feAlloc, note:'Taux 2025 : '+taux.toFixed(2).replace('.',',')+' %'});
    if (dopAlloc>0) rows.push({name:'DOP (taux fixe 5,00 %/an)', srri:2, ytd:null, a1:5, a3:15, a5:25, alloc:dopAlloc});
    p.funds.forEach(fi=>{
      if (fi.enabled===false) return;
      const fd = getFund(fi.isin); if (!fd) return;
      const ik = isinKey(fi.isin);
      const pctEl = document.getElementById('perso-pct-'+p.id+'-'+ik);
      const alloc = pctEl ? parseFloat(pctEl.textContent.replace(',','.')) : null;
      rows.push({name:fd.name, isin:fd.isin, srri:fd.srri, ytd:fd.ytd, a1:fd.a1, a3:fd.a3, a5:fd.a5, vol:fd.vol, alloc:isNaN(alloc)?null:alloc});
    });
    const tot = (window._PERSO_BLENDED||{})[p.id] || {};
    openPrintDoc('Portefeuille « '+p.label+' »', rows, tot);
  }

  function init() { load(); checkHash(); render(); }

  return {init, switchTo, createNew, duplicate, deletePortfolio, rename,
          openSelector, closeSelector, applySelector, updateAllocs, save, setEncours, filterSel,
          exportJson, importJson, shareLink, printPerso};
})();

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', ()=>PersoMgr.init());
} else {
  PersoMgr.init();
}
</script>""")

output = ''.join(html_parts)
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(output)
print(f"✅ Written {len(output):,} chars → {out_path}")

covered = sum(1 for cat in CATEGORIES for f in cat["funds"] if f.get("m1") is not None)
total_all = sum(len(c["funds"]) for c in CATEGORIES)
removed_d = ["Conservateur Oblig. CT (D)","Conservateur Oblig. MT (D)","Conservateur Horizon 2027 (D)",
             "Conservateur Diversifié (D)","Conservateur Immo-Or (D)","Conservateur Diversifié Réactif (D)",
             "Conservateur Rendement Flexible (D)","Conservateur Actions Euro (D)",
             "Conservateur Actions Flexibles (D)","Conservateur Emploi Durable (D)",
             "Conservateur Actions Monde (D)","Conservateur Reverso (D)"]
print(f"📊 Fonds : {total_all} | Boursorama coverage : {covered}/{total_all}")
print(f"🗑️  Supprimés : Tikehau 2027, Tikehau 2029, Carmignac Portfolio Tech Solutions (A) + {len(removed_d)} parts (D)")
