import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="A365 BCP - Centro de Operaciones", layout="wide", page_icon="isotipobcp.png")

# --- LOGO ---
def get_b64(p):
    try:
        with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return None

logo_b64 = get_b64("A366BCP.png")
logo_img = f'<img src="data:image/png;base64,{logo_b64}" style="height:40px;">' if logo_b64 else ''

# --- COLORS ---
BG = "#0E1117"
CARD = "#161B22"
BORDER = "#21262D"
TEXT = "#E6EDF3"
TEXT2 = "#8B949E"
ORANGE = "#FF7A00"
BLUE = "#58A6FF"
NAVY = "#1F6FEB"

# --- CSS ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Manrope', sans-serif !important; }}
    #MainMenu, footer {{ visibility: hidden; }}
    .block-container {{ padding-top: 0 !important; padding-bottom: 1rem !important; max-width: 1440px; }}

    .topbar {{ display:flex; align-items:center; justify-content:space-between; padding:14px 0; border-bottom:1px solid rgba(128,128,128,0.2); margin-bottom:20px; }}
    .topbar-left {{ display:flex; align-items:center; gap:14px; }}
    .topbar-tag {{ font-size:11px; font-weight:700; opacity:0.5; text-transform:uppercase; letter-spacing:1px; }}
    .topbar-right {{ font-size:11px; opacity:0.5; }}

    .kpi-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:24px; }}
    .kpi {{ border:1px solid rgba(128,128,128,0.2); border-radius:10px; padding:18px 20px; }}
    .kpi-label {{ font-size:10px; font-weight:700; opacity:0.5; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:6px; }}
    .kpi-val {{ font-size:26px; font-weight:800; letter-spacing:-0.5px; }}
    .kpi-val.accent {{ color:{ORANGE}; }}
    .kpi-sub {{ font-size:11px; opacity:0.5; margin-top:2px; }}

    .sec {{ display:flex; align-items:center; gap:8px; margin:24px 0 12px 0; }}
    .sec-dot {{ width:8px; height:8px; border-radius:50%; background:{ORANGE}; }}
    .sec-label {{ font-size:12px; font-weight:700; opacity:0.5; text-transform:uppercase; letter-spacing:0.5px; }}

    h1,h2,h3,h4 {{ font-weight:700 !important; font-size:15px !important; }}
    div[data-testid="stMetricLabel"], div[data-testid="stMetricValue"] {{ display:none; }}
    div[data-testid="stDataFrame"] {{ border:1px solid rgba(128,128,128,0.2); border-radius:8px; overflow:hidden; }}

    /* Multiselect: ocultar los chips/cuadraditos naranjas */
    span[data-baseweb="tag"] {{ display:none !important; }}
    div[data-baseweb="select"] > div {{ min-height: 38px !important; }}

</style>
""", unsafe_allow_html=True)

# --- TOPBAR ---
now = datetime.now().strftime("%d/%m/%Y  %H:%M")
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">{logo_img}<span class="topbar-tag">Centro de Operaciones</span></div>
    <div class="topbar-right">Ultima sincronizacion: {now}</div>
</div>
""", unsafe_allow_html=True)

