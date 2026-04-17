# ═══════════════════════════════════════════════════════════════════
# app.py — Индустриялық Қазақстан: интерактивті практикалық сабақ
# 2-курс география педагогтары студенттері үшін
# 2 сағатта аяқталатын деректер + диаграмма + карта + қорытынды
# ═══════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import folium
from streamlit_folium import st_folium
import io
import base64
from datetime import datetime

# ── Беттің конфигурациясы ─────────────────────────────────────────
st.set_page_config(
    page_title="Индустриялық Қазақстан · Практика",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Стиль ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}
h1, h2, h3 {
    font-family: 'Merriweather', serif;
    color: #1B2A4A;
}

/* Прогресс панель */
.step-bar {
    display: flex; gap: 8px; margin-bottom: 24px;
}
.step-item {
    flex: 1; padding: 10px 6px; border-radius: 6px;
    text-align: center; font-size: 12px; font-weight: 600;
    font-family: 'IBM Plex Mono', monospace;
    border: 2px solid #DEE2E6;
    color: #6C757D; background: #F8F9FA;
    transition: all .3s;
}
.step-item.done   { background:#D4EDDA; border-color:#28A745; color:#155724; }
.step-item.active { background:#1B2A4A; border-color:#1B2A4A; color:#FFD166; }

/* Уақыт бадж */
.time-badge {
    display:inline-block; background:#FFD166; color:#1B2A4A;
    border-radius:20px; padding:4px 14px; font-size:13px;
    font-weight:700; font-family:'IBM Plex Mono',monospace;
    margin-bottom:12px;
}

/* Нұсқаулық блок */
.tip-box {
    background:#EEF4FF; border-left:4px solid #4263EB;
    padding:14px 18px; border-radius:0 8px 8px 0;
    margin:12px 0; font-size:14px; color:#1B2A4A;
}
.warn-box {
    background:#FFF9DB; border-left:4px solid #F59F00;
    padding:14px 18px; border-radius:0 8px 8px 0;
    margin:12px 0; font-size:14px; color:#5C3D00;
}

/* Рубрика кесте */
.rubric-table { width:100%; border-collapse:collapse; font-size:13px; }
.rubric-table th {
    background:#1B2A4A; color:#FFD166;
    padding:10px 14px; text-align:left;
}
.rubric-table td { padding:9px 14px; border-bottom:1px solid #DEE2E6; }
.rubric-table tr:nth-child(even) { background:#F8F9FA; }

/* Студент аты */
.student-header {
    background: linear-gradient(135deg,#1B2A4A 0%,#2C4A7C 100%);
    color:white; padding:20px 28px; border-radius:12px;
    margin-bottom:24px; font-family:'Merriweather',serif;
}
.student-header span { color:#FFD166; }

/* Баллдар блогы */
.score-block {
    background:#1B2A4A; color:white;
    padding:20px; border-radius:10px;
    text-align:center; font-family:'IBM Plex Mono',monospace;
}
.score-block .big { font-size:48px; font-weight:700; color:#FFD166; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# SIDEBAR — студент ақпараты + прогресс
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 👤 Студент ақпараты")
    student_name  = st.text_input("Аты-жөніңіз", placeholder="Мысалы: Айгүл Сейітова")
    student_group = st.text_input("Топ / курс",  placeholder="Мысалы: ГП-22-1")
    student_region = st.selectbox("Зерттеу өңірі", [
        "Қарағанды облысы",
        "Павлодар облысы",
        "Шығыс Қазақстан облысы",
        "Маңғыстау облысы",
        "Атырау облысы",
        "Жамбыл облысы",
    ])

    st.divider()
    st.markdown("### ⏱ Уақыт бюджеті")
    st.markdown("""
    | Бөлім | Уақыт |
    |---|---|
    | Глоссарий | 15 мин |
    | Деректер | 25 мин |
    | Диаграмма | 25 мин |
    | Карта | 25 мин |
    | Қорытынды | 15 мин |
    | **Барлығы** | **2 сағат** |
    """)

    st.divider()
    st.markdown("### 📋 Рубрика (100 балл)")
    rubric_items = {
        "Глоссарий (терминдер)": 15,
        "Деректер кестесі": 20,
        "Диаграмма сапасы": 20,
        "Карта элементтері": 20,
        "Аналитикалық қорытынды": 25,
    }
    for k, v in rubric_items.items():
        st.markdown(f"- **{k}** — {v} балл")


# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
name_display = student_name if student_name else "___________"
group_display = student_group if student_group else "___"

st.markdown(f"""
<div class="student-header">
    <div style="font-size:22px; margin-bottom:6px;">
        🏭 Индустриялық Қазақстан: цифрлық практика
    </div>
    <div style="font-size:15px; opacity:.85;">
        Студент: <span>{name_display}</span> &nbsp;·&nbsp;
        Топ: <span>{group_display}</span> &nbsp;·&nbsp;
        Өңір: <span>{student_region}</span>
    </div>
    <div style="font-size:12px; opacity:.6; margin-top:6px;">
        {datetime.now().strftime("%Y-%m-%d %H:%M")} &nbsp;·&nbsp;
        2-курс географиялық педагогика бағдарламасы
    </div>
</div>
""", unsafe_allow_html=True)

# Прогресс жолағы
st.markdown("""
<div class="step-bar">
  <div class="step-item done">① Глоссарий</div>
  <div class="step-item active">② Деректер</div>
  <div class="step-item">③ Диаграмма</div>
  <div class="step-item">④ Карта</div>
  <div class="step-item">⑤ Қорытынды</div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TABS — сабақтың 5 бөлімі
# ══════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📖 ① Глоссарий",
    "📊 ② Деректер кестесі",
    "📈 ③ Диаграммалар",
    "🗺️ ④ Карта",
    "✍️ ⑤ Қорытынды",
])


# ══════════════════════════════════════════════════════════════════
# TAB 1 — ГЛОССАРИЙ
# ══════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="time-badge">⏱ 15 минут</div>', unsafe_allow_html=True)
    st.markdown("## 📖 Негізгі терминдер глоссарийі")

    st.markdown('<div class="tip-box">📌 <b>Тапсырма:</b> Төмендегі 5 терминнің анықтамасын <b>мектеп оқушысына түсіндіретіндей</b> бір-екі сөйлеммен <b>өз сөзіңізбен</b> жазыңыз. Кейін педагогикалық идея бөліміне de толтырыңыз.</div>', unsafe_allow_html=True)

    # Берілген терминдер
    terms = {
        "Отын-энергетикалық кешен (ОЭК)": "Отын (көмір, мұнай, газ) өндіру және электр энергиясын өндіру салаларының жиынтығы.",
        "Жаңартылатын энергия көздері (ЖЭК)": "Жел, күн, су, геотермалды және басқа сарқылмайтын ресурстарға негізделген энергия.",
        "Қара металлургия": "Темір рудасын шойын, болат және прокатқа айналдыратын өндіріс саласы.",
        "Өнеркәсіптік кластер": "Бір аймақта шоғырланған, өзара байланысты өнеркәсіп кәсіпорындарының жүйесі.",
        "Экологиялық жүктеме": "Өндіріс көлеміне байланысты табиғатқа түсетін шартты әсер көрсеткіші.",
    }

    glossary_answers = {}
    pedagogy_answers = {}

    for i, (term, definition) in enumerate(terms.items(), 1):
        with st.expander(f"**{i}. {term}**", expanded=(i <= 2)):
            st.markdown(f"📚 **Ресми анықтама:** _{definition}_")
            col_a, col_b = st.columns(2)
            with col_a:
                glossary_answers[term] = st.text_area(
                    f"Өз сөзіңізбен түсіндіріңіз:",
                    placeholder="Мектеп оқушысына түсінікті болатындай жазыңыз...",
                    key=f"gloss_{i}", height=100
                )
            with col_b:
                pedagogy_answers[term] = st.text_area(
                    f"Мектеп сабағында қалай қолданасыз?",
                    placeholder="Мысалы: 9-сыныпта карта жұмысы кезінде...",
                    key=f"ped_{i}", height=100
                )

    # Глоссарий толтырылды ма?
    filled = sum(1 for v in glossary_answers.values() if len(v.strip()) > 10)
    st.progress(filled / 5, text=f"Толтырылған: {filled}/5 термин")

    if filled == 5:
        st.success("✅ Глоссарий толығымен толтырылды! Келесі бөлімге өтіңіз.")
    else:
        st.markdown('<div class="warn-box">⚠️ Барлық 5 терминді толтырыңыз — бұл бағалау критерийінің бөлігі.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# TAB 2 — ДЕРЕКТЕР КЕСТЕСІ
# ══════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="time-badge">⏱ 25 минут</div>', unsafe_allow_html=True)
    st.markdown(f"## 📊 Деректер кестесі — {student_region}")

    st.markdown('<div class="tip-box">📌 <b>Тапсырма:</b> Өзіңіздің өңіріңіздегі 4 кәсіпорынды таңдаңыз (нақты немесе шартты). Мәндерді нақты интернет деректерінен немесе оқулықтан алуға тырысыңыз. <b>Экожүктеме автоматты есептеледі.</b></div>', unsafe_allow_html=True)

    # Әдепкі деректер (Қарағанды мысалы)
    DEFAULT_DATA = {
        "Қарағанды облысы": {
            "Кәсіпорын":         ["Қарағанды көмір кеніші", "Жезқазған ЖЭС", "ArcelorMittal Теміртау", "Қарбид зауыты"],
            "Сала":              ["Көмір өндіру", "Электроэнергетика", "Қара металлургия", "Химия өнеркәсібі"],
            "Өнім_мың_т":        [30000, 4200, 3800, 120],
            "Жұмысшы_мың_адам":  [18.5, 2.1, 12.3, 0.8],
            "Ластану_коэф":      [0.70, 0.82, 0.91, 0.78],
            "lat":               [49.80, 49.63, 50.06, 49.92],
            "lon":               [73.10, 72.90, 72.95, 73.20],
        },
        "Павлодар облысы": {
            "Кәсіпорын":         ["Майқайын шахтасы", "Павлодар ЖЭС", "Алюминий зауыты", "Химия мегакомбинаты"],
            "Сала":              ["Көмір өндіру", "Электроэнергетика", "Түсті металлургия", "Химия өнеркәсібі"],
            "Өнім_мың_т":        [8000, 7500, 950, 200],
            "Жұмысшы_мың_адам":  [5.2, 3.1, 6.8, 1.2],
            "Ластану_коэф":      [0.65, 0.85, 0.78, 0.82],
            "lat":               [52.10, 52.28, 52.30, 52.15],
            "lon":               [76.95, 76.98, 77.02, 77.10],
        },
    }

    region_key = student_region if student_region in DEFAULT_DATA else "Қарағанды облысы"
    default = DEFAULT_DATA[region_key]

    st.markdown("### ✏️ Деректерді енгізіңіз немесе өзгертіңіз")

    col_hint, col_space = st.columns([3, 1])
    with col_hint:
        st.markdown('<div class="warn-box">💡 Төмендегі кестедегі мәндерді нақты деректермен алмастырыңыз. Ластану_коэф — 0-ден 1-ге дейінгі шартты коэффициент.</div>', unsafe_allow_html=True)

    # Редактирлейтін DataFrame
    df_input = pd.DataFrame({
        "Кәсіпорын":        default["Кәсіпорын"],
        "Сала":             default["Сала"],
        "Өнім (мың т)":    default["Өнім_мың_т"],
        "Жұмысшы (мың)":   default["Жұмысшы_мың_адам"],
        "Ластану_коэф":     default["Ластану_коэф"],
        "Ендік (lat)":      default["lat"],
        "Бойлық (lon)":     default["lon"],
    })

    edited_df = st.data_editor(
        df_input,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Өнім (мың т)":  st.column_config.NumberColumn(min_value=0, max_value=500000, step=100),
            "Жұмысшы (мың)": st.column_config.NumberColumn(min_value=0, max_value=100, step=0.1, format="%.1f"),
            "Ластану_коэф":  st.column_config.NumberColumn(min_value=0.0, max_value=1.0, step=0.01, format="%.2f"),
            "Ендік (lat)":   st.column_config.NumberColumn(format="%.4f"),
            "Бойлық (lon)":  st.column_config.NumberColumn(format="%.4f"),
        },
        key="data_editor",
    )

    # Есептеу
    df = edited_df.copy()
    df.columns = ["Кәсіпорын","Сала","Өнім_мың_т","Жұмысшы_мың","Ластану_коэф","lat","lon"]
    df["Экожүктеме"] = (df["Өнім_мың_т"] * df["Ластану_коэф"]).round(1)
    df["Еңбек_өнімділік"] = (df["Өнім_мың_т"] / df["Жұмысшы_мың"]).round(1)

    st.markdown("### 📋 Есептелген кесте")
    st.dataframe(
        df[["Кәсіпорын","Сала","Өнім_мың_т","Жұмысшы_мың","Ластану_коэф","Экожүктеме","Еңбек_өнімділік"]],
        use_container_width=True,
    )

    # Экономикалық талдау
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Жалпы өнім (мың т)", f"{df['Өнім_мың_т'].sum():,.0f}")
    col2.metric("Жалпы жұмысшы (мың)", f"{df['Жұмысшы_мың'].sum():.1f}")
    col3.metric("Орт. ластану коэф.", f"{df['Ластану_коэф'].mean():.2f}")
    col4.metric("Жалпы экожүктеме", f"{df['Экожүктеме'].sum():,.0f}")

    # Session state-ке сақтау
    st.session_state["df_main"] = df


# ══════════════════════════════════════════════════════════════════
# TAB 3 — ДИАГРАММАЛАР
# ══════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="time-badge">⏱ 25 минут</div>', unsafe_allow_html=True)
    st.markdown("## 📈 Диаграммалар жасау")

    if "df_main" not in st.session_state:
        st.warning("⚠️ Алдымен ② бөліміндегі деректерді толтырыңыз!")
        st.stop()

    df = st.session_state["df_main"]

    st.markdown('<div class="tip-box">📌 <b>Тапсырма:</b> Төмендегі диаграммаларды талдаңыз. Әр диаграмма астында берілген сұраққа жауап жазыңыз.</div>', unsafe_allow_html=True)

    # ── Диаграммалар ──────────────────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.patch.set_facecolor('#F8F9FA')

    colors_main  = ['#1B2A4A','#2C4A7C','#4263EB','#74C0FC']
    colors_eco   = ['#D9534F','#E07B39','#F0AD4E','#C9302C']

    # Диаграмма 1 — Өнім көлемі
    ax1 = axes[0, 0]
    bars = ax1.bar(df["Сала"], df["Өнім_мың_т"], color=colors_main, edgecolor='white', linewidth=0.8)
    ax1.set_title("Өнім көлемі (мың т)", fontsize=12, fontweight='bold', pad=10)
    ax1.set_ylabel("Мың тонна")
    ax1.tick_params(axis='x', rotation=20)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax1.set_facecolor('#FFFFFF')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, h + h*0.01,
                 f"{h:,.0f}", ha='center', va='bottom', fontsize=8, fontweight='600')

    # Диаграмма 2 — Экологиялық жүктеме
    ax2 = axes[0, 1]
    bars2 = ax2.bar(df["Сала"], df["Экожүктеме"], color=colors_eco, edgecolor='white', linewidth=0.8)
    ax2.set_title("Экологиялық жүктеме (шартты)", fontsize=12, fontweight='bold', pad=10)
    ax2.set_ylabel("Шартты бірлік")
    ax2.tick_params(axis='x', rotation=20)
    ax2.set_facecolor('#FFFFFF')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    for bar in bars2:
        h = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, h + h*0.01,
                 f"{h:,.0f}", ha='center', va='bottom', fontsize=8, fontweight='600')

    # Диаграмма 3 — Еңбек өнімділігі
    ax3 = axes[1, 0]
    ax3.barh(df["Сала"], df["Еңбек_өнімділік"], color='#4263EB', edgecolor='white')
    ax3.set_title("Еңбек өнімділігі (мың т / 1 мың жұмысшы)", fontsize=11, fontweight='bold', pad=10)
    ax3.set_xlabel("Мың т / мың жұмысшы")
    ax3.set_facecolor('#FFFFFF')
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)

    # Диаграмма 4 — Ластану коэф. / Өнім (scatter)
    ax4 = axes[1, 1]
    scatter = ax4.scatter(
        df["Өнім_мың_т"], df["Ластану_коэф"],
        s=df["Жұмысшы_мың"] * 25, c=colors_main[:len(df)],
        alpha=0.85, edgecolors='white', linewidths=1.5
    )
    for i, row in df.iterrows():
        ax4.annotate(row["Сала"][:15], (row["Өнім_мың_т"], row["Ластану_коэф"]),
                     textcoords="offset points", xytext=(6, 4), fontsize=7.5)
    ax4.set_title("Өнім vs Ластану (шеңбер = жұмысшы саны)", fontsize=11, fontweight='bold', pad=10)
    ax4.set_xlabel("Өнім көлемі (мың т)")
    ax4.set_ylabel("Ластану коэффициенті")
    ax4.set_facecolor('#FFFFFF')
    ax4.spines['top'].set_visible(False)
    ax4.spines['right'].set_visible(False)

    plt.suptitle(f"Өнеркәсіп талдауы — {student_region}",
                 fontsize=14, fontweight='bold', y=1.01, color='#1B2A4A')
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

    # Талдау сұрақтары
    st.markdown("### 🔍 Диаграмма талдауы")
    st.markdown('<div class="tip-box">📌 Диаграммаларды мұқият қарап, төмендегі сұрақтарға жауап беріңіз.</div>', unsafe_allow_html=True)

    q_col1, q_col2 = st.columns(2)
    with q_col1:
        chart_q1 = st.text_area(
            "1️⃣ Қай саланың экожүктемесі ең жоғары? Неге?",
            placeholder="Диаграмма 2-ге қарап жауап беріңіз...",
            height=100, key="chart_q1"
        )
        chart_q2 = st.text_area(
            "2️⃣ Еңбек өнімділігі жоғары саланы атаңыз. Бұл не туралы айтады?",
            placeholder="Диаграмма 3 негізінде...",
            height=100, key="chart_q2"
        )
    with q_col2:
        chart_q3 = st.text_area(
            "3️⃣ Scatter диаграммасынан қандай заңдылық байқайсыз?",
            placeholder="Өнім мен ластану арасындағы байланыс...",
            height=100, key="chart_q3"
        )
        chart_q4 = st.text_area(
            "4️⃣ Бұл диаграммаларды мектеп географиясында қалай қолданасыз?",
            placeholder="Мысалы: 9-сыныпта ТЭК тақырыбын өткенде...",
            height=100, key="chart_q4"
        )

    filled_q = sum(1 for q in [chart_q1,chart_q2,chart_q3,chart_q4] if len(q.strip()) > 15)
    st.progress(filled_q/4, text=f"Жауап берілді: {filled_q}/4 сұрақ")


# ══════════════════════════════════════════════════════════════════
# TAB 4 — КАРТА
# ══════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="time-badge">⏱ 25 минут</div>', unsafe_allow_html=True)
    st.markdown("## 🗺️ Интерактивті карта — кәсіпорындар")

    if "df_main" not in st.session_state:
        st.warning("⚠️ Алдымен ② бөліміндегі деректерді толтырыңыз!")
        st.stop()

    df = st.session_state["df_main"]

    st.markdown('<div class="tip-box">📌 <b>Тапсырма:</b> Картадағы маркерлерді тексеріңіз. Координаттар ② бөліміндегі деректерден алынады. Карта сұрақтарына жауап беріңіз.</div>', unsafe_allow_html=True)

    # Карта параметрлері
    col_map_opt, col_map_info = st.columns([1, 2])
    with col_map_opt:
        map_type = st.selectbox("Карта стилі", [
            "OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"
        ])
        show_polyline = st.checkbox("Кәсіпорындарды сызықпен байланыстыру", value=True)
        show_circle   = st.checkbox("Экожүктемені шеңберлер арқылы көрсету", value=True)

    color_map = {
        "Көмір өндіру": "black",
        "Электроэнергетика": "orange",
        "Қара металлургия": "darkred",
        "Түсті металлургия": "purple",
        "Химия өнеркәсібі": "green",
        "Мұнай өндіру": "darkblue",
        "Газ өндіру": "blue",
    }

    center_lat = df["lat"].mean()
    center_lon = df["lon"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=9,
                   tiles=map_type)

    # Маркерлер
    for _, row in df.iterrows():
        color = color_map.get(row["Сала"], "gray")
        popup_html = f"""
        <b style='font-size:14px'>{row['Кәсіпорын']}</b><br>
        <hr style='margin:4px 0'>
        Сала: <b>{row['Сала']}</b><br>
        Өнім: <b>{row['Өнім_мың_т']:,} мың т</b><br>
        Жұмысшы: <b>{row['Жұмысшы_мың']} мың адам</b><br>
        Ластану коэф.: <b>{row['Ластану_коэф']}</b><br>
        <b style='color:red'>Экожүктеме: {row['Экожүктеме']:,}</b>
        """
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=row["Кәсіпорын"],
            icon=folium.Icon(color=color, icon="industry", prefix="fa")
        ).add_to(m)

        if show_circle:
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=max(5, row["Экожүктеме"] / df["Экожүктеме"].max() * 35),
                color="red", fill=True, fill_opacity=0.15,
                popup=f"Экожүктеме: {row['Экожүктеме']:,.0f}"
            ).add_to(m)

    # Сызықтар
    if show_polyline and len(df) > 1:
        coords = df[["lat","lon"]].values.tolist()
        folium.PolyLine(
            coords, color="#1B2A4A", weight=2,
            opacity=0.6, dash_array="5",
            tooltip="Өнеркәсіптік байланыс"
        ).add_to(m)

    # Легенда
    legend_html = """
    <div style='position:fixed;bottom:40px;left:40px;
         background:white;padding:12px 16px;border-radius:8px;
         border:1px solid #dee2e6;font-size:12px;z-index:999;
         box-shadow:0 2px 8px rgba(0,0,0,.15)'>
    <b style='font-size:13px'>Шеңбер — Экожүктеме</b><br>
    (Шеңбер үлкен = жүктеме жоғары)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    map_output = st_folium(m, width=None, height=520, use_container_width=True)

    # Карта талдауы
    st.markdown("### 🔍 Кеңістіктік талдау")
    col_mq1, col_mq2 = st.columns(2)
    with col_mq1:
        map_q1 = st.text_area(
            "🗺 Неге бұл кәсіпорындар бір-біріне жақын орналасқан?",
            placeholder="Шикізат, энергия, су, нарыққа жақындық...",
            height=110, key="map_q1"
        )
    with col_mq2:
        map_q2 = st.text_area(
            "🏫 Осы картаны мектеп сабағында қалай пайдаланасыз?",
            placeholder="Мысалы: 9-сыныпта экономикалық карта жұмысында...",
            height=110, key="map_q2"
        )

    map_q3 = st.text_area(
        "🌿 Ең жоғары экологиялық жүктемесі бар кәсіпорын қайда? Оның экологиялық салдарын сипаттаңыз:",
        placeholder="Картадағы шеңберлерге қарап жауап беріңіз...",
        height=100, key="map_q3"
    )


# ══════════════════════════════════════════════════════════════════
# TAB 5 — ҚОРЫТЫНДЫ
# ══════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="time-badge">⏱ 15 минут</div>', unsafe_allow_html=True)
    st.markdown("## ✍️ Аналитикалық қорытынды")

    st.markdown('<div class="tip-box">📌 <b>Тапсырма:</b> Төмендегі кестені толтырыңыз және рефлексия сұрақтарына жауап беріңіз. Сонан соң <b>Нәтижені жүктеп алыңыз</b>.</div>', unsafe_allow_html=True)

    # Педагогикалық қорытынды кесте
    st.markdown("### 📋 Педагогикалық қорытынды кесте")

    if "df_main" in st.session_state:
        df = st.session_state["df_main"]
        sectors = df["Сала"].tolist()
    else:
        sectors = ["Сала 1", "Сала 2", "Сала 3"]

    concl_data = {
        "Сала": sectors[:3] if len(sectors) >= 3 else sectors,
        "Негізгі орналасу факторы": [""] * min(3, len(sectors)),
        "Экологиялық проблема": [""] * min(3, len(sectors)),
        "Мектеп сабағындағы тақырып": [""] * min(3, len(sectors)),
    }
    df_concl = pd.DataFrame(concl_data)

    edited_concl = st.data_editor(
        df_concl, use_container_width=True, num_rows="fixed",
        key="concl_editor"
    )

    st.divider()
    st.markdown("### 💭 Рефлексия сұрақтары")

    refl_col1, refl_col2 = st.columns(2)
    with refl_col1:
        refl1 = st.text_area(
            "1️⃣ Бүгінгі сабақта қай бөлік сізге ең пайдалы болды?",
            placeholder="Кесте, диаграмма, карта немесе талдау бөлімі...",
            height=120, key="refl1"
        )
        refl2 = st.text_area(
            "2️⃣ Қандай қиындықтар кездесті?",
            placeholder="Деректер табу, код жазу, картаға қою...",
            height=120, key="refl2"
        )
    with refl_col2:
        refl3 = st.text_area(
            "3️⃣ Болашақ мұғалім ретінде осы тәсілді мектепте қалай қолданасыз?",
            placeholder="Нақты сынып, тақырып, технология...",
            height=120, key="refl3"
        )
        refl4 = st.text_area(
            "4️⃣ Цифрлық картография — мектеп географиясы үшін маңызды ма?",
            placeholder="Пікіріңізді дәлелмен жазыңыз...",
            height=120, key="refl4"
        )

    st.divider()

    # ── Балл есептеу ─────────────────────────────────────────────
    st.markdown("### 🏆 Автобағалау нәтижесі")

    score = 0
    breakdown = {}

    # Глоссарий (15 балл)
    gloss_score = min(15, sum(3 for v in [
        st.session_state.get("gloss_1",""),
        st.session_state.get("gloss_2",""),
        st.session_state.get("gloss_3",""),
        st.session_state.get("gloss_4",""),
        st.session_state.get("gloss_5",""),
    ] if len(v.strip()) > 10))
    breakdown["📖 Глоссарий"] = (gloss_score, 15)

    # Деректер (20 балл)
    has_data = "df_main" in st.session_state
    data_score = 20 if has_data else 0
    breakdown["📊 Деректер кестесі"] = (data_score, 20)

    # Диаграмма сұрақтары (20 балл)
    chart_answered = sum(1 for k in ["chart_q1","chart_q2","chart_q3","chart_q4"]
                         if len(st.session_state.get(k,"").strip()) > 15)
    chart_score = chart_answered * 5
    breakdown["📈 Диаграмма талдауы"] = (chart_score, 20)

    # Карта сұрақтары (20 балл)
    map_answered = sum(1 for k in ["map_q1","map_q2","map_q3"]
                       if len(st.session_state.get(k,"").strip()) > 15)
    map_score = min(20, map_answered * 7)
    breakdown["🗺️ Карта талдауы"] = (map_score, 20)

    # Рефлексия + қорытынды (25 балл)
    refl_answered = sum(1 for k in ["refl1","refl2","refl3","refl4"]
                        if len(st.session_state.get(k,"").strip()) > 15)
    refl_score = min(25, refl_answered * 6)
    breakdown["✍️ Қорытынды + рефлексия"] = (refl_score, 25)

    total_score = sum(v[0] for v in breakdown.values())

    col_score, col_breakdown = st.columns([1, 2])
    with col_score:
        grade = "A (Өте жақсы)" if total_score >= 85 else \
                "B (Жақсы)"     if total_score >= 70 else \
                "C (Орташа)"    if total_score >= 55 else "D (Толтырыңыз)"
        st.markdown(f"""
        <div class="score-block">
            <div style="font-size:13px; margin-bottom:4px; opacity:.7;">Жинаған балл</div>
            <div class="big">{total_score}</div>
            <div style="font-size:13px; opacity:.7;">/ 100</div>
            <div style="margin-top:12px; font-size:16px; color:#A8D5BA;">{grade}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_breakdown:
        st.markdown("**Бөлім бойынша балл:**")
        for crit, (earned, max_pts) in breakdown.items():
            pct = earned / max_pts if max_pts > 0 else 0
            color = "normal" if pct >= 0.7 else ("off" if pct < 0.4 else "normal")
            st.metric(label=crit, value=f"{earned}/{max_pts}", delta=f"{pct*100:.0f}%")

    # ── Нәтижені жүктеп алу ──────────────────────────────────────
    st.divider()
    st.markdown("### 💾 Нәтижені жүктеп алу")

    if st.button("📄 Есепті жасау және жүктеу (TXT)", use_container_width=True):
        report_lines = [
            "=" * 60,
            "ИНДУСТРИЯЛЫҚ ҚАЗАҚСТАН — ПРАКТИКАЛЫҚ ЖҰМЫС ЕСЕБІ",
            "=" * 60,
            f"Студент    : {student_name or 'Белгісіз'}",
            f"Топ        : {student_group or '—'}",
            f"Өңір       : {student_region}",
            f"Күні       : {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            f"ЖАЛПЫ БАЛЛ : {total_score} / 100  ({grade})",
            "",
            "─" * 40,
            "БӨЛІМ БОЙЫНША БАЛЛ:",
            "─" * 40,
        ]
        for crit, (earned, max_pts) in breakdown.items():
            report_lines.append(f"  {crit}: {earned}/{max_pts}")

        report_lines += ["", "─" * 40, "ДЕРЕКТЕР КЕСТЕСІ:", "─" * 40]
        if "df_main" in st.session_state:
            report_lines.append(st.session_state["df_main"].to_string(index=False))

        report_lines += ["", "─" * 40, "РЕФЛЕКСИЯ:", "─" * 40]
        for i, k in enumerate(["refl1","refl2","refl3","refl4"], 1):
            report_lines.append(f"Сұрақ {i}: {st.session_state.get(k,'—')}")

        report_text = "\n".join(report_lines)

        st.download_button(
            label="⬇️ Есепті жүктеу (.txt)",
            data=report_text.encode("utf-8"),
            file_name=f"report_{student_name or 'student'}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    st.markdown('<div class="warn-box">⚠️ <b>Тапсыру:</b> Есепті жүктеп алып, мұғалімге <b>Google Classroom</b> немесе <b>электрондық пошта</b> арқылы жіберіңіз.</div>', unsafe_allow_html=True)
