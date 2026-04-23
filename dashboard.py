import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de página
st.set_page_config(page_title="Dashboard Fuvex", layout="wide", page_icon="📊")
st.title("📊 Panel de Control - Rendimiento Fuvex")
st.markdown("Dashboard interactivo conectado en tiempo real a Google Sheets.")

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

with st.spinner('Cargando datos en tiempo real...'):
    df = load_data()

# Filtros (Sidebar)
st.sidebar.header("Filtros")
supervisor_list = df['SUPERVISOR'].dropna().unique().tolist()
selected_supervisor = st.sidebar.multiselect("Supervisor", supervisor_list, default=supervisor_list)

estado_list = df['ESTADO LIMPIO'].dropna().unique().tolist()
selected_estado = st.sidebar.multiselect("Estado", estado_list, default=estado_list)

# Aplicar filtros
filtered_df = df[
    (df['SUPERVISOR'].isin(selected_supervisor)) & 
    (df['ESTADO LIMPIO'].isin(selected_estado))
]

# 3. KPIs
st.markdown("### 📈 Métricas Clave")
col1, col2, col3 = st.columns(3)
monto_total = filtered_df['MAF NETO_Num'].sum()
cantidad_ops = len(filtered_df)
monto_promedio = filtered_df['MAF NETO_Num'].mean() if cantidad_ops > 0 else 0

col1.metric("Monto Total", f"S/ {monto_total:,.2f}")
col2.metric("Cantidad de Operaciones", f"{cantidad_ops}")
col3.metric("Monto Promedio por Op.", f"S/ {monto_promedio:,.2f}")

st.divider()

# 4. Gráficos
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### Ventas Totales por Supervisor")
    ventas_super = filtered_df.groupby('SUPERVISOR')['MAF NETO_Num'].sum().reset_index()
    fig1 = px.bar(ventas_super, x='SUPERVISOR', y='MAF NETO_Num', color='SUPERVISOR', text_auto='.2s')
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.markdown("#### Distribución de Estados")
    estados_dist = filtered_df['ESTADO LIMPIO'].value_counts().reset_index()
    estados_dist.columns = ['ESTADO LIMPIO', 'Cantidad']
    fig2 = px.pie(estados_dist, names='ESTADO LIMPIO', values='Cantidad', hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("#### Desempeño por Convenio")
ventas_conv = filtered_df.groupby('CONVENIO')['MAF NETO_Num'].sum().reset_index()
fig3 = px.bar(ventas_conv, x='CONVENIO', y='MAF NETO_Num', color='CONVENIO', text_auto='.2s')
st.plotly_chart(fig3, use_container_width=True)

# Mostrar Tabla de datos original (opcional)
if st.checkbox("Mostrar tabla de datos"):
    st.dataframe(filtered_df)
