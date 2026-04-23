import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de página
st.set_page_config(page_title="Rendimiento Fuvex", layout="wide", page_icon="📊")

# INYECCIÓN DE CSS LIGERA (Polish: Solo tipografía y ajustes menores, sin romper layout nativo)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    /* Tipografía Global */
    html, body, [class*="css"]  {
        font-family: 'Manrope', sans-serif !important;
        color: #1D1D1F;
    }
    
    /* Ocultar elementos por defecto de Streamlit (hamburger y footer) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Reducir el padding superior agresivo de Streamlit */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }

    /* Títulos de sección */
    h1, h2, h3, h4 {
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
        color: #002A8D !important;
    }
    
    h1 {
        font-size: 32px !important;
        margin-bottom: 0px !important;
    }
    
    .subtitle {
        font-size: 16px;
        color: #6E6E73;
        margin-bottom: 24px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.title("Rendimiento Operativo")
st.markdown('<p class="subtitle">Panel de Gestión Integral - Fuvex BCP</p>', unsafe_allow_html=True)

# 2. Conexión a datos
@st.cache_data(ttl=300)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/16PzK230jtrjkpHYq5mYSFrdeXk-0B6N7/export?format=csv&gid=305780908"
    df = pd.read_csv(url)
    
    # Limpieza de 'MAF NETO'
    if 'MAF NETO' in df.columns:
        df['MAF NETO'] = df['MAF NETO'].fillna("0")
        df['MAF NETO_Num'] = df['MAF NETO'].str.replace('S/', '', regex=False).str.strip()
        df['MAF NETO_Num'] = df['MAF NETO_Num'].str.replace('.', '', regex=False)
        df['MAF NETO_Num'] = df['MAF NETO_Num'].str.replace(',', '.', regex=False)
        df['MAF NETO_Num'] = pd.to_numeric(df['MAF NETO_Num'], errors='coerce').fillna(0)
    
    # Rellenar vacíos en categorías
    df['SUPERVISOR'] = df['SUPERVISOR'].fillna('SIN SUPERVISOR')
    df['PLAZA DE VENTA'] = df['PLAZA DE VENTA'].fillna('SIN PLAZA')
    df['ESTADO LIMPIO'] = df['ESTADO LIMPIO'].fillna('SIN ESTADO')
    
    return df

with st.spinner('Sincronizando base de datos...'):
    df = load_data()

# Filtros Globales (Barra Superior para dejar más espacio al dashboard)
st.markdown("### 🎛️ Filtros Globales")
col_f1, col_f2 = st.columns(2)
supervisor_list = df['SUPERVISOR'].unique().tolist()
selected_supervisor = col_f1.multiselect("Filtrar por Supervisor", supervisor_list, default=supervisor_list)

estado_list = df['ESTADO LIMPIO'].unique().tolist()
selected_estado = col_f2.multiselect("Filtrar por Estado", estado_list, default=estado_list)

# Aplicar filtros
filtered_df = df[
    (df['SUPERVISOR'].isin(selected_supervisor)) & 
    (df['ESTADO LIMPIO'].isin(selected_estado))
]

st.divider()

# Paleta Corporativa BCP
bcp_colors = ["#FF7A00", "#002A8D", "#00A4E4", "#FFB300", "#001B5A", "#4A4A4A"]

# --- LÓGICA DE TABLAS DINÁMICAS (MATRIZ) ---
def build_matrix(data, group_col):
    if data.empty:
        return pd.DataFrame()
        
    pivot_sum = data.pivot_table(index=group_col, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='sum', fill_value=0)
    pivot_count = data.pivot_table(index=group_col, columns='ESTADO LIMPIO', values='MAF NETO_Num', aggfunc='count', fill_value=0)
    
    res = pd.DataFrame(index=pivot_sum.index)
    
    if group_col == 'SUPERVISOR':
        # Asignar la zona más frecuente (moda) al supervisor
        res['ZONA'] = data.groupby('SUPERVISOR')['PLAZA DE VENTA'].agg(lambda x: x.mode()[0] if not x.mode().empty else 'N/A')
        
    def get_val(df_pivot, col):
        return df_pivot[col] if col in df_pivot.columns else 0

    res['TOTAL DESEMBOLSO'] = get_val(pivot_sum, 'DESEMBOLSADO')
    res['Q DESEMBOLSO'] = get_val(pivot_count, 'DESEMBOLSADO')
    res['APROBADA'] = get_val(pivot_sum, 'APROBADA')
    res['POR INGRESAR'] = get_val(pivot_sum, 'POR INGRESAR')
    res['EVALUACION BCP'] = get_val(pivot_sum, 'EN EVALUACION BCP')
    res['PENDIENTE DE BACK'] = get_val(pivot_sum, 'PENDIENTE DE BACK OFFICE')
    res['PENDIENTE DE REMESA'] = get_val(pivot_sum, 'PENDIENTE DE REMESA')
    
    # Usaremos una meta referencial por ahora
    res['META OBJETIVO'] = 1000000.00
    res['AVANCE'] = (res['TOTAL DESEMBOLSO'] / res['META OBJETIVO']).fillna(0)
    
    res['Q POR INGRESAR'] = get_val(pivot_count, 'POR INGRESAR')
    res['Q EVALUACION BCP'] = get_val(pivot_count, 'EN EVALUACION BCP')
    res['Q PENDIENTE DE BACK'] = get_val(pivot_count, 'PENDIENTE DE BACK OFFICE')
    
    # Fila de Totales
    total_row = res.sum(numeric_only=True)
    if group_col == 'SUPERVISOR':
        total_row['ZONA'] = ''
    
    total_row['AVANCE'] = (total_row['TOTAL DESEMBOLSO'] / total_row['META OBJETIVO']) if total_row['META OBJETIVO'] > 0 else 0
    res.loc['TOTAL'] = total_row
    
    return res.reset_index()

# Construir matrices con TODOS los datos (sin filtro de estado, porque la matriz ya desglosa por estado)
matrix_df = df[df['SUPERVISOR'].isin(selected_supervisor)] # Solo filtramos por supervisor
df_super = build_matrix(matrix_df, 'SUPERVISOR')
df_plaza = build_matrix(matrix_df, 'PLAZA DE VENTA')

# --- CONFIGURACIÓN DE COLUMNAS PARA DATA_EDITOR ---
# Esto permite renderizar monedas, porcentajes y resaltar con colores (como en Excel)
column_config = {
    "TOTAL DESEMBOLSO": st.column_config.NumberColumn("TOTAL DESEMBOLSO", format="S/ %d"),
    "APROBADA": st.column_config.NumberColumn("APROBADA", format="S/ %d"),
    "POR INGRESAR": st.column_config.NumberColumn("POR INGRESAR", format="S/ %d"),
    "EVALUACION BCP": st.column_config.NumberColumn("EVALUACION BCP", format="S/ %d"),
    "PENDIENTE DE BACK": st.column_config.NumberColumn("PENDIENTE DE BACK", format="S/ %d"),
    "PENDIENTE DE REMESA": st.column_config.NumberColumn("PENDIENTE DE REMESA", format="S/ %d"),
    "META OBJETIVO": st.column_config.NumberColumn("META OBJETIVO", format="S/ %d"),
    "AVANCE": st.column_config.ProgressColumn("AVANCE", format="%.2f%%", min_value=0, max_value=1.0),
    "Q DESEMBOLSO": st.column_config.NumberColumn("Q DESEMBOLSO", format="%d"),
    "Q POR INGRESAR": st.column_config.NumberColumn("Q POR ING.", format="%d"),
    "Q EVALUACION BCP": st.column_config.NumberColumn("Q EVAL.", format="%d"),
    "Q PENDIENTE DE BACK": st.column_config.NumberColumn("Q BACK", format="%d")
}

st.markdown("### 📋 Vista Por Supervisor")
if not df_super.empty:
    st.dataframe(df_super, use_container_width=True, hide_index=True, column_config=column_config)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🏢 Vista Por Plaza")
if not df_plaza.empty:
    st.dataframe(df_plaza, use_container_width=True, hide_index=True, column_config=column_config)

st.divider()

# --- GRÁFICOS Y KPIs (Con data filtrada completa) ---
st.markdown("### 📈 Análisis Gráfico")

col1, col2, col3 = st.columns(3)
monto_total = filtered_df['MAF NETO_Num'].sum()
cantidad_ops = len(filtered_df)
monto_promedio = filtered_df['MAF NETO_Num'].mean() if cantidad_ops > 0 else 0

col1.metric("Volumen Total", f"S/ {monto_total:,.2f}")
col2.metric("Operaciones", f"{cantidad_ops:,}")
col3.metric("Ticket Promedio", f"S/ {monto_promedio:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

def clean_plotly_layout(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Manrope", color="#1D1D1F"),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,42,141,0.05)', zeroline=False)
    return fig

with col_a:
    st.markdown("#### Volumen por Supervisor")
    ventas_super = filtered_df.groupby('SUPERVISOR')['MAF NETO_Num'].sum().reset_index()
    ventas_super = ventas_super.sort_values('MAF NETO_Num', ascending=True)
    
    fig1 = px.bar(ventas_super, y='SUPERVISOR', x='MAF NETO_Num', color='SUPERVISOR', 
                  color_discrete_sequence=bcp_colors, text_auto='.2s', orientation='h')
    fig1.update_traces(textposition='outside')
    fig1 = clean_plotly_layout(fig1)
    fig1.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.markdown("#### Composición de Estados")
    estados_dist = filtered_df['ESTADO LIMPIO'].value_counts().reset_index()
    estados_dist.columns = ['ESTADO LIMPIO', 'Cantidad']
    
    fig2 = px.pie(estados_dist, names='ESTADO LIMPIO', values='Cantidad', hole=0.55,
                  color_discrete_sequence=bcp_colors)
    fig2 = clean_plotly_layout(fig2)
    fig2.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)
