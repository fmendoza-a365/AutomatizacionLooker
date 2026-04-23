import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64

# --- CONSTANTES ---
ZONAS_MAP = {
    'NAHOMI': 'CHICLAYO', 'JORGE': 'CHICLAYO', 'JHON': 'CHICLAYO',
    'WINNIE': 'LIMA', 'KENNY': 'LIMA', 'ANGIE': 'LIMA', 'MARIELLA': 'LIMA',
    'LUIS CHUSE': 'LIMA', 'LUIS SHEPHERD': 'LIMA', 'LUIS MENDOZA': 'LIMA',
    'JIMMY': 'TARAPOTO', 'JULIA': 'TRUJILLO',
}
META_GLOBAL = 11950000.00
NORTE = ['CHICLAYO', 'PIURA', 'TRUJILLO']

ESTADO_COLORS = {
    'POR INGRESAR': '#2B7DE9', 'EN EVALUACION BCP': '#E6A817', 'APROBADA': '#2D9A3F',
    'PENDIENTE DE BACK OFFICE': '#7C5CBF', 'PENDIENTE DE REMESA': '#C94277',
    'DESEMBOLSADO': '#E67212', 'RECHAZADA': '#C43A31', 'OBSERVADO FFVV': '#7A7A82',
    'OBSERVADO BACK': '#5C5C66', 'PENDIENTE DE DOCUMENTAR': '#1A4FA0',
}

REGION_COLORS = {'LIMA': '#1A4FA0', 'NORTE': '#E67212', 'OTROS': '#2B7DE9'}

# --- PAGE CONFIG ---
st.set_page_config(page_title="A365 BCP - Centro de Operaciones", layout="wide", page_icon="isotipobcp.png")

# --- LOGO ---
def get_b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

logo_b64 = get_b64("A366BCP.png")
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:44px;" alt="Logo A365 BCP">' if logo_b64 else '<span style="font-weight:800;font-size:22px;color:#1A4FA0;">A365 BCP</span>'

