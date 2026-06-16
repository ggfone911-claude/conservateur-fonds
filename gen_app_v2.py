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
            if _VL_OVERRIDE_DATE is None and "date" in _data:
                _VL_OVERRIDE_DATE = _data["date"]
        print(f"📡 vl_overrides.json chargé — {len(_VL_OVERRIDES)} fonds (date: {_VL_OVERRIDE_DATE})")
    except Exception as _e:
        print(f"⚠️  Impossible de lire vl_overrides.json : {_e}")

# ─────────────────────────────────────────────────────────────────────────────
# Boursorama performance data collected 12/05/2026 (calculs fin de mois 30/04/2026)
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
    ("FR0013287315","0P0001CB5C","0.64,0.16,0.96,1.99,9.51,10.14,"),
    ("FR0011461334","0P0000ZL7R","0.28,0.46,0.51,1.92,10.19,7.29,6.38"),
    ("FR0011461326","0P0000ZL7Q","0.28,0.46,0.51,1.93,10.21,7.25,7.4"),
    ("LU1585265066","0P0001KJDD","0.18,0.54,0.55,2.12,12.0,9.08,11.27"),
    ("LU1694790202","0P0001CH1A","1.37,0.66,0.05,1.86,2.18,13.28,"),
    ("FR0013505450","0P0001KE62","0.15,0.95,0.8,3.15,20.97,10.57,"),
    ("FR001400K2B5","0P0001S8T9","-0.25,1.19,-0.52,2.39,,,"),
    ("FR0010915314","MP-805617","-0.41,0.94,-0.82,1.52,12.15,-2.12,5.15"),
    ("FR0010564328","MP-460761","-0.39,0.96,-0.77,1.03,11.65,3.27,8.99"),
    ("FR0007497813","MP-305918","-0.39,0.96,-0.76,1.03,11.7,3.39,8.83"),
    ("LU1752460292","0P0001EITS","-1.27,0.38,-1.51,0.55,11.38,3.94,"),
    ("FR0013398294","0P0001HS9U","0.52,0.59,0.76,2.44,16.56,9.77,"),
    ("FR0013426657","0P0001IFLQ","0.45,0.42,0.92,2.65,13.69,11.32,"),
    ("FR0013398302","0P0001HS9V","0.42,0.56,0.61,2.13,15.5,8.09,"),
    ("FR0013398310","0P0001HS9W","0.42,0.56,0.61,2.13,15.5,8.08,"),
    ("FR001400PKZ3","0P0001UGT4","0.07,1.58,0.46,3.78,,,"),
    ("FR001400PL02","0P0001UGT3","-0.09,1.53,0.21,3.36,,,"),
    ("LU0512124107","0P0000P3DN","6.65,4.67,6.21,13.38,26.57,11.82,19.8"),
    ("FR0010135103","MP-829413","3.21,3.47,2.39,12.75,26.88,10.27,31.93"),
    ("FR0010564336","MP-495318","1.41,1.05,2.97,9.06,20.64,12.4,26.79"),
    ("FR0010057711","MP-495316","1.41,1.05,2.98,9.42,22.24,13.84,28.04"),
    ("FR0007051040","MP-804518","1.28,1.9,1.74,4.8,18.36,21.76,33.86"),
    ("FR0011199314","0P0000VYE0","1.36,1.39,2.19,8.71,20.99,10.75,27.77"),
    ("FR0011199322","0P0000VYE1","1.36,1.39,2.19,8.71,21.02,10.85,28.39"),
    ("FR0010489542","MP-514618","0.59,2.53,0.36,4.3,18.04,11.55,25.25"),
    ("FR0010510370","0P0000JZWQ","0.59,2.53,0.36,4.3,18.05,11.53,25.04"),
    ("FR0007439666","0P00005VUH","1.03,2.9,0.75,4.66,18.42,14.33,32.34"),
    ("FR001400UAZ4","0P0001XK54",",2.8,,,,,"),
    ("FR0013087152","0P00019OMO","-0.38,0.98,-0.85,1.21,14.37,16.68,18.38"),
    ("FR0013108982","0P00019OMN","-0.38,0.98,-0.84,1.22,14.46,16.99,18.63"),
    ("LU1694789451","0P0001CH1D","0.76,1.2,0.42,3.62,12.8,27.13,"),
    ("FR0007076930","MP-805274","7.61,6.56,13.12,13.61,34.41,54.99,78.53"),
    ("FR001400U512","0P0001UVBG","1.99,6.66,5.56,12.31,,,"),
    ("FR0000989899","MP-802731","-0.03,3.52,1.45,9.19,1.1,-1.29,55.79"),
    ("FR0010547869","MP-928594","-0.8,5.68,1.99,13.24,12.46,1.99,95.89"),
    ("FR0000978439","MP-800357","-2.04,8.46,-0.48,11.51,7.76,-2.9,49.38"),
    ("FR0010574434","MP-828166","-4.6,7.11,-2.43,3.27,2.65,2.94,41.84"),
    ("FR0000427445","MP-803445","-5.42,2.45,-1.02,10.9,-1.47,-15.22,40.17"),
    ("FR0010321810","MP-805948","6.17,8.74,6.53,11.87,10.76,-7.15,75.19"),
    ("FR0010106500","MP-420630","3.41,9.79,5.83,13.53,28.7,11.02,100.4"),
    ("FR0000983819","MP-805200","2.04,7.17,4.45,14.07,30.84,36.45,106.23"),
    ("FR0014008EH4","0P0001P8TC","1.91,6.05,3.95,15.39,42.07,,"),
    ("FR0011606268","0P00011IDZ","1.53,8.52,3.1,17.81,4.84,-13.91,68.1"),
    ("FR0014008EI2","0P0001P8TA","1.46,5.94,3.25,13.85,36.23,,"),
    ("FR0014008EJ0","0P0001P8TB","1.45,5.93,3.25,13.85,59.93,,"),
    ("FR0010321802","MP-800952","0.88,3.41,2.61,9.25,24.96,24.99,17.28"),
    ("FR0000989915","MP-800743","1.88,6.37,0.64,4.22,23.82,-11.7,9.52"),
    ("FR0010298596","MP-807288","0.13,5.39,2.44,18.73,21.33,31.69,110.52"),
    ("FR0013256930","0P0001HI3U","0.63,5.08,3.15,12.2,18.65,15.96,"),
    ("FR0013256922","0P0001HI3T","0.64,5.09,3.15,12.2,18.66,15.97,"),
    ("LU0870553020","0P0000XTFD","-0.76,3.94,-2.34,2.29,-2.45,-1.28,67.91"),
    ("FR0010149179","MP-802605","-0.61,1.12,1.28,1.94,5.37,2.95,49.18"),
    ("FR0010038257","MP-806670","-4.31,5.05,-4.96,,4.45,24.13,55.41"),
    ("FR0000930471","MP-829178","-4.31,5.06,-4.94,0.03,4.45,24.16,55.44"),
    ("LU1490785091","0P000195NQ","-3.22,5.07,-3.56,-5.59,0.93,-10.17,"),
    ("LU0280435388","MP-990541","24.8,18.42,21.27,65.87,77.07,69.38,253.52"),
    ("LU2809794220","0P0001T914","20.14,22.94,16.46,80.73,,,"),
    ("FR0000292278","MP-829227","16.7,16.34,16.76,39.96,38.19,0.89,38.99"),
    ("FR0010649079","MP-534378","16.0,13.69,15.7,29.16,33.48,40.82,118.16"),
    ("LU0115768185","MP-356085","11.11,12.19,8.61,35.99,32.86,7.96,108.78"),
    ("LU1744646933","0P0001DK5M","13.39,9.46,11.84,44.04,51.19,48.25,"),
    ("LU1819480192","0P0001DYQM","9.09,21.33,-0.71,40.64,130.6,30.49,"),
    ("LU0592698954","0P0000TIYB","8.32,5.1,8.39,23.47,29.86,14.96,64.88"),
    ("LU0592699093","0P0000TIYE","8.05,4.98,7.98,22.54,26.76,10.75,53.28"),
    ("LU2254337392","0P0001LOB8","8.11,8.68,11.91,21.99,26.82,26.16,"),
    ("FR0010148981","MP-800128","6.43,10.75,5.43,36.18,76.9,46.16,154.18"),
    ("FR0010863688","MP-664642","5.23,6.06,4.42,3.67,18.38,9.44,95.59"),
    ("LU1261432659","0P00016FY4","5.94,10.5,5.55,28.8,55.11,51.27,186.82"),
    ("LU1902443420","0P0001FLNU","4.08,9.13,2.77,18.01,40.77,45.84,"),
    ("FR0010564229","MP-460332","3.34,7.7,3.41,19.3,41.8,39.12,95.15"),
    ("FR0007499470","MP-958966","3.35,7.7,3.41,19.3,41.81,39.12,95.15"),
    ("LU1103305709","0P000172SH","7.71,0.08,8.05,12.6,12.97,36.25,76.32"),
    ("LU1244893696","0P00016P7T","0.26,4.08,-0.52,12.54,42.46,54.89,239.4"),
    ("LU1120766388","0P00016ALF","3.59,-0.93,9.03,44.08,48.84,58.69,171.38"),
    ("FR0000974149","MP-803486","1.25,3.88,1.18,15.51,13.16,-4.52,64.42"),
    ("LU0528228074","0P0000VTJH","1.68,11.84,0.53,20.37,26.25,14.03,104.66"),
    ("LU1892829828","0P0001EVSZ","4.69,5.49,4.11,11.12,18.39,8.42,"),
    ("LU1653748860","0P0001BOX5","1.59,-0.27,0.42,-5.59,-8.24,-10.94,"),
    ("FR0013367265","0P0001F34F","-1.97,0.88,-2.02,9.1,27.97,19.65,"),
    ("FR0012844140","0P00016HZ8","-4.93,2.33,-3.86,-1.86,1.21,0.79,41.69"),
    ("LU1160365091","0P00016716","-7.5,1.72,-14.92,4.87,9.7,-33.81,28.02"),
    ("LU0366534344","MP-521217","-4.75,0.67,-5.98,-11.51,-19.26,-27.0,17.17"),
    ("FR0000295230","MP-829523","-8.61,3.24,-10.44,-12.8,-9.52,1.32,81.27"),
    ("LU0217139020","MP-119337","-9.44,2.25,-6.59,0.93,-1.83,9.17,110.14"),
    ("FR0010479931","MP-806384","-11.84,6.08,-15.29,-17.45,11.23,19.03,88.61"),
    ("FR0010097683","MP-802713","-0.11,4.68,-0.23,9.67,15.41,13.27,31.1"),
    ("LU2147879543","0P0001L9PD","-0.17,4.29,-0.04,5.76,16.71,11.95,27.5"),
    ("FR0011175652","0P00015XU2","-0.08,0.24,-1.18,-0.62,2.7,-21.21,-18.54"),
    ("FR0011184191","0P00015XU4","-0.07,0.26,-1.18,-0.61,2.72,-21.18,-18.83"),
    ("FR0010286013","MP-805700","-2.47,2.16,-3.16,2.52,5.06,4.86,20.23"),
    ("FR0011253624","0P00017T6E","-3.41,0.92,-3.21,15.3,38.15,38.37,141.71"),
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
    {"isin":"FR0007051040","name":"DNCA Eurose (C)","mgr":"DNCA Finance","vl":474.81,"ytd":2.07,"srri":3},
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
    {"isin":"FR0013367265","name":"R-co Valor Balanced (C)","mgr":"Rothschild et Cie Gestion","vl":146.47,"ytd":-2.42,"srri":5},
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

