import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(layout="wide", page_title="Cotizador BCP")

# Ocultar elementos de Streamlit para que parezca una web independiente
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0;}
    iframe {border: none;}
    </style>
""", unsafe_allow_html=True)

# Leer y mostrar el HTML
file_path = "bcp_convenios_banner_recontrafinal.html"
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Renderizar el HTML en un componente que ocupe todo el ancho
    components.html(html_content, height=1200, scrolling=True)
else:
    st.error("No se encontró el archivo de cotización.")