# --- CSS (neutrales tintados hacia azul marca hue ~260) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{ font-family: 'Manrope', sans-serif !important; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 0 !important; padding-bottom: 1rem !important; max-width: 1400px; }}

    .topbar {{ display:flex; align-items:center; justify-content:space-between; padding:14px 0; border-bottom:1px solid #DDDDE5; margin-bottom:20px; }}
    .topbar-left {{ display:flex; align-items:center; gap:14px; }}
    .topbar-title {{ font-size:13px; font-weight:600; color:#7B7B8A; letter-spacing:0.5px; text-transform:uppercase; }}
    .topbar-right {{ font-size:12px; color:#7B7B8A; display:flex; align-items:center; gap:6px; }}

    .section-header {{ display:flex; align-items:center; gap:8px; margin:28px 0 14px 0; padding-bottom:6px; border-bottom:2px solid #1A4FA0; }}
    .section-icon {{ width:20px; height:20px; border-radius:4px; background:#E67212; display:flex; align-items:center; justify-content:center; flex-shrink:0; }}
    .section-icon svg {{ width:12px; height:12px; fill:white; }}
    .section-label {{ font-size:13px; font-weight:700; color:#1A4FA0; text-transform:uppercase; letter-spacing:0.4px; }}

    /* KPI row — responsive con auto-fit */
    .kpi-row {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:14px; margin-bottom:24px; }}
    .kpi-card {{
        background:#FFFFFF;
        border:1px solid #DDDDE5;
        border-radius:10px;
        padding:20px 22px;
    }}
    .kpi-card[data-accent="true"] .kpi-value {{ color:#E67212; }}
    .kpi-label {{ font-size:10px; font-weight:700; color:#7B7B8A; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:8px; }}
    .kpi-value {{ font-size:26px; font-weight:800; color:#1C1C1E; letter-spacing:-0.5px; }}
    .kpi-sub {{ font-size:11px; color:#7B7B8A; margin-top:4px; }}

    h1,h2,h3,h4 {{ font-weight:700 !important; color:#1A4FA0 !important; }}
    div[data-testid="stMetricLabel"], div[data-testid="stMetricValue"] {{ display:none; }}
    div[data-testid="stDataFrame"] {{ border:1px solid #DDDDE5; border-radius:10px; overflow:hidden; }}

    section[data-testid="stSidebar"] {{ background:#F7F7FB; border-right:1px solid #DDDDE5; }}
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{ font-size:13px; }}

    /* Responsive: gráficos en mobile */
    @media (max-width: 768px) {{
        .kpi-row {{ grid-template-columns: repeat(2, 1fr); }}
        .block-container {{ padding-left: 1rem !important; padding-right: 1rem !important; }}
    }}
    /* Estilo Premium de Tarjetas */
    .stPlotlyChart {{
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #f0f0f5;
        padding: 10px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        overflow: hidden !important; /* Elimina scrollbars */
    }}
    .stPlotlyChart:hover {{
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
        transform: translateY(-2px);
    }}
    
    /* Optimización Móvil */
    @media (max-width: 768px) {{
        .kpi-row {{
            grid-template-columns: 1fr !important;
            gap: 12px !important;
        }}
        .section-header {{
            margin-top: 20px !important;
            padding: 12px !important;
        }}
        [data-testid="stMetricValue"] {{
            font-size: 1.8rem !important;
        }}
    }}
    
    /* Ajuste de Espaciado General */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- TOPBAR ---
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">{logo_html}<span class="topbar-title">Centro de Operaciones</span></div>
    <div class="topbar-right">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="#7B7B8A"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zm1 11h-2V7h2zm0 4h-2v-2h2z"/></svg>
        Datos actualizados cada 5 min
    </div>
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
    df['ZONA_SUP'] = df['SUPERVISOR'].map(ZONAS_MAP).fillna('N/A')
    df['REGION'] = df['ZONA_SUP'].apply(lambda z: 'LIMA' if z == 'LIMA' else ('NORTE' if z in NORTE else 'OTROS'))
    return df

with st.spinner('Conectando...'):
    df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center;padding:12px 0 8px 0;">{logo_html}</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Filtros**")
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
desembolsado_df = filtered_df[filtered_df['ESTADO LIMPIO'] == 'DESEMBOLSADO']
monto_desembolso = desembolsado_df['MAF NETO_Num'].sum()
q_desembolso = len(desembolsado_df)
avance = (monto_desembolso / META_GLOBAL * 100) if META_GLOBAL > 0 else 0
cantidad_ops = len(filtered_df)
ticket_prom = desembolsado_df['MAF NETO_Num'].mean() if q_desembolso > 0 else 0

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card" role="status" aria-label="Desembolso total: S/ {monto_desembolso:,.0f}">
        <div class="kpi-label">Desembolso Total</div>
        <div class="kpi-value">S/ {monto_desembolso:,.0f}</div>
        <div class="kpi-sub">{q_desembolso} operaciones desembolsadas</div>
    </div>
    <div class="kpi-card" data-accent="true" role="status" aria-label="Avance vs meta: {avance:.1f} porciento">
        <div class="kpi-label">Avance vs Meta</div>
        <div class="kpi-value">{avance:.1f}%</div>
        <div class="kpi-sub">Meta: S/ {META_GLOBAL:,.0f}</div>
    </div>
    <div class="kpi-card" role="status" aria-label="Operaciones totales: {cantidad_ops}">
        <div class="kpi-label">Operaciones Totales</div>
        <div class="kpi-value">{cantidad_ops}</div>
        <div class="kpi-sub">Todos los estados</div>
    </div>
    <div class="kpi-card" role="status" aria-label="Ticket promedio: S/ {ticket_prom:,.0f}">
        <div class="kpi-label">Ticket Promedio</div>
        <div class="kpi-value">S/ {ticket_prom:,.0f}</div>
        <div class="kpi-sub">Promedio por desembolso</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- HELPER ---
def clean_fig(fig, h=300):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Manrope", color="#1C1C1E", size=11),
        margin=dict(l=60, r=60, t=5, b=5), height=h, # Márgenes reducidos para evitar scroll
        dragmode=False,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=9), automargin=True)
    fig.update_yaxes(showgrid=True, gridcolor='#F0F0F5', zeroline=False, tickfont=dict(size=9), automargin=True)
    return fig

# --- SECCIÓN: GRÁFICOS ---
st.markdown("""<div class="section-header">
    <div class="section-icon"><svg viewBox="0 0 24 24"><path d="M3 13h2v8H3zm4-4h2v12H7zm4-2h2v14h-2zm4 6h2v8h-2zm4-8h2v16h-2z"/></svg></div>
    <span class="section-label">Análisis de Rendimiento</span>
</div>""", unsafe_allow_html=True)

title_style = 'style="font-size:15px; font-weight:700; color:#1A4FA0; margin-bottom:12px; margin-top:0px;"'

# ROW 1
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown(f'<p {title_style}>Desembolso por Supervisor</p>', unsafe_allow_html=True)
    v_sup = desembolsado_df.groupby('SUPERVISOR')['MAF NETO_Num'].sum().reset_index().sort_values('MAF NETO_Num', ascending=True)
    fig1 = go.Figure(go.Bar(
        y=v_sup['SUPERVISOR'], x=v_sup['MAF NETO_Num'], orientation='h',
        marker=dict(color='#E67212', cornerradius=4),
        text=[f"S/ {v:,.0f}" for v in v_sup['MAF NETO_Num']], textposition='outside',
        textfont=dict(size=11, family="Manrope", color="#1C1C1E"),
        cliponaxis=False # Evita que se corte el texto
    ))
    fig1 = clean_fig(fig1, 300)
    # Ampliar el rango del eje X un 40% para dar espacio total a la etiqueta
    mx = v_sup['MAF NETO_Num'].max()
    fig1.update_xaxes(range=[0, mx * 1.40] if mx > 0 else None)
    fig1.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

with c2:
    st.markdown(f'<p {title_style}>Funnel por Estado</p>', unsafe_allow_html=True)
    e_dist = filtered_df['ESTADO LIMPIO'].value_counts().reset_index()
    e_dist.columns = ['Estado', 'Cantidad']
    e_dist = e_dist.sort_values('Cantidad', ascending=True) # Mayor a menor (Plotly dibuja de abajo a arriba)
    
    fig2 = go.Figure()
    for _, row in e_dist.iterrows():
        fig2.add_trace(go.Bar(
            y=[row['Estado']], x=[row['Cantidad']], orientation='h',
            marker=dict(color=ESTADO_COLORS.get(row['Estado'], '#7A7A82'), cornerradius=4),
            text=[str(int(row['Cantidad']))], textposition='outside',
            textfont=dict(size=11, family="Manrope"), showlegend=False,
            cliponaxis=False
        ))
    fig2 = clean_fig(fig2, 300)
    # Espacio extra en el eje X para el Funnel (40% buffer)
    mxf = e_dist['Cantidad'].max()
    fig2.update_xaxes(range=[0, mxf * 1.40] if mxf > 0 else None)
    fig2.update_layout(barmode='stack', xaxis_title="", yaxis_title="")
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

# ROW 2
c3, c4, c5 = st.columns(3)

with c3:
    st.markdown(f'<p {title_style}>Desembolso por Convenio</p>', unsafe_allow_html=True)
    v_conv = desembolsado_df.groupby('CONVENIO')['MAF NETO_Num'].sum().reset_index().sort_values('MAF NETO_Num', ascending=False)
    fig3 = go.Figure(go.Bar(
        x=v_conv['CONVENIO'], y=v_conv['MAF NETO_Num'],
        marker=dict(color='#1A4FA0', cornerradius=4), # Usamos Azul BCP para variar del naranja
        text=[f"{v/1000:.0f}K" for v in v_conv['MAF NETO_Num']], textposition='outside',
        textfont=dict(size=10, family="Manrope", color="#1C1C1E")
    ))
    fig3 = clean_fig(fig3, 260)
    fig3.update_layout(xaxis_title="", yaxis_title="")
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})

with c4:
    st.markdown(f'<p {title_style}>Distribución por Región</p>', unsafe_allow_html=True)
    v_reg = desembolsado_df.groupby('REGION')['MAF NETO_Num'].sum().reset_index().sort_values('MAF NETO_Num', ascending=False)
    fig4 = go.Figure(go.Pie(
        labels=v_reg['REGION'], values=v_reg['MAF NETO_Num'], hole=0.7,
        textposition='outside', textinfo='label+percent',
        textfont=dict(size=11, family="Manrope", color="#1C1C1E"),
        marker=dict(colors=[REGION_COLORS.get(r, '#7A7A82') for r in v_reg['REGION']],
                    line=dict(color='#FFFFFF', width=2))
    ))
    fig4 = clean_fig(fig4, 230)
    fig4.update_traces(domain=dict(x=[0, 1], y=[0, 1])) # Ocupar todo el espacio disponible
    fig4.update_layout(
        showlegend=False,
        margin=dict(l=120, r=120, t=20, b=20), # Márgenes fijos y simétricos
        autosize=True,
        annotations=[dict(
            text=f'<span style="font-size:12px; font-weight:bold; color:#1A4FA0">S/ {monto_desembolso/1e6:.1f}M</span><br><span style="font-size:8px; color:#7A7A82">Total</span>', 
            x=0.5, y=0.5, showarrow=False, xanchor='center', yanchor='middle',
            font=dict(family="Manrope")
        )]
    )
    st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

with c5:
    st.markdown(f'<p {title_style}>Top Asesores por Desembolso</p>', unsafe_allow_html=True)
    if 'NOMBRES Y APELLIDOS' in desembolsado_df.columns:
        top_asesores = desembolsado_df.groupby('NOMBRES Y APELLIDOS')['MAF NETO_Num'].sum().nlargest(5).reset_index()
        top_asesores = top_asesores.sort_values('MAF NETO_Num', ascending=True)
        top_asesores['Nombre'] = top_asesores['NOMBRES Y APELLIDOS'].apply(lambda n: str(n)[:20] + '...' if len(str(n)) > 20 else str(n))
        fig5 = go.Figure(go.Bar(
            y=top_asesores['Nombre'], x=top_asesores['MAF NETO_Num'], orientation='h',
            marker=dict(color='#E67212', cornerradius=4),
            text=[f"S/ {v:,.0f}" for v in top_asesores['MAF NETO_Num']], textposition='outside',
            textfont=dict(size=10, family="Manrope", color="#1C1C1E"),
            cliponaxis=False
        ))
        fig5 = clean_fig(fig5, 260)
        # Espacio extra en el eje X para Top Asesores (40% buffer)
        mx5 = top_asesores['MAF NETO_Num'].max()
        fig5.update_xaxes(range=[0, mx5 * 1.40] if mx5 > 0 else None)
        fig5.update_layout(xaxis_title="", yaxis_title="")
        st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Columna de nombres no disponible.")

# --- SECCIÓN: TABLAS ---
st.markdown("""<div class="section-header">
    <div class="section-icon"><svg viewBox="0 0 24 24"><path d="M3 3h18v18H3zm2 2v4h6V5zm8 0v4h6V5zm-8 6v4h6v-4zm8 0v4h6v-4zM5 17v2h6v-2zm8 0v2h6v-2z"/></svg></div>
    <span class="section-label">Tablas de Gestión</span>
</div>""", unsafe_allow_html=True)

def build_matrix(data, group_col):
    if data.empty: return pd.DataFrame()
    ps = data.pivot_table(index=group_col, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='sum', fill_value=0)
    pc = data.pivot_table(index=group_col, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='count', fill_value=0)
    res = pd.DataFrame(index=ps.index)
    if group_col == 'SUPERVISOR':
        res['ZONA'] = [ZONAS_MAP.get(s, 'N/A') for s in res.index]
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
    # Limpieza de columnas feas para el detalle
    bad_cols = ['MAF NETO_Num', 'ZONA_SUP', 'REGION', 'PLAZA DE VENTA', 'FECHA FILTRO', 'FECHA DE INGRESO', 'FECHA DE DESEMBOLSO']
    show_df = filtered_df.copy()
    # Eliminar columnas Unnamed
    show_df = show_df.loc[:, ~show_df.columns.str.contains('^Unnamed')]
    # Eliminar otras columnas técnicas
    show_df = show_df.drop(columns=[c for c in bad_cols if c in show_df.columns])
    st.dataframe(show_df, use_container_width=True, hide_index=True)

