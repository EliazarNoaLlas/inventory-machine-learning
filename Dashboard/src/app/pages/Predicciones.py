# File: Predicciones.py
# Author: victo
# Copyright: 2024, Smart Cities Peru.
# License: MIT
#
# Purpose:
# This is the entry point for the application.
#
# Last Modified: 2024-05-03

# ================================= Importando Librerias =============================
from pages.Modelo_ import bosque
# Importar las columnas del modelo
from pages.Modelo_ import X
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from fpdf import FPDF
import base64


# ========== Configurar la página ================
st.set_page_config(
    page_title="Predicciones de Ventas",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="expanded"  # Puedes ajustar según tus preferencias
)

# ==========================================  Baner ====================================================================
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
st.markdown("## :chart_with_upwards_trend: Predicciones")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# Componente para cargar un archivo Excel
uploaded_file = st.file_uploader(":file_folder: Cargar archivo Excel", type=["xlsx", "xls"])
# ================================================  Cargar Datos  ======================================================
# Leer el conjunto de datos por defecto
df = pd.read_excel("./data/Diclofenaco-prediccion.xlsx", engine="openpyxl")
# Carga el archivo y crea un DataFrame si se ha cargado un archivo
if uploaded_file is not None:
    filename = uploaded_file.name
    st.write(filename)
    try:
        new_df = pd.read_excel(uploaded_file, engine="openpyxl")
        new_df.columns = df.columns
        #  verifica si la cantidad de columnas no es la misma.
        if len(df.columns) != len(new_df.columns):
            st.error("Error: El archivo cargado no tiene la misma cantidad de columnas que el archivo por defecto.")
        #  verifica si los tipos de datos de las columnas no son iguales.
        else:
            # Guardar y actualizar el nuevo DataFrame
            new_df.to_excel("./data/Diclofenaco-prediccion.xlsx", index=False)
            df = new_df
            st.success("El archivo se ha cargado con éxito.")
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}")
else:
    st.warning("Ningún archivo se ha cargado, se utilizará un archivo por defecto.")
# ============================================================================================================================

# Filtrar las características necesarias utilizando las columnas del modelo
columnas_necesarias = X.columns
nuevos_datos = df[columnas_necesarias]
predicciones = bosque.predict(nuevos_datos) + 10
predicciones = np.round(predicciones).astype(int)
# Crear un nuevo DataFrame con las predicciones
df_predicciones = pd.DataFrame({"PRODUCTOS VENDIDOS": predicciones})

# Agregar la columna de predicciones al DataFrame original
df_con_predicciones = pd.concat([df, df_predicciones], axis=1)

# Crear una tabla con Plotly sin formato de coma decimal en la columna 'PRODUCTOS VENDIDOS'
fig_predicciones = go.Figure(data=[go.Table(
    header=dict(values=['PRODUCTOS QUE SE VENDERÁN' if col == 'PRODUCTOS VENDIDOS' else col for col in
                        df_con_predicciones.columns],
                fill_color='darkslategray', line_color='white', align='center'),
    cells=dict(values=[
        df_con_predicciones[col] if col != 'PRODUCTOS VENDIDOS' else df_con_predicciones[col].apply(
            lambda x: f'{int(x)}' if not pd.isna(x) else '')
        for col in df_con_predicciones.columns
    ],
        fill_color=['dimgray' if col != 'PRODUCTOS VENDIDOS' else 'steelblue' for col in df_con_predicciones.columns],
        line_color='white', align='center',
        format=[None if col != 'PRODUCTOS VENDIDOS' else None for col in df_con_predicciones.columns])
)])

# Estilo adicional para la tabla
fig_predicciones.update_layout(
    margin=dict(l=0, r=0, b=0, t=0),
)

# Usar contenedores y columnas para organizar el diseño
container1 = st.container()
container2 = st.container()

with container1:
    # Dividir la página en dos columnas
    col1, col2 = st.columns(2)

    with col1:
        # Mostrar la tabla con predicciones debajo de los gráficos
        st.subheader("Cantidad de Productos que se Venderán:")
        st.plotly_chart(fig_predicciones)
    with col2:
        # Crear gráfico de dispersión entre Demanda del Producto y Productos Vendidos Predichos
        scatter_predicciones = px.scatter(df_con_predicciones, x='DEMANDA DEL PRODUCTO', y='PRODUCTOS VENDIDOS',
                                          title='Diagrama de Dispersión: Demanda del Producto vs Productos Vendidos',
                                          labels={'DEMANDA DEL PRODUCTO': 'DEMANDA DEL PRODUCTO',
                                                  'PRODUCTOS VENDIDOS': 'PRODUCTOS VENDIDOS'})
        # Mostrar el gráfico de dispersión
        st.plotly_chart(scatter_predicciones)

