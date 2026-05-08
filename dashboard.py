import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from io import BytesIO
import requests

# --- HELPER EXCEL ---
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def create_download_link(df, filename, label):
    data = to_excel(df)
    b64 = base64.b64encode(data).decode()
    href = f'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}'
    icon_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/><path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"/></svg>"""
    return f'<a href="{href}" download="{filename}" class="export-button">{icon_svg}&nbsp;&nbsp;{label}</a>'

# --- CONSTANTES ---
ZONAS_MAP = {
    'NAHOMI DIAZ': 'CHICLAYO', 'JORGE RAMIREZ': 'CHICLAYO', 'JHON ZAMORA': 'CHICLAYO',
    'CRISTINA BRACAMONTE': 'CHICLAYO',                                          # MAYO - Nuevo
    'MILAGROS TUESTA': 'LIMA', 'KENNY MORALES': 'LIMA', 'ANGIE SILVERA': 'LIMA', 'MARIELLA PAÑAHUA': 'LIMA',
    'LUIS CHUSE': 'LIMA', 'LUIS SHEPHERD': 'LIMA', 'LUIS MENDOZA': 'LIMA', 'PERCY ADRIANZEN': 'LIMA',  # MAYO - Nuevo
    'JIMMY COLLAZOS': 'TARAPOTO', 'JULIA OBLITAS': 'TRUJILLO',
    'VIOLETA LLERENA': 'AREQUIPA',                                              # MAYO - Nuevo (→ OTROS)
    'WINNIE': 'LIMA'
}
NORTE = ['CHICLAYO', 'PIURA', 'TRUJILLO']

# --- CONFIGURACIÓN POR MES (URL + Formato + Metas) ---
MESES_CONFIG = {
    'ABRIL': {
        'url': 'https://docs.google.com/spreadsheets/d/16PzK230jtrjkpHYq5mYSFrdeXk-0B6N7/export?format=csv&gid=305780908',
        'format': 'csv',
        'metas': {
            'ANGIE SILVERA': 1_000_000, 'NAHOMI DIAZ': 1_000_000, 'MILAGROS TUESTA': 1_000_000,
            'JHON ZAMORA': 1_000_000, 'MARIELLA PAÑAHUA': 650_000, 'JIMMY COLLAZOS': 650_000,
            'KENNY MORALES': 650_000, 'LUIS CHUSE': 1_000_000, 'JULIA OBLITAS': 1_000_000,
            'JORGE RAMIREZ': 1_000_000, 'LUIS SHEPHERD': 500_000, 'LUIS MENDOZA': 500_000,
            'WINNIE': 1_000_000,  # alias de MILAGROS TUESTA
        }
    },
    'MAYO': {
        'url': 'https://docs.google.com/spreadsheets/d/1zJONhh_3kih4HZUNvi3DC4Ybou84U-SUsiaOdbwEVJw/export?format=xlsx',
        'format': 'excel_multisheet',
        'metas': {
            'CRISTINA BRACAMONTE': 1_000_000, 'JHON ZAMORA': 1_000_000, 'JORGE RAMIREZ': 1_000_000,
            'ANGIE SILVERA': 2_500_000, 'LUIS CHUSE': 1_500_000, 'LUIS MENDOZA': 1_000_000,
            'JIMMY COLLAZOS': 1_000_000, 'KENNY MORALES': 1_000_000, 'MILAGROS TUESTA': 1_500_000,
            'MARIELLA PAÑAHUA': 1_000_000, 'PERCY ADRIANZEN': 1_000_000,
            'NAHOMI DIAZ': 1_000_000, 'VIOLETA LLERENA': 1_000_000,
            'WINNIE': 1_500_000,  # alias de MILAGROS TUESTA
        }
    },
    # Para agregar JUNIO: copiar este bloque, completar url y metas.
    # 'JUNIO': { 'url': '...', 'format': 'csv', 'metas': { ... } }
}

def get_meta_supervisor(supervisor, meses_activos):
    """Meta acumulada de un supervisor para los meses seleccionados."""
    key = str(supervisor).upper().strip()
    return sum(MESES_CONFIG.get(m, {}).get('metas', {}).get(key, 0) for m in meses_activos)

