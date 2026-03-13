import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import base64
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIG & PALETTE
# ─────────────────────────────────────────────
NAVY    = "#262E4B"
TEAL    = "#86B9B7"
GOLD    = "#D3A021"
GREEN   = "#A4D65E"
WHITE   = "#FFFFFF"
GREY_BG = "#F7F8FA"
GREY_TX = "#6B7280"
PALETTE = [TEAL, GOLD, GREEN, NAVY, "#E8786F", "#9B8EC5"]

# Logo (base64-embedded for Streamlit Cloud compatibility)
LOGO_PATH = Path(__file__).parent / "Logo_NB_actenergy_négatif.png"
LOGO_B64 = ""
if LOGO_PATH.exists():
    try:
        from PIL import Image
        import io
        img = Image.open(LOGO_PATH).convert("RGBA")
        pixels = img.load()
        # Black background → transparent (white logo stays)
        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = pixels[x, y]
                if r < 40 and g < 40 and b < 40:
                    pixels[x, y] = (0, 0, 0, 0)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        LOGO_B64 = base64.b64encode(buf.getvalue()).decode()
    except Exception:
        LOGO_B64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()

st.set_page_config(
    page_title="Act Energy — Portfolio Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700;1,9..40,300&display=swap');

    /* ── Global ── */
    html, body, [class*="st-"] {{
        font-family: 'DM Sans', sans-serif;
    }}
    .stApp {{
        background-color: {GREY_BG};
    }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {{
        background-color: {NAVY};
    }}
    section[data-testid="stSidebar"] * {{
        color: {WHITE} !important;
    }}
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stRadio label {{
        color: {TEAL} !important;
        font-weight: 500;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* ── Multiselect tags (green instead of red) ── */
    span[data-baseweb="tag"] {{
        background-color: {GREEN} !important;
        color: {NAVY} !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }}
    span[data-baseweb="tag"] span {{
        color: {NAVY} !important;
    }}
    span[data-baseweb="tag"] svg {{
        color: {NAVY} !important;
        fill: {NAVY} !important;
    }}

    /* ── Checkbox: green box only, not the label ── */
    [data-testid="stCheckbox"] [data-testid="stWidgetLabel"] {{
        background: transparent !important;
    }}
    /* Override Streamlit red accent globally */
    :root {{
        --primary-color: {GREEN} !important;
    }}
    /* Target the checkbox square via baseweb */
    [data-baseweb="checkbox"] > div:first-child {{
        border-color: {GREEN} !important;
    }}
    [data-baseweb="checkbox"] > div:first-child[aria-hidden="true"] {{
        background-color: {GREEN} !important;
        border-color: {GREEN} !important;
    }}
    /* Checkmark stroke */
    [data-baseweb="checkbox"] svg {{
        fill: {GREEN} !important;
    }}

    /* ── Radio button: green dot only ── */
    div[data-baseweb="radio"] > div:first-child > div {{
        background-color: {GREEN} !important;
        border-color: {GREEN} !important;
    }}

    /* ── KPI cards ── */
    .kpi-card {{
        background: {WHITE};
        border-radius: 12px;
        padding: 1.4rem 1.6rem;
        box-shadow: 0 1px 4px rgba(38,46,75,0.06);
        border-left: 4px solid {TEAL};
        transition: transform 0.15s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(38,46,75,0.10);
    }}
    .kpi-label {{
        font-size: 0.75rem;
        font-weight: 500;
        color: {GREY_TX};
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.25rem;
    }}
    .kpi-value {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {NAVY};
        line-height: 1.1;
    }}
    .kpi-sub {{
        font-size: 0.78rem;
        color: {GREY_TX};
        margin-top: 0.2rem;
    }}
    .kpi-gold  {{ border-left-color: {GOLD}; }}
    .kpi-green {{ border-left-color: {GREEN}; }}
    .kpi-navy  {{ border-left-color: {NAVY}; }}

    /* ── Section headers ── */
    .section-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {NAVY};
        margin: 2rem 0 0.6rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 2px solid {TEAL};
        display: inline-block;
    }}

    /* ── Page header ── */
    .page-header {{
        font-size: 0.65rem;
        font-weight: 500;
        color: {TEAL};
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: -0.3rem;
    }}
    .page-title {{
        font-size: 1.6rem;
        font-weight: 700;
        color: {NAVY};
        margin-bottom: 1.5rem;
    }}

    /* ── Hide Streamlit defaults ── */
    #MainMenu, footer {{visibility: hidden;}}

    /* ── Sidebar collapse/expand button — nuclear reset ── */
    /* Hide absolutely everything inside the buttons */
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] *,
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] * {{
        font-size: 0px !important;
        color: transparent !important;
        letter-spacing: -9999px !important;
        text-indent: -9999px !important;
        overflow: hidden !important;
    }}
    /* Style the button containers */
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapseButton"] button {{
        background: {GREY_BG} !important;
        border: 1px solid #E0E2E8 !important;
        border-radius: 8px !important;
        width: 2rem !important;
        height: 2rem !important;
        min-width: 2rem !important;
        min-height: 2rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative !important;
        cursor: pointer !important;
        padding: 0 !important;
    }}
    [data-testid="collapsedControl"] button:hover,
    [data-testid="stSidebarCollapseButton"] button:hover {{
        background: {WHITE} !important;
        border-color: {TEAL} !important;
    }}
    /* Inject arrow via ::after — expand button (sidebar closed): → */
    [data-testid="collapsedControl"] button::after {{
        content: "›" !important;
        font-size: 1.4rem !important;
        color: {NAVY} !important;
        text-indent: 0 !important;
        letter-spacing: normal !important;
        position: absolute !important;
        inset: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
        font-weight: 300 !important;
    }}
    [data-testid="collapsedControl"] button:hover::after {{
        color: {TEAL} !important;
    }}
    /* Inject arrow via ::after — collapse button (sidebar open): ‹ */
    [data-testid="stSidebarCollapseButton"] button::after {{
        content: "‹" !important;
        font-size: 1.4rem !important;
        color: {WHITE} !important;
        text-indent: 0 !important;
        letter-spacing: normal !important;
        position: absolute !important;
        inset: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
        font-weight: 300 !important;
    }}
    [data-testid="stSidebarCollapseButton"] button:hover::after {{
        color: {GREEN} !important;
    }}
    /* Collapse button (inside sidebar) — transparent bg */
    [data-testid="stSidebarCollapseButton"] button {{
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        box-shadow: none !important;
    }}
    [data-testid="stSidebarCollapseButton"] button:hover {{
        background: rgba(255,255,255,0.08) !important;
        border-color: {TEAL} !important;
    }}
    /* Transparent header bar */
    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    /* ── Dataframes ── */
    .stDataFrame {{
        border-radius: 8px;
        overflow: hidden;
    }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
DATA_FILE = Path(__file__).parent / "MyAct_Final_Fuzzy.xlsx"

@st.cache_data
def load_data():
    import openpyxl
    wb = openpyxl.load_workbook(DATA_FILE, read_only=True)
    sheets = wb.sheetnames
    wb.close()

    inv = pd.read_excel(DATA_FILE, sheet_name="Inventaire")

    # Anomalies sheet
    if "Anomalies" in sheets:
        ano = pd.read_excel(DATA_FILE, sheet_name="Anomalies")
    else:
        ano = pd.DataFrame(columns=["Type", "EAN", "Détail"])

    # Fuzzy report — handle both naming conventions
    fuz_sheet = next((s for s in sheets if s.lower().startswith("rapport") or s.lower().startswith("harmoni")), None)
    if fuz_sheet:
        fuz = pd.read_excel(DATA_FILE, sheet_name=fuz_sheet)
        # Normalize columns for both formats
        if "Nb EAN Affectés" not in fuz.columns and "Nb enregistrements" in fuz.columns:
            fuz = fuz.rename(columns={"Nb enregistrements": "Nb EAN Affectés"})
        for col in ["Type", "Confiance", "Nb EAN Affectés"]:
            if col not in fuz.columns:
                fuz[col] = "N/A" if col != "Nb EAN Affectés" else 0
    else:
        fuz = pd.DataFrame(columns=["Type", "Confiance", "Nb EAN Affectés"])

    inv["conso_mwh"] = inv["site_consommation_annuelle"] / 1000
    inv["injection_mwh"] = inv["site_injection_annuelle"] / 1000
    inv["has_injection"] = inv["site_injection_annuelle"] > 0
    inv["vecteur"] = np.where(
        inv["has_injection"], "Injection",
        np.where(inv["site_type_energie"] == "Gaz", "Gaz", "Électricité")
    )
    return inv, ano, fuz

df_all, df_ano, df_fuz = load_data()


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    if LOGO_B64:
        st.markdown(f"""
            <div style="text-align:center; padding: 1.2rem 1rem 0.4rem 1rem;">
                <img src="data:image/png;base64,{LOGO_B64}"
                     style="max-width:170px; width:100%; height:auto;" />
                <div style="font-size:0.68rem; color:{GREY_TX}; letter-spacing:0.10em; margin-top:0.6rem;">
                    PORTFOLIO DASHBOARD
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div style="text-align:center; padding: 1rem 0 1.5rem 0;">
                <div style="font-size:1.5rem; font-weight:700; color:{TEAL};">Act Energy</div>
                <div style="font-size:0.72rem; color:{GREY_TX}; letter-spacing:0.08em; margin-top:0.2rem;">
                    PORTFOLIO DASHBOARD
                </div>
            </div>
        """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Vue d'ensemble", "Segmentation", "Groupes", "Sociétés"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(f'<div style="font-size:0.7rem; color:{TEAL}; font-weight:600; letter-spacing:0.08em; margin-bottom:0.5rem;">FILTRES</div>', unsafe_allow_html=True)

    f_segment = st.multiselect("Segment", ["Public", "Privé"], default=["Public", "Privé"])
    f_energie = st.multiselect("Énergie", sorted(df_all["site_type_energie"].unique()), default=sorted(df_all["site_type_energie"].unique()))
    f_releve  = st.multiselect("Relevé", sorted(df_all["site_type_releve"].unique()), default=sorted(df_all["site_type_releve"].unique()))
    f_lot     = st.multiselect("Lot", sorted(df_all["site_lot"].unique()), default=sorted(df_all["site_lot"].unique()))
    f_actif   = st.checkbox("Groupes actifs uniquement", value=True)

# Apply filters
df = df_all.copy()
df = df[df["groupe_type"].isin(f_segment)]
df = df[df["site_type_energie"].isin(f_energie)]
df = df[df["site_type_releve"].isin(f_releve)]
df = df[df["site_lot"].isin(f_lot)]
if f_actif:
    df = df[df["groupe_actif"] == True]


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def kpi_card(label, value, sub="", style=""):
    return f"""
    <div class="kpi-card {style}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """

def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)

def chart_layout(fig, h=380):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color=NAVY, size=12),
        margin=dict(l=20, r=20, t=40, b=20),
        height=h,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=11),
            title_text="",
        ),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#EAECF0", zeroline=False)
    return fig

