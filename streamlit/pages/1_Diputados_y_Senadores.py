from __future__ import annotations
from pathlib import Path
import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from importlib import reload
import streamlit.components.v1 as components
import json
from datetime import datetime as dt

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.constantes import(
    BASE,
    ELECTORES_PATH
)

from src.funciones_streamlit.funciones import (
    crear_dataframe,
    contar_votos_por_tipo_eleccion,
    contar_total_electores,
    sumar_votos,
    crear_diccionario_votos_por_partido,
    calcular_porcentaje_partidos,
    mostrar_diccionario_como_tabla,
    votos_partido_y_validos_por_seccion,
    calcular_porcentaje_partido_por_seccion,
)


st.set_page_config(layout="wide")

if st.session_state.get("datos_actualizados", False):
    st.cache_data.clear()  # fuerza recarga
    st.session_state["datos_actualizados"] = False
# Sidebar para navegar
pagina = st.sidebar.selectbox(
    "📂 Elegí una sección",
    ["General", "Análisis por partido", "Bancas"],
)

df = crear_dataframe(BASE,",", "DIPUTADOS PROVINCIALES", "SENADORES PROVINCIALES")
# df = crear_dataframe(BASE, ",", "CONCEJALES")
df_electores = crear_dataframe(ELECTORES_PATH, ";")
if df is None:
    st.error("No se pudieron cargar los datos necesarios")
    st.stop()

df_resumen = contar_votos_por_tipo_eleccion(df)
total_votos = sumar_votos(df_resumen, "votos_validos")

participacion = (total_votos /  14227683) * 100
if pagina == "General":
    st.subheader("Analisis General")
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total de votos",
            value=f"{total_votos:,}".replace(",", "."),
            delta=None,
        )

    with col2:
        st.metric(label="Votantes habilitados", value= "14.227.683")

    with col3:
        st.metric(label="Participación", value=f"{round(participacion)}%")

    st.divider()

    dicc_general = crear_diccionario_votos_por_partido(df)
    mostrar_diccionario_como_tabla(dicc_general)

    serie = calcular_porcentaje_partidos(dicc_general)
    st.subheader("📊 Porcentaje de votos por partido")
    st.bar_chart(serie)
elif pagina == "Análisis por partido":
    st.subheader("Analisís por Partido")
    st.divider()
    st.markdown(
        """
<h1 style='color:#00BFFF; font-size: 48px; text-align: center;'>
    FUERZA PATRIA
</h1>
""",
        unsafe_allow_html=True,
    )
    datos_FP = votos_partido_y_validos_por_seccion(df, "FUERZA PATRIA")
    solo_votos_partido_fp = {
        seccion: datos["votos_partido"] for seccion, datos in datos_FP.items()
    }
    mostrar_diccionario_como_tabla(solo_votos_partido_fp, "📋 Total de votos por sección")
    porcentajes_FP = calcular_porcentaje_partido_por_seccion(datos_FP)
    st.subheader("📊 Porcentaje por secciones")
    st.bar_chart(porcentajes_FP)
    st.markdown(
        """
<h1 style='color:#C8A2C8; font-size: 48px; text-align: center;'>
    LA LIBERTAD AVANZA
</h1>
""",
        unsafe_allow_html=True,
    )
    datos_LLA = votos_partido_y_validos_por_seccion(df, "LA LIBERTAD AVANZA")
    solo_votos_partido_lla = {
        seccion: datos["votos_partido"] for seccion, datos in datos_LLA.items()
    }
    mostrar_diccionario_como_tabla(solo_votos_partido_lla, "📋 Total de votos por sección")
    porcentajes_lla = calcular_porcentaje_partido_por_seccion(datos_LLA)
    st.subheader("📊 Porcentaje por secciones")
    st.bar_chart(porcentajes_lla)