# --- DATA ---
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/16PzK230jtrjkpHYq5mYSFrdeXk-0B6N7/export?format=csv&gid=305780908"
    df = pd.read_csv(url)
    if 'MAF NETO' in df.columns:
        df['MAF NETO'] = df['MAF NETO'].fillna("0")
        df['MAF NETO_Num'] = df['MAF NETO'].str.replace('S/', '', regex=False).str.strip()
        df['MAF NETO_Num'] = df['MAF NETO_Num'].str.replace('.', '', regex=False)
        df['MAF NETO_Num'] = df['MAF NETO_Num'].str.replace(',', '.', regex=False)
        df['MAF NETO_Num'] = pd.to_numeric(df['MAF NETO_Num'], errors='coerce').fillna(0)
    df['SUPERVISOR'] = df['SUPERVISOR'].fillna('SIN SUPERVISOR')
    df['PLAZA DE VENTA'] = df['PLAZA DE VENTA'].fillna('SIN PLAZA').str.strip()
    df['ESTADO LIMPIO'] = df['ESTADO LIMPIO'].fillna('SIN ESTADO')
    df['CONVENIO'] = df['CONVENIO'].fillna('SIN CONVENIO').str.strip().str.upper()
    zonas = {'NAHOMI':'CHICLAYO','JORGE':'CHICLAYO','JHON':'CHICLAYO',
             'WINNIE':'LIMA','KENNY':'LIMA','ANGIE':'LIMA','MARIELLA':'LIMA',
             'LUIS CHUSE':'LIMA','LUIS SHEPHERD':'LIMA','LUIS MENDOZA':'LIMA',
             'JIMMY':'TARAPOTO','JULIA':'TRUJILLO'}
    df['ZONA_SUP'] = df['SUPERVISOR'].map(zonas).fillna('N/A')
    norte = ['CHICLAYO', 'PIURA', 'TRUJILLO']
    df['REGION'] = df['ZONA_SUP'].apply(lambda z: 'LIMA' if z == 'LIMA' else ('NORTE' if z in norte else 'OTROS'))
    return df

with st.spinner('Conectando...'):
    df = load_data()

# --- FILTROS VISIBLES EN LA PAGINA ---
st.markdown(f'<div class="sec"><div class="sec-dot"></div><span class="sec-label">Filtros</span></div>', unsafe_allow_html=True)
fc1, fc2, fc3 = st.columns(3)
with fc1:
    sel_region = st.multiselect("Plaza", ['LIMA', 'NORTE', 'OTROS'], default=['LIMA', 'NORTE', 'OTROS'])
with fc2:
    sup_opts = sorted(df[df['REGION'].isin(sel_region)]['SUPERVISOR'].unique().tolist())
    sel_sup = st.multiselect("Supervisor", sup_opts, default=sup_opts)
with fc3:
    conv_opts = sorted(df['CONVENIO'].unique().tolist())
    sel_conv = st.multiselect("Convenio", conv_opts, default=conv_opts)

fdf = df[(df['REGION'].isin(sel_region)) & (df['SUPERVISOR'].isin(sel_sup)) & (df['CONVENIO'].isin(sel_conv))]
desemb = fdf[fdf['ESTADO LIMPIO'] == 'DESEMBOLSADO']

# --- KPIs ---
META = 11950000.0
m_des = desemb['MAF NETO_Num'].sum()
q_des = len(desemb)
avance = (m_des / META * 100) if META > 0 else 0
q_total = len(fdf)
ticket = desemb['MAF NETO_Num'].mean() if q_des > 0 else 0

st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi"><div class="kpi-label">Desembolso Total</div><div class="kpi-val">S/ {m_des:,.0f}</div><div class="kpi-sub">{q_des} operaciones</div></div>
    <div class="kpi"><div class="kpi-label">Avance vs Meta</div><div class="kpi-val accent">{avance:.1f}%</div><div class="kpi-sub">Meta: S/ {META:,.0f}</div></div>
    <div class="kpi"><div class="kpi-label">Total Registros</div><div class="kpi-val">{q_total}</div><div class="kpi-sub">Todos los estados</div></div>
    <div class="kpi"><div class="kpi-label">Ticket Promedio</div><div class="kpi-val">S/ {ticket:,.0f}</div><div class="kpi-sub">Por desembolso</div></div>
