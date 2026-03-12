import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# ── CONFIG ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ACT Energy — BI Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PALETTE ─────────────────────────────────────────────────────────────────
C = {
    'bg':       '#0D1117',
    'card':     '#161B22',
    'border':   '#21262D',
    'accent':   '#00D4AA',
    'accent2':  '#4ECDC4',
    'accent3':  '#F7B731',
    'red':      '#FF4757',
    'orange':   '#FF6348',
    'blue':     '#2F86EB',
    'purple':   '#7C4DFF',
    'text':     '#E6EDF3',
    'muted':    '#8B949E',
    'ht':       '#2F86EB',
    'bt':       '#00D4AA',
    'hp':       '#7C4DFF',
    'bp':       '#4ECDC4',
}

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {C['bg']};
    color: {C['text']};
}}
.stApp {{ background-color: {C['bg']}; }}

/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: {C['card']};
    border-right: 1px solid {C['border']};
}}
[data-testid="stSidebar"] * {{ color: {C['text']} !important; }}

/* Remove default padding */
.block-container {{ padding-top: 1rem; padding-bottom: 2rem; }}

/* KPI Cards */
.kpi-card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 12px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
}}
.kpi-card.green::before  {{ background: {C['accent']}; }}
.kpi-card.blue::before   {{ background: {C['blue']}; }}
.kpi-card.yellow::before {{ background: {C['accent3']}; }}
.kpi-card.red::before    {{ background: {C['red']}; }}
.kpi-card.purple::before {{ background: {C['purple']}; }}

.kpi-label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: {C['muted']};
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 6px;
}}
.kpi-value {{
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 4px;
}}
.kpi-sub {{
    font-size: 0.78rem;
    color: {C['muted']};
    font-weight: 300;
}}
.kpi-badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 500;
    font-family: 'DM Mono', monospace;
}}
.badge-green  {{ background: rgba(0,212,170,0.15); color: {C['accent']}; }}
.badge-red    {{ background: rgba(255,71,87,0.15);  color: {C['red']}; }}
.badge-yellow {{ background: rgba(247,183,49,0.15); color: {C['accent3']}; }}
.badge-blue   {{ background: rgba(47,134,235,0.15); color: {C['blue']}; }}

/* Section headers */
.section-header {{
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    color: {C['muted']};
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin: 28px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid {C['border']};
}}

/* Page title */
.dash-title {{
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: {C['text']};
    display: flex;
    align-items: center;
    gap: 10px;
}}
.dash-subtitle {{
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: {C['muted']};
    margin-top: 2px;
}}

/* Table */
.styled-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
}}
.styled-table th {{
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {C['muted']};
    padding: 8px 12px;
    border-bottom: 1px solid {C['border']};
    text-align: left;
    white-space: nowrap;
}}
.styled-table td {{
    padding: 7px 12px;
    border-bottom: 1px solid rgba(33,38,45,0.5);
    color: {C['text']};
}}
.styled-table tr:hover td {{ background: rgba(0,212,170,0.04); }}

/* Lot badges */
.lot-ht {{ background:rgba(47,134,235,0.2);  color:{C['ht']};     padding:1px 7px; border-radius:4px; font-family:'DM Mono',monospace; font-size:0.72rem; }}
.lot-bt {{ background:rgba(0,212,170,0.2);   color:{C['bt']};     padding:1px 7px; border-radius:4px; font-family:'DM Mono',monospace; font-size:0.72rem; }}
.lot-hp {{ background:rgba(124,77,255,0.2);  color:{C['hp']};     padding:1px 7px; border-radius:4px; font-family:'DM Mono',monospace; font-size:0.72rem; }}
.lot-bp {{ background:rgba(78,205,196,0.2);  color:{C['bp']};     padding:1px 7px; border-radius:4px; font-family:'DM Mono',monospace; font-size:0.72rem; }}

