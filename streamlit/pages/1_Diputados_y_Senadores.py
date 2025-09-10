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
    analizar_rangos_votos,
    votos_por_seccion,
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

    # Selector de sección para análisis detallado
    st.divider()
    st.subheader("🔍 Análisis detallado por sección")

    # Obtener lista de secciones disponibles
    secciones_disponibles = sorted(df["Seccion"].unique())
    seccion_seleccionada = st.selectbox(
        "Selecciona una sección para analizar:",
        secciones_disponibles,
        help="Elige una sección electoral para ver el detalle de votos por partido",
    )

    if seccion_seleccionada:
        # Calcular datos para la sección seleccionada
        datos_seccion = votos_por_seccion(df, seccion_seleccionada)

        if datos_seccion:
            col1, col2 = st.columns([2, 1])

            with col1:
                st.subheader(f"📊 Porcentajes de votos - {seccion_seleccionada}")

                # Crear gráfico de barras con porcentajes
                import pandas as pd

                df_grafico = pd.DataFrame(
                    {
                        "Partido": datos_seccion["partidos"][:10],  # Top 10 partidos
                        "Porcentaje": [
                            datos_seccion["porcentajes"][partido]
                            for partido in datos_seccion["partidos"][:10]
                        ],
                    }
                )

                # Crear gráfico de barras usando matplotlib
                import matplotlib.pyplot as plt

                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.barh(df_grafico["Partido"], df_grafico["Porcentaje"])

                # Personalizar el gráfico
                ax.set_xlabel("Porcentaje de votos (%)")
                titulo = f"Distribución de votos en {seccion_seleccionada}"
                if datos_seccion.get("votos_blancos", 0) > 0:
                    titulo += " (incluye votos en blanco)"
                ax.set_title(titulo)
                ax.grid(True, alpha=0.3)

                # Agregar etiquetas con los valores
                for bar, valor in zip(bars, df_grafico["Porcentaje"]):
                    ax.text(
                        bar.get_width() + 0.1,
                        bar.get_y() + bar.get_height() / 2,
                        f"{valor:.1f}%",
                        ha="left",
                        va="center",
                    )

                # Invertir el eje Y para que el partido con más votos aparezca arriba
                ax.invert_yaxis()

                st.pyplot(fig)

            with col2:
                titulo_tabla = f"📋 Votos por partido - {seccion_seleccionada}"
                if datos_seccion.get("votos_blancos", 0) > 0:
                    titulo_tabla += " (+ votos en blanco)"
                st.subheader(titulo_tabla)

                # Crear tabla con votos
                df_tabla = pd.DataFrame(
                    {
                        "Partido": datos_seccion["partidos"],
                        "Votos": [
                            datos_seccion["votos"][partido]
                            for partido in datos_seccion["partidos"]
                        ],
                        "Porcentaje": [
                            f"{datos_seccion['porcentajes'][partido]:.1f}%"
                            for partido in datos_seccion["partidos"]
                        ],
                    }
                )

                # Resaltar votos en blanco si existen
                if datos_seccion.get("votos_blancos", 0) > 0:
                    st.info(
                        f"📝 **Votos en blanco:** {datos_seccion['votos_blancos']:,} votos ({(datos_seccion['votos_blancos'] / datos_seccion['total_votos'] * 100):.1f}%)"
                    )

                st.dataframe(
                    df_tabla,
                    use_container_width=True,
                    column_config={
                        "Votos": st.column_config.NumberColumn(format="%d"),
                        "Porcentaje": st.column_config.TextColumn(),
                    },
                )

                # Mostrar total de votos
                st.metric(
                    label="Total de votos válidos",
                    value=f"{datos_seccion['total_votos']:,}".replace(",", "."),
                )
        else:
            st.error(f"No se encontraron datos para la sección {seccion_seleccionada}")

    # Información adicional
    st.info(
        "💡 **Cómo usar:** Selecciona una sección del desplegable para ver el detalle de votos por partido en esa sección específica, tanto en gráfico como en tabla. Los votos en blanco se incluyen como un 'partido' adicional cuando existen."
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
        fp_total = conteo_total.get("Fuerza Patria", 0)
        st.metric("FP (Total)", fp_total)

    with col4:
        fp_amba = conteo_amba.get("Fuerza Patria", 0)
        st.metric("FP (AMBA)", fp_amba)

    # Mostrar rangos de porcentaje de votos
    st.divider()
    st.subheader("📊 Rangos de porcentaje de votos")

    # Calcular rangos de votos para los partidos principales
    partidos_rangos = ["Fuerza Patria", "La Libertad Avanza"]
    rangos_resultados = analizar_rangos_votos(df, partidos_rangos)

    if rangos_resultados:
        # Crear tabla comparativa
        import pandas as pd

        # Crear DataFrame con los rangos
        df_rangos = pd.DataFrame(rangos_resultados)
        df_rangos = df_rangos.reset_index().rename(columns={"index": "Rango"})

        # Mostrar tabla
        st.dataframe(df_rangos, use_container_width=True)

        # Agregar información adicional
        st.info(
            "💡 **Interpretación:** Esta tabla muestra cuántos municipios obtuvo cada porcentaje de votos para Fuerza Patria y La Libertad Avanza."
        )

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