def fmt_mwh(v):
    if v >= 1_000_000:
        return f"{v/1_000_000:,.1f} TWh"
    if v >= 1_000:
        return f"{v/1_000:,.1f} GWh"
    return f"{v:,.0f} MWh"


# ═══════════════════════════════════════════════
# PAGE: VUE D'ENSEMBLE
# ═══════════════════════════════════════════════
if page == "Vue d'ensemble":
    st.markdown('<div class="page-header">Portfolio Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Vue d\'ensemble</div>', unsafe_allow_html=True)

    # ── KPI ROW ──
    total_ean = len(df)
    total_grp = df["groupe_nom"].nunique()
    total_soc = df["societe_nom"].nunique()
    total_mwh = df["conso_mwh"].sum()
    total_inj = df[df["has_injection"]].shape[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(kpi_card("Compteurs EAN", f"{total_ean:,}", f"sur {len(df_all):,} total"), unsafe_allow_html=True)
    c2.markdown(kpi_card("Groupes", f"{total_grp}", f"{df[df.groupe_type=='Public']['groupe_nom'].nunique()} pub · {df[df.groupe_type=='Privé']['groupe_nom'].nunique()} priv", "kpi-gold"), unsafe_allow_html=True)
    c3.markdown(kpi_card("Sociétés", f"{total_soc:,}", "", "kpi-green"), unsafe_allow_html=True)
    c4.markdown(kpi_card("Consommation", fmt_mwh(total_mwh), "annuelle totale", "kpi-navy"), unsafe_allow_html=True)
    c5.markdown(kpi_card("Prosumers", f"{total_inj}", f"{fmt_mwh(df['injection_mwh'].sum())} injectés", "kpi-gold"), unsafe_allow_html=True)

    st.markdown("")

    # ── CHARTS ROW 1 ──
    col1, col2, col3 = st.columns(3)

    with col1:
        section("Vecteur énergétique")
        vec = df["vecteur"].value_counts().reset_index()
        vec.columns = ["Vecteur", "Count"]
        fig = px.pie(
            vec, names="Vecteur", values="Count", hole=0.55,
            color="Vecteur",
            color_discrete_map={"Électricité": TEAL, "Gaz": GOLD, "Injection": GREEN},
        )
        fig.update_traces(
            textinfo="label+percent", textfont_size=12,
            marker=dict(line=dict(color=WHITE, width=2)),
        )
        chart_layout(fig, 320)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Type de relevé")
        rel = df["site_type_releve"].value_counts().reindex(["AMR","MMR","SMR","YMR"]).fillna(0).reset_index()
        rel.columns = ["Type", "Count"]
        fig = px.bar(
            rel, x="Count", y="Type", orientation="h",
            color_discrete_sequence=[TEAL],
            text="Count",
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", textfont_size=11)
        chart_layout(fig, 320)
        fig.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        section("Lot tarifaire")
        lot = df["site_lot"].value_counts().reset_index()
        lot.columns = ["Lot", "Count"]
        fig = px.bar(
            lot, x="Count", y="Lot", orientation="h",
            color_discrete_sequence=[GOLD],
            text="Count",
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", textfont_size=11)
        chart_layout(fig, 320)
        fig.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    # ── CHARTS ROW 2 ──
    col1, col2 = st.columns(2)

    with col1:
        section("Type de compteur")
        cpt = df["site_type_compteur"].value_counts().reset_index()
        cpt.columns = ["Type", "Count"]
        fig = px.bar(
            cpt, x="Type", y="Count",
            color="Type",
            color_discrete_sequence=[TEAL, GOLD, GREEN],
            text="Count",
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", textfont_size=11)
        chart_layout(fig, 340)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Énergie × Relevé — matrice")
        ct = pd.crosstab(df["site_type_energie"], df["site_type_releve"])
        fig = px.imshow(
            ct, text_auto=True,
            color_continuous_scale=[[0, WHITE], [0.5, TEAL], [1, NAVY]],
            aspect="auto",
        )
        chart_layout(fig, 340)
        fig.update_layout(coloraxis_showscale=False, xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════
# PAGE: SEGMENTATION
# ═══════════════════════════════════════════════
elif page == "Segmentation":
    st.markdown('<div class="page-header">Public vs Privé</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Segmentation</div>', unsafe_allow_html=True)

    seg = df.groupby("groupe_type").agg(
        nb_ean=("site_EAN", "count"),
        nb_grp=("groupe_nom", "nunique"),
        nb_soc=("societe_nom", "nunique"),
        conso=("conso_mwh", "sum"),
    ).reset_index()

    c1, c2 = st.columns(2)
    for i, row in seg.iterrows():
        col = c1 if row.groupe_type == "Public" else c2
        accent = TEAL if row.groupe_type == "Public" else GOLD
        with col:
            st.markdown(f"""
                <div style="background:{WHITE}; border-radius:14px; padding:1.8rem;
                     box-shadow:0 1px 6px rgba(38,46,75,0.07); border-top:4px solid {accent};">
                    <div style="font-size:1.3rem; font-weight:700; color:{NAVY}; margin-bottom:1rem;">
                        {'🏛️' if row.groupe_type=='Public' else '🏢'} {row.groupe_type}
                    </div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
                        <div><span style="font-size:0.72rem; color:{GREY_TX}; text-transform:uppercase;">EAN</span><br>
                             <span style="font-size:1.5rem; font-weight:700; color:{NAVY};">{row.nb_ean:,}</span></div>
                        <div><span style="font-size:0.72rem; color:{GREY_TX}; text-transform:uppercase;">Groupes</span><br>
                             <span style="font-size:1.5rem; font-weight:700; color:{NAVY};">{row.nb_grp}</span></div>
                        <div><span style="font-size:0.72rem; color:{GREY_TX}; text-transform:uppercase;">Sociétés</span><br>
                             <span style="font-size:1.5rem; font-weight:700; color:{NAVY};">{row.nb_soc:,}</span></div>
                        <div><span style="font-size:0.72rem; color:{GREY_TX}; text-transform:uppercase;">Consommation</span><br>
                             <span style="font-size:1.5rem; font-weight:700; color:{NAVY};">{fmt_mwh(row.conso)}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns(2)

    with col1:
        section("EAN par segment et vecteur")
        seg_vec = df.groupby(["groupe_type", "vecteur"]).size().reset_index(name="count")
        fig = px.bar(
            seg_vec, x="groupe_type", y="count", color="vecteur",
            barmode="group",
            color_discrete_map={"Électricité": TEAL, "Gaz": GOLD, "Injection": GREEN},
            text="count",
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", textfont_size=11)
        chart_layout(fig, 380)
        fig.update_layout(xaxis_title="", yaxis_title="Nombre d'EAN")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Consommation par segment (MWh)")
        seg_e = df.groupby(["groupe_type", "site_type_energie"])["conso_mwh"].sum().reset_index()
        fig = px.bar(
            seg_e, x="groupe_type", y="conso_mwh", color="site_type_energie",
            barmode="stack",
            color_discrete_map={"Electricité": TEAL, "Gaz": GOLD, "Électricité": TEAL},
            text_auto=".3s",
        )
        chart_layout(fig, 380)
        fig.update_layout(xaxis_title="", yaxis_title="MWh")
        st.plotly_chart(fig, use_container_width=True)

    # ── Relevé & Lot par segment ──
    col1, col2 = st.columns(2)
    with col1:
        section("Type de relevé par segment")
        seg_rel = df.groupby(["groupe_type","site_type_releve"]).size().reset_index(name="count")
        fig = px.bar(
            seg_rel, x="site_type_releve", y="count", color="groupe_type",
            barmode="group",
            color_discrete_map={"Public": TEAL, "Privé": GOLD},
            text="count",
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", textfont_size=10)
        chart_layout(fig, 360)
        fig.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Lot tarifaire par segment")
        seg_lot = df.groupby(["groupe_type","site_lot"]).size().reset_index(name="count")
        fig = px.bar(
            seg_lot, x="site_lot", y="count", color="groupe_type",
            barmode="group",
            color_discrete_map={"Public": TEAL, "Privé": GOLD},
            text="count",
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", textfont_size=10)
        chart_layout(fig, 360)
        fig.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════
# PAGE: GROUPES
# ═══════════════════════════════════════════════
elif page == "Groupes":
    st.markdown('<div class="page-header">Analyse par groupe</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Groupes clients</div>', unsafe_allow_html=True)

    # ── Aggregation ──
    grp = df.groupby(["groupe_nom","groupe_type"]).agg(
        nb_ean=("site_EAN","count"),
        nb_soc=("societe_nom","nunique"),
        conso_mwh=("conso_mwh","sum"),
        conso_elec_grp=("groupe_consommation_totale_electricite","first"),
        conso_gaz_grp=("groupe_consommation_totale_gaz","first"),
        nb_amr=("site_type_releve", lambda x: (x=="AMR").sum()),
        nb_ymr=("site_type_releve", lambda x: (x=="YMR").sum()),
        nb_mmr=("site_type_releve", lambda x: (x=="MMR").sum()),
    ).reset_index().sort_values("nb_ean", ascending=False)

    # ── Top 20 bar chart ──
    section("Top 20 groupes — nombre d'EAN")
    top20 = grp.head(20)
    fig = px.bar(
        top20, x="nb_ean", y="groupe_nom", orientation="h",
        color="groupe_type",
        color_discrete_map={"Public": TEAL, "Privé": GOLD},
        text="nb_ean",
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", textfont_size=11)
    fig.update_yaxes(categoryorder="total ascending")
    chart_layout(fig, max(400, len(top20)*28))
    fig.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    # ── Consumption stacked ──
    col1, col2 = st.columns(2)
    with col1:
        section("Consommation par groupe (MWh)")
        grp_e = df.groupby(["groupe_nom","site_type_energie"])["conso_mwh"].sum().reset_index()
        grp_e_top = grp_e[grp_e.groupe_nom.isin(top20.groupe_nom)]
        fig = px.bar(
            grp_e_top, x="conso_mwh", y="groupe_nom", orientation="h",
            color="site_type_energie",
            color_discrete_map={"Electricité": TEAL, "Gaz": GOLD, "Électricité": TEAL},
        )
        fig.update_yaxes(categoryorder="total ascending")
        chart_layout(fig, max(400, len(top20)*26))
        fig.update_layout(xaxis_title="MWh", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Profil de relevé par groupe")
        melt = top20[["groupe_nom","nb_amr","nb_ymr","nb_mmr"]].melt(
            id_vars="groupe_nom", var_name="type", value_name="count"
        )
        melt["type"] = melt["type"].map({"nb_amr":"AMR","nb_ymr":"YMR","nb_mmr":"MMR"})
        fig = px.bar(
            melt, x="count", y="groupe_nom", orientation="h",
            color="type", barmode="stack",
            color_discrete_map={"AMR": GREEN, "YMR": TEAL, "MMR": GOLD},
        )
        fig.update_yaxes(categoryorder="total ascending")
        chart_layout(fig, max(400, len(top20)*26))
        fig.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    # ── Drill-down ──
    section("Détail d'un groupe")
    selected_grp = st.selectbox(
        "Sélectionner un groupe",
        grp["groupe_nom"].tolist(),
        label_visibility="collapsed",
    )
    if selected_grp:
        sub = df[df["groupe_nom"] == selected_grp]
        gc1, gc2, gc3, gc4 = st.columns(4)
        gc1.markdown(kpi_card("EAN", f"{len(sub):,}"), unsafe_allow_html=True)
        gc2.markdown(kpi_card("Sociétés", f"{sub['societe_nom'].nunique()}", "", "kpi-gold"), unsafe_allow_html=True)
        gc3.markdown(kpi_card("Conso totale", fmt_mwh(sub['conso_mwh'].sum()), "", "kpi-green"), unsafe_allow_html=True)
        gc4.markdown(kpi_card("Segment", sub['groupe_type'].iloc[0], "", "kpi-navy"), unsafe_allow_html=True)

        st.markdown("")
        soc_detail = sub.groupby("societe_nom").agg(
            EAN=("site_EAN","count"),
            Conso_MWh=("conso_mwh","sum"),
            Élec=("site_type_energie", lambda x: (x=="Electricité").sum() + (x=="Électricité").sum()),
            Gaz=("site_type_energie", lambda x: (x=="Gaz").sum()),
        ).sort_values("EAN", ascending=False).reset_index()
        soc_detail.columns = ["Société", "EAN", "Conso (MWh)", "Élec", "Gaz"]
        soc_detail["Conso (MWh)"] = soc_detail["Conso (MWh)"].round(1)
        st.dataframe(
            soc_detail,
            use_container_width=True,
            hide_index=True,
            height=min(400, 35 * len(soc_detail) + 38),
        )


# ═══════════════════════════════════════════════
# PAGE: SOCIÉTÉS
# ═══════════════════════════════════════════════
elif page == "Sociétés":
    st.markdown('<div class="page-header">Analyse par société</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Sociétés</div>', unsafe_allow_html=True)

    soc = df.groupby("societe_nom").agg(
        nb_ean=("site_EAN","count"),
        conso_mwh=("conso_mwh","sum"),
        groupe=("groupe_nom","first"),
        segment=("groupe_type","first"),
    ).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        section("Top 20 sociétés — nombre d'EAN")
        top_soc = soc.nlargest(20, "nb_ean")
        fig = px.bar(
            top_soc, x="nb_ean", y="societe_nom", orientation="h",
            color="segment",
            color_discrete_map={"Public": TEAL, "Privé": GOLD},
            text="nb_ean",
        )
        fig.update_traces(texttemplate="%{text}", textposition="outside", textfont_size=11)
        fig.update_yaxes(categoryorder="total ascending")
        chart_layout(fig, 500)
        fig.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("Top 20 sociétés — consommation (MWh)")
        top_conso = soc.nlargest(20, "conso_mwh")
        fig = px.bar(
            top_conso, x="conso_mwh", y="societe_nom", orientation="h",
            color="segment",
            color_discrete_map={"Public": TEAL, "Privé": GOLD},
        )
        fig.update_yaxes(categoryorder="total ascending")
        chart_layout(fig, 500)
        fig.update_layout(xaxis_title="MWh", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    # ── Distribution ──
    section("Distribution — EAN par société")
    bins = [0, 1, 5, 10, 50, 100, float("inf")]
    labels = ["1", "2-5", "6-10", "11-50", "51-100", "100+"]
    soc["tranche"] = pd.cut(soc["nb_ean"], bins=bins, labels=labels, right=True)
    dist = soc["tranche"].value_counts().reindex(labels).fillna(0).reset_index()
    dist.columns = ["Tranche", "Sociétés"]
    fig = px.bar(
        dist, x="Tranche", y="Sociétés",
        color_discrete_sequence=[TEAL],
        text="Sociétés",
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside", textfont_size=12)
    chart_layout(fig, 340)
    fig.update_layout(xaxis_title="Nombre d'EAN", yaxis_title="Nombre de sociétés")
    st.plotly_chart(fig, use_container_width=True)

    # ── Distribution consommation ──
    section("Distribution — consommation annuelle par site (échelle log)")
    df_pos = df[df["site_consommation_annuelle"] > 0].copy()
    df_pos["log_conso"] = np.log10(df_pos["site_consommation_annuelle"])
    fig = px.histogram(
        df_pos, x="log_conso", nbins=50,
        color_discrete_sequence=[TEAL],
        labels={"log_conso": "log₁₀(kWh)"},
    )
    chart_layout(fig, 320)
    fig.update_layout(yaxis_title="Nombre de sites", xaxis_title="log₁₀(consommation kWh)")
    st.plotly_chart(fig, use_container_width=True)