</div>
""", unsafe_allow_html=True)

# --- PLOTLY THEME ---
PLOTLY_COLORS = ["#FF7A00", "#58A6FF", "#3FB950", "#D2A8FF", "#FFB300", "#F778BA", "#79C0FF", "#FFA657"]

def style_fig(fig, h=360):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Manrope", size=12),
        margin=dict(l=8, r=16, t=8, b=8), height=h,
        showlegend=False
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True, gridcolor='rgba(128,128,128,0.15)', zeroline=False, tickfont=dict(size=10))
    return fig

# --- CHARTS ---
st.markdown(f'<div class="sec"><div class="sec-dot"></div><span class="sec-label">Analisis de Rendimiento</span></div>', unsafe_allow_html=True)

c1, c2 = st.columns([3, 2])

with c1:
    st.markdown("#### Desembolso por Supervisor")
    vs = desemb.groupby('SUPERVISOR')['MAF NETO_Num'].sum().reset_index().sort_values('MAF NETO_Num')
    fig1 = go.Figure(go.Bar(
        y=vs['SUPERVISOR'], x=vs['MAF NETO_Num'], orientation='h',
        marker=dict(color=ORANGE, cornerradius=4),
        text=[f"S/ {v:,.0f}" for v in vs['MAF NETO_Num']], textposition='outside',
        textfont=dict(size=1)
    ))
    fig1 = style_fig(fig1, 380)
    fig1.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown("#### Pipeline de Estados")
    ep = fdf['ESTADO LIMPIO'].value_counts().reset_index()
    ep.columns = ['Estado', 'Qty']
    ep = ep.sort_values('Qty')
    fig2 = go.Figure(go.Bar(
        y=ep['Estado'], x=ep['Qty'], orientation='h',
        marker=dict(color=[PLOTLY_COLORS[i % len(PLOTLY_COLORS)] for i in range(len(ep))], cornerradius=4),
        text=ep['Qty'], textposition='outside',
        textfont=dict(size=1)
    ))
    fig2 = style_fig(fig2, 380)
    fig2.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(fig2, use_container_width=True)

# ROW 2
c3, c4, c5 = st.columns(3)

with c3:
    st.markdown("#### Por Convenio")
    vc = desemb.groupby('CONVENIO')['MAF NETO_Num'].sum().reset_index().sort_values('MAF NETO_Num', ascending=False)
    fig3 = go.Figure(go.Bar(
        x=vc['CONVENIO'], y=vc['MAF NETO_Num'],
        marker=dict(color=PLOTLY_COLORS[:len(vc)], cornerradius=4),
        text=[f"S/ {v:,.0f}" for v in vc['MAF NETO_Num']], textposition='outside',
        textfont=dict(size=1)
    ))
    fig3 = style_fig(fig3, 320)
    fig3.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.markdown("#### Por Region")
    vr = desemb.groupby('REGION')['MAF NETO_Num'].sum().reset_index()
    fig4 = go.Figure(go.Pie(
        labels=vr['REGION'], values=vr['MAF NETO_Num'], hole=0.55,
        marker=dict(colors=["#58A6FF", "#FF7A00", "#3FB950"], line=dict(color=" rgba 0 0 0 0.15 \, width=2)),
        textinfo='percent+label', textfont=dict(color=TEXT, size=12),
        insidetextorientation='radial'
    ))
    fig4 = style_fig(fig4, 320)
    st.plotly_chart(fig4, use_container_width=True)

with c5:
    st.markdown("#### Estados (Proporcion)")
    es = fdf['ESTADO LIMPIO'].value_counts().reset_index()
    es.columns = ['Estado', 'Qty']
    fig5 = go.Figure(go.Pie(
        labels=es['Estado'], values=es['Qty'], hole=0.55,
        marker=dict(colors=PLOTLY_COLORS[:len(es)], line=dict(color=" rgba 0 0 0 0.15 \, width=2)),
        textinfo='percent+label', textfont=dict(size=1),
        insidetextorientation='radial'
    ))
    fig5 = style_fig(fig5, 320)
    st.plotly_chart(fig5, use_container_width=True)

# --- TABLAS ---
st.markdown(f'<div class="sec"><div class="sec-dot"></div><span class="sec-label">Tablas de Gestion</span></div>', unsafe_allow_html=True)

def build_matrix(data, gcol):
    if data.empty: return pd.DataFrame()
    ps = data.pivot_table(index=gcol, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='sum', fill_value=0)
    pc = data.pivot_table(index=gcol, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='count', fill_value=0)
    r = pd.DataFrame(index=ps.index)
    if gcol == 'SUPERVISOR':
        zm = {'NAHOMI':'CHICLAYO','JORGE':'CHICLAYO','JHON':'CHICLAYO','WINNIE':'LIMA','KENNY':'LIMA',
              'ANGIE':'LIMA','MARIELLA':'LIMA','LUIS CHUSE':'LIMA','LUIS SHEPHERD':'LIMA',
              'LUIS MENDOZA':'LIMA','JIMMY':'TARAPOTO','JULIA':'TRUJILLO'}
        r['ZONA'] = [zm.get(s, 'N/A') for s in r.index]
    g = lambda p, c: p[c] if c in p.columns else 0
    r['TOTAL DESEMBOLSO'] = g(ps, 'DESEMBOLSADO')
    r['Q DESEMBOLSO'] = g(pc, 'DESEMBOLSADO')
    r['APROBADA'] = g(ps, 'APROBADA')
    r['POR INGRESAR'] = g(ps, 'POR INGRESAR')
    r['EVALUACION BCP'] = g(ps, 'EN EVALUACION BCP')
    r['PENDIENTE DE BACK'] = g(ps, 'PENDIENTE DE BACK OFFICE')
    r['PENDIENTE DE REMESA'] = g(ps, 'PENDIENTE DE REMESA')
    r['META OBJETIVO'] = 1000000.00
    r['AVANCE'] = (r['TOTAL DESEMBOLSO'] / r['META OBJETIVO']).fillna(0)
    r['Q POR INGRESAR'] = g(pc, 'POR INGRESAR')
    r['Q EVALUACION BCP'] = g(pc, 'EN EVALUACION BCP')
    r['Q PENDIENTE DE BACK'] = g(pc, 'PENDIENTE DE BACK OFFICE')
    t = r.sum(numeric_only=True)
    if gcol == 'SUPERVISOR': t['ZONA'] = ''
    t['AVANCE'] = (t['TOTAL DESEMBOLSO'] / t['META OBJETIVO']) if t['META OBJETIVO'] > 0 else 0
    r.loc['TOTAL'] = t
    return r.reset_index()

mdf = df[df['SUPERVISOR'].isin(sel_sup) & df['CONVENIO'].isin(sel_conv) & df['REGION'].isin(sel_region)]
df_s = build_matrix(mdf, 'SUPERVISOR')

def build_plaza(data):
    if data.empty: return pd.DataFrame()
    d2 = data.copy(); d2['PLAZA'] = d2['REGION']
    return build_matrix(d2, 'PLAZA')

df_p = build_plaza(mdf)

cc = {
    "TOTAL DESEMBOLSO": st.column_config.NumberColumn("Total Desemb.", format="S/ %d"),
    "APROBADA": st.column_config.NumberColumn("Aprobada", format="S/ %d"),
    "POR INGRESAR": st.column_config.NumberColumn("Por Ingresar", format="S/ %d"),
    "EVALUACION BCP": st.column_config.NumberColumn("Eval. BCP", format="S/ %d"),
    "PENDIENTE DE BACK": st.column_config.NumberColumn("Pend. Back", format="S/ %d"),
    "PENDIENTE DE REMESA": st.column_config.NumberColumn("Pend. Remesa", format="S/ %d"),
    "META OBJETIVO": st.column_config.NumberColumn("Meta", format="S/ %d"),
    "AVANCE": st.column_config.ProgressColumn("Avance", format="%.1f%%", min_value=0, max_value=1.0),
    "Q DESEMBOLSO": st.column_config.NumberColumn("Q Desemb.", format="%d"),
    "Q POR INGRESAR": st.column_config.NumberColumn("Q Ingr.", format="%d"),
    "Q EVALUACION BCP": st.column_config.NumberColumn("Q Eval.", format="%d"),
    "Q PENDIENTE DE BACK": st.column_config.NumberColumn("Q Back", format="%d"),
}

t1, t2 = st.tabs(["Por Supervisor", "Por Plaza"])
with t1:
    if not df_s.empty: st.dataframe(df_s, use_container_width=True, hide_index=True, column_config=cc)
with t2:
    if not df_p.empty: st.dataframe(df_p, use_container_width=True, hide_index=True, column_config=cc)

# --- DETALLE ---
st.markdown(f'<div class="sec"><div class="sec-dot"></div><span class="sec-label">Detalle de Operaciones</span></div>', unsafe_allow_html=True)
with st.expander("Expandir tabla completa"):
    st.dataframe(fdf, use_container_width=True, hide_index=True)