# Merge Boursorama data into each fund
for cat in CATEGORIES:
    for f in cat["funds"]:
        b = BOURSO_DATA.get(f["isin"])
        if b:
            f["m1"]  = b["m1"]
            f["m6"]  = b["m6"]
            f["a1"]  = b["a1"]
            f["a3"]  = b["a3"]
            f["a5"]  = b["a5"]
            f["bid"] = b["bid"]
        else:
            f["m1"] = f["m6"] = f["a1"] = f["a3"] = f["a5"] = None
            f["bid"] = None
        # Écrase VL (et éventuellement YTD) avec les données scrapées en live
        ov = _VL_OVERRIDES.get(f["isin"])
        if ov:
            if ov.get("vl") and ov["vl"] > 0:
                f["vl"] = round(ov["vl"], 4)
            if ov.get("ytd") is not None:
                f["ytd"] = ov["ytd"]

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
<title>Le Conservateur – Analyse des Fonds 12/05/2026</title>
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
.tabs{display:flex;gap:0;padding:0 32px;background:#fff;border-bottom:2px solid #e2e8f0;overflow-x:auto;white-space:nowrap}
.tab{padding:12px 16px;cursor:pointer;border-bottom:3px solid transparent;font-size:13px;font-weight:500;color:#4a5568;transition:all .2s;flex-shrink:0}
.tab:hover{color:#3266ad;background:#f7fafc}
.tab.active{color:#3266ad;border-bottom-color:#3266ad;font-weight:600}
.section{display:none;padding:24px 32px}
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
.chart-wrap{background:#fff;border-radius:10px;padding:16px;margin-bottom:24px;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.chart-wrap h3{font-size:14px;font-weight:600;color:#4a5568;margin-bottom:4px}
.chart-wrap .chart-sub{font-size:11px;color:#a0aec0;margin-bottom:12px}
.charts-row{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px}
@media(max-width:900px){.charts-row{grid-template-columns:1fr}}
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
.source-note{font-size:11px;color:#a0aec0;margin-bottom:8px}
.filter-bar{display:flex;gap:10px;padding:12px 32px;background:#fff;border-bottom:2px solid #e2e8f0;align-items:center;flex-wrap:wrap}
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
@media(max-width:768px){.section{padding:16px}.tabs{padding:0 16px}.stats-bar{padding:12px 16px}}
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
<p>VL &amp; YTD : courscotations.conservateur.fr au 11 mai 2026 · Performances historiques : Boursorama (fin de mois 30/04/2026)</p>
</header>
<div class="stats-bar">
  <div class="stat"><div class="val">{total}</div><div class="lbl">Fonds analysés</div></div>
  <div class="stat"><div class="val">{cats_str}</div><div class="lbl">Catégories</div></div>
  <div class="stat"><div class="val pos">+{best['ytd']:.2f}%</div><div class="lbl">Meilleur YTD · {best['name']}</div></div>
  <div class="stat"><div class="val neg">{worst['ytd']:.2f}%</div><div class="lbl">Moins bon YTD · {worst['name']}</div></div>
</div>
""")

# ── Barre de filtres (recherche + SRRI) ──────────────────────────────────────
html_parts.append("""<div class="filter-bar">
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
        <th style="text-align:center">Boursorama</th>
      </tr></thead>
      <tbody id="filteredBody"></tbody>
    </table>
  </div>
</div>
""")

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

    html_parts.append(f'<div class="section {active}" id="sec_{cid}">\n')
    html_parts.append(f'<div class="cat-header"><h2>{cat["label"]}</h2><span class="badge">{len(cat["funds"])} fonds</span></div>\n')
    html_parts.append('<div class="source-note">📅 Performances historiques issues de Boursorama — calcul fin de mois au 30/04/2026 · YTD (depuis le 1er janv.) issu de courscotations.conservateur.fr au 11/05/2026</div>\n')

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
<div class="chart-sub">YTD au 11/05/2026 · Historique Boursorama fin de mois 30/04/2026</div>
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

    # Chart 2 : courbe multi-périodes (valeurs brutes %, pas de base 100)
    html_parts.append(f'''<div class="chart-wrap">
<h3>Performances cumulées multi-horizons</h3>
<div class="chart-sub">Données Boursorama fin de mois 30/04/2026 — axe Y : % cumulé réel</div>
<div class="period-btns">
  <button class="period-btn active" data-cat="{cid}" data-period="5A" onclick="filterLinePeriod('{cid}','5A')">5 Ans</button>
  <button class="period-btn" data-cat="{cid}" data-period="3A" onclick="filterLinePeriod('{cid}','3A')">3 Ans</button>
  <button class="period-btn" data-cat="{cid}" data-period="1A" onclick="filterLinePeriod('{cid}','1A')">1 An</button>
  <button class="period-btn" data-cat="{cid}" data-period="6M" onclick="filterLinePeriod('{cid}','6M')">6 Mois</button>
  <button class="period-btn" data-cat="{cid}" data-period="1M" onclick="filterLinePeriod('{cid}','1M')">1 Mois</button>
  <button class="period-btn" data-cat="{cid}" data-period="YTD" onclick="filterLinePeriod('{cid}','YTD')">YTD</button>
</div>
<canvas id="line_{cid}" height="{height_bar}"></canvas>
</div>
''')

    html_parts.append('</div>\n')  # end charts-row

    # ── Préparer données JS ────────────────────────────────────────────────────
    # Bar chart — toutes périodes stockées, on switche dynamiquement
    bar_labels = [f["name"][:28] for f in funds_sorted]

    def bar_period(key):
        vals = [f.get(key) for f in funds_sorted]
        cols = [color if (v is not None and v >= 0) else "#e53e3e" for v in vals]
        return {"data": vals, "colors": cols}

    all_bar_charts.append({
        "id": f"bar_{cid}",
        "labels": bar_labels,
        "color": color,
        "periods": {
            "YTD": bar_period("ytd"),
            "1M":  bar_period("m1"),
            "6M":  bar_period("m6"),
            "1A":  bar_period("a1"),
            "3A":  bar_period("a3"),
            "5A":  bar_period("a5"),
        }
    })

    # Line chart — périodes de la plus ancienne à la plus récente
    # X-axis: 5 Ans → 3 Ans → 1 An → 6 Mois → 1 Mois → YTD
    line_datasets = []
    for fi, f in enumerate(funds_sorted):
        pts = [
            f.get("a5"),   # 5 Ans
            f.get("a3"),   # 3 Ans
            f.get("a1"),   # 1 An
            f.get("m6"),   # 6 Mois
            f.get("m1"),   # 1 Mois
            f.get("ytd"),  # YTD
        ]
        # Seulement si au moins 2 points non nuls
        non_null = sum(1 for p in pts if p is not None)
        if non_null < 2:
            continue
        lc = LINE_PALETTE[fi % len(LINE_PALETTE)]
        line_datasets.append({
            "label": f["name"][:35],
            "data": pts,       # données affichées (modifiées lors du filtrage)
            "fullData": pts,   # référence complète 6 points — ne jamais modifier
            "borderColor": lc,
            "backgroundColor": lc + "22",
            "borderWidth": 2,
            "pointRadius": 4,
            "pointHoverRadius": 6,
            "tension": 0.3,
            "spanGaps": False,
        })
    all_line_charts.append({"id": f"line_{cid}", "datasets": line_datasets})

    # ── Table ──────────────────────────────────────────────────────────────────
    html_parts.append(f'''<div class="table-wrap">
<table id="tbl_{cid}">
<thead><tr>
  <th onclick="sortTable('tbl_{cid}',0)">#</th>
  <th onclick="sortTable('tbl_{cid}',1)">Fonds</th>
  <th onclick="sortTable('tbl_{cid}',2)">Gérant</th>
  <th onclick="sortTable('tbl_{cid}',3)" style="text-align:center">SRRI</th>
  <th onclick="sortTable('tbl_{cid}',4)" style="text-align:right">VL</th>
  <th onclick="sortTable('tbl_{cid}',5)" style="text-align:right" title="YTD au 11/05/2026">YTD</th>
  <th onclick="sortTable('tbl_{cid}',6)" style="text-align:right" title="1 mois — fin de mois 30/04/2026">1 Mois</th>
  <th onclick="sortTable('tbl_{cid}',7)" style="text-align:right" title="6 mois — fin de mois 30/04/2026">6 Mois</th>
  <th onclick="sortTable('tbl_{cid}',8)" style="text-align:right" title="1 an — fin de mois 30/04/2026">1 An</th>
  <th onclick="sortTable('tbl_{cid}',9)" style="text-align:right" title="3 ans — fin de mois 30/04/2026">3 Ans</th>
  <th onclick="sortTable('tbl_{cid}',10)" style="text-align:right" title="5 ans — fin de mois 30/04/2026">5 Ans</th>
  <th style="text-align:center">Boursorama</th>
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
  <td class="fund-name" data-val="{f['name']}">{f["name"]}<br><span class="isin-cell">{f["isin"]}</span></td>
  <td data-val="{f['mgr']}">{f["mgr"]}</td>
  <td style="text-align:center" data-val="{srri}"><span class="srri-badge srri-{srri}">{srri}</span></td>
  <td style="text-align:right" data-val="{f['vl'] or 0}">{fmt_vl(f["vl"])}</td>
  <td style="text-align:right" data-val="{f['ytd'] if f['ytd'] is not None else -9999}">{fmt(f["ytd"])}</td>
  <td style="text-align:right" data-val="{f['m1'] if f['m1'] is not None else -9999}">{fmt(f["m1"])}</td>
  <td style="text-align:right" data-val="{f['m6'] if f['m6'] is not None else -9999}">{fmt(f["m6"])}</td>
  <td style="text-align:right" data-val="{f['a1'] if f['a1'] is not None else -9999}">{fmt(f["a1"])}</td>
  <td style="text-align:right" data-val="{f['a3'] if f['a3'] is not None else -9999}">{fmt(f["a3"])}</td>
  <td style="text-align:right" data-val="{f['a5'] if f['a5'] is not None else -9999}">{fmt(f["a5"])}</td>
  <td style="text-align:center">{bourso_cell}</td>
</tr>
''')
    html_parts.append('</tbody></table></div>\n')
    html_parts.append('</div>\n')  # end section

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
            "bid": f.get("bid"),
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
    this.labels  = cfg.labels  || [];
    this.datasets= cfg.datasets|| [];
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
  setData(labels, datasets) { this.labels=labels; this.datasets=datasets; this._resize(); }
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
    const PL=50, PR=12, PT=14, PB=30+LEGH;
    const cW=W-PL-PR, cH=H-PT-PB;
    const allV=ds.flatMap(d=>(d.data||[]).filter(v=>v!=null&&!isNaN(v)));
    if (!allV.length) return;
    const dmin=Math.min(...allV), dmax=Math.max(...allV);
    const pad=(dmax-dmin||1)*0.08;
    const ymin=dmin-pad, ymax=dmax+pad, yr=ymax-ymin;
    const xP=i=>PL+(n===1?cW/2:(i/(n-1))*cW);
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
    // x vertical grid lines (légères)
    ctx.strokeStyle='#edf2f7'; ctx.lineWidth=1; ctx.setLineDash([2,4]);
    for(let i=0;i<n;i++){
      ctx.beginPath(); ctx.moveTo(xP(i),PT); ctx.lineTo(xP(i),PT+cH); ctx.stroke();
    }
    ctx.setLineDash([]);
    // x labels
    ctx.fillStyle='#4a5568'; ctx.font='bold 11px system-ui'; ctx.textAlign='center';
    labels.forEach((l,i)=>ctx.fillText(l, xP(i), PT+cH+16));
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
    // lines
    ds.forEach(d=>{
      ctx.strokeStyle=d.borderColor||'#3266ad'; ctx.lineWidth=d.borderWidth||2;
      ctx.lineJoin='round'; let st=false; ctx.beginPath();
      (d.data||[]).forEach((v,i)=>{
        if(v==null||isNaN(v)){st=false;return;}
        if(!st){ctx.moveTo(xP(i),yP(v));st=true;}else ctx.lineTo(xP(i),yP(v));
      });
      ctx.stroke();
    });
    // dots + valeurs sur chaque point
    ds.forEach(d=>{
      (d.data||[]).forEach((v,i)=>{
        if(v==null||isNaN(v)) return;
        const isHov=i===hovXIdx;
        const r=isHov?6:(d.pointRadius||4);
        ctx.beginPath(); ctx.arc(xP(i),yP(v),r,0,Math.PI*2);
        ctx.fillStyle='#fff'; ctx.fill();
        ctx.strokeStyle=d.borderColor||'#3266ad'; ctx.lineWidth=2; ctx.stroke();
        // Valeur affichée sur le point (sauf si trop de courbes → lisibilité)
        if (ds.length<=6 || isHov) {
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
    const bourso = bid ? `<a href="https://www.boursorama.com/bourse/opcvm/cours/${{bid}}/" target="_blank" class="bourso-link">Voir →</a>` : '<span class="na">—</span>';
    const sc = srriColor(f.srri);
    return `<tr>
      <td data-val="${'{i+1}'}">${'{i+1}'}</td>
      <td class="fund-name" data-val="${'{f.name}'}">${'{f.name}'}<br><span class="isin-cell">${'{f.isin}'}</span></td>
      <td data-val="${'{f.cat_label}'}" style="font-size:11px;color:#718096">${'{f.cat_label}'}</td>
      <td style="text-align:center" data-val="${'{f.srri}'}">${{`<span class="srri-badge" style="background:${{sc}}">${{f.srri}}</span>`}}</td>
      <td style="text-align:right" data-val="${'{f.vl || 0}'}">${{fmtVL(f.vl)}}</td>
      <td style="text-align:right" data-val="${'{f.ytd ?? -9999}'}">${{fmt(f.ytd)}}</td>
      <td style="text-align:right" data-val="${'{f.m1 ?? -9999}'}">${{fmt(f.m1)}}</td>
      <td style="text-align:right" data-val="${'{f.m6 ?? -9999}'}">${{fmt(f.m6)}}</td>
      <td style="text-align:right" data-val="${'{f.a1 ?? -9999}'}">${{fmt(f.a1)}}</td>
      <td style="text-align:right" data-val="${'{f.a3 ?? -9999}'}">${{fmt(f.a3)}}</td>
      <td style="text-align:right" data-val="${'{f.a5 ?? -9999}'}">${{fmt(f.a5)}}</td>
      <td style="text-align:center">${{bourso}}</td>
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
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.getElementById('tab_'+id).classList.add('active');
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

BAR_CHARTS.forEach(c => {{
  const canvas = document.getElementById(c.id);
  if (!canvas) return;
  const catId = c.id.replace('bar_','');
  const pd = c.periods['YTD'];
  barInstances[catId] = new TinyChart(canvas, {{
    type: 'hbar',
    labels: c.labels,
    datasets: [{{ data: pd.data, backgroundColor: pd.colors }}]
  }});
}});

const BAR_PERIOD_TITLES = {{'YTD':'YTD (au 11/05/2026)','1M':'1 Mois','6M':'6 Mois','1A':'1 An','3A':'3 Ans','5A':'5 Ans'}};

function filterBarPeriod(catId, period) {{
  document.querySelectorAll('.period-btn[data-cat="'+catId+'"][data-bperiod]').forEach(b => {{
    b.classList.toggle('active', b.dataset.bperiod === period);
  }});
  const chart = barInstances[catId];
  if (!chart) return;
  const barDef = BAR_CHARTS.find(c => c.id === 'bar_'+catId);
  if (!barDef) return;
  const pd = barDef.periods[period];
  chart.setData(barDef.labels, [{{ data: pd.data, backgroundColor: pd.colors }}]);
  const el = document.getElementById('bartitle_'+catId);
  if (el) el.textContent = 'Performance ' + BAR_PERIOD_TITLES[period];
}}

// ── Line charts (TinyChart) — % cumulés bruts, pas de base 100 ─────────────
const LINE_ALL_LABELS = ['5 Ans','3 Ans','1 An','6 Mois','1 Mois','YTD'];
const PERIOD_START = {{'5A':0,'3A':1,'1A':2,'6M':3,'1M':4,'YTD':5}};
const LINE_CHARTS = {line_js};
const lineInstances = {{}};
const lineFullDs = {{}};   // catId → tableau complet des datasets (fullData intacts)

LINE_CHARTS.forEach(c => {{
  const canvas = document.getElementById(c.id);
  if (!canvas || !c.datasets.length) return;
  const catId = c.id.replace('line_','');
  // Construire les datasets avec fullData séparé
  const builtDs = c.datasets.map(ds => ({{
    label: ds.label,
    data: (ds.fullData||ds.data).slice(),
    fullData: (ds.fullData||ds.data).slice(),
    borderColor: ds.borderColor,
    borderWidth: ds.borderWidth || 2,
    pointRadius: ds.pointRadius || 4
  }}));
  lineFullDs[catId] = builtDs;
  lineInstances[catId] = new TinyChart(canvas, {{
    type: 'line',
    labels: LINE_ALL_LABELS.slice(),
    datasets: builtDs.map(ds => ({{ ...ds, data: ds.fullData.slice() }}))
  }});
}});

function filterLinePeriod(catId, period) {{
  document.querySelectorAll('.period-btn[data-cat="'+catId+'"][data-period]').forEach(b => {{
    b.classList.toggle('active', b.dataset.period === period);
  }});
  const chart = lineInstances[catId];
  if (!chart) return;
  const start = PERIOD_START[period];
  const newDs = (lineFullDs[catId]||[]).map(ds => ({{
    ...ds,
    data: ds.fullData.slice(start)
  }}));
  chart.setData(LINE_ALL_LABELS.slice(start), newDs);
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
}});
</script>
</body>
</html>
""")

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
