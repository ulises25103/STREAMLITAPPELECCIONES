import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="📊 Mesas Electorales", page_icon="🗳️", layout="wide")

st.title("📊 MESAS ELECTORALES CON EXTRANJEROS - PADRON 2025")
st.markdown("---")


@st.cache_data
def cargar_datos():
    """Carga los datos del archivo CSV consolidado con extranjeros"""
    # Método más robusto para encontrar el directorio raíz del proyecto
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Buscar hacia arriba hasta encontrar el directorio raíz del proyecto
    project_root = None
    for _ in range(10):  # Máximo 10 niveles hacia arriba
        if os.path.exists(
            os.path.join(current_dir, "utils", "data", "mesas_con_extranjeros.csv")
        ):
            project_root = current_dir
            break
        parent = os.path.dirname(current_dir)
        if parent == current_dir:  # Llegamos a la raíz del sistema
            break
        current_dir = parent

    if project_root:
        ruta_csv = os.path.join(
            project_root, "utils", "data", "mesas_con_extranjeros.csv"
        )
    else:
        # Fallback: usar ruta relativa desde donde esté corriendo el script
        ruta_csv = os.path.join("utils", "data", "mesas_con_extranjeros.csv")

    try:
        df = pd.read_csv(ruta_csv)
        return df
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'mesas_con_extranjeros.csv'")
        st.info(f"💡 Ruta buscada: {ruta_csv}")
        st.info("💡 El archivo debería estar en: utils/data/")
        st.info("💡 Asegúrate de haber ejecutado 'unir_extranjeros_mesas.py' primero")

        # Mostrar archivos disponibles en el directorio actual
        current_dir = os.getcwd()
        st.info(f"📁 Directorio actual: {current_dir}")

        # Mostrar archivos disponibles
        try:
            archivos = os.listdir(current_dir)
            st.info("📁 Archivos en directorio actual:")
            for archivo in archivos:
                st.write(f"  - {archivo}")
        except:
            st.write("  - No se pudo listar archivos")

        # Intentar buscar en utils/data si existe
        utils_data = os.path.join(current_dir, "utils", "data")
        if os.path.exists(utils_data):
            st.info(f"📁 Archivos en {utils_data}:")
            archivos_data = os.listdir(utils_data)
            for archivo in archivos_data:
                st.write(f"  - {archivo}")

        return None


# Cargar datos
df = cargar_datos()

