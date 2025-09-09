from __future__ import annotations
import streamlit as st
from pathlib import Path
import sys
import pandas as pd


project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.funciones_streamlit.funciones import guardar_archivo_subido
from utils.constantes import DATA_PATH
# Configuración general de la página
st.set_page_config(page_title="Elecciones 2025", layout="wide")
st.title("RESULTADOS ELECTORALES")

# Ruta relativa para los links
PAGES_DIR = Path("pages")

st.info(
    """
    **Sistema en Python para procesar datos electorales**
    """
)
st.divider()

st.subheader("CARGA DE DATOS")

archivo = st.file_uploader(
    "📂 Cargar base de datos",
    type=["csv", "xlsx", "zip"],
)
if archivo:
    # Mostrar nombre original
    st.success(f"Archivo subido: {archivo.name}")

    # Guardar archivo en carpeta local
    ruta_guardada_dipsen = guardar_archivo_subido(archivo, archivo.name, DATA_PATH)

    if ruta_guardada_dipsen:
        st.info(f"Guardado en: {ruta_guardada_dipsen}")

st.info(
    """
**📂 Archivos necesarios:**

- `Base_Elecciones.csv`    
- `ELECTORES.csv`  

**⚠️ Importante:** *Respetar el nombre exacto de los archivos*
    """
)
