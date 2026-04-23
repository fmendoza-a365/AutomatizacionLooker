import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from pathlib import Path

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="A365 BCP - Centro de Operaciones",
    layout="wide",
    page_icon="isotipobcp.png"
)

# --- LOAD LOGO AS BASE64 ---
def get_base64_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

logo_b64 = get_base64_image("A366BCP.png")
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:48px;">' if logo_b64 else '<span style="font-weight:800;font-size:24px;color:#002A8D;">A365 BCP</span>'

# --- CSS PROFESIONAL ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,1,0');

    html, body, [class*="css"] {{
        font-family: 'Manrope', sans-serif !important;
    }}

    #MainMenu, footer, header {{visibility: hidden;}}

    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 1rem !important;
        max-width: 1400px;
    }}

    /* --- TOPBAR --- */
    .topbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 0;
        border-bottom: 1px solid #E8E8ED;
        margin-bottom: 24px;
    }}
    .topbar-left {{
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    .topbar-title {{
        font-size: 14px;
        font-weight: 600;
        color: #6E6E73;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }}
    .topbar-right {{
        font-size: 13px;
        color: #8E8E93;
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    /* --- SECTION HEADERS --- */
    .section-header {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 32px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #002A8D;
    }}
    .section-header .material-symbols-rounded {{
        font-size: 22px;
        color: #FF7A00;
    }}
    .section-header span:last-child {{
        font-size: 16px;
        font-weight: 700;
        color: #002A8D;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }}

    /* --- KPI CARDS --- */
    .kpi-row {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 28px;
    }}
    .kpi-card {{
        background: #FFFFFF;
        border: 1px solid #E8E8ED;
        border-radius: 10px;
        padding: 20px 24px;
        position: relative;
        overflow: hidden;
    }}
    .kpi-card::after {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #FF7A00, #FFB300);
    }}
    .kpi-label {{
        font-size: 11px;
        font-weight: 700;
        color: #8E8E93;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }}
    .kpi-label .material-symbols-rounded {{
        font-size: 16px;
        color: #FF7A00;
    }}
    .kpi-value {{
        font-size: 28px;
        font-weight: 800;
        color: #1D1D1F;
        letter-spacing: -0.5px;
    }}
    .kpi-sub {{
        font-size: 12px;
        color: #8E8E93;
        margin-top: 4px;
    }}

    /* --- STREAMLIT OVERRIDES --- */
    h1, h2, h3, h4 {{
        font-weight: 700 !important;
        color: #002A8D !important;
        letter-spacing: -0.01em !important;
    }}

    div[data-testid="stMetricLabel"] {{ display: none; }}
    div[data-testid="stMetricValue"] {{ display: none; }}

    /* Clean dataframe */
    div[data-testid="stDataFrame"] {{
        border: 1px solid #E8E8ED;
        border-radius: 10px;
        overflow: hidden;
    }}
</style>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,1,0">
""", unsafe_allow_html=True)

# --- TOPBAR ---
from datetime import datetime
now = datetime.now().strftime("%d/%m/%Y  %H:%M")
st.markdown(f"""
<div class="topbar">
    <div class="topbar-left">
        {logo_html}
        <span class="topbar-title">Centro de Operaciones</span>
    </div>
    <div class="topbar-right">
        <span class="material-symbols-rounded" style="font-size:16px;">schedule</span>
        Actualizado: {now}
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
    df['PLAZA DE VENTA'] = df['PLAZA DE VENTA'].fillna('SIN PLAZA')
    df['ESTADO LIMPIO'] = df['ESTADO LIMPIO'].fillna('SIN ESTADO')
    df['CONVENIO'] = df['CONVENIO'].fillna('SIN CONVENIO')
    # Limpiar espacios extras en categorías
    df['PLAZA DE VENTA'] = df['PLAZA DE VENTA'].str.strip()
    df['CONVENIO'] = df['CONVENIO'].str.strip().str.upper()
    return df

with st.spinner('Conectando con la base de datos...'):
    df = load_data()

# --- FILTROS ---
st.markdown("""
<div class="section-header">
    <span class="material-symbols-rounded">filter_alt</span>
    <span>Filtros</span>
</div>
""", unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)
supervisor_list = sorted(df['SUPERVISOR'].unique().tolist())
selected_supervisor = col_f1.multiselect("Supervisor", supervisor_list, default=supervisor_list)
estado_list = sorted(df['ESTADO LIMPIO'].unique().tolist())
selected_estado = col_f2.multiselect("Estado", estado_list, default=estado_list)
convenio_list = sorted(df['CONVENIO'].unique().tolist())
selected_convenio = col_f3.multiselect("Convenio", convenio_list, default=convenio_list)

filtered_df = df[
    (df['SUPERVISOR'].isin(selected_supervisor)) &
    (df['ESTADO LIMPIO'].isin(selected_estado)) &
    (df['CONVENIO'].isin(selected_convenio))
]

# --- KPIs ---
monto_total = filtered_df['MAF NETO_Num'].sum()
cantidad_ops = len(filtered_df)
monto_promedio = filtered_df['MAF NETO_Num'].mean() if cantidad_ops > 0 else 0
n_supervisores = filtered_df['SUPERVISOR'].nunique()

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card">
        <div class="kpi-label"><span class="material-symbols-rounded">payments</span>Volumen Total</div>
        <div class="kpi-value">S/ {monto_total:,.0f}</div>
        <div class="kpi-sub">Monto acumulado neto</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label"><span class="material-symbols-rounded">receipt_long</span>Operaciones</div>
        <div class="kpi-value">{cantidad_ops:,}</div>
        <div class="kpi-sub">Total de registros</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label"><span class="material-symbols-rounded">avg_pace</span>Ticket Promedio</div>
        <div class="kpi-value">S/ {monto_promedio:,.0f}</div>
        <div class="kpi-sub">Promedio por operacion</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label"><span class="material-symbols-rounded">groups</span>Supervisores</div>
        <div class="kpi-value">{n_supervisores}</div>
        <div class="kpi-sub">Equipos activos</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- PALETA ---
bcp_colors = ["#FF7A00", "#002A8D", "#00A4E4", "#FFB300", "#001B5A", "#6E6E73", "#D4380D", "#389E0D"]

def clean_plotly(fig, height=380):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Manrope", color="#1D1D1F", size=12),
        margin=dict(l=0, r=16, t=32, b=0),
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5, font=dict(size=11))
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=11))
    fig.update_yaxes(showgrid=True, gridcolor='#F0F0F5', zeroline=False, tickfont=dict(size=11))
    return fig

# --- GRÁFICOS ---
st.markdown("""
<div class="section-header">
    <span class="material-symbols-rounded">monitoring</span>
    <span>Analisis Grafico</span>
</div>
""", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### Volumen por Supervisor")
    v_sup = filtered_df.groupby('SUPERVISOR')['MAF NETO_Num'].sum().reset_index().sort_values('MAF NETO_Num', ascending=True)
    fig1 = px.bar(v_sup, y='SUPERVISOR', x='MAF NETO_Num', color='SUPERVISOR',
                  color_discrete_sequence=bcp_colors, text_auto='.2s', orientation='h')
    fig1.update_traces(textposition='outside')
    fig1 = clean_plotly(fig1)
    fig1.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.markdown("#### Composicion de Estados")
    e_dist = filtered_df['ESTADO LIMPIO'].value_counts().reset_index()
    e_dist.columns = ['ESTADO LIMPIO', 'Cantidad']
    fig2 = px.pie(e_dist, names='ESTADO LIMPIO', values='Cantidad', hole=0.55,
                  color_discrete_sequence=bcp_colors)
    fig2 = clean_plotly(fig2)
    fig2.update_traces(textposition='inside', textinfo='percent+label',
                       marker=dict(line=dict(color='#FFFFFF', width=2)))
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

# --- TABLAS DINÁMICAS ---
st.markdown("""
<div class="section-header">
    <span class="material-symbols-rounded">table_chart</span>
    <span>Tablas de Gestion</span>
</div>
""", unsafe_allow_html=True)

def build_matrix(data, group_col):
    if data.empty:
        return pd.DataFrame()
    pivot_sum = data.pivot_table(index=group_col, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='sum', fill_value=0)
    pivot_count = data.pivot_table(index=group_col, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='count', fill_value=0)
    res = pd.DataFrame(index=pivot_sum.index)
    if group_col == 'SUPERVISOR':
        res['ZONA'] = data.groupby('SUPERVISOR')['PLAZA DE VENTA'].agg(lambda x: x.mode()[0] if not x.mode().empty else 'N/A')
    def g(p, c):
        return p[c] if c in p.columns else 0
    res['TOTAL DESEMBOLSO'] = g(pivot_sum, 'DESEMBOLSADO')
    res['Q DESEMBOLSO'] = g(pivot_count, 'DESEMBOLSADO')
    res['APROBADA'] = g(pivot_sum, 'APROBADA')
    res['POR INGRESAR'] = g(pivot_sum, 'POR INGRESAR')
    res['EVALUACION BCP'] = g(pivot_sum, 'EN EVALUACION BCP')
    res['PENDIENTE DE BACK'] = g(pivot_sum, 'PENDIENTE DE BACK OFFICE')
    res['PENDIENTE DE REMESA'] = g(pivot_sum, 'PENDIENTE DE REMESA')
    res['META OBJETIVO'] = 1000000.00
    res['AVANCE'] = (res['TOTAL DESEMBOLSO'] / res['META OBJETIVO']).fillna(0)
    res['Q POR INGRESAR'] = g(pivot_count, 'POR INGRESAR')
    res['Q EVALUACION BCP'] = g(pivot_count, 'EN EVALUACION BCP')
    res['Q PENDIENTE DE BACK'] = g(pivot_count, 'PENDIENTE DE BACK OFFICE')
    total_row = res.sum(numeric_only=True)
    if group_col == 'SUPERVISOR':
        total_row['ZONA'] = ''
    total_row['AVANCE'] = (total_row['TOTAL DESEMBOLSO'] / total_row['META OBJETIVO']) if total_row['META OBJETIVO'] > 0 else 0
    res.loc['TOTAL'] = total_row
    return res.reset_index()

matrix_df = df[df['SUPERVISOR'].isin(selected_supervisor) & df['CONVENIO'].isin(selected_convenio)]
df_super = build_matrix(matrix_df, 'SUPERVISOR')
df_plaza = build_matrix(matrix_df, 'PLAZA DE VENTA')

col_config = {
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
    if not df_super.empty:
        st.dataframe(df_super, use_container_width=True, hide_index=True, column_config=col_config)
with tab2:
    if not df_plaza.empty:
        st.dataframe(df_plaza, use_container_width=True, hide_index=True, column_config=col_config)

# --- DETALLE ---
st.markdown("""
<div class="section-header">
    <span class="material-symbols-rounded">database</span>
    <span>Detalle de Operaciones</span>
</div>
""", unsafe_allow_html=True)

with st.expander("Expandir tabla de datos completa"):
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
