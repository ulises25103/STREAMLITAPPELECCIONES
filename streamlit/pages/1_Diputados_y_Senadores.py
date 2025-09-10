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

from utils.constantes import BASE, ELECTORES_PATH, MUNICIPIOS_AMBA

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
    secciones_ganadas,
    municipios_ganados,
)


st.set_page_config(layout="wide")

if st.session_state.get("datos_actualizados", False):
    st.cache_data.clear()  # fuerza recarga
    st.session_state["datos_actualizados"] = False
# Sidebar para navegar
pagina = st.sidebar.selectbox(
    "📂 Elegí una sección",
    ["General", "Análisis por secciones", "Municipios", "Bancas"],
)

df = crear_dataframe(BASE, ",", "DIPUTADOS PROVINCIALES", "SENADORES PROVINCIALES")
# df = crear_dataframe(BASE, ",", "CONCEJALES")
df_electores = crear_dataframe(ELECTORES_PATH, ";")
if df is None:
    st.error("No se pudieron cargar los datos necesarios")
    st.stop()

df_resumen = contar_votos_por_tipo_eleccion(df)
total_votos = sumar_votos(df_resumen, "votos_validos")

participacion = (total_votos / 14227683) * 100
if pagina == "General":
    st.subheader("Analisis General")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Total de votos",
            value=f"{total_votos:,}".replace(",", "."),
            delta=None,
        )

    with col2:
        st.metric(label="Votantes habilitados", value="14.227.683")

    with col3:
        st.metric(label="Participación", value=f"{round(participacion)}%")

    st.divider()

    dicc_general = crear_diccionario_votos_por_partido(df)
    mostrar_diccionario_como_tabla(dicc_general)

    serie = calcular_porcentaje_partidos(dicc_general)
    st.subheader("📊 Porcentaje de votos por partido")
    st.bar_chart(serie)
elif pagina == "Análisis por secciones":
    st.subheader("Analisís por secciones")
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
    mostrar_diccionario_como_tabla(
        solo_votos_partido_fp, "📋 Total de votos por sección"
    )
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
    mostrar_diccionario_como_tabla(
        solo_votos_partido_lla, "📋 Total de votos por sección"
    )
    porcentajes_lla = calcular_porcentaje_partido_por_seccion(datos_LLA)
    st.subheader("📊 Porcentaje por secciones")
    st.bar_chart(porcentajes_lla)
    st.markdown(
        """
<h1 style='color:#9fccbc; font-size: 48px; text-align: center;'>
    SECCIONES
</h1>
""",
        unsafe_allow_html=True,
    )
    partidos = ["Fuerza Patria", "La Libertad Avanza"]
    conteo, ganadores = secciones_ganadas(df, partidos)

    # Tabla resumen
    st.subheader("Secciones ganadas por partido")
    st.table(
        conteo.reset_index().rename(
            columns={"index": "Partido", 0: "Secciones ganadas"}
        )
    )

elif pagina == "Municipios":
    st.subheader("Análisis por Municipios")
    st.divider()

    st.markdown(
        """
    <h1 style='color:#4CAF50; font-size: 48px; text-align: center;'>
        🏛️ MUNICIPIOS (5 partidos principales)
    </h1>
    """,
        unsafe_allow_html=True,
    )

    st.info(
        "ℹ️ Incluyendo los 5 partidos principales: Fuerza Patria, La Libertad Avanza, Somos Buenos Aires, FTE Izquierda y ESP. Abierto (91.8% del total)"
    )

    # Incluir los 5 principales partidos (91.8% de votos totales)
    partidos = [
        "Fuerza Patria",
        "La Libertad Avanza",
        "Somos Buenos Aires",
        "Esp. Abierto Para El Des. Y La Int. Social",
        "Fte De Izq. Y De Trabajadores - Unidad",
    ]
    conteo_total, conteo_amba, ganadores_total, ganadores_amba = municipios_ganados(
        df, partidos, MUNICIPIOS_AMBA
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Municipios ganados (Total)")
        st.table(
            conteo_total.reset_index().rename(
                columns={"index": "Partido", 0: "Municipios"}
            )
        )

    with col2:
        st.subheader("Municipios ganados en AMBA")
        st.table(
            conteo_amba.reset_index().rename(
                columns={"index": "Partido", 0: "Municipios AMBA"}
            )
        )

    # Métricas destacadas
    st.divider()
    st.subheader("📈 Métricas destacadas")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_municipios = len(ganadores_total)
        st.metric("Total municipios", total_municipios)

    with col2:
        municipios_amba_count = len(ganadores_amba)
        st.metric("Municipios AMBA", municipios_amba_count)

    with col3:
        lla_total = conteo_total.get("La Libertad Avanza", 0)
        st.metric("LLA (Total)", lla_total)

    with col4:
        lla_amba = conteo_amba.get("La Libertad Avanza", 0)
        st.metric("LLA (AMBA)", lla_amba)

    # Mostrar detalle de municipios ganados
    st.divider()
    st.subheader("📋 Detalle de municipios ganados")

    if not ganadores_total.empty:
        # Mostrar tabla con municipios ganados
        st.write("**Municipios ganados por partido:**")
        tabla_ganadores = ganadores_total.copy()
        tabla_ganadores = tabla_ganadores.sort_values(["Agrupacion", "Distrito"])
        st.dataframe(
            tabla_ganadores[["Distrito", "Agrupacion", "votos"]],
            use_container_width=True,
        )

    if not ganadores_amba.empty:
        st.write("**Municipios del AMBA ganados:**")
        tabla_amba = ganadores_amba.copy()
        tabla_amba = tabla_amba.sort_values(["Agrupacion", "Distrito"])
        st.dataframe(
            tabla_amba[["Distrito", "Agrupacion", "votos"]], use_container_width=True
        )