with container2:
    # ------------------------ Realizar Predicciones ---------------------------
    # Formulario para ingresar nuevos datos y botón de predicción
    st.header("Ingresar Datos para Predicción")
    # Mostrar todas las variables en el formulario
    new_data = {
        "MES": st.number_input("MES", min_value=1, max_value=12, key="mes_input"),
        "PRODUCTOS ALMACENADOS": st.number_input("NUMERO DE PRODUCTOS ALMACENADOS", min_value=0),
        "GASTO DE MARKETING": st.number_input("GASTO DE MARKETING", min_value=0.0, step=1.0),
        "GASTO DE ALMACENAMIENTO": st.number_input("GASTO DE ALMACENAMIENTO", min_value=0.0, step=1.0),
        "DEMANDA DEL PRODUCTO": st.number_input("DEMANDA DEL PRODUCTO", min_value=1, max_value=10),
        "FESTIVIDAD": st.number_input("FESTIVIDAD", min_value=0, max_value=1),
        "PRECIO DE VENTA": st.number_input("PRECIO DE VENTA", min_value=0.0, step=1.0)
    }

    # Botón para realizar predicción
    if st.button("Realizar Predicción"):
        # Filtrar las variables que no son consideradas ruido
        new_data_filtered = {key: value for key, value in new_data.items() if key in X.columns}
        new_data_df = pd.DataFrame(new_data_filtered, index=[0])
        new_predictions = bosque.predict(new_data_df) + 10
        new_predictions = np.round(new_predictions).astype(int)
        # Estilo del cuadro de texto
        style = """
            padding: 10px;
            background-color: #001F3F; /* Color plateado o gris claro */
            border: 2px solid #C0C0C0; /* Borde del cuadro */
            border-radius: 5px; /* Esquinas redondeadas */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Sombra */
            color: #001F3F; /* Texto en azul oscuro */
            font-size: 18px; /* Tamaño de fuente más grande */
        """

        # Imprimir predicción en el cuadro de texto con estilo
        rounded_prediction = int(round(new_predictions[0]))
        st.markdown(f'<div style="{style}">Predicción de Productos que se venderán: {rounded_prediction}</div>',
                    unsafe_allow_html=True)


# Crear una clase personalizada que herede de FPDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Resultados de Predicciones', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')


# Función para crear el PDF
def create_pdf(df):
    pdf = PDF()
    pdf.add_page()

    # Título del PDF
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Resultados de Predicciones', 0, 1, 'C')
    pdf.ln(10)

    # Encabezados de columna en negrita
    pdf.set_font('Arial', 'B', 5)
    col_width = 25
    row_height = 10
    for col in df.columns:
        # Dividir el nombre de la columna en dos partes
        col_name_parts = col.split()
        # Imprimir cada parte con un salto de línea entre ellas
        for part in col_name_parts:
            pdf.cell(col_width, row_height, part, 1)
            pdf.ln(row_height / 2)  # Salto de línea más pequeño
        pdf.ln(row_height / 2)  # Salto de línea más pequeño adicional para separar las columnas
    pdf.ln()

    # Contenido de la tabla
    pdf.set_font('Arial', '', 12)
    for index, row in df.iterrows():
        for col in df.columns:
            pdf.cell(col_width, row_height, str(row[col]), 1)
        pdf.ln()

    # Guardar el PDF
    pdf_filename = "resultados_prediccion.pdf"
    pdf.output(pdf_filename)

    return pdf_filename


# Botón para descargar PDF
if st.button("Descargar Resultados como PDF"):
    # Generar el PDF
    pdf_filename = create_pdf(df_con_predicciones)
    st.success(f"El reporte se ha descargado como {pdf_filename}")

    # Convertir el PDF en bytes para descargarlo
    with open(pdf_filename, "rb") as f:
        pdf_bytes = f.read()

    # Codificar el PDF en base64
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    href = f'<a href="data:application/pdf;base64,{pdf_base64}" download="resultados_prediccion.pdf">Descargar PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
