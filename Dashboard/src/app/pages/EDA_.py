# File: EDA_.py
# Author: victo
# Copyright: 2024, Smart Cities Peru.
# License: MIT
#
# Purpose:
# This is the entry point for the application.
#
# Last Modified: 2024-05-03

# ==========================================  Importaciones de bibliotecas ==================================

import streamlit as st
import plotly.express as px
import pandas as pd
import seaborn as sns
import altair as alt
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from streamlit_extras.dataframe_explorer import dataframe_explorer
import calendar

# ==========================================  Configurar la página ==================================================
st.set_page_config(
    page_title="Análisis Exploratorio de Datos (EDA)",
    page_icon=":bar_chart:",
    layout="wide"
)
# ==================================================================================================================
# Cargar el componente de BannerPersonalizado.html
with open("./utils/Baner.html", "r", encoding="utf-8") as file:
    custom_banner_html = file.read()

# Agregar estilos CSS desde la carpeta utils
with open("./utils/Baner_style.css", "r", encoding="utf-8") as file:
    custom_styles_css = file.read()
# Mostrar el componente de Banner en Streamlit con los estilos CSS
st.markdown("""
    <style>
        %s
    </style>
""" % custom_styles_css, unsafe_allow_html=True)
st.markdown(custom_banner_html, unsafe_allow_html=True)

# ==========================================  Titulo de la Pagina ======================================================
st.markdown("## :bar_chart: Análisis Exploratorio de Datos (EDA) 👋")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# ================================================  Cargar Datos  ======================================================
# Leer el conjunto de datos por defecto
df = pd.read_excel("data/Melsol-test.xlsx", engine="openpyxl")

#  =========================================== Sidebar para realzar de los Filtros  =========================
# Definir nombres de los meses en español
meses_espanol = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}

#  =========================================== Sidebar para realzar de los Filtros  =========================
st.sidebar.header("Configuración de Filtros:")

#  =========================================== POR MES  =========================
st.sidebar.subheader("Filtrar por Mes")
# Widget para seleccionar el mes
meses_seleccionados = st.sidebar.multiselect("Seleccionar Meses",
                                             list(meses_espanol.values()),
                                             default=list(meses_espanol.values()))
# Convertir los nombres de los meses seleccionados a números
meses = [list(meses_espanol.keys())[list(meses_espanol.values()).index(mes)] for mes in meses_seleccionados]

# Filtrar el DataFrame por los meses seleccionados
if meses:
    df = df[df["MES"].isin(meses)]

#  =========================================== POR RANGO DE PRODUCTOS ALMACENADOS =========================
st.sidebar.subheader("Filtrar por rango de Productos Almacenados")
# Obtener el valor máximo de la columna "PRODUCTOS ALMACENADOS"
max_productos_almacenados = df["PRODUCTOS ALMACENADOS"].max()
# Widget para filtrar por rango de Productos Almacenados
almacenados_range = st.sidebar.slider("Filtrar por Rango de Productos Almacenados",
                                      min_value=0,
                                      max_value=max_productos_almacenados,
                                      value=(0, max_productos_almacenados))

# Filtrar los datos por el rango seleccionado
df = df[(df["PRODUCTOS ALMACENADOS"] >= almacenados_range[0]) &
        (df["PRODUCTOS ALMACENADOS"] <= almacenados_range[1])]

#  =========================================== POR DEMANDA DEL PRODUCTO =========================
st.sidebar.subheader("Filtrar por Demanda del Producto")
demanda_options = df["DEMANDA DEL PRODUCTO"].unique()
selected_demanda = st.sidebar.multiselect("Filtrar por Demanda del Producto", demanda_options, default=demanda_options)
df = df[df["DEMANDA DEL PRODUCTO"].isin(selected_demanda)]

#  =========================================== POR FESTIVIDAD =========================
st.sidebar.subheader("Filtrar por Festividad")
# Definir el mapeo de valores de festividad a etiquetas deseadas
mapeo_festividad = {0: "NO HAY FESTIVIDAD", 1: "SI HAY FESTIVIDAD"}
# Widget para filtrar por festividad
festividad_seleccionada = st.sidebar.multiselect("Filtrar por Festividad",
                                                 options=list(mapeo_festividad.values()),
                                                 default=list(mapeo_festividad.values()))

# Convertir las etiquetas seleccionadas de festividad a los valores correspondientes
festividad_seleccionada = [list(mapeo_festividad.keys())[list(mapeo_festividad.values()).index(label)]
                           for label in festividad_seleccionada]

# Filtrar los datos por el rango seleccionado y la festividad seleccionada
df = df[(df["FESTIVIDAD"].isin(festividad_seleccionada))]


filtered_data = df

# =============================================== Mostrar los datos filtrados
# Mostrar el DataFrame usando la función dataframe_explorer
st.write("## Conjunto de Datos:")
st.write(df)

# Mostrar estadísticas descriptivas
st.write("## Estadísticas Descriptivas:")
st.write(filtered_data.describe())

# Gráfico de dispersión
st.write("## Gráfico de Dispersión:")
scatter_fig = px.scatter(filtered_data, x="PRODUCTOS ALMACENADOS", y="PRODUCTOS VENDIDOS", color="DEMANDA DEL PRODUCTO")
st.plotly_chart(scatter_fig)

# ==================================== Panel de Estadísticas Rápidas ===============================================

# Calcular las estadísticas requeridas
# Calcular el precio de compra del producto
df["PRECIO DE COMPRA"] = df["GASTO DE ALMACENAMIENTO"] + df["GASTO DE MARKETING"] * df["DEMANDA DEL PRODUCTO"]

# Calcular la inversión realizada
inversionRealizada = (df['PRODUCTOS ALMACENADOS'] * df['PRECIO DE COMPRA']).sum()

# Calcular los gastos totales
gastosTotales = df["GASTO DE ALMACENAMIENTO"].sum() + (df["GASTO DE MARKETING"] * df["DEMANDA DEL PRODUCTO"]).sum()

# Calcular el retorno de ventas
retornoVentas = (df['PRECIO DE VENTA'] * df['PRODUCTOS VENDIDOS']).sum()

# Definir estilo CSS para las cartas
st.markdown("""
    <style>
        .card {
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
            background-color: #f9f9f9;
            margin-bottom: 20px;
        }
        .card-title {
            font-weight: bold;
            margin-bottom: 10px;
        }
        .card-content {
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Mostrar las cartas con las estadísticas rápidas
st.write("## Estadísticas Rápidas:")
st.markdown(
    f"""
    <div class="card">
        <div class="card-title">Inversión Realizada</div>
        <div class="card-content">${inversionRealizada}</div>
    </div>
    <div class="card">
        <div class="card-title">Gastos Totales</div>
        <div class="card-content">${gastosTotales}</div>
    </div>
    <div class="card">
        <div class="card-title">Retorno de Ventas</div>
        <div class="card-content">${retornoVentas}</div>
    </div>
    """,
    unsafe_allow_html=True
)