if df is not None:
    # Separar datos de mesas locales y extranjeras
    df_locales = df[df["seccion_electoral"] != "EXTRANJEROS"]
    df_extranjeros = df[df["seccion_electoral"] == "EXTRANJEROS"]

    # Métricas principales
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("🏛️ Municipios", f"{df['nombre_distrito'].nunique():,}")

    with col2:
        st.metric("📋 Mesas Totales", f"{len(df):,}")

    with col3:
        st.metric("🏠 Mesas Locales", f"{len(df_locales):,}")

    with col4:
        st.metric("🌍 Mesas Extranjeros", f"{len(df_extranjeros):,}")

    with col5:
        st.metric("👥 Electores Locales", f"{df_locales['electores'].sum():,}")

    with col6:
        st.metric("🧑‍🤝‍🧑 Extranjeros", f"{df_extranjeros['extranjeros'].sum():,}")

    st.markdown("---")

    # Filtros
    st.subheader("🔍 Filtros")

    col1, col2, col3 = st.columns(3)

    with col1:
        tipo_mesa = st.selectbox(
            "🏷️ Tipo de Mesa:",
            ["Todas las mesas", "Solo mesas locales", "Solo mesas de extranjeros"],
            help="Filtrar por tipo de mesa electoral",
        )

    with col2:
        municipios = ["Todos"] + sorted(df["nombre_distrito"].unique().tolist())
        municipio_seleccionado = st.selectbox(
            "🏛️ Filtrar por Municipio:",
            municipios,
            help="Selecciona un municipio para filtrar la tabla",
        )

    with col3:
        # Filtrar secciones según el tipo de mesa seleccionado
        if tipo_mesa == "Solo mesas locales":
            secciones_base = df_locales["seccion_electoral"].unique().tolist()
        elif tipo_mesa == "Solo mesas de extranjeros":
            secciones_base = ["EXTRANJEROS"]
        else:
            secciones_base = df["seccion_electoral"].unique().tolist()

        secciones = ["Todos"] + sorted(secciones_base)
        seccion_seleccionada = st.selectbox(
            "🗳️ Filtrar por Sección Electoral:",
            secciones,
            help="Selecciona una sección electoral para filtrar la tabla",
        )

    # Aplicar filtros
    df_filtrado = df.copy()

    # Aplicar filtro de tipo de mesa
    if tipo_mesa == "Solo mesas locales":
        df_filtrado = df_filtrado[df_filtrado["seccion_electoral"] != "EXTRANJEROS"]
    elif tipo_mesa == "Solo mesas de extranjeros":
        df_filtrado = df_filtrado[df_filtrado["seccion_electoral"] == "EXTRANJEROS"]

    if municipio_seleccionado != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["nombre_distrito"] == municipio_seleccionado
        ]

    if seccion_seleccionada != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["seccion_electoral"] == seccion_seleccionada
        ]

    # Mostrar estadísticas del filtro
    if tipo_mesa == "Solo mesas de extranjeros":
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mesas en selección", f"{len(df_filtrado):,}")
        with col2:
            st.metric(
                "Extranjeros en selección", f"{df_filtrado['extranjeros'].sum():,}"
            )
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mesas en selección", f"{len(df_filtrado):,}")
        with col2:
            st.metric("Electores locales", f"{df_filtrado['electores'].sum():,}")
        with col3:
            st.metric("Total electores", f"{df_filtrado['electores_total'].sum():,}")

    st.markdown("---")

    # Tabla principal
    st.subheader("📋 TABLA DE MESAS ELECTORALES")

    # Configurar la tabla para mostrar mejor
    if tipo_mesa == "Solo mesas de extranjeros":
        # Configuración para mesas de extranjeros
        column_config = {
            "nombre_distrito": st.column_config.TextColumn("Municipio", width="medium"),
            "seccion_electoral": st.column_config.TextColumn(
                "Sección Electoral", width="medium"
            ),
            "cod_circ": st.column_config.TextColumn("Código Circuito", width="small"),
            "establecimiento": st.column_config.TextColumn("Escuela", width="large"),
            "nro_mesa": st.column_config.NumberColumn("Mesa", width="small"),
            "electores": st.column_config.NumberColumn(
                "Electores Locales", width="small"
            ),
            "extranjeros": st.column_config.NumberColumn("Extranjeros", width="small"),
            "electores_total": st.column_config.NumberColumn(
                "Total Electores", width="small"
            ),
        }
    else:
        # Configuración para mesas locales o todas
        column_config = {
            "nombre_distrito": st.column_config.TextColumn("Municipio", width="medium"),
            "seccion_electoral": st.column_config.TextColumn(
                "Sección Electoral", width="medium"
            ),
            "cod_circ": st.column_config.TextColumn("Código Circuito", width="small"),
            "establecimiento": st.column_config.TextColumn("Escuela", width="large"),
            "nro_mesa": st.column_config.NumberColumn("Mesa", width="small"),
            "electores": st.column_config.NumberColumn(
                "Electores Locales", width="small"
            ),
            "extranjeros": st.column_config.NumberColumn("Extranjeros", width="small"),
            "electores_total": st.column_config.NumberColumn(
                "Total Electores", width="small"
            ),
        }

    st.dataframe(
        df_filtrado,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
    )

    # Información adicional
    with st.expander("ℹ️ Información del Dataset"):
        st.markdown(
            f"""
        **📊 Estadísticas del Dataset:**
        - **Total de mesas:** {len(df):,}
        - **Mesas locales:** {len(df_locales):,}
        - **Mesas de extranjeros:** {len(df_extranjeros):,}
        - **Municipios únicos:** {df['nombre_distrito'].nunique()}
        - **Secciones únicas:** {df['seccion_electoral'].nunique()}
        - **Escuelas únicas:** {df['establecimiento'].nunique()}
        - **Electores locales:** {df_locales['electores'].sum():,}
        - **Extranjeros:** {df_extranjeros['extranjeros'].sum():,}
        - **Total de electores:** {df['electores_total'].sum():,}

        **📋 Columnas disponibles:**
        - `nombre_distrito`: Municipio
        - `seccion_electoral`: Sección electoral (EXTRANJEROS para mesas de extranjeros)
        - `cod_circ`: Código del circuito electoral
        - `establecimiento`: Nombre de la escuela
        - `nro_mesa`: Número de mesa
        - `electores`: Cantidad de electores locales en la mesa
        - `extranjeros`: Cantidad de extranjeros en la mesa
        - `electores_total`: Total de electores (locales + extranjeros)
        """
        )

else:
    st.error("❌ No se pudieron cargar los datos")
    st.info(
        "💡 Verifica que el archivo 'mesas_con_extranjeros.csv' exista en: utils/data/"
    )
    st.info("💡 Asegúrate de haber ejecutado 'unir_extranjeros_mesas.py' primero")
