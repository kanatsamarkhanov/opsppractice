# ═══════════════════════════════════════════════════════════════════
# app.py — Индустриялық Қазақстан · v3
# Барлық 17 облыс · Реактивті карта · Word есеп · Gmail email
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import io, smtplib, base64
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.base      import MIMEBase
from email                import encoders
from datetime             import datetime

st.set_page_config(
    page_title="Индустриялық Қазақстан · Практика",
    page_icon="🏭", layout="wide",
    initial_sidebar_state="expanded",
)

TEACHER_EMAIL = "samarkhanov_kb@enu.kz"

# ── CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'IBM Plex Sans',sans-serif;}
h1,h2,h3{font-family:'Merriweather',serif;color:#1B2A4A;}
.step-bar{display:flex;gap:8px;margin-bottom:20px;}
.step-item{flex:1;padding:9px 4px;border-radius:6px;text-align:center;
  font-size:11px;font-weight:600;font-family:'IBM Plex Mono',monospace;
  border:2px solid #DEE2E6;color:#6C757D;background:#F8F9FA;}
.step-item.done  {background:#D4EDDA;border-color:#28A745;color:#155724;}
.step-item.active{background:#1B2A4A;border-color:#1B2A4A;color:#FFD166;}
.time-badge{display:inline-block;background:#FFD166;color:#1B2A4A;
  border-radius:20px;padding:4px 14px;font-size:13px;font-weight:700;
  font-family:'IBM Plex Mono',monospace;margin-bottom:12px;}
.tip-box{background:#EEF4FF;border-left:4px solid #4263EB;
  padding:12px 16px;border-radius:0 8px 8px 0;margin:10px 0;font-size:14px;color:#1B2A4A;}
.warn-box{background:#FFF9DB;border-left:4px solid #F59F00;
  padding:12px 16px;border-radius:0 8px 8px 0;margin:10px 0;font-size:14px;color:#5C3D00;}
.ok-box{background:#D4EDDA;border-left:4px solid #28A745;
  padding:12px 16px;border-radius:0 8px 8px 0;margin:10px 0;font-size:14px;color:#155724;}
.s-header{background:linear-gradient(135deg,#1B2A4A 0%,#2C4A7C 100%);
  color:white;padding:18px 24px;border-radius:12px;margin-bottom:20px;}
.s-header span{color:#FFD166;}
.score-block{background:#1B2A4A;color:white;padding:20px;border-radius:10px;text-align:center;}
.score-block .big{font-size:50px;font-weight:700;color:#FFD166;line-height:1.1;}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# ДЕРЕКТЕР БАЗАСЫ — БАРЛЫҚ 17 ОБЛЫС
# Кәсіпорын | Сала | Өнім_мың_т | Жұмысшы_мың | Ластану_коэф | lat | lon
# ══════════════════════════════════════════════════════════════════
ALL_DATA = {

    "Қарағанды облысы": [
        ["Қарағандыкөмір шахтасы","Көмір өндіру",         30000, 18.5, 0.70, 49.806, 73.089],
        ["ArcelorMittal Теміртау","Қара металлургия",      4100,  12.3, 0.91, 50.067, 72.963],
        ["Жезқазған ЖЭС",         "Электроэнергетика",     4200,   2.1, 0.82, 47.801, 67.714],
        ["Қарбид зауыты",         "Химия өнеркәсібі",       120,   0.8, 0.78, 49.835, 73.103],
    ],

    "Павлодар облысы": [
        ["Майқайын кеніші",        "Көмір өндіру",          8000,  5.2, 0.65, 52.100, 76.950],
        ["Павлодар ЖЭС-3",         "Электроэнергетика",     7500,  3.1, 0.85, 52.284, 76.983],
        ["Қазақстан алюминийі",    "Түсті металлургия",      950,  6.8, 0.78, 52.303, 77.020],
        ["«Каустик» химия з-ды",   "Химия өнеркәсібі",       200,  1.2, 0.82, 52.261, 76.950],
    ],

    "Шығыс Қазақстан облысы": [
        ["Өскемен титан-магний",   "Түсті металлургия",      320,  5.6, 0.83, 49.948, 82.628],
        ["«Казцинк» Өскемен",      "Түсті металлургия",     1800,  9.2, 0.88, 49.952, 82.607],
        ["Бұқтырма ГЭС",           "Электроэнергетика",     2700,  1.4, 0.12, 49.019, 84.432],
        ["Шығыс Қазақстан ЖЭС",    "Электроэнергетика",     1200,  1.8, 0.80, 49.970, 82.590],
    ],

    "Атырау облысы": [
        ["Атырау МҚЗ",             "Мұнай өңдеу",           5000,  4.5, 0.80, 47.114, 51.926],
        ["«ТШО» Теңіз кеніші",     "Мұнай өндіру",         26000,  8.0, 0.72, 45.507, 52.985],
        ["Атырау ЖЭС",             "Электроэнергетика",      700,  1.2, 0.81, 47.106, 51.978],
        ["«АНПЗ» химия кешені",    "Химия өнеркәсібі",       350,  0.9, 0.75, 47.099, 51.945],
    ],

    "Маңғыстау облысы": [
        ["«ОзенМунайГаз» кеніші",  "Мұнай өндіру",          4800,  5.2, 0.70, 43.608, 52.853],
        ["Маңғыстау АЭС",          "Атом электроэнергет.",    350,  1.8, 0.05, 43.646, 51.152],
        ["Ақтау порты — теңіз зауыты","Мұнай өңдеу",         600,  2.1, 0.74, 43.656, 51.166],
        ["Маңғыстау ЖЭС",          "Электроэнергетика",      450,  1.0, 0.80, 43.660, 51.175],
    ],

    "Жамбыл облысы": [
        ["«Казфосфат» Тараз",       "Химия өнеркәсібі",      800,  3.5, 0.85, 42.900, 71.379],
        ["Жамбыл ЖЭС",              "Электроэнергетика",     1200,  1.9, 0.82, 42.875, 71.401],
        ["«Каратаукалий»",          "Тау-кен өндіру",         250,  1.2, 0.70, 43.196, 70.464],
        ["Тараз цемент зауыты",     "Құрылыс материалдары",  1100,  0.9, 0.65, 42.913, 71.355],
    ],

    "Ақтөбе облысы": [
        ["«Казхром» Ақтөбе",        "Түсті металлургия",     2200,  4.8, 0.86, 50.279, 57.207],
        ["ЗЖҚК хром кені",          "Тау-кен өндіру",        3500,  2.3, 0.75, 50.278, 57.234],
        ["Ақтөбе ЖЭС",              "Электроэнергетика",     1100,  1.5, 0.81, 50.294, 57.149],
        ["«ТОО Ақтөбе мұнай»",      "Мұнай өндіру",          1200,  1.8, 0.68, 50.360, 57.210],
    ],

    "Қостанай облысы": [
        ["«ССГПО» Рудный",          "Тау-кен (темір)",       40000, 14.5, 0.65, 52.956, 63.116],
        ["«АрселорМиттал» Лисаков", "Тау-кен (темір)",        8000,  3.2, 0.62, 52.650, 62.500],
        ["Қостанай ЖЭС",            "Электроэнергетика",      900,  1.4, 0.78, 53.214, 63.626],
        ["Жітіқара алтын кеніші",   "Түсті металлургия",       55,  0.8, 0.72, 52.188, 61.197],
    ],

    "Батыс Қазақстан облысы": [
        ["«Ажіп» Қарашығанақ",      "Газ өндіру",           15000,  3.5, 0.62, 50.933, 53.600],
        ["Орал ЖЭС",                "Электроэнергетика",     1200,  1.3, 0.79, 51.230, 51.390],
        ["«Казтрансгаз» БҚО",       "Газ тасымалы",          1500,  0.9, 0.55, 51.228, 51.381],
        ["Орал машина зауыты",      "Машина жасау",           180,  1.1, 0.60, 51.225, 51.375],
    ],

    "Солтүстік Қазақстан облысы": [
        ["«Қазмұнайгаз» СҚО",       "Мұнай өндіру",           350,  0.9, 0.65, 54.866, 69.154],
        ["Петропавл ЖЭС-2",         "Электроэнергетика",     2200,  2.0, 0.80, 54.869, 69.178],
        ["«Казсельмаш»",            "Ауыл шаруашылық машин.", 120,  1.2, 0.55, 54.875, 69.161],
        ["Ертіс су қоймасы ГЭС",    "Электроэнергетика",      240,  0.4, 0.08, 54.530, 70.102],
    ],

    "Қызылорда облысы": [
        ["«ПетроҚазақстан» Кумкөл", "Мұнай өндіру",          6500,  2.8, 0.68, 44.937, 65.513],
        ["«Тұраналем» Арыс",        "Химия өнеркәсібі",        80,  0.5, 0.72, 42.429, 68.808],
        ["Қызылорда ЖЭС",           "Электроэнергетика",      700,  1.0, 0.79, 44.852, 65.509],
        ["«Шымбай» тамақ өнеркәсібі","Тамақ өнеркәсібі",      200,  0.8, 0.42, 44.843, 65.491],
    ],

    "Түркістан облысы": [
        ["«Казфосфат» Тараз-2",     "Химия өнеркәсібі",       650,  2.8, 0.83, 42.302, 68.271],
        ["Арыс-2 жылу электрст.",   "Электроэнергетика",       800,  1.1, 0.81, 42.434, 68.799],
        ["Шымкент МҚЗ",             "Мұнай өңдеу",            5200,  4.2, 0.78, 42.317, 69.596],
        ["«Южполиметалл» Шымкент",  "Түсті металлургия",       420,  2.1, 0.84, 42.301, 69.588],
    ],

    "Алматы облысы": [
        ["Балқаш мыс зауыты",       "Түсті металлургия",     1700,  7.2, 0.87, 46.836, 74.965],
        ["«Қазатомпром» Созақ",     "Уран өндіру",            500,  2.0, 0.50, 44.155, 73.634],
        ["Жетісу Балқаш ЖЭС",       "Электроэнергетика",     2800,  2.8, 0.84, 46.869, 75.003],
        ["«КГОК» Қоңыратбасы",      "Тау-кен (мыс)",         3200,  4.5, 0.76, 46.979, 74.892],
    ],

    "Ақмола облысы": [
        ["«Васильков Алтын» кені",  "Түсті металлургия",      170,  2.8, 0.70, 51.671, 71.044],
        ["Ақмола ЖЭС",              "Электроэнергетика",      500,  1.0, 0.77, 51.183, 71.446],
        ["«Степногорск» химия к-ті","Химия өнеркәсібі",        80,  0.7, 0.75, 52.345, 71.882],
        ["«Қазатомпром» Есіл",      "Уран өндіру",            420,  1.5, 0.48, 51.880, 68.052],
    ],

    "Абай облысы": [
        ["«Казцинк» Семей",         "Түсті металлургия",      650,  3.2, 0.83, 50.414, 80.251],
        ["Семей ЖЭС",               "Электроэнергетика",     1100,  1.6, 0.80, 50.420, 80.276],
        ["«СемейЭнерго»",           "Электроэнергетика",      350,  0.8, 0.76, 50.412, 80.249],
        ["Шар-Семей темір жол цехі","Машина жасау",           200,  1.0, 0.58, 50.389, 80.230],
    ],

    "Жетісу облысы": [
        ["«Казцинк» Текелі",        "Түсті металлургия",      380,  2.4, 0.84, 44.861, 78.776],
        ["Талдықорған цемент зауыты","Құрылыс материалдары",  950,  0.9, 0.63, 44.981, 78.368],
        ["Жетісу ЖЭС",              "Электроэнергетика",      600,  1.1, 0.78, 44.975, 78.372],
        ["«АграрноҚазақстан» Тексті","Тамақ өнеркәсібі",      350,  1.2, 0.40, 44.972, 78.359],
    ],

    "Ұлытау облысы": [
        ["«Қазмыс» Жезқазған",      "Түсті металлургия",     1200,  6.1, 0.86, 47.801, 67.713],
        ["Жезді кені",               "Тау-кен (мыс)",        2100,  3.4, 0.74, 48.124, 67.423],
        ["Ұлытау ЖЭС",              "Электроэнергетика",      320,  0.9, 0.79, 48.619, 66.943],
        ["«Kazakhmys» Жайрем",       "Тау-кен (полимет.)",    1600,  2.2, 0.78, 48.467, 70.114],
    ],
}

# Аудандар тізімі (sorted)
REGION_LIST = sorted(ALL_DATA.keys())

# Сала → маркер түсі картасы
SECTOR_COLOR = {
    "Көмір өндіру":          "black",
    "Қара металлургия":      "darkred",
    "Түсті металлургия":     "purple",
    "Электроэнергетика":     "orange",
    "Атом электроэнергет.":  "beige",
    "Мұнай өндіру":          "darkblue",
    "Мұнай өңдеу":           "blue",
    "Газ өндіру":            "cadetblue",
    "Газ тасымалы":          "lightblue",
    "Химия өнеркәсібі":      "green",
    "Тау-кен өндіру":        "gray",
    "Тау-кен (темір)":       "lightgray",
    "Тау-кен (мыс)":         "darkpurple",
    "Тау-кен (полимет.)":    "pink",
    "Машина жасау":          "red",
    "Тамақ өнеркәсібі":      "lightgreen",
    "Уран өндіру":           "white",
    "Құрылыс материалдары":  "lightred",
}


# ══════════════════════════════════════════════════════════════════
# УТИЛИТАЛАР
# ══════════════════════════════════════════════════════════════════
def region_to_df(region: str) -> pd.DataFrame:
    rows = ALL_DATA.get(region, ALL_DATA["Қарағанды облысы"])
    df = pd.DataFrame(rows, columns=[
        "Кәсіпорын","Сала","Өнім_мың_т",
        "Жұмысшы_мың","Ластану_коэф","lat","lon",
    ])
    df["Экожүктеме"]       = (df["Өнім_мың_т"] * df["Ластану_коэф"]).round(1)
    df["Еңбек_өнімділік"]  = (df["Өнім_мың_т"] / df["Жұмысшы_мың"]).round(1)
    return df


def compute_score(ss: dict) -> tuple:
    bd = {
        "📖 Глоссарий":          (min(15, sum(3 for i in range(1,6) if len(ss.get(f"gloss_{i}","").strip())>10)), 15),
        "📊 Деректер кестесі":   (20 if "df_main" in ss else 0, 20),
        "📈 Диаграмма талдауы":  (min(20, sum(5 for k in ["chart_q1","chart_q2","chart_q3","chart_q4"] if len(ss.get(k,"").strip())>15)), 20),
        "🗺️ Карта талдауы":     (min(20, sum(7 for k in ["map_q1","map_q2","map_q3"] if len(ss.get(k,"").strip())>15)), 20),
        "✍️ Рефлексия":          (min(25, sum(6 for k in ["refl1","refl2","refl3","refl4"] if len(ss.get(k,"").strip())>15)), 25),
    }
    return sum(v[0] for v in bd.values()), bd


def get_grade(s):
    return ("A — Өте жақсы" if s>=85 else "B — Жақсы" if s>=70
            else "C — Орташа" if s>=55 else "D — Аяқтаңыз")


# ══════════════════════════════════════════════════════════════════
# HTML ЕСЕП  (python-docx жоқ — ешқандай сыртқы пакет қажет емес)
# Word-та ашуға болады: File → Open → файл.html
# ══════════════════════════════════════════════════════════════════
def build_html_report(name, group, region, score, grade, breakdown, df, ss, chart_b):
    """Generates a self-contained HTML report with embedded chart."""

    # Диаграмманы base64-ке айналдыру
    chart_tag = ""
    if chart_b:
        b64 = base64.b64encode(chart_b).decode("utf-8")
        chart_tag = f'<img src="data:image/png;base64,{b64}" style="max-width:100%;margin:16px 0;border:1px solid #dee2e6;border-radius:6px" />'

    # Студент ақпараты кестесі
    info_rows = "".join(
        f"<tr><td><b>{k}</b></td><td>{v}</td></tr>"
        for k, v in [
            ("Студент",    name  or "—"),
            ("Топ",        group or "—"),
            ("Өңір",       region),
            ("Күні",       datetime.now().strftime("%Y-%m-%d %H:%M")),
            ("Жалпы балл", f"<b>{score}/100</b>"),
            ("Баға",       f"<b>{grade}</b>"),
        ]
    )

    # Балл кестесі
    score_rows = ""
    for crit, (earned, max_pts) in breakdown.items():
        pct  = earned / max_pts * 100 if max_pts else 0
        clr  = "#28a745" if pct >= 70 else "#ffc107" if pct >= 40 else "#dc3545"
        bar  = f'<div style="height:8px;width:{pct:.0f}%;background:{clr};border-radius:4px"></div>'
        score_rows += (f"<tr><td>{crit}</td>"
                       f"<td style='color:{clr};font-weight:bold'>{earned}/{max_pts}</td>"
                       f"<td>{pct:.0f}%&nbsp;{bar}</td></tr>")

    # Деректер кестесі
    data_cols = ["Кәсіпорын","Сала","Өнім_мың_т","Жұмысшы_мың","Ластану_коэф","Экожүктеме"]
    data_header = "".join(f"<th>{c}</th>" for c in data_cols if df is not None and c in df.columns)
    data_rows   = ""
    if df is not None and not df.empty:
        cols = [c for c in data_cols if c in df.columns]
        for _, row in df[cols].iterrows():
            data_rows += "<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>"

    # Жауаптар
    qa_items = [
        ("📈 Диаграмма 1 — Экожүктеме",          ss.get("chart_q1","")),
        ("📈 Диаграмма 2 — Еңбек өнімділігі",    ss.get("chart_q2","")),
        ("📈 Диаграмма 3 — Scatter заңдылығы",   ss.get("chart_q3","")),
        ("📈 Диаграмма 4 — Педагогикалық идея",  ss.get("chart_q4","")),
        ("🗺️ Карта 1 — Орналасу факторы",        ss.get("map_q1","")),
        ("🗺️ Карта 2 — Мектепте пайдалану",     ss.get("map_q2","")),
        ("🗺️ Карта 3 — Экологиялық салдар",     ss.get("map_q3","")),
        ("💭 Рефлексия 1",                        ss.get("refl1","")),
        ("💭 Рефлексия 2",                        ss.get("refl2","")),
        ("💭 Рефлексия 3",                        ss.get("refl3","")),
        ("💭 Рефлексия 4",                        ss.get("refl4","")),
    ]
    qa_rows = "".join(
        f"<tr><td><b>{q}</b></td>"
        f"<td>{'<em style=\"color:#aaa\">Жауап берілмеген</em>' if not a.strip() else a}</td></tr>"
        for q, a in qa_items
    )

    html = f"""<!DOCTYPE html>
<html lang="kk">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Практикалық жұмыс — {name or 'Студент'}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',Arial,sans-serif;max-width:960px;margin:0 auto;
       padding:24px;color:#1B2A4A;background:#fff;font-size:14px}}
  h1{{background:linear-gradient(135deg,#1B2A4A,#2C4A7C);color:#fff;
      padding:22px 28px;border-radius:10px;margin-bottom:20px;font-size:22px}}
  h1 span{{color:#FFD166}}
  h2{{color:#1B2A4A;border-bottom:2px solid #1B2A4A;padding-bottom:6px;
      margin:28px 0 14px;font-size:16px}}
  table{{width:100%;border-collapse:collapse;margin-bottom:16px;font-size:13px}}
  th{{background:#1B2A4A;color:#FFD166;padding:10px 12px;text-align:left;font-weight:600}}
  td{{padding:9px 12px;border-bottom:1px solid #dee2e6;vertical-align:top}}
  tr:nth-child(even){{background:#f8f9fa}}
  .score-box{{display:inline-block;background:#1B2A4A;color:#fff;
             padding:20px 32px;border-radius:10px;text-align:center;margin:16px 0}}
  .score-big{{font-size:52px;font-weight:700;color:#FFD166;line-height:1}}
  .footer{{font-size:11px;color:#aaa;margin-top:40px;text-align:center;
           border-top:1px solid #dee2e6;padding-top:16px}}
  @media print{{body{{max-width:100%;padding:0}}}}
</style>
</head>
<body>
<h1>🏭 ИНДУСТРИЯЛЫҚ ҚАЗАҚСТАН<br>
    <span>Практикалық жұмыс есебі</span></h1>

<table><tr><th>Параметр</th><th>Мән</th></tr>{info_rows}</table>

<div class="score-box">
  <div class="score-big">{score}</div>
  <div style="font-size:13px;opacity:.8;margin-top:4px">/ 100 баллдан</div>
  <div style="margin-top:10px;font-size:15px;color:#A8D5BA">{grade}</div>
</div>

<h2>1. Балл кестесі</h2>
<table>
<tr><th>Бөлім</th><th>Балл</th><th>Пайыз</th></tr>
{score_rows}
</table>

<h2>2. Деректер кестесі</h2>
<table><tr>{data_header}</tr>{data_rows}</table>

<h2>3. Диаграммалар</h2>
{chart_tag if chart_tag else '<p style="color:#aaa">Диаграмма жоқ (③ бөлімін ашыңыз).</p>'}

<h2>4. Талдау жауаптары</h2>
<table>
<tr><th style="width:35%">Сұрақ</th><th>Жауап</th></tr>
{qa_rows}
</table>

<div class="footer">
  Автоматты жасалды · {datetime.now().strftime('%Y-%m-%d %H:%M')} ·
  Индустриялық Қазақстан практика жүйесі · 2-курс, географиялық педагогика
</div>
</body>
</html>"""

    return html.encode("utf-8")


# ══════════════════════════════════════════════════════════════════
# EMAIL
# ══════════════════════════════════════════════════════════════════
def send_email(name, group, score, grade, word_b, filename):
    try:
        cfg=st.secrets.get("email",{})
        sender=cfg.get("sender",""); passwd=cfg.get("password","")
        if not sender or not passwd:
            return False,("❌ Email баптанбаған.\nStreamlit Cloud → Settings → Secrets:\n\n"
                          "[email]\nsender = \"bot@gmail.com\"\npassword = \"xxxx xxxx xxxx xxxx\"")
        msg=MIMEMultipart()
        msg["From"]=sender; msg["To"]=TEACHER_EMAIL
        msg["Subject"]=(f"[ГеоПрактика] {name or 'Студент'} · "
                        f"{group or '—'} · {score}/100 · "
                        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        body=(f"Сәлем, Қанат Берікұлы!\n\nСтудент жұмысты аяқтады.\n\n"
              f"Студент: {name or '—'}\nТоп: {group or '—'}\n"
              f"Балл: {score}/100\nБаға: {grade}\n"
              f"Күн: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
              f"Word есеп тіркемеде.")
        msg.attach(MIMEText(body,"plain","utf-8"))
        part=MIMEBase("application","octet-stream"); part.set_payload(word_b)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition",f'attachment; filename="{filename}"')
        msg.attach(part)
        with smtplib.SMTP_SSL("smtp.gmail.com",465,timeout=15) as s:
            s.login(sender,passwd); s.sendmail(sender,TEACHER_EMAIL,msg.as_string())
        return True,f"✅ Есеп {TEACHER_EMAIL} мекенжайына жіберілді!"
    except smtplib.SMTPAuthenticationError:
        return False,"❌ Gmail аутентификация қатесі. App Password тексеріңіз."
    except Exception as e:
        return False,f"❌ Жіберу қатесі: {e}"


# ══════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 👤 Студент ақпараты")
    student_name  = st.text_input("Аты-жөніңіз", placeholder="Айгүл Сейітова")
    student_group = st.text_input("Топ / курс",   placeholder="ГП-22-1")

    st.markdown("### 🗺 Зерттеу өңірі")
    student_region = st.selectbox(
        "Облысты таңдаңыз:",
        REGION_LIST,
        index=REGION_LIST.index("Қарағанды облысы"),
    )

    # ▼ Өңір өзгерсе — деректерді автоматты жаңарту
    if st.session_state.get("_last_region") != student_region:
        st.session_state["_last_region"] = student_region
        st.session_state["df_main"] = region_to_df(student_region)

    st.divider()
    st.markdown("### ⏱ 2 сағат бюджеті")
    for r,t in [("Глоссарий","15 мин"),("Деректер","25 мин"),
                ("Диаграмма","25 мин"),("Карта","25 мин"),
                ("Тапсыру","15 мин"),("**Барлығы**","**2 сағат**")]:
        st.markdown(f"- {r}: {t}")
    st.divider()
    st.markdown(f"### 📧 Тапсыру\n**{TEACHER_EMAIL}**")


# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
nd=student_name  or "___________"
gd=student_group or "___"
st.markdown(f"""
<div class="s-header">
  <div style="font-size:21px;margin-bottom:5px;">🏭 Индустриялық Қазақстан: цифрлық практика</div>
  <div style="font-size:14px;opacity:.85;">
    Студент: <span>{nd}</span> &nbsp;·&nbsp;
    Топ: <span>{gd}</span> &nbsp;·&nbsp;
    Өңір: <span>{student_region}</span>
  </div>
  <div style="font-size:11px;opacity:.6;margin-top:5px;">
    {datetime.now().strftime("%Y-%m-%d %H:%M")} &nbsp;·&nbsp; 2-курс, географиялық педагогика
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""<div class="step-bar">
  <div class="step-item done">① Глоссарий</div>
  <div class="step-item active">② Деректер</div>
  <div class="step-item">③ Диаграмма</div>
  <div class="step-item">④ Карта</div>
  <div class="step-item">⑤ Тапсыру</div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════
tab1,tab2,tab3,tab4,tab5,tab_t = st.tabs([
    "📖 ① Глоссарий","📊 ② Деректер",
    "📈 ③ Диаграммалар","🗺️ ④ Карта",
    "📧 ⑤ Тапсыру","🔒 Мұғалім",
])


# ── TAB 1 ─────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="time-badge">⏱ 15 минут</div>',unsafe_allow_html=True)
    st.markdown("## 📖 Глоссарий")
    st.markdown('<div class="tip-box">📌 5 терминді <b>өз сөзіңізбен</b> (мектеп оқушысына) жазыңыз.</div>',unsafe_allow_html=True)
    terms={
        "Отын-энергетикалық кешен (ОЭК)":"Отын (көмір, мұнай, газ) өндіру және электр энергиясын өндіру салаларының жиынтығы.",
        "Жаңартылатын энергия (ЖЭК)":"Жел, күн, су — сарқылмайтын ресурстарға негізделген энергия.",
        "Қара металлургия":"Темір рудасын шойын, болат, прокатқа айналдыратын өндіріс.",
        "Өнеркәсіптік кластер":"Бір аймақта шоғырланған, өзара байланысты кәсіпорындар жүйесі.",
        "Экологиялық жүктеме":"Өндіріс көлеміне байланысты табиғатқа түсетін шартты әсер.",
    }
    for i,(term,defn) in enumerate(terms.items(),1):
        with st.expander(f"**{i}. {term}**", expanded=(i<=2)):
            st.markdown(f"📚 _{defn}_")
            c1,c2=st.columns(2)
            with c1: st.text_area("Өз сөзіңізбен:",placeholder="Мектеп оқушысына...",key=f"gloss_{i}",height=85)
            with c2: st.text_area("Мектеп сабағында:",placeholder="9-сыныпта...",key=f"ped_{i}",height=85)
    filled=sum(1 for i in range(1,6) if len(st.session_state.get(f"gloss_{i}","").strip())>10)
    st.progress(filled/5,text=f"Толтырылған: {filled}/5")
    if filled==5: st.success("✅ Глоссарий толық!")


# ── TAB 2 ─────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="time-badge">⏱ 25 минут</div>',unsafe_allow_html=True)
    st.markdown(f"## 📊 Деректер — {student_region}")
    st.markdown('<div class="tip-box">📌 Деректерді тексеріңіз немесе өзгертіңіз. <b>Экожүктеме</b> автоматты есептеледі.</div>',unsafe_allow_html=True)

    df_default = region_to_df(student_region)

    df_display = df_default[["Кәсіпорын","Сала","Өнім_мың_т",
                              "Жұмысшы_мың","Ластану_коэф","lat","lon"]].copy()
    df_display.columns=["Кәсіпорын","Сала","Өнім (мың т)",
                         "Жұмысшы (мың)","Ластану_коэф","lat","lon"]

    edited=st.data_editor(
        df_display, use_container_width=True, num_rows="dynamic",
        column_config={
            "Өнім (мың т)": st.column_config.NumberColumn(min_value=0,max_value=500000,step=100),
            "Жұмысшы (мың)":st.column_config.NumberColumn(min_value=0,max_value=100,step=0.1,format="%.1f"),
            "Ластану_коэф": st.column_config.NumberColumn(min_value=0.0,max_value=1.0,step=0.01,format="%.2f"),
            "lat":           st.column_config.NumberColumn(format="%.4f"),
            "lon":           st.column_config.NumberColumn(format="%.4f"),
        }, key="de_" + student_region.replace(" ","_").replace(".",""),
    )

    df=edited.copy()
    df.columns=["Кәсіпорын","Сала","Өнім_мың_т","Жұмысшы_мың","Ластану_коэф","lat","lon"]
    df["Экожүктеме"]      =(df["Өнім_мың_т"]*df["Ластану_коэф"]).round(1)
    df["Еңбек_өнімділік"] =(df["Өнім_мың_т"]/df["Жұмысшы_мың"]).round(1)
    st.session_state["df_main"]=df

    st.dataframe(
        df[["Кәсіпорын","Сала","Өнім_мың_т","Жұмысшы_мың",
            "Ластану_коэф","Экожүктеме","Еңбек_өнімділік"]],
        use_container_width=True,
    )
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Жалпы өнім",f"{df['Өнім_мың_т'].sum():,.0f} мың т")
    c2.metric("Жалпы жұмысшы",f"{df['Жұмысшы_мың'].sum():.1f} мың")
    c3.metric("Орт. ластану коэф.",f"{df['Ластану_коэф'].mean():.2f}")
    c4.metric("Жалпы экожүктеме",f"{df['Экожүктеме'].sum():,.0f}")


# ── TAB 3 ─────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="time-badge">⏱ 25 минут</div>',unsafe_allow_html=True)
    st.markdown("## 📈 Диаграммалар")
    df=st.session_state.get("df_main")
    if df is None:
        st.warning("⚠️ Алдымен ② Деректер бөлімін тексеріңіз!")
    else:
        CM=['#1B2A4A','#2C4A7C','#4263EB','#74C0FC']
        CE=['#D9534F','#E07B39','#F0AD4E','#C9302C']
        fig,axes=plt.subplots(2,2,figsize=(13,8))
        fig.patch.set_facecolor('#F8F9FA')
        for ax,y,title,clrs in [
            (axes[0,0],"Өнім_мың_т","Өнім көлемі (мың т)",CM),
            (axes[0,1],"Экожүктеме","Экологиялық жүктеме",CE),
        ]:
            bars=ax.bar(df["Сала"],df[y],color=clrs[:len(df)],edgecolor="white")
            ax.set_title(title,fontsize=11,fontweight="bold")
            ax.tick_params(axis="x",rotation=25,labelsize=8)
            ax.set_facecolor("#FFF"); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
            for b in bars:
                h=b.get_height()
                ax.text(b.get_x()+b.get_width()/2,h+h*0.01,f"{h:,.0f}",ha="center",va="bottom",fontsize=7.5)
        axes[1,0].barh(df["Сала"],df["Еңбек_өнімділік"],color="#4263EB",edgecolor="white")
        axes[1,0].set_title("Еңбек өнімділігі (мың т / мың жұм.)",fontsize=11,fontweight="bold")
        axes[1,0].tick_params(axis="y",labelsize=8); axes[1,0].set_facecolor("#FFF")
        axes[1,0].spines["top"].set_visible(False); axes[1,0].spines["right"].set_visible(False)
        axes[1,1].scatter(df["Өнім_мың_т"],df["Ластану_коэф"],
            s=df["Жұмысшы_мың"]*25,c=CM[:len(df)],
            alpha=0.85,edgecolors="white",linewidths=1.5)
        for i,row in df.iterrows():
            axes[1,1].annotate(row["Сала"][:12],(row["Өнім_мың_т"],row["Ластану_коэф"]),
                textcoords="offset points",xytext=(5,3),fontsize=7)
        axes[1,1].set_title("Өнім vs Ластану",fontsize=11,fontweight="bold")
        axes[1,1].set_facecolor("#FFF"); axes[1,1].spines["top"].set_visible(False); axes[1,1].spines["right"].set_visible(False)
        plt.suptitle(f"Өнеркәсіп талдауы — {student_region}",
                     fontsize=13,fontweight="bold",y=1.01,color="#1B2A4A")
        plt.tight_layout()
        st.pyplot(fig,use_container_width=True)
        buf=io.BytesIO(); fig.savefig(buf,format="png",dpi=110,bbox_inches="tight"); plt.close(fig)
        st.session_state["chart_bytes"]=buf.getvalue()

        st.markdown("### 🔍 Талдау сұрақтары")
        c1,c2=st.columns(2)
        with c1:
            st.text_area("1️⃣ Қай саланың экожүктемесі ең жоғары? Неге?",key="chart_q1",height=90)
            st.text_area("2️⃣ Еңбек өнімділігі жоғары саланы атаңыз.",key="chart_q2",height=90)
        with c2:
            st.text_area("3️⃣ Scatter диаграммасынан қандай заңдылық?",key="chart_q3",height=90)
            st.text_area("4️⃣ Мектеп географиясында қалай қолданасыз?",key="chart_q4",height=90)


# ── TAB 4 ─────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="time-badge">⏱ 25 минут</div>',unsafe_allow_html=True)
    st.markdown(f"## 🗺️ Карта — {student_region}")

    # ▼ Карта SESSION STATE-ке байланысты емес, тікелей student_region бойынша алынады
    df_map = region_to_df(student_region)
    # Студент редактирлеген деректер болса — оны қолдану
    if "df_main" in st.session_state:
        edited_df = st.session_state["df_main"]
        # Тек ағымдағы өңір деректері болса қолдан
        if len(edited_df) > 0:
            df_map = edited_df

    co,_=st.columns([1,2])
    with co:
        map_tile    =st.selectbox("Карта стилі",["OpenStreetMap","CartoDB positron","CartoDB dark_matter"])
        show_poly   =st.checkbox("Сызықпен байланыстыру",True)
        show_circle =st.checkbox("Экожүктеме шеңберлері",True)

    center_lat=df_map["lat"].mean()
    center_lon=df_map["lon"].mean()
    m=folium.Map(location=[center_lat,center_lon],zoom_start=9,tiles=map_tile)

    max_eco = df_map["Экожүктеме"].max() if df_map["Экожүктеме"].max()>0 else 1
    for _,row in df_map.iterrows():
        color=SECTOR_COLOR.get(row["Сала"],"gray")
        popup=(f"<b style='font-size:13px'>{row['Кәсіпорын']}</b><br>"
               f"Сала: <b>{row['Сала']}</b><br>"
               f"Өнім: {row['Өнім_мың_т']:,} мың т<br>"
               f"Жұмысшы: {row['Жұмысшы_мың']} мың<br>"
               f"Ластану: {row['Ластану_коэф']}<br>"
               f"<b style='color:red'>Экожүктеме: {row['Экожүктеме']:,}</b>")
        folium.Marker(
            [row["lat"],row["lon"]],
            popup=folium.Popup(popup,max_width=240),
            tooltip=row["Кәсіпорын"],
            icon=folium.Icon(color=color,icon="industry",prefix="fa"),
        ).add_to(m)
        if show_circle:
            folium.CircleMarker(
                [row["lat"],row["lon"]],
                radius=max(6, row["Экожүктеме"]/max_eco*40),
                color="red",fill=True,fill_opacity=0.15,
                tooltip=f"Экожүктеме: {row['Экожүктеме']:,}",
            ).add_to(m)
    if show_poly and len(df_map)>1:
        folium.PolyLine(df_map[["lat","lon"]].values.tolist(),
            color="#1B2A4A",weight=2,opacity=0.6,dash_array="5").add_to(m)

    # Сала аңызы
    legend_html="<div style='position:fixed;bottom:30px;right:30px;background:white;padding:12px;border-radius:8px;border:1px solid #ccc;font-size:11px;z-index:999'>"
    for sala in df_map["Сала"].unique():
        c=SECTOR_COLOR.get(sala,"gray")
        legend_html+=f"<div style='margin:3px 0'><span style='background:{c};display:inline-block;width:12px;height:12px;border-radius:50%;margin-right:5px'></span>{sala}</div>"
    legend_html+="</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=None, height=520, use_container_width=True,
              key="folium_" + student_region.replace(" ","_").replace(".",""))

    st.markdown("### 🔍 Кеңістіктік талдау")
    c1,c2=st.columns(2)
    with c1: st.text_area("🗺 Неге кәсіпорындар бір-біріне жақын?",
                          placeholder="Шикізат, энергия, су...",height=95,key="map_q1")
    with c2: st.text_area("🏫 Картаны мектеп сабағында қалай пайдаланасыз?",
                          placeholder="9-сыныпта...",height=95,key="map_q2")
    st.text_area("🌿 Ең жоғары экожүктемесі бар кәсіпорынның экологиялық салдары:",
                 placeholder="Картадағы шеңберлерге қарап...",height=85,key="map_q3")


# ── TAB 5 — ТАПСЫРУ ──────────────────────────────────────────────
with tab5:
    st.markdown('<div class="time-badge">⏱ 15 минут</div>',unsafe_allow_html=True)
    st.markdown("## 📧 Жұмысты тапсыру")

    st.markdown("### 💭 Рефлексия")
    rc1,rc2=st.columns(2)
    with rc1:
        st.text_area("1️⃣ Қай бөлік ең пайдалы болды?",key="refl1",height=95)
        st.text_area("2️⃣ Қандай қиындықтар кездесті?",key="refl2",height=95)
    with rc2:
        st.text_area("3️⃣ Болашақ мұғалім ретінде осы тәсілді қалай қолданасыз?",key="refl3",height=95)
        st.text_area("4️⃣ Цифрлық картография мектеп географиясы үшін маңызды ма?",key="refl4",height=95)

    st.divider()
    total_score,breakdown=compute_score(st.session_state)
    grade=get_grade(total_score)
    bc1,bc2=st.columns([1,2])
    with bc1:
        st.markdown(f"""<div class="score-block">
          <div style="font-size:12px;opacity:.7;">Жинаған балл</div>
          <div class="big">{total_score}</div>
          <div style="font-size:12px;opacity:.7;">/ 100</div>
          <div style="margin-top:10px;font-size:14px;color:#A8D5BA;">{grade}</div>
        </div>""",unsafe_allow_html=True)
    with bc2:
        for crit,(e,m) in breakdown.items():
            st.metric(crit,f"{e}/{m}",f"{e/m*100:.0f}%")

    st.divider()
    st.markdown("### 📄 HTML есеп + Email")
    if not student_name:
        st.markdown('<div class="warn-box">⚠️ Sidebar-дан аты-жөніңізді толтырыңыз!</div>',unsafe_allow_html=True)
    else:
        df_rep  = st.session_state.get("df_main")
        chart_b = st.session_state.get("chart_bytes")
        ts=datetime.now().strftime("%Y%m%d_%H%M")
        sn=student_name.replace(" ","_")
        fname=f"report_{sn}_{ts}.html"
        word_b=build_html_report(student_name,student_group,student_region,
                          total_score,grade,breakdown,
                          df_rep,dict(st.session_state),chart_b)
        cd,cs=st.columns(2)
        with cd:
            st.download_button("⬇️ HTML есепті жүктеп алу",
                data=word_b,file_name=fname,
                mime="text/html",
                use_container_width=True)
        with cs:
            if st.button(f"📧 Мұғалімге жіберу → {TEACHER_EMAIL}",
                         type="primary",use_container_width=True):
                with st.spinner("Жіберілуде..."):
                    ok,msg=send_email(student_name,student_group,total_score,grade,word_b,fname)
                if ok: st.markdown(f'<div class="ok-box">{msg}</div>',unsafe_allow_html=True); st.balloons()
                else:  st.markdown(f'<div class="warn-box">{msg}</div>',unsafe_allow_html=True)

        st.markdown(f"""<div class="tip-box">
        📌 1. ⬇️ HTML жүктеп алыңыз (браузерде немесе Word-та ашыңыз) &nbsp;
        2. 📧 «Мұғалімге жіберу» → есеп автоматты <b>{TEACHER_EMAIL}</b> мекенжайына жіберіледі
        </div>""",unsafe_allow_html=True)


# ── TAB 6 — МҰҒАЛІМ ПАНЕЛІ ───────────────────────────────────────
with tab_t:
    st.markdown("## 🔒 Мұғалімнің панелі")
    st.markdown('<div class="warn-box">⚠️ Тек мұғалімге арналған.</div>',unsafe_allow_html=True)
    TPASS=st.secrets.get("teacher",{}).get("password","enu2025geo")
    pwd=st.text_input("Пароль:",type="password",key="tpwd")
    if pwd!=TPASS:
        if pwd: st.error("Пароль дұрыс емес.")
        st.stop()

    st.success("✅ Кіру рұқсат етілді.")
    total_score,breakdown=compute_score(st.session_state)
    grade=get_grade(total_score)
    df=st.session_state.get("df_main")

    st.markdown("### 👤 Студент жұмысы")
    ci,cs=st.columns([2,1])
    with ci:
        for k,v in [("Студент",student_name or "—"),("Топ",student_group or "—"),
                    ("Өңір",student_region),("Балл",f"{total_score}/100"),("Баға",grade)]:
            st.markdown(f"**{k}:** {v}")
    with cs:
        st.markdown(f"""<div class="score-block">
          <div class="big">{total_score}</div>
          <div style="font-size:12px;opacity:.7;">/ 100 · {grade}</div>
        </div>""",unsafe_allow_html=True)

    st.markdown("### 🗂 Балл кестесі")
    st.dataframe(pd.DataFrame(
        [(k,e,m,f"{e/m*100:.0f}%") for k,(e,m) in breakdown.items()],
        columns=["Бөлім","Балл","Макс","Пайыз"],
    ),use_container_width=True,hide_index=True)

    st.markdown("### 📝 Жауаптар")
    for lbl,key in [
        ("📊 Диаграмма 1","chart_q1"),("📊 Диаграмма 2","chart_q2"),
        ("📊 Диаграмма 3","chart_q3"),("📊 Диаграмма 4","chart_q4"),
        ("🗺️ Карта 1","map_q1"),("🗺️ Карта 2","map_q2"),("🗺️ Карта 3","map_q3"),
        ("💭 Рефлексия 1","refl1"),("💭 Рефлексия 2","refl2"),
        ("💭 Рефлексия 3","refl3"),("💭 Рефлексия 4","refl4"),
    ]:
        ans=st.session_state.get(key,"")
        icon="✅" if len(ans.strip())>30 else ("⚠️" if len(ans.strip())>10 else "❌")
        with st.expander(f"{icon} {lbl}"):
            st.write(ans or "_Жауап берілмеген_")

    if df is not None:
        st.markdown("### 📊 Деректер кестесі")
        st.dataframe(df,use_container_width=True)

    # Мұғалім Word нұсқасы
    wb=build_html_report(student_name,student_group,student_region,
                  total_score,grade,breakdown,df,dict(st.session_state),
                  st.session_state.get("chart_bytes"))
    ts=datetime.now().strftime("%Y%m%d_%H%M")
    sn=(student_name or "student").replace(" ","_")
    st.download_button("⬇️ HTML есеп (мұғалім нұсқасы)",
        data=wb,file_name=f"teacher_{sn}_{ts}.html",
        mime="text/html",
        use_container_width=True)
