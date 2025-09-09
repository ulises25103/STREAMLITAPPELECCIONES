from pathlib import Path
import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from importlib import reload
import streamlit.components.v1 as components
import json
from datetime import datetime as dt
from __future__ import annotations

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.constantes import(
    BASE_CONCEJALES,
    ELECTORES_PATH
)

from src.funciones_streamlit.funciones import (
    crear_dataframe,
    contar_votos_por_tipo_eleccion,
    contar_total_electores,
    sumar_votos_validos,
    sumar_votos_nulos)


st.set_page_config(layout="wide")
st.subheader("📊 Indicadores clave")

if st.session_state.get("datos_actualizados", False):
    st.cache_data.clear()  # fuerza recarga
    st.session_state["datos_actualizados"] = False

st.divider()

df = crear_dataframe(BASE_CONCEJALES)
df_electores = crear_dataframe(ELECTORES_PATH)
if df is None:
    st.error("No se pudieron cargar los datos necesarios")
    st.stop
total_electores = contar_total_electores(df_electores)
df_resumen = contar_votos_por_tipo_eleccion(df)
total_validos = sumar_votos_validos(df_resumen)
total_nulos = sumar_votos_nulos(df_resumen)
total_votos = total_validos + total_nulos

participacion = (total_votos / total_electores) * 100

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total de votos", value=total_votos, delta=None)

with col2:
    st.metric(label="Votantes habilitados", value=total_electores)

with col3:
    st.metric(label="Participación", value=f"{round(participacion)}%")
