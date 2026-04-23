import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de página
st.set_page_config(page_title="Rendimiento Fuvex", layout="wide", page_icon="📊")

# INYECCIÓN DE CSS (Metodología Impeccable)
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
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* Estilos Premium para los KPIs */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 42, 141, 0.05); /* Sombra con tinte azul institucional */
        border: 1px solid rgba(0, 42, 141, 0.05);
        transition: transform 0.2s ease-out;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 42, 141, 0.08);
    }

    /* Etiqueta del KPI */
    div[data-testid="stMetricLabel"] p {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #002A8D !important; /* Azul BCP */
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Valor Numérico del KPI */
    div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #1D1D1F !important;
        margin-top: 8px !important;
    }

    /* Títulos de sección */
    h1, h2, h3, h4 {
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
        color: #002A8D !important;
    }
    
    h1 {
        font-size: 36px !important;
        margin-bottom: 8px !important;
    }
    
    .subtitle {
        font-size: 16px;
        color: #6E6E73;
        margin-bottom: 32px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.title("Rendimiento Operativo")
st.markdown('<p class="subtitle">Visión general en tiempo real de operaciones Fuvex</p>', unsafe_allow_html=True)

# 2. Conexión a datos (Cache para no saturar la red en cada clic)
@st.cache_data(ttl=300) # Se refresca cada 5 minutos
def load_data():
    url = "https://docs.google.com/spreadsheets/d/16PzK230jtrjkpHYq5mYSFrdeXk-0B6N7/export?format=csv&gid=305780908"
    df = pd.read_csv(url)
    
    # Limpieza: Convertir 'MAF NETO' de string a float
    # Ej: "S/  76.900,00 " -> 76900.00
    if 'MAF NETO' in df.columns:
        # Rellenar vacíos
        df['MAF NETO'] = df['MAF NETO'].fillna("0")
        # Quitar símbolos S/ y espacios
        df['MAF NETO_Num'] = df['MAF NETO'].str.replace('S/', '', regex=False).str.strip()
        # Quitar puntos de miles
        df['MAF NETO_Num'] = df['MAF NETO_Num'].str.replace('.', '', regex=False)
        # Cambiar coma de decimal por punto
        df['MAF NETO_Num'] = df['MAF NETO_Num'].str.replace(',', '.', regex=False)
        # Convertir a float
        df['MAF NETO_Num'] = pd.to_numeric(df['MAF NETO_Num'], errors='coerce').fillna(0)
    
    return df

with st.spinner('Sincronizando base de datos...'):
    df = load_data()

# Filtros (Sidebar)
st.sidebar.markdown("### 🎛️ Filtros Activos")
st.sidebar.markdown("---")
supervisor_list = df['SUPERVISOR'].dropna().unique().tolist()
selected_supervisor = st.sidebar.multiselect("Supervisor", supervisor_list, default=supervisor_list)

estado_list = df['ESTADO LIMPIO'].dropna().unique().tolist()
selected_estado = st.sidebar.multiselect("Estado", estado_list, default=estado_list)

# Aplicar filtros
filtered_df = df[
    (df['SUPERVISOR'].isin(selected_supervisor)) & 
    (df['ESTADO LIMPIO'].isin(selected_estado))
]

# Paleta Corporativa BCP
bcp_colors = ["#FF7A00", "#002A8D", "#00A4E4", "#FFB300", "#001B5A", "#4A4A4A"]

# 3. KPIs
col1, col2, col3 = st.columns(3)
monto_total = filtered_df['MAF NETO_Num'].sum()
cantidad_ops = len(filtered_df)
monto_promedio = filtered_df['MAF NETO_Num'].mean() if cantidad_ops > 0 else 0

col1.metric("Volumen Total", f"S/ {monto_total:,.2f}")
col2.metric("Operaciones", f"{cantidad_ops:,}")
col3.metric("Ticket Promedio", f"S/ {monto_promedio:,.2f}")

st.markdown("<br><br>", unsafe_allow_html=True)

# 4. Gráficos
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
    st.markdown("#### Distribución de Volumen por Supervisor")
    ventas_super = filtered_df.groupby('SUPERVISOR')['MAF NETO_Num'].sum().reset_index()
    # Ordenar para mejor visualización
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

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### Rendimiento por Convenio")
ventas_conv = filtered_df.groupby('CONVENIO')['MAF NETO_Num'].sum().reset_index()
ventas_conv = ventas_conv.sort_values('MAF NETO_Num', ascending=False)

fig3 = px.bar(ventas_conv, x='CONVENIO', y='MAF NETO_Num', color='CONVENIO', 
              color_discrete_sequence=bcp_colors, text_auto='.2s')
fig3 = clean_plotly_layout(fig3)
fig3.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
# Mostrar Tabla de datos original (opcional)
with st.expander("Ver datos en crudo"):
    st.dataframe(filtered_df, use_container_width=True)