def get_metas_supervisores(supervisores, meses_activos):
    """Meta total acumulada para una lista de supervisores y meses seleccionados."""
    total = sum(get_meta_supervisor(s, meses_activos) for s in supervisores)
    if total == 0:
        total = sum(sum(cfg['metas'].values()) for cfg in MESES_CONFIG.values())
    return total



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
    
    /* Estilo Premium para Botones de Exportación */
    .export-button {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 7px 15px;
        background-color: #FFFFFF;
        color: #1A4FA0 !important;
        border: 1px solid #1A4FA0;
        border-radius: 8px;
        text-decoration: none !important;
        font-size: 12px;
        font-weight: 700;
        margin-top: 12px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }}
    .export-button:hover {{
        background-color: #1A4FA0;
        color: #FFFFFF !important;
        box-shadow: 0 4px 8px rgba(26, 79, 160, 0.2);
        transform: translateY(-1px);
    }}
    .export-button svg {{
        margin-right: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# --- TOPBAR ---
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">{logo_html}<span class="topbar-title">Centro de Operaciones</span></div>
    <div class="topbar-right">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="#7B7B8A"><path d="M12 2a10 10 0 100 20 10 10 0 000-20zm1 11h-2V7h2zm0 4h-2v-2h2z"/></svg>
        Datos actualizados cada 1 min
    </div>
</div>
""", unsafe_allow_html=True)

# --- DATA ---
ESTADO_MAPPING = {
    'EVALUACIÓN BCP': 'EN EVALUACION BCP', 'EVALUACION BCP': 'EN EVALUACION BCP',
    'PENDIENTE DE BACKOFFICE': 'PENDIENTE DE BACK OFFICE', 'PENDIENTE DE BACK': 'PENDIENTE DE BACK OFFICE',
    'OBS BACKOFFICE': 'OBSERVADO BACK', 'OBS BCP': 'OBSERVADO FFVV',
    'RECHAZADO': 'RECHAZADA', 'APROBADA': 'APROBADA', 'DESEMBOLSADO': 'DESEMBOLSADO',
    'PENDIENTE DE DOCUMENTAR': 'PENDIENTE DE DOCUMENTAR', 'PENDIENTE DE REMESA': 'PENDIENTE DE REMESA'
}

def _load_excel_multisheet(url):
    """Carga un Excel multi-hoja donde cada hoja es un supervisor. Reutilizable para cualquier mes."""
    all_dfs = []
    sheet_names = []
    try:
        res = requests.get(url)
        if res.status_code == 200:
            xls = pd.ExcelFile(BytesIO(res.content))
            sheet_names = xls.sheet_names
            for sheet in sheet_names:
                df_raw = pd.read_excel(xls, sheet_name=sheet, header=None)
                header_idx = -1
                for idx, row in df_raw.iterrows():
                    if row.astype(str).str.contains('PLAZA DE VENTA', na=False, case=False).any():
                        header_idx = idx
                        break
                if header_idx != -1:
                    df_raw.columns = df_raw.iloc[header_idx]
                    df_sheet = df_raw.iloc[header_idx + 1:].copy()
                    df_sheet = df_sheet.loc[:, df_sheet.columns.notna()]
                    df_sheet = df_sheet.dropna(how='all')
                    if not df_sheet.empty:
                        df_sheet['SUPERVISOR'] = sheet
                        all_dfs.append(df_sheet)
    except Exception as e:
        st.error(f"Error técnico cargando Excel: {e}")
    df_result = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
    # Normalizar columna ESTADO
    if not df_result.empty:
        if 'ESTADO' in df_result.columns and 'ESTADO LIMPIO' not in df_result.columns:
            df_result = df_result.rename(columns={'ESTADO': 'ESTADO LIMPIO'})
        if 'ESTADO LIMPIO' in df_result.columns:
            df_result['ESTADO LIMPIO'] = df_result['ESTADO LIMPIO'].astype(str).str.strip().str.upper()
            df_result['ESTADO LIMPIO'] = df_result['ESTADO LIMPIO'].map(lambda x: ESTADO_MAPPING.get(x, x))
    return df_result, sheet_names

@st.cache_data(ttl=60)
def load_data():
    all_monthly = []
    debug_info = {}
    for mes, config in MESES_CONFIG.items():
        try:
            if config['format'] == 'csv':
                df_mes = pd.read_csv(config['url'])
                debug_info[mes] = {'cargado': not df_mes.empty, 'registros': len(df_mes)}
            elif config['format'] == 'excel_multisheet':
                df_mes, sheets = _load_excel_multisheet(config['url'])
                debug_info[mes] = {'cargado': not df_mes.empty, 'registros': len(df_mes), 'hojas': sheets}
            else:
                continue
            if not df_mes.empty:
                df_mes['MES'] = mes
                all_monthly.append(df_mes)
        except Exception as e:
            st.error(f"Error cargando {mes}: {e}")
            debug_info[mes] = {'cargado': False, 'registros': 0}
    st.session_state['debug_meses'] = debug_info
    if not all_monthly:
        return pd.DataFrame()
    df = pd.concat(all_monthly, ignore_index=True)

    # --- LIMPIEZA UNIFICADA ---
    if 'MAF NETO' in df.columns:
        df['MAF NETO'] = df['MAF NETO'].fillna("0")
        df['MAF NETO_Num'] = df['MAF NETO'].astype(str).str.replace('S/', '', regex=False).str.strip()
        df['MAF NETO_Num'] = df['MAF NETO_Num'].str.replace('.', '', regex=False)
        df['MAF NETO_Num'] = df['MAF NETO_Num'].str.replace(',', '.', regex=False)
        df['MAF NETO_Num'] = pd.to_numeric(df['MAF NETO_Num'], errors='coerce').fillna(0)
    df['SUPERVISOR'] = df['SUPERVISOR'].fillna('SIN SUPERVISOR').astype(str).str.strip().str.upper()
    if 'PLAZA DE VENTA' in df.columns:
        df['PLAZA DE VENTA'] = df['PLAZA DE VENTA'].fillna('SIN PLAZA').astype(str).str.strip()
    if 'ESTADO LIMPIO' in df.columns:
        df['ESTADO LIMPIO'] = df['ESTADO LIMPIO'].fillna('SIN ESTADO').astype(str).str.strip().str.upper()
    if 'CONVENIO' in df.columns:
        df['CONVENIO'] = df['CONVENIO'].fillna('SIN CONVENIO').astype(str).str.strip().str.upper()
    if 'EJECUTIVO' in df.columns:
        df['EJECUTIVO'] = df['EJECUTIVO'].fillna('SIN ASIGNAR').astype(str).str.strip().str.upper()
    df['ZONA_SUP'] = df['SUPERVISOR'].map(ZONAS_MAP).fillna('N/A')
    df['REGION'] = df['ZONA_SUP'].apply(lambda z: 'LIMA' if z == 'LIMA' else ('NORTE' if z in NORTE else 'OTROS'))
    return df

with st.spinner('Conectando...'):
    df = load_data()

# --- DIAGNÓSTICO DE DATOS ---
debug_meses = st.session_state.get('debug_meses', {})
meses_fallidos = [m for m, info in debug_meses.items() if not info.get('cargado', False)]
if meses_fallidos:
    with st.expander(f"⚠️ Aviso: No se detectaron datos de {', '.join(meses_fallidos)}", expanded=False):
        for mes in meses_fallidos:
            info = debug_meses[mes]
            st.warning(f"No se encontraron registros válidos en {mes}.")
            if 'hojas' in info:
                st.info(f"Hojas encontradas: {', '.join(info['hojas'])}")
        st.markdown("""
        **Posibles causas:**
        1. Ninguna hoja tiene una columna llamada exactamente **'PLAZA DE VENTA'**.
        2. Las hojas están vacías o el archivo no es accesible.
        """)

# --- FILTROS GLOBALES SUPERIORES ---
c_f1, c_f2 = st.columns([1, 3])
with c_f1:
    mes_opts = sorted(df['MES'].dropna().unique().tolist())
    with st.popover("📅 Seleccionar Mes", use_container_width=True):
        st.markdown("**Meses de Gestión**")
        selected_mes = []
        for m in mes_opts:
            if st.checkbox(m, value=True, key=f"global_mes_{m}"):
                selected_mes.append(m)
with c_f2:
    # Espacio para info o dejar vacío para alinear a la izquierda
    st.markdown('<div style="margin-top:10px; color:#7B7B8A; font-size:12px;">Filtro global: Afecta a KPIs, Gráficos y Tablas</div>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center;padding:12px 0 8px 0;">{logo_html}</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Filtros Adicionales**")
    
    region_opts = ['LIMA', 'NORTE', 'OTROS']
    selected_region = st.multiselect("Plaza", region_opts, default=region_opts)
    supervisor_list = sorted(df[df['REGION'].isin(selected_region)]['SUPERVISOR'].unique().tolist())
    selected_supervisor = st.multiselect("Supervisor", supervisor_list, default=supervisor_list)
    convenio_list = sorted(df['CONVENIO'].unique().tolist())
    selected_convenio = st.multiselect("Convenio", convenio_list, default=convenio_list)
    ejecutivo_list = sorted(df[df['SUPERVISOR'].isin(selected_supervisor)]['EJECUTIVO'].unique().tolist())
    selected_ejecutivo = st.multiselect("Ejecutivo", ejecutivo_list, default=ejecutivo_list)

filtered_df = df[
    (df['MES'].isin(selected_mes)) &
    (df['REGION'].isin(selected_region)) &
    (df['SUPERVISOR'].isin(selected_supervisor)) &
    (df['CONVENIO'].isin(selected_convenio)) &
    (df['EJECUTIVO'].isin(selected_ejecutivo))
]

# --- KPIs ---
desembolsado_df = filtered_df[filtered_df['ESTADO LIMPIO'] == 'DESEMBOLSADO']

# --- CALCULO META DINÁMICA ---
# Base: suma directa desde MESES_CONFIG para los meses activos (incluye sups sin datos aún)
meta_base = sum(
    sum(v for k, v in MESES_CONFIG.get(m, {}).get('metas', {}).items() if k != 'WINNIE')
    for m in selected_mes
)
# Restar solo lo que el usuario deseleccionó explícitamente en el sidebar
sups_deseleccionados = (set(supervisor_list) - set(selected_supervisor)) - {'WINNIE'}
meta_excluida = get_metas_supervisores(sups_deseleccionados, selected_mes)
meta_actual = max(meta_base - meta_excluida, 0) or meta_base


monto_desembolso = desembolsado_df['MAF NETO_Num'].sum()
q_desembolso = len(desembolsado_df)
avance = (monto_desembolso / meta_actual * 100) if meta_actual > 0 else 0
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
        <div class="kpi-sub">Meta: S/ {meta_actual:,.0f}</div>
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
c_head1, c_head2 = st.columns([3, 1])
with c_head1:
    st.markdown("""<div class="section-header" style="margin-top:10px;">
        <div class="section-icon"><svg viewBox="0 0 24 24"><path d="M3 13h2v8H3zm4-4h2v12H7zm4-2h2v14h-2zm4 6h2v8h-2zm4-8h2v16h-2z"/></svg></div>
        <span class="section-label">Análisis de Rendimiento</span>
    </div>""", unsafe_allow_html=True)

with c_head2:
    st.markdown('<div style="margin-top:18px;">', unsafe_allow_html=True)
    with st.popover("🔍 Filtrar por Zona", use_container_width=True):
        st.markdown("**Seleccionar Zonas**")
        # Obtenemos zonas del df ya filtrado por la sidebar para mantener coherencia
        zonas_disponibles = sorted([z for z in filtered_df['ZONA_SUP'].unique() if z != 'N/A'])
        selected_zonas_sec = []
        for zona in zonas_disponibles:
            if st.checkbox(zona, value=True, key=f"sec_{zona}"):
                selected_zonas_sec.append(zona)
    st.markdown('</div>', unsafe_allow_html=True)

# DF específico para esta sección
if not selected_zonas_sec:
    section_df = filtered_df.iloc[:0] # Vacío si no hay nada seleccionado
else:
    section_df = filtered_df[filtered_df['ZONA_SUP'].isin(selected_zonas_sec)]

desembolsado_sec = section_df[section_df['ESTADO LIMPIO'] == 'DESEMBOLSADO']

title_style = 'style="font-size:15px; font-weight:700; color:#1A4FA0; margin-bottom:12px; margin-top:0px;"'

# ROW 1
c1, c2 = st.columns([3, 2])

with c1:
    st.markdown(f'<p {title_style}>Desembolso por Supervisor</p>', unsafe_allow_html=True)
    v_sup = desembolsado_sec.groupby('SUPERVISOR')['MAF NETO_Num'].sum().reset_index().sort_values('MAF NETO_Num', ascending=True)
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
    e_dist = section_df.groupby('ESTADO LIMPIO').agg(
        Cantidad=('ESTADO LIMPIO', 'count'),
        Monto=('MAF NETO_Num', 'sum')
    ).reset_index().rename(columns={'ESTADO LIMPIO': 'Estado'})
    e_dist = e_dist.sort_values('Cantidad', ascending=True) # Mayor a menor (Plotly dibuja de abajo a arriba)
    
    fig2 = go.Figure()
    for _, row in e_dist.iterrows():
        # Formatear el monto de forma compacta
        monto_f = f"S/ {row['Monto']:,.0f}" if row['Monto'] < 1000000 else f"S/ {row['Monto']/1e6:.1f}M"
        fig2.add_trace(go.Bar(
            y=[row['Estado']], x=[row['Cantidad']], orientation='h',
            marker=dict(color=ESTADO_COLORS.get(row['Estado'], '#7A7A82'), cornerradius=4),
            text=[f"{int(row['Cantidad'])} ({monto_f})"], textposition='outside',
            hovertemplate=f"<b>{row['Estado']}</b><br>Cantidad: {int(row['Cantidad'])}<br>Monto: {monto_f}<extra></extra>",
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
    v_conv = desembolsado_sec.groupby('CONVENIO')['MAF NETO_Num'].sum().reset_index().sort_values('MAF NETO_Num', ascending=False)
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
    fig4 = clean_fig(fig4, 260) # Altura normalizada para alinear la base de la tarjeta
    fig4.update_layout(
        showlegend=False,
        margin=dict(l=100, r=100, t=30, b=30), # Margen grande para que el círculo se vea pequeño y centrado
        annotations=[dict(
            text=f'<span style="font-size:12px; font-weight:bold; color:#1A4FA0">S/ {monto_desembolso/1e6:.1f}M</span><br><span style="font-size:8px; color:#7A7A82">Total</span>', 
            x=0.5, y=0.5, showarrow=False, xanchor='center', yanchor='middle',
            font=dict(family="Manrope")
        )]
    )
    st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})

with c5:
    st.markdown(f'<p {title_style}>Top Ejecutivos por Desembolso</p>', unsafe_allow_html=True)
    if 'EJECUTIVO' in desembolsado_sec.columns:
        top_asesores = desembolsado_sec.groupby('EJECUTIVO')['MAF NETO_Num'].sum().nlargest(5).reset_index()
        top_asesores = top_asesores.sort_values('MAF NETO_Num', ascending=True)
        top_asesores['Nombre'] = top_asesores['EJECUTIVO'].apply(lambda n: str(n)[:20] + '...' if len(str(n)) > 20 else str(n))
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

def build_matrix(data, group_col, meses_activos):
    g = lambda p, c: p[c] if c in p.columns else 0

    if group_col == 'SUPERVISOR':
        # Supervisores con meta asignada en los meses activos
        sups_con_meta = sorted(
            s for mes in meses_activos
            for s in MESES_CONFIG.get(mes, {}).get('metas', {})
            if s != 'WINNIE'
        )
        # Supervisores que tienen datos reales (normalizados a mayúsculas)
        data = data.copy()
        if not data.empty:
            data[group_col] = data[group_col].str.upper().str.strip()
        sups_en_datos = list(data[group_col].unique()) if not data.empty else []
        full_index = sorted(set(sups_con_meta) | set(sups_en_datos))

        if not data.empty:
            ps = data.pivot_table(index=group_col, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='sum', fill_value=0)
            pc = data.pivot_table(index=group_col, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='count', fill_value=0)
        else:
            ps = pd.DataFrame(index=pd.Index([], name=group_col))
            pc = pd.DataFrame(index=pd.Index([], name=group_col))
        ps = ps.reindex(full_index, fill_value=0)
        pc = pc.reindex(full_index, fill_value=0)
        res = pd.DataFrame(index=ps.index)
        res['ZONA'] = [ZONAS_MAP.get(s, 'N/A') for s in res.index]
    else:
        if data.empty: return pd.DataFrame()
        ps = data.pivot_table(index=group_col, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='sum', fill_value=0)
        pc = data.pivot_table(index=group_col, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='count', fill_value=0)
        res = pd.DataFrame(index=ps.index)

    res['TOTAL DESEMBOLSO'] = g(ps, 'DESEMBOLSADO')
    res['Q DESEMBOLSO'] = g(pc, 'DESEMBOLSADO')
    res['APROBADA'] = g(ps, 'APROBADA')
    res['POR INGRESAR'] = g(ps, 'POR INGRESAR')
    res['EVALUACION BCP'] = g(ps, 'EN EVALUACION BCP')
    res['PENDIENTE DE BACK'] = g(ps, 'PENDIENTE DE BACK OFFICE')
    res['PENDIENTE DE REMESA'] = g(ps, 'PENDIENTE DE REMESA')
    # --- Metas Dinámicas por mes seleccionado ---
    if group_col == 'SUPERVISOR':
        res['META OBJETIVO'] = [get_meta_supervisor(s, meses_activos) for s in res.index]
    else:
        plazas_metas = {'LIMA': 0, 'NORTE': 0, 'OTROS': 0}
        for mes in meses_activos:
            for sup, meta in MESES_CONFIG.get(mes, {}).get('metas', {}).items():
                if sup == 'WINNIE':
                    continue
                zona = ZONAS_MAP.get(sup, 'OTROS')
                region = 'LIMA' if zona == 'LIMA' else ('NORTE' if zona in NORTE else 'OTROS')
                plazas_metas[region] += meta
        res['META OBJETIVO'] = [plazas_metas.get(p, 0) for p in res.index]
    res['AVANCE'] = (res['TOTAL DESEMBOLSO'] / res['META OBJETIVO'] * 100).fillna(0)
    res['Q POR INGRESAR'] = g(pc, 'POR INGRESAR')
    res['Q EVALUACION BCP'] = g(pc, 'EN EVALUACION BCP')
    res['Q PENDIENTE DE BACK'] = g(pc, 'PENDIENTE DE BACK OFFICE')
    tot = res.sum(numeric_only=True)
    if group_col == 'SUPERVISOR': tot['ZONA'] = ''
    tot['AVANCE'] = (tot['TOTAL DESEMBOLSO'] / tot['META OBJETIVO'] * 100) if tot['META OBJETIVO'] > 0 else 0
    res.loc['TOTAL'] = tot
    return res.reset_index()

# Usamos filtered_df que ya tiene el filtro de mes aplicado desde arriba
m_df = filtered_df
df_super = build_matrix(m_df, 'SUPERVISOR', selected_mes)

def build_plaza_matrix(data, meses_activos):
    if data.empty: return pd.DataFrame()
    data = data.copy()
    data['PLAZA'] = data['REGION']
    return build_matrix(data, 'PLAZA', meses_activos)

df_plaza = build_plaza_matrix(m_df, selected_mes)


cc = {
    "TOTAL DESEMBOLSO": st.column_config.NumberColumn("Total Desembolso", format="S/ %,.0f"),
    "APROBADA": st.column_config.NumberColumn("Aprobada", format="S/ %,.0f"),
    "POR INGRESAR": st.column_config.NumberColumn("Por Ingresar", format="S/ %,.0f"),
    "EVALUACION BCP": st.column_config.NumberColumn("Eval. BCP", format="S/ %,.0f"),
    "PENDIENTE DE BACK": st.column_config.NumberColumn("Pend. Back", format="S/ %,.0f"),
    "PENDIENTE DE REMESA": st.column_config.NumberColumn("Pend. Remesa", format="S/ %,.0f"),
    "META OBJETIVO": st.column_config.NumberColumn("Meta", format="S/ %,.0f"),
    "AVANCE": st.column_config.ProgressColumn("Avance", format="%.1f%%", min_value=0, max_value=100),
    "Q DESEMBOLSO": st.column_config.NumberColumn("Q Desemb.", format="%,.0f"),
    "Q POR INGRESAR": st.column_config.NumberColumn("Q Ingr.", format="%,.0f"),
    "Q EVALUACION BCP": st.column_config.NumberColumn("Q Eval.", format="%,.0f"),
    "Q PENDIENTE DE BACK": st.column_config.NumberColumn("Q Back", format="%,.0f"),
}

tab1, tab2 = st.tabs(["Por Supervisor", "Por Plaza"])

def color_total_row(row):
    is_total = any(str(val).upper() == 'TOTAL' for val in row.values)
    return ['background-color: #FFEDD5; font-weight: 700;' if is_total else '' for _ in row]

with tab1:
    if not df_super.empty: 
        st.dataframe(df_super.style.apply(color_total_row, axis=1), use_container_width=True, hide_index=True, column_config=cc)
        st.markdown(create_download_link(df_super, "Gestion_Supervisor.xlsx", "Exportar Supervisor"), unsafe_allow_html=True)
with tab2:
    if not df_plaza.empty: 
        st.dataframe(df_plaza.style.apply(color_total_row, axis=1), use_container_width=True, hide_index=True, column_config=cc)
        st.markdown(create_download_link(df_plaza, "Gestion_Plaza.xlsx", "Exportar Plaza"), unsafe_allow_html=True)

# --- DETALLE ---
st.markdown("""<div class="section-header">
    <div class="section-icon"><svg viewBox="0 0 24 24"><path d="M4 6h16v2H4zm0 5h16v2H4zm0 5h16v2H4z"/></svg></div>
    <span class="section-label">Detalle de Operaciones</span>
</div>""", unsafe_allow_html=True)

with st.expander("Detalle detallado por estado", expanded=True):
    # Limpieza de columnas para el detalle
    bad_cols = ['MAF NETO_Num', 'ZONA_SUP', 'REGION', 'PLAZA DE VENTA', 'FECHA FILTRO', 'FECHA DE INGRESO', 'FECHA DE DESEMBOLSO']
    show_df = filtered_df.copy()
    show_df = show_df.loc[:, ~show_df.columns.str.contains('^Unnamed')]
    show_df = show_df.drop(columns=[c for c in bad_cols if c in show_df.columns])
    
    # Crear lista de estados únicos (excluyendo vacíos)
    estados_raw = sorted([e for e in show_df['ESTADO LIMPIO'].unique() if e != 'SIN ESTADO'])
    
    # "Todos" + Estados en formato Nombre Propio
    tabs_nombres = ["Todos"] + [e.title() for e in estados_raw]
    
    # Crear las pestañas
    tabs_detalle = st.tabs(tabs_nombres)
    
    for i, tab in enumerate(tabs_detalle):
        with tab:
            nombre_tab = tabs_nombres[i]
            if nombre_tab == "Todos":
                df_tab = show_df
            else:
                # Buscamos el estado original (en mayúsculas) para filtrar correctamente
                estado_original = estados_raw[i-1] 
                df_tab = show_df[show_df['ESTADO LIMPIO'] == estado_original]
            
            if not df_tab.empty:
                st.dataframe(df_tab, use_container_width=True, hide_index=True)
                st.markdown(create_download_link(df_tab, f"Detalle_{nombre_tab.replace(' ', '_')}.xlsx", f"Exportar {nombre_tab}"), unsafe_allow_html=True)
            else:
                st.info(f"No hay operaciones en estado: {nombre_tab}")

