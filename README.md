# 📊 Automatización Looker - Centro de Operaciones A365 BCP

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)

Este repositorio contiene la solución de **Business Intelligence** diseñada para **Impulsa365**, enfocada en el monitoreo en tiempo real de las operaciones financieras del **Banco de Crédito del Perú (BCP)**. El sistema transforma datos crudos de Google Sheets en un tablero de control ejecutivo con KPIs críticos y análisis de rendimiento.

---

## 🚀 Funcionalidades Clave

- **📈 Monitoreo de KPIs en Tiempo Real:** Visualización instantánea de Desembolso Total, Avance vs Meta, Ticket Promedio y Volumen de Operaciones.
- **🎯 Metas Dinámicas:** Sistema inteligente que calcula el cumplimiento de objetivos segmentado por Supervisor y Región (LIMA, NORTE, OTROS).
- **📉 Análisis Visual Avanzado:**
  - Funnel de conversión por estado de operación.
  - Distribución geográfica de ventas.
  - Ranking de rendimiento de ejecutivos y supervisores.
- **📂 Gestión de Datos Detallada:** Interfaz de pestañas (Tabs) para explorar el detalle de operaciones por estado con filtros dinámicos.
- **📥 Exportación Premium:** Botones personalizados para exportar reportes detallados directamente a formatos Excel (XLSX) con un solo clic.

---

## 🛠️ Stack Tecnológico

| Componente | Herramienta |
| :--- | :--- |
| **Framework UI** | [Streamlit](https://streamlit.io/) |
| **Procesamiento de Datos** | [Pandas](https://pandas.pydata.org/) |
| **Visualización** | [Plotly Graph Objects](https://plotly.com/python/) |
| **Data Source** | Google Sheets (vía CSV Export) |
| **Exportación** | XlsxWriter |

---

## 💻 Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/fmendoza-a365/AutomatizacionLooker.git
   cd AutomatizacionLooker
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   ```bash
   streamlit run dashboard.py
   ```

---

## 🏗️ Arquitectura de la Solución

El tablero utiliza una capa de **CSS personalizado** para garantizar una experiencia de usuario (UX) premium, siguiendo la línea gráfica corporativa. La lógica de negocio está centralizada en `dashboard.py`, que maneja desde la limpieza de datos (Data Wrangling) hasta la renderización de componentes dinámicos.

---

## 👤 Autor
**Franco Alonzo Mendoza Salazar**
*Data & Systems Architect @ Impulsa365*
- [LinkedIn](https://www.linkedin.com/in/fmendoza-a365/)
- [GitHub](https://github.com/fmendoza-a365)

---
<div align="center">
  <sub>Construido con ❤️ para la optimización de procesos financieros.</sub>
</div>