div[data-testid="stSelectbox"] label,
div[data-testid="stMultiSelect"] label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {C['muted']} !important;
}}
div[data-testid="stTabs"] button {{
    font-family: 'Syne', sans-serif;
    font-weight: 600;
}}
</style>
""", unsafe_allow_html=True)

# ── DATA ────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Chargement du SSoT Master…")
def load_data():
    df = pd.read_excel("ACT_Energy_SSoT_Final_v3.xlsx", sheet_name="SSoT Master", header=1)
    df.columns = df.columns.str.strip()
    df['conso_kwh'] = pd.to_numeric(df['Site_Consommation annuelle réelle'], errors='coerce').fillna(0)
    df['conso_gwh'] = df['conso_kwh'] / 1e6
    df['Lot'] = df['Lot'].fillna('').astype(str).str.strip()
    df['Source'] = df['Source'].fillna('').astype(str).str.strip()
    df['Type_Energie'] = df['Type_Energie'].fillna('').astype(str).str.strip()
    df['Groupe_Type'] = df['Groupe_Type'].fillna('').astype(str).str.strip()
    df['Région'] = df['Région'].fillna('Inconnue').astype(str).str.strip()
    df['GRD'] = df['GRD'].fillna('Inconnu').astype(str).str.strip()
    df['Site_Nom'] = df['Site_Nom'].fillna('').astype(str).str.strip()
    df['Groupe_Nom'] = df['Groupe_Nom'].fillna('').astype(str).str.strip()
    df['is_anomaly_zero']     = df['conso_kwh'] == 0
    df['is_anomaly_tiny']     = (df['conso_kwh'] > 0) & (df['conso_kwh'] < 10)
    df['is_anomaly_ht_small'] = df['Lot'].isin(['HT','HP']) & (df['conso_kwh'] > 0) & (df['conso_kwh'] < 50000)
    df['has_anomaly'] = df['is_anomaly_zero'] | df['is_anomaly_tiny'] | df['is_anomaly_ht_small']

    # Monthly cols
    months = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
    for m in months:
        for t in ['HP','HC']:
            col = f'{m} {t}'
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
    return df, months

df, MONTHS = load_data()

# ── PLOTLY THEME ─────────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter, sans-serif', color=C['text'], size=11),
    margin=dict(l=12, r=12, t=28, b=12),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=10)),
    xaxis=dict(gridcolor=C['border'], linecolor=C['border'], tickfont=dict(size=10)),
    yaxis=dict(gridcolor=C['border'], linecolor=C['border'], tickfont=dict(size=10)),
)

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:12px 0 20px 0">
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;color:{C['text']}">
            ⚡ ACT Energy
        </div>
        <div style="font-family:'DM Mono',monospace;font-size:0.65rem;color:{C['muted']};margin-top:3px">
            SSoT Master — Intelligence Portefeuille
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.selectbox("Navigation", [
        "📊 Vue Portefeuille",
        "🏢 Vue Client",
        "⚡ Vue EAN",
        "🚨 Anomalies"
    ], label_visibility="collapsed")

    st.markdown(f'<div class="section-header">Filtres globaux</div>', unsafe_allow_html=True)

    sources_all = sorted([s for s in df['Source'].unique() if s])
    sel_sources = st.multiselect("Source", sources_all, default=sources_all, placeholder="Toutes les sources")

    lots_all = ['HT','BT','HP','BP']
    sel_lots = st.multiselect("Lot", lots_all, default=lots_all, placeholder="Tous les lots")

    type_all = ['Electricité','Gaz','Injection']
    sel_types = st.multiselect("Énergie", type_all, default=['Electricité','Gaz'], placeholder="Tous")

    st.markdown(f'<div class="section-header">Qualité données</div>', unsafe_allow_html=True)
    hide_zero = st.toggle("Masquer conso = 0", value=False)

    st.markdown(f"""
    <div style="margin-top:auto;padding-top:32px;font-family:'DM Mono',monospace;font-size:0.62rem;color:{C['muted']};line-height:1.8">
        SSoT v3 · {len(df):,} EANs<br>
        21 sources · 53 colonnes<br>
        Belgique — Wallonie / BXL / Flandre
    </div>
    """, unsafe_allow_html=True)

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
dff = df.copy()
if sel_sources: dff = dff[dff['Source'].isin(sel_sources)]
if sel_lots:    dff = dff[dff['Lot'].isin(sel_lots)]
if sel_types:   dff = dff[dff['Type_Energie'].isin(sel_types)]
if hide_zero:   dff = dff[dff['conso_kwh'] > 0]

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — VUE PORTEFEUILLE
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Vue Portefeuille":

    st.markdown(f"""
    <div class="dash-title">📊 Vue Portefeuille</div>
    <div class="dash-subtitle">Périmètre global · {len(dff):,} EANs sélectionnés sur {len(df):,}</div>
    """, unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">Indicateurs clés</div>', unsafe_allow_html=True)
    k1, k2, k3, k4, k5 = st.columns(5)

    total_gwh  = dff['conso_gwh'].sum()
    eans_actifs = (dff['conso_kwh'] > 0).sum()
    pub_gwh    = dff[dff['Groupe_Type']=='Public']['conso_gwh'].sum()
    prv_gwh    = dff[dff['Groupe_Type']=='Privé']['conso_gwh'].sum()
    n_anom     = dff['has_anomaly'].sum()
    pct_actif  = eans_actifs / len(dff) * 100 if len(dff) > 0 else 0

    with k1:
        st.markdown(f"""
        <div class="kpi-card green">
            <div class="kpi-label">Volume portefeuille</div>
            <div class="kpi-value" style="color:{C['accent']}">{total_gwh:.0f}</div>
            <div class="kpi-sub">GWh / an · <span class="kpi-badge badge-green">énergie gérée</span></div>
        </div>""", unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="kpi-card blue">
            <div class="kpi-label">EANs actifs</div>
            <div class="kpi-value" style="color:{C['blue']}">{eans_actifs:,}</div>
            <div class="kpi-sub">sur {len(dff):,} · <span class="kpi-badge badge-blue">{pct_actif:.0f}% couverture</span></div>
        </div>""", unsafe_allow_html=True)

    with k3:
        pct_pub = pub_gwh / total_gwh * 100 if total_gwh > 0 else 0
        st.markdown(f"""
        <div class="kpi-card yellow">
            <div class="kpi-label">Secteur public</div>
            <div class="kpi-value" style="color:{C['accent3']}">{pub_gwh:.0f}</div>
            <div class="kpi-sub">GWh · <span class="kpi-badge badge-yellow">{pct_pub:.0f}% du total</span></div>
        </div>""", unsafe_allow_html=True)

    with k4:
        n_clients = dff['Groupe_Nom'].nunique()
        st.markdown(f"""
        <div class="kpi-card purple">
            <div class="kpi-label">Groupements clients</div>
            <div class="kpi-value" style="color:{C['purple']}">{n_clients}</div>
            <div class="kpi-sub">entités · <span class="kpi-badge" style="background:rgba(124,77,255,0.15);color:{C['purple']}">21 sources</span></div>
        </div>""", unsafe_allow_html=True)

    with k5:
        pct_anom = n_anom / len(dff) * 100 if len(dff) > 0 else 0
        st.markdown(f"""
        <div class="kpi-card red">
            <div class="kpi-label">Anomalies détectées</div>
            <div class="kpi-value" style="color:{C['red']}">{n_anom:,}</div>
            <div class="kpi-sub">EANs · <span class="kpi-badge badge-red">{pct_anom:.1f}% du stock</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ROW 1: GWh par Source + Répartition Lot ───────────────────────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="section-header">Volume par source (GWh)</div>', unsafe_allow_html=True)
        src_gwh = dff.groupby('Source')['conso_gwh'].sum().sort_values(ascending=True)
        src_gwh = src_gwh[src_gwh > 0]

        colors = [C['accent'] if v == src_gwh.max() else C['blue'] for v in src_gwh.values]
        fig = go.Figure(go.Bar(
            x=src_gwh.values,
            y=src_gwh.index,
            orientation='h',
            marker=dict(color=colors, line=dict(width=0)),
            text=[f"{v:.1f}" for v in src_gwh.values],
            textposition='outside',
            textfont=dict(family='DM Mono, monospace', size=9, color=C['muted']),
            hovertemplate='<b>%{y}</b><br>%{x:.2f} GWh<extra></extra>',
        ))
        fig.update_layout(**PLOT_LAYOUT, height=360,
            xaxis_title="GWh/an", showlegend=False,
            bargap=0.35)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Répartition par lot</div>', unsafe_allow_html=True)
        lot_gwh = dff.groupby('Lot')['conso_gwh'].sum()
        lot_gwh = lot_gwh[lot_gwh.index.isin(['HT','BT','HP','BP'])]
        lot_colors = {'HT': C['ht'], 'BT': C['bt'], 'HP': C['hp'], 'BP': C['bp']}

        fig = go.Figure(go.Pie(
            labels=lot_gwh.index,
            values=lot_gwh.values,
            hole=0.6,
            marker=dict(colors=[lot_colors.get(l, C['muted']) for l in lot_gwh.index],
                       line=dict(color=C['bg'], width=3)),
            textinfo='label+percent',
            textfont=dict(family='DM Mono, monospace', size=10),
            hovertemplate='<b>%{label}</b><br>%{value:.1f} GWh (%{percent})<extra></extra>',
        ))
        fig.update_layout(**PLOT_LAYOUT, height=220, showlegend=True,
            annotations=[dict(text=f"<b>{lot_gwh.sum():.0f}</b><br><span style='font-size:10px'>GWh</span>",
                             x=0.5, y=0.5, xref='paper', yref='paper',
                             showarrow=False, font=dict(size=18, color=C['text']))])
        st.plotly_chart(fig, use_container_width=True)

        # Public vs Privé
        st.markdown('<div class="section-header">Public vs Privé</div>', unsafe_allow_html=True)
        pv = dff[dff['Groupe_Type'].isin(['Public','Privé'])].groupby('Groupe_Type')['conso_gwh'].sum()
        fig2 = go.Figure(go.Bar(
            x=pv.index, y=pv.values,
            marker_color=[C['accent3'], C['blue']],
            text=[f"{v:.0f} GWh" for v in pv.values],
            textposition='inside', textfont=dict(size=11, color=C['bg']),
        ))
        fig2.update_layout(**PLOT_LAYOUT, height=130, showlegend=False, bargap=0.4,
                          margin=dict(l=0,r=0,t=12,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    # ── ROW 2: Profil mensuel + GRD ───────────────────────────────────────────
    col3, col4 = st.columns([3, 2])

    with col3:
        st.markdown('<div class="section-header">Profil mensuel HP / HC (GWh agrégé — EANs HT uniquement)</div>', unsafe_allow_html=True)
        hp_cols = [f'{m} HP' for m in MONTHS]
        hc_cols = [f'{m} HC' for m in MONTHS]
        dff_ht = dff[dff['Lot'].isin(['HT','HP'])]
        hp_vals = [dff_ht[c].sum()/1e6 if c in dff_ht.columns else 0 for c in hp_cols]
        hc_vals = [dff_ht[c].sum()/1e6 if c in dff_ht.columns else 0 for c in hc_cols]

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Heures Pleines', x=MONTHS, y=hp_vals,
            marker_color=C['blue'], opacity=0.9,
            hovertemplate='<b>%{x} HP</b>: %{y:.1f} GWh<extra></extra>'))
        fig.add_trace(go.Bar(name='Heures Creuses', x=MONTHS, y=hc_vals,
            marker_color=C['accent'], opacity=0.85,
            hovertemplate='<b>%{x} HC</b>: %{y:.1f} GWh<extra></extra>'))
        fig.update_layout(**PLOT_LAYOUT, height=260, barmode='stack',
            legend=dict(orientation='h', x=0, y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Top 8 GRDs (GWh)</div>', unsafe_allow_html=True)
        grd_gwh = dff.groupby('GRD')['conso_gwh'].sum().sort_values(ascending=False).head(8)
        fig = go.Figure(go.Bar(
            y=grd_gwh.index, x=grd_gwh.values, orientation='h',
            marker=dict(
                color=grd_gwh.values,
                colorscale=[[0,'#21262D'],[1, C['accent']]],
                showscale=False
            ),
            text=[f"{v:.1f}" for v in grd_gwh.values],
            textposition='outside',
            textfont=dict(size=9, family='DM Mono, monospace', color=C['muted']),
            hovertemplate='<b>%{y}</b><br>%{x:.2f} GWh<extra></extra>',
        ))
        fig.update_layout(**PLOT_LAYOUT, height=260, showlegend=False,
            xaxis_title="GWh", bargap=0.3, margin=dict(l=8,r=40,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    # ── ROW 3: Répartition régionale ─────────────────────────────────────────
    st.markdown('<div class="section-header">Répartition régionale (EANs)</div>', unsafe_allow_html=True)
    reg_eans = dff.groupby('Région').agg(
        nb_eans=('EAN','count'),
        gwh=('conso_gwh','sum')
    ).reset_index().sort_values('nb_eans', ascending=False)
    reg_eans = reg_eans[reg_eans['Région'] != 'Inconnue']

    fig = go.Figure()
    fig.add_trace(go.Bar(name='EANs', x=reg_eans['Région'], y=reg_eans['nb_eans'],
        marker_color=C['blue'], yaxis='y', opacity=0.8,
        hovertemplate='<b>%{x}</b><br>%{y:,} EANs<extra></extra>'))
    fig.add_trace(go.Scatter(name='GWh', x=reg_eans['Région'], y=reg_eans['gwh'],
        mode='lines+markers', line=dict(color=C['accent'], width=2.5),
        marker=dict(size=8), yaxis='y2',
        hovertemplate='<b>%{x}</b><br>%{y:.1f} GWh<extra></extra>'))
    fig.update_layout(**PLOT_LAYOUT, height=220,
        yaxis=dict(title='EANs', gridcolor=C['border']),
        yaxis2=dict(title='GWh', overlaying='y', side='right', gridcolor='rgba(0,0,0,0)'),
        legend=dict(orientation='h', x=0, y=1.1),
        bargap=0.35)
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — VUE CLIENT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏢 Vue Client":
    st.markdown(f'<div class="dash-title">🏢 Vue Client</div>', unsafe_allow_html=True)

    groupes = sorted(dff['Groupe_Nom'].dropna().unique())
    if not groupes:
        st.warning("Aucun groupement disponible avec les filtres actuels.")
        st.stop()

    sel_groupe = st.selectbox("Sélectionner un groupement client", groupes)
    grp_df = dff[dff['Groupe_Nom'] == sel_groupe].copy()

    # Header client
    gtype = grp_df['Groupe_Type'].iloc[0] if len(grp_df) > 0 else '—'
    gactif = grp_df['Groupe_Actif'].iloc[0] if 'Groupe_Actif' in grp_df.columns else True
    badge_col = C['accent3'] if gtype == 'Public' else C['blue']
    n_ean_grp = len(grp_df)
    gwh_grp = grp_df['conso_gwh'].sum()
    anom_grp = grp_df['has_anomaly'].sum()

    st.markdown(f"""
    <div style="background:{C['card']};border:1px solid {C['border']};border-radius:12px;padding:20px 24px;margin:12px 0">
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
            <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800">{sel_groupe}</div>
            <span class="kpi-badge" style="background:rgba(0,0,0,0.3);border:1px solid {badge_col};color:{badge_col}">{gtype}</span>
            <span class="kpi-badge badge-{'green' if gactif else 'red'}">{'Actif' if gactif else 'Inactif'}</span>
        </div>
        <div style="display:flex;gap:32px;margin-top:16px;flex-wrap:wrap">
            <div><div class="kpi-label">EANs</div><div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:{C['accent']}">{n_ean_grp}</div></div>
            <div><div class="kpi-label">Conso totale</div><div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:{C['blue']}">{gwh_grp:.2f} <span style="font-size:1rem;font-weight:400">GWh</span></div></div>
            <div><div class="kpi-label">Anomalies</div><div style="font-family:'Syne',sans-serif;font-size:1.6rem;font-weight:800;color:{C['red'] if anom_grp>0 else C['accent']}">{anom_grp}</div></div>
            <div><div class="kpi-label">Sources</div><div style="font-family:'DM Mono',monospace;font-size:0.9rem;margin-top:6px">{', '.join(grp_df['Source'].unique())}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Charts client
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">Répartition par Lot</div>', unsafe_allow_html=True)
        lot_c = grp_df.groupby('Lot')['conso_gwh'].sum()
        lot_c = lot_c[lot_c.index.isin(['HT','BT','HP','BP'])]
        if len(lot_c) > 0:
            fig = go.Figure(go.Pie(
                labels=lot_c.index, values=lot_c.values, hole=0.55,
                marker=dict(colors=[{'HT':C['ht'],'BT':C['bt'],'HP':C['hp'],'BP':C['bp']}.get(l,C['muted']) for l in lot_c.index],
                           line=dict(color=C['bg'], width=2)),
                textinfo='label+percent',
                textfont=dict(family='DM Mono, monospace', size=10),
            ))
            fig.update_layout(**PLOT_LAYOUT, height=220, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-header">Énergie / Région</div>', unsafe_allow_html=True)
        reg_c = grp_df.groupby(['Région','Type_Energie'])['conso_gwh'].sum().reset_index()
        if len(reg_c) > 0:
            fig = px.bar(reg_c, x='Région', y='conso_gwh', color='Type_Energie',
                        color_discrete_map={'Electricité':C['blue'],'Gaz':C['accent3'],'Injection':C['accent']},
                        labels={'conso_gwh':'GWh'})
            fig.update_layout(**PLOT_LAYOUT, height=220, showlegend=True,
                             legend=dict(orientation='h',x=0,y=1.1), bargap=0.35,
                             margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)

    # Table EANs du groupement
    st.markdown('<div class="section-header">Liste des EANs</div>', unsafe_allow_html=True)

    display_cols = ['EAN','Site_Nom','Lot','Type_Energie','Site_Type de relevé',
                    'Site_Consommation annuelle réelle','GRD','Région','Source','Remarques']
    display_cols = [c for c in display_cols if c in grp_df.columns]
    show_df = grp_df[display_cols].copy()
    show_df['Site_Consommation annuelle réelle'] = show_df['Site_Consommation annuelle réelle'].apply(
        lambda x: f"{float(x):,.0f} kWh" if pd.notna(x) else '—')

    lot_filter = st.multiselect("Filtrer par lot", ['HT','BT','HP','BP'], default=['HT','BT','HP','BP'], key='lot_client')
    show_df2 = show_df[show_df['Lot'].isin(lot_filter)] if lot_filter else show_df

    st.dataframe(show_df2.reset_index(drop=True), use_container_width=True, height=340,
                column_config={
                    'EAN': st.column_config.TextColumn('EAN', width=180),
                    'Site_Consommation annuelle réelle': st.column_config.TextColumn('Conso annuelle'),
                })


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — VUE EAN
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚡ Vue EAN":
    st.markdown('<div class="dash-title">⚡ Vue EAN — Fiche compteur</div>', unsafe_allow_html=True)

    search = st.text_input("🔍 Rechercher par EAN ou nom de site", placeholder="ex: 541456700... ou INTRADEL")
    if not search:
        st.info("Entrez un EAN (18 chiffres) ou un nom de site pour afficher la fiche complète.")
        st.stop()

    mask = dff['EAN'].astype(str).str.contains(search, na=False) | \
           dff['Site_Nom'].str.contains(search, case=False, na=False)
    results = dff[mask].copy()

    if len(results) == 0:
        st.warning("Aucun EAN trouvé. Vérifiez votre recherche.")
        st.stop()

    if len(results) > 1:
        options = [f"{r['EAN']} — {r['Site_Nom']} ({r['Source']})" for _, r in results.iterrows()]
        sel_idx = st.selectbox("Plusieurs résultats — choisir :", options)
        row = results.iloc[options.index(sel_idx)]
    else:
        row = results.iloc[0]

    # Fiche EAN
    lot_color = {'HT':C['ht'],'BT':C['bt'],'HP':C['hp'],'BP':C['bp']}.get(str(row.get('Lot','')), C['muted'])
    conso_v = float(row.get('Site_Consommation annuelle réelle', 0) or 0)

    st.markdown(f"""
    <div style="background:{C['card']};border:1px solid {C['border']};border-radius:12px;padding:24px;margin:12px 0">
        <div style="font-family:'DM Mono',monospace;font-size:0.75rem;color:{C['muted']}">CODE EAN</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;letter-spacing:0.04em;margin:4px 0">{row.get('EAN','—')}</div>
        <div style="font-size:1rem;color:{C['muted']};margin-bottom:16px">{row.get('Site_Nom','—')}</div>
        <div style="display:flex;gap:24px;flex-wrap:wrap">
            <div><div class="kpi-label">Lot</div>
                 <span class="lot-{str(row.get('Lot','')).lower()}">{row.get('Lot','—')}</span></div>
            <div><div class="kpi-label">Type énergie</div>
                 <div style="margin-top:2px;font-size:0.9rem">{row.get('Type_Energie','—')}</div></div>
            <div><div class="kpi-label">Type relevé</div>
                 <div style="font-family:'DM Mono',monospace;margin-top:2px">{row.get('Site_Type de relevé','—')}</div></div>
            <div><div class="kpi-label">Type compteur</div>
                 <div style="margin-top:2px;font-size:0.9rem">{row.get('Site_Type de compteur','—')}</div></div>
            <div><div class="kpi-label">Conso annuelle</div>
                 <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:{C['accent']};margin-top:2px">{conso_v:,.0f} kWh</div></div>
            <div><div class="kpi-label">Source</div>
                 <div style="font-family:'DM Mono',monospace;margin-top:2px;font-size:0.8rem">{row.get('Source','—')}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">Localisation & Réseau</div>', unsafe_allow_html=True)
        fields = [
            ('Adresse', row.get('Adresse livraison','—')),
            ('CP / Ville', f"{row.get('CP','—')} {row.get('Ville','—')}"),
            ('GRD', row.get('GRD','—')),
            ('Région', row.get('Région','—')),
            ('Groupement', row.get('Groupe_Nom','—')),
            ('Société', row.get('Societe_Nom','—')),
        ]
        tbl = "".join([f"<tr><td style='color:{C['muted']};font-family:DM Mono,monospace;font-size:0.72rem;white-space:nowrap'>{k}</td><td style='padding-left:16px'>{v}</td></tr>" for k, v in fields])
        st.markdown(f"<table class='styled-table'>{tbl}</table>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-header">Qualité & Traçabilité</div>', unsafe_allow_html=True)
        jours = row.get('Jours conso', '—')
        complet = row.get('Complétude %', '—')
        inj = row.get('Injection kWh', 0) or 0
        rq  = row.get('Remarques','—') or '—'
        fields2 = [
            ('Jours conso', f"{jours}" + (' ⚠️' if pd.notna(jours) and float(jours or 0) > 366 else '')),
            ('Complétude', f"{complet}%"),
            ('Injection', f"{float(inj):,.0f} kWh" if inj else '—'),
            ('Anomalie', '🔴 Oui' if row.get('has_anomaly') else '✅ Non'),
            ('Remarques', str(rq)[:80] + ('…' if len(str(rq)) > 80 else '')),
        ]
        tbl2 = "".join([f"<tr><td style='color:{C['muted']};font-family:DM Mono,monospace;font-size:0.72rem;white-space:nowrap;vertical-align:top'>{k}</td><td style='padding-left:16px;font-size:0.82rem'>{v}</td></tr>" for k, v in fields2])
        st.markdown(f"<table class='styled-table'>{tbl2}</table>", unsafe_allow_html=True)

    # Profil mensuel si disponible
    hp_vals = [row.get(f'{m} HP', None) for m in MONTHS]
    hc_vals = [row.get(f'{m} HC', None) for m in MONTHS]
    has_monthly = any(v is not None and not (isinstance(v, float) and np.isnan(v)) for v in hp_vals)

    if has_monthly:
        st.markdown('<div class="section-header">Profil mensuel HP / HC</div>', unsafe_allow_html=True)
        hp_clean = [float(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else 0 for v in hp_vals]
        hc_clean = [float(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else 0 for v in hc_vals]

        fig = go.Figure()
        fig.add_trace(go.Bar(name='HP', x=MONTHS, y=hp_clean,
            marker_color=C['blue'], hovertemplate='<b>%{x} HP</b>: %{y:,.0f} kWh<extra></extra>'))
        fig.add_trace(go.Bar(name='HC', x=MONTHS, y=hc_clean,
            marker_color=C['accent'], hovertemplate='<b>%{x} HC</b>: %{y:,.0f} kWh<extra></extra>'))
        tot_m = sum(hp_clean)+sum(hc_clean)
        fig.update_layout(**PLOT_LAYOUT, height=260, barmode='group',
            title=dict(text=f"Total mensuel : {tot_m:,.0f} kWh", font=dict(size=11, color=C['muted'])),
            legend=dict(orientation='h', x=0, y=1.1))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Pas de données mensuelles HP/HC disponibles pour cet EAN.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — ANOMALIES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🚨 Anomalies":
    st.markdown('<div class="dash-title">🚨 Centre d\'Anomalies</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="dash-subtitle">Backlog qualité · {dff["has_anomaly"].sum():,} anomalies détectées</div>', unsafe_allow_html=True)

    # KPIs anomalies
    k1,k2,k3 = st.columns(3)
    with k1:
        n = dff['is_anomaly_zero'].sum()
        st.markdown(f"""<div class="kpi-card red"><div class="kpi-label">🔴 Conso = 0 kWh</div>
        <div class="kpi-value" style="color:{C['red']}">{n:,}</div>
        <div class="kpi-sub">EANs sans consommation · compteurs inactifs ou données manquantes</div></div>""", unsafe_allow_html=True)
    with k2:
        n2 = dff['is_anomaly_ht_small'].sum()
        st.markdown(f"""<div class="kpi-card orange" style="--c:{C['orange']}"><div class="kpi-label">🟠 HT/HP &lt; 50 MWh</div>
        <div class="kpi-value" style="color:{C['orange']}">{n2:,}</div>
        <div class="kpi-sub">EANs HT/HP avec conso incohérente vs type de relevé AMR/MMR</div></div>""", unsafe_allow_html=True)
    with k3:
        n3 = dff['is_anomaly_tiny'].sum()
        st.markdown(f"""<div class="kpi-card yellow"><div class="kpi-label">🟡 Conso &lt; 10 kWh</div>
        <div class="kpi-value" style="color:{C['accent3']}">{n3:,}</div>
        <div class="kpi-sub">EANs avec valeur suspicieusement basse — probable erreur d'unité</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Anomalies par source
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Anomalies conso=0 par source</div>', unsafe_allow_html=True)
        src_z = dff[dff['is_anomaly_zero']].groupby('Source').size().sort_values(ascending=False)
        src_z = src_z[src_z > 0]
        colors_z = [C['red'] if i==0 else C['orange'] if i<3 else C['border'] for i in range(len(src_z))]
        fig = go.Figure(go.Bar(y=src_z.index, x=src_z.values, orientation='h',
            marker_color=colors_z,
            text=src_z.values, textposition='outside',
            textfont=dict(size=9, family='DM Mono, monospace'),
            hovertemplate='<b>%{y}</b><br>%{x} EANs à 0<extra></extra>'))
        fig.update_layout(**PLOT_LAYOUT, height=280, showlegend=False, bargap=0.35)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">HT/HP < 50 MWh par source</div>', unsafe_allow_html=True)
        src_ht = dff[dff['is_anomaly_ht_small']].groupby('Source').size().sort_values(ascending=False)
        src_ht = src_ht[src_ht > 0]
        fig2 = go.Figure(go.Bar(y=src_ht.index, x=src_ht.values, orientation='h',
            marker_color=C['orange'],
            text=src_ht.values, textposition='outside',
            textfont=dict(size=9, family='DM Mono, monospace'),
            hovertemplate='<b>%{y}</b><br>%{x} EANs<extra></extra>'))
        fig2.update_layout(**PLOT_LAYOUT, height=280, showlegend=False, bargap=0.35)
        st.plotly_chart(fig2, use_container_width=True)

    # Table anomalies filtrables
    st.markdown('<div class="section-header">Détail des EANs en anomalie</div>', unsafe_allow_html=True)
    anom_type = st.radio("Type", ["Conso = 0", "HT/HP < 50 MWh", "Conso < 10 kWh"], horizontal=True)

    if anom_type == "Conso = 0":
        anom_df = dff[dff['is_anomaly_zero']]
        badge_txt = "🔴 Conso = 0 kWh"
    elif anom_type == "HT/HP < 50 MWh":
        anom_df = dff[dff['is_anomaly_ht_small']]
        badge_txt = "🟠 HT/HP < 50 MWh"
    else:
        anom_df = dff[dff['is_anomaly_tiny']]
        badge_txt = "🟡 < 10 kWh"

    st.markdown(f'<span class="kpi-badge badge-red">{badge_txt}</span> &nbsp; <span style="color:{C["muted"]};font-size:0.82rem">{len(anom_df):,} EANs</span>', unsafe_allow_html=True)

    disp = ['EAN','Site_Nom','Lot','Type_Energie','Site_Consommation annuelle réelle','GRD','Région','Source','Remarques']
    disp = [c for c in disp if c in anom_df.columns]
    show = anom_df[disp].copy()
    show['Site_Consommation annuelle réelle'] = show['Site_Consommation annuelle réelle'].apply(
        lambda x: f"{float(x):,.0f} kWh" if pd.notna(x) else '—')

    filter_src = st.multiselect("Filtrer par source", sorted(anom_df['Source'].unique()), key='anom_src')
    if filter_src: show = show[show['Source'].isin(filter_src)]

    st.dataframe(show.reset_index(drop=True), use_container_width=True, height=400,
                column_config={
                    'EAN': st.column_config.TextColumn('EAN', width=180),
                    'Site_Consommation annuelle réelle': st.column_config.TextColumn('Conso'),
                })

    # Export
    csv = show.to_csv(index=False).encode('utf-8')
    st.download_button(f"⬇️ Exporter {anom_type} en CSV", csv,
                      f"anomalies_{anom_type.replace(' ','_')}.csv", "text/csv")
