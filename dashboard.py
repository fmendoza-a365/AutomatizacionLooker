import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="A365 BCP - Centro de Operaciones", layout="wide", page_icon="isotipobcp.png")

# --- LOGO ---
def get_b64(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return None

logo_b64 = get_b64("A366BCP.png")
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:44px;">' if logo_b64 else '<span style="font-weight:800;font-size:22px;color:#002A8D;">A365 BCP</span>'

# --- CSS ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Manrope', sans-serif !important; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 0 !important; padding-bottom: 1rem !important; max-width: 1400px; }}

    .topbar {{ display:flex; align-items:center; justify-content:space-between; padding:14px 0; border-bottom:1px solid #E8E8ED; margin-bottom:20px; }}
    .topbar-left {{ display:flex; align-items:center; gap:14px; }}
    .topbar-title {{ font-size:13px; font-weight:600; color:#8E8E93; letter-spacing:0.5px; text-transform:uppercase; }}
    .topbar-right {{ font-size:12px; color:#8E8E93; }}

    .section-header {{ display:flex; align-items:center; gap:8px; margin:28px 0 14px 0; padding-bottom:6px; border-bottom:2px solid #002A8D; }}
    .section-icon {{ width:20px; height:20px; border-radius:4px; background:#FF7A00; display:flex; align-items:center; justify-content:center; }}
    .section-icon svg {{ width:12px; height:12px; fill:white; }}
    .section-label {{ font-size:13px; font-weight:700; color:#002A8D; text-transform:uppercase; letter-spacing:0.4px; }}

    .kpi-row {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:24px; }}
    .kpi-card {{ background:#fff; border:1px solid #E8E8ED; border-radius:10px; padding:18px 20px; position:relative; overflow:hidden; }}
    .kpi-card::after {{ content:''; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg,#FF7A00,#FFB300); }}
    .kpi-label {{ font-size:10px; font-weight:700; color:#8E8E93; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:6px; }}
    .kpi-value {{ font-size:26px; font-weight:800; color:#1D1D1F; letter-spacing:-0.5px; }}
    .kpi-sub {{ font-size:11px; color:#8E8E93; margin-top:3px; }}
    .kpi-accent {{ color:#FF7A00; font-weight:700; }}

    h1,h2,h3,h4 {{ font-weight:700 !important; color:#002A8D !important; }}
    div[data-testid="stMetricLabel"], div[data-testid="stMetricValue"] {{ display:none; }}
    div[data-testid="stDataFrame"] {{ border:1px solid #E8E8ED; border-radius:10px; overflow:hidden; }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{ background:#FAFAFC; border-right:1px solid #E8E8ED; }}
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{ font-size:13px; }}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,1,0">
""", unsafe_allow_html=True)

# --- TOPBAR ---
now = datetime.now().strftime("%d/%m/%Y  %H:%M")
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">{logo_html}<span class="topbar-title">Centro de Operaciones</span></div>
    <div class="topbar-right">Actualizado: {now}</div>
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

    # Mapear plazas a regiones
    norte = ['CHICLAYO', 'PIURA', 'TRUJILLO']
    df['REGION'] = df['PLAZA DE VENTA'].apply(lambda x: 'LIMA' if x == 'LIMA' else ('NORTE' if x in norte else 'OTROS'))

    # Mapear zonas de supervisor
    zonas = {'NAHOMI':'CHICLAYO','JORGE':'CHICLAYO','JHON':'CHICLAYO',
             'WINNIE':'LIMA','KENNY':'LIMA','ANGIE':'LIMA','MARIELLA':'LIMA',
             'LUIS CHUSE':'LIMA','LUIS SHEPHERD':'LIMA','LUIS MENDOZA':'LIMA',
             'JIMMY':'TARAPOTO','JULIA':'TRUJILLO'}
    df['ZONA_SUP'] = df['SUPERVISOR'].map(zonas).fillna('N/A')
    return df

with st.spinner('Conectando...'):
    df = load_data()

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.markdown(f"""<div style="text-align:center;padding:12px 0 8px 0;">{logo_html}</div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Filtros**")

    # Plaza como región agrupada
    region_opts = ['LIMA', 'NORTE', 'OTROS']
    selected_region = st.multiselect("Plaza", region_opts, default=region_opts)

    supervisor_list = sorted(df[df['REGION'].isin(selected_region)]['SUPERVISOR'].unique().tolist())
    selected_supervisor = st.multiselect("Supervisor", supervisor_list, default=supervisor_list)

    convenio_list = sorted(df['CONVENIO'].unique().tolist())
    selected_convenio = st.multiselect("Convenio", convenio_list, default=convenio_list)

filtered_df = df[
    (df['REGION'].isin(selected_region)) &
    (df['SUPERVISOR'].isin(selected_supervisor)) &
    (df['CONVENIO'].isin(selected_convenio))
]

# --- KPIs ---
META_GLOBAL = 11950000.00
desembolsado_df = filtered_df[filtered_df['ESTADO LIMPIO'] == 'DESEMBOLSADO']
monto_desembolso = desembolsado_df['MAF NETO_Num'].sum()
q_desembolso = len(desembolsado_df)
avance = (monto_desembolso / META_GLOBAL * 100) if META_GLOBAL > 0 else 0
cantidad_ops = len(filtered_df)

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card">
        <div class="kpi-label">Desembolso Total</div>
        <div class="kpi-value">S/ {monto_desembolso:,.0f}</div>
        <div class="kpi-sub">{q_desembolso} operaciones desembolsadas</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Avance vs Meta</div>
        <div class="kpi-value kpi-accent">{avance:.1f}%</div>
        <div class="kpi-sub">Meta: S/ {META_GLOBAL:,.0f}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Operaciones Totales</div>
        <div class="kpi-value">{cantidad_ops}</div>
        <div class="kpi-sub">Todos los estados</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Ticket Promedio</div>
        <div class="kpi-value">S/ {(desembolsado_df['MAF NETO_Num'].mean() if q_desembolso > 0 else 0):,.0f}</div>
        <div class="kpi-sub">Promedio por desembolso</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- HELPER ---
bcp = ["#FF7A00", "#002A8D", "#00A4E4", "#FFB300", "#001B5A", "#6E6E73", "#D4380D", "#389E0D", "#722ED1", "#EB2F96"]

def clean_fig(fig, h=360):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Manrope", color="#1D1D1F", size=12),
        margin=dict(l=8, r=8, t=36, b=8), height=h,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5, font=dict(size=10))
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True, gridcolor='#F0F0F5', zeroline=False, tickfont=dict(size=10))
    return fig

# --- SECTION: GRAFICOS ---
st.markdown("""<div class="section-header">
    <div class="section-icon"><svg viewBox="0 0 24 24"><path d="M3 13h2v8H3zm4-4h2v12H7zm4-2h2v14h-2zm4 6h2v8h-2zm4-8h2v16h-2z"/></svg></div>
    <span class="section-label">Analisis de Rendimiento</span>
</div>""", unsafe_allow_html=True)

# ROW 1: Desembolso por Supervisor + Funnel de Estados
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown("#### Desembolso por Supervisor")
    v_sup = desembolsado_df.groupby('SUPERVISOR')['MAF NETO_Num'].sum().reset_index().sort_values('MAF NETO_Num')
    fig1 = px.bar(v_sup, y='SUPERVISOR', x='MAF NETO_Num', orientation='h',
                  color_discrete_sequence=["#FF7A00"], text_auto='.2s')
    fig1.update_traces(textposition='outside', marker_line_width=0)
    fig1 = clean_fig(fig1, 400)
    fig1.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown("#### Pipeline por Estado")
    # Orden lógico del funnel
    estado_order = ['POR INGRESAR', 'EN EVALUACION BCP', 'APROBADA', 'PENDIENTE DE BACK OFFICE',
                    'PENDIENTE DE REMESA', 'DESEMBOLSADO', 'RECHAZADA', 'OBSERVADO FFVV', 'OBSERVADO BACK',
                    'PENDIENTE DE DOCUMENTAR']
    e_dist = filtered_df['ESTADO LIMPIO'].value_counts().reset_index()
    e_dist.columns = ['Estado', 'Cantidad']
    # Reorder
    e_dist['Estado'] = pd.Categorical(e_dist['Estado'], categories=estado_order, ordered=True)
    e_dist = e_dist.sort_values('Estado').dropna(subset=['Estado'])

    fig2 = px.bar(e_dist, x='Cantidad', y='Estado', orientation='h',
                  color='Estado', color_discrete_sequence=bcp, text_auto=True)
    fig2.update_traces(textposition='outside', marker_line_width=0)
    fig2 = clean_fig(fig2, 400)
    fig2.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig2, use_container_width=True)

# ROW 2: Por Convenio + Por Region + Top Asesores
c3, c4, c5 = st.columns(3)

with c3:
    st.markdown("#### Desembolso por Convenio")
    v_conv = desembolsado_df.groupby('CONVENIO')['MAF NETO_Num'].sum().reset_index().sort_values('MAF NETO_Num', ascending=False)
    fig3 = px.bar(v_conv, x='CONVENIO', y='MAF NETO_Num', color='CONVENIO',
                  color_discrete_sequence=bcp, text_auto='.2s')
    fig3.update_traces(textposition='outside', marker_line_width=0)
    fig3 = clean_fig(fig3, 340)
    fig3.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.markdown("#### Distribucion por Region")
    v_reg = desembolsado_df.groupby('REGION')['MAF NETO_Num'].sum().reset_index()
    fig4 = px.pie(v_reg, names='REGION', values='MAF NETO_Num', hole=0.5,
                  color_discrete_sequence=["#002A8D", "#FF7A00", "#00A4E4"])
    fig4 = clean_fig(fig4, 340)
    fig4.update_traces(textposition='inside', textinfo='percent+label',
                       marker=dict(line=dict(color='#fff', width=2)))
    fig4.update_layout(showlegend=False)
    st.plotly_chart(fig4, use_container_width=True)

with c5:
    st.markdown("#### Composicion de Estados")
    e_pie = filtered_df['ESTADO LIMPIO'].value_counts().reset_index()
    e_pie.columns = ['Estado', 'Cantidad']
    fig5 = px.pie(e_pie, names='Estado', values='Cantidad', hole=0.5, color_discrete_sequence=bcp)
    fig5 = clean_fig(fig5, 340)
    fig5.update_traces(textposition='inside', textinfo='percent+label',
                       marker=dict(line=dict(color='#fff', width=2)))
    fig5.update_layout(showlegend=False)
    st.plotly_chart(fig5, use_container_width=True)

# --- SECTION: TABLAS ---
st.markdown("""<div class="section-header">
    <div class="section-icon"><svg viewBox="0 0 24 24"><path d="M3 3h18v18H3zm2 2v4h6V5zm8 0v4h6V5zm-8 6v4h6v-4zm8 0v4h6v-4zM5 17v2h6v-2zm8 0v2h6v-2z"/></svg></div>
    <span class="section-label">Tablas de Gestion</span>
</div>""", unsafe_allow_html=True)

def build_matrix(data, group_col):
    if data.empty: return pd.DataFrame()
    ps = data.pivot_table(index=group_col, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='sum', fill_value=0)
    pc = data.pivot_table(index=group_col, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='count', fill_value=0)
    res = pd.DataFrame(index=ps.index)
    if group_col == 'SUPERVISOR':
        zm = {'NAHOMI':'CHICLAYO','JORGE':'CHICLAYO','JHON':'CHICLAYO','WINNIE':'LIMA','KENNY':'LIMA',
              'ANGIE':'LIMA','MARIELLA':'LIMA','LUIS CHUSE':'LIMA','LUIS SHEPHERD':'LIMA',
              'LUIS MENDOZA':'LIMA','JIMMY':'TARAPOTO','JULIA':'TRUJILLO'}
        res['ZONA'] = [zm.get(s, 'N/A') for s in res.index]
    g = lambda p, c: p[c] if c in p.columns else 0
    res['TOTAL DESEMBOLSO'] = g(ps, 'DESEMBOLSADO')
    res['Q DESEMBOLSO'] = g(pc, 'DESEMBOLSADO')
    res['APROBADA'] = g(ps, 'APROBADA')
    res['POR INGRESAR'] = g(ps, 'POR INGRESAR')
    res['EVALUACION BCP'] = g(ps, 'EN EVALUACION BCP')
    res['PENDIENTE DE BACK'] = g(ps, 'PENDIENTE DE BACK OFFICE')
    res['PENDIENTE DE REMESA'] = g(ps, 'PENDIENTE DE REMESA')
    res['META OBJETIVO'] = 1000000.00
    res['AVANCE'] = (res['TOTAL DESEMBOLSO'] / res['META OBJETIVO']).fillna(0)
    res['Q POR INGRESAR'] = g(pc, 'POR INGRESAR')
    res['Q EVALUACION BCP'] = g(pc, 'EN EVALUACION BCP')
    res['Q PENDIENTE DE BACK'] = g(pc, 'PENDIENTE DE BACK OFFICE')
    tot = res.sum(numeric_only=True)
    if group_col == 'SUPERVISOR': tot['ZONA'] = ''
    tot['AVANCE'] = (tot['TOTAL DESEMBOLSO'] / tot['META OBJETIVO']) if tot['META OBJETIVO'] > 0 else 0
    res.loc['TOTAL'] = tot
    return res.reset_index()

m_df = df[df['SUPERVISOR'].isin(selected_supervisor) & df['CONVENIO'].isin(selected_convenio) & df['REGION'].isin(selected_region)]
df_super = build_matrix(m_df, 'SUPERVISOR')

# Build plaza matrix using REGION
def build_plaza_matrix(data):
    if data.empty: return pd.DataFrame()
    data = data.copy()
    data['PLAZA'] = data['REGION']
    return build_matrix(data, 'PLAZA')

df_plaza = build_plaza_matrix(m_df)

cc = {
    "TOTAL DESEMBOLSO": st.column_config.NumberColumn("Total Desembolso", format="S/ %d"),
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

tab1, tab2 = st.tabs(["Por Supervisor", "Por Plaza"])
with tab1:
    if not df_super.empty: st.dataframe(df_super, use_container_width=True, hide_index=True, column_config=cc)
with tab2:
    if not df_plaza.empty: st.dataframe(df_plaza, use_container_width=True, hide_index=True, column_config=cc)

# --- DETALLE ---
st.markdown("""<div class="section-header">
    <div class="section-icon"><svg viewBox="0 0 24 24"><path d="M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z"/></svg></div>
    <span class="section-label">Detalle de Operaciones</span>
</div>""", unsafe_allow_html=True)

with st.expander("Expandir tabla completa"):
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
