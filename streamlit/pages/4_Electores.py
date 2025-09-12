import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="📊 Mesas Electorales", page_icon="🗳️", layout="wide")

st.title("📊 MESAS ELECTORALES - PADRON 2025")
st.markdown("---")


@st.cache_data
def cargar_datos():
    """Carga los datos del archivo CSV de mesas electores consolidado"""
    # Método más robusto para encontrar el directorio raíz del proyecto
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Buscar hacia arriba hasta encontrar el directorio raíz del proyecto
    project_root = None
    for _ in range(10):  # Máximo 10 niveles hacia arriba
        if os.path.exists(
            os.path.join(current_dir, "utils", "data", "base_mesas_electores.csv")
        ):
            project_root = current_dir
            break
        parent = os.path.dirname(current_dir)
        if parent == current_dir:  # Llegamos a la raíz del sistema
            break
        current_dir = parent

    if project_root:
        ruta_csv = os.path.join(
            project_root, "utils", "data", "base_mesas_electores.csv"
        )
    else:
        # Fallback: usar ruta relativa desde donde esté corriendo el script
        ruta_csv = os.path.join("utils", "data", "base_mesas_electores.csv")

    try:
        df = pd.read_csv(ruta_csv)

        # Agregar columna de distrito como string para mejor visualización
        df["distrito_str"] = df["distrito"].astype(str)

        return df
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'base_mesas_electores.csv'")
        st.info(f"💡 Ruta buscada: {ruta_csv}")
        st.info("💡 El archivo debería estar en: utils/data/")
        st.info("💡 Asegúrate de haber ejecutado el procesamiento de las bases ZIP")

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

        return None


# Cargar datos
df = cargar_datos()

if df is not None:
    # Separar datos de mesas nativas y extranjeras
    df_nativas = df[df["tipo"] == "NATIVA"]
    df_extranjeras = df[df["tipo"] == "EXTRANJERA"]

    # Métricas principales
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("🏛️ Distritos", f"{df['distrito'].nunique():,}")

    with col2:
        st.metric("📋 Mesas Totales", f"{len(df):,}")

    with col3:
        st.metric("🏠 Mesas Nativas", f"{len(df_nativas):,}")

    with col4:
        st.metric("🌍 Mesas Extranjeras", f"{len(df_extranjeras):,}")

    with col5:
        st.metric("👥 Electores Nativos", f"{df_nativas['cantidad_electores'].sum():,}")

    with col6:
        st.metric(
            "🧑‍🤝‍🧑 Extranjeros", f"{df_extranjeras['cantidad_electores'].sum():,}"
        )

    st.markdown("---")

    # Filtros
    st.subheader("🔍 Filtros")

    col1, col2, col3 = st.columns(3)

    with col1:
        tipo_mesa = st.selectbox(
            "🏷️ Tipo de Mesa:",
            ["Todas las mesas", "Solo mesas nativas", "Solo mesas extranjeras"],
            help="Filtrar por tipo de mesa electoral",
        )

    with col2:
        distritos = ["Todos"] + sorted(df["distrito"].unique().tolist())
        distrito_seleccionado = st.selectbox(
            "🏛️ Filtrar por Distrito:",
            distritos,
            help="Selecciona un distrito para filtrar la tabla",
        )

    with col3:
        # Filtrar circuitos según el tipo de mesa seleccionado
        if tipo_mesa == "Solo mesas nativas":
            circuitos_base = df_nativas["cod_circ"].unique().tolist()
        elif tipo_mesa == "Solo mesas extranjeras":
            circuitos_base = df_extranjeras["cod_circ"].unique().tolist()
        else:
            circuitos_base = df["cod_circ"].unique().tolist()

        circuitos = ["Todos"] + sorted(circuitos_base)
        circuito_seleccionado = st.selectbox(
            "🗳️ Filtrar por Circuito:",
            circuitos,
            help="Selecciona un circuito electoral para filtrar la tabla",
        )

    # Aplicar filtros
    df_filtrado = df.copy()

    # Aplicar filtro de tipo de mesa
    if tipo_mesa == "Solo mesas nativas":
        df_filtrado = df_filtrado[df_filtrado["tipo"] == "NATIVA"]
    elif tipo_mesa == "Solo mesas extranjeras":
        df_filtrado = df_filtrado[df_filtrado["tipo"] == "EXTRANJERA"]

    if distrito_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["distrito"] == distrito_seleccionado]

    if circuito_seleccionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["cod_circ"] == circuito_seleccionado]

    # Mostrar estadísticas del filtro
    if tipo_mesa == "Solo mesas extranjeras":
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mesas en selección", f"{len(df_filtrado):,}")
        with col2:
            st.metric(
                "Extranjeros en selección",
                f"{df_filtrado['cantidad_electores'].sum():,}",
            )
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mesas en selección", f"{len(df_filtrado):,}")
        with col2:
            st.metric(
                "Electores nativos", f"{df_filtrado['cantidad_electores'].sum():,}"
            )
        with col3:
            st.metric("Total electores", f"{df['cantidad_electores'].sum():,}")

    st.markdown("---")

    # Tabla principal
    st.subheader("📋 TABLA DE MESAS ELECTORALES")

    # Configurar la tabla para mostrar mejor
    column_config = {
        "distrito_str": st.column_config.TextColumn("Distrito", width="small"),
        "cod_circ": st.column_config.TextColumn("Código Circuito", width="small"),
        "establecimiento": st.column_config.TextColumn("Escuela", width="large"),
        "nro_mesa": st.column_config.NumberColumn("Mesa", width="small"),
        "cantidad_electores": st.column_config.NumberColumn("Electores", width="small"),
        "tipo": st.column_config.TextColumn("Tipo", width="medium"),
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
        - **Mesas nativas:** {len(df_nativas):,}
        - **Mesas extranjeras:** {len(df_extranjeras):,}
        - **Distritos únicos:** {df['distrito'].nunique()}
        - **Circuitos únicos:** {df['cod_circ'].nunique()}
        - **Escuelas únicas:** {df['establecimiento'].nunique()}
        - **Electores nativos:** {df_nativas['cantidad_electores'].sum():,}
        - **Extranjeros:** {df_extranjeras['cantidad_electores'].sum():,}
        - **Total de electores:** {df['cantidad_electores'].sum():,}

        **📋 Columnas disponibles:**
        - `distrito`: Código del distrito/municipio
        - `cod_circ`: Código del circuito electoral
        - `establecimiento`: Nombre de la escuela
        - `nro_mesa`: Número de mesa
        - `cantidad_electores`: Cantidad de electores en la mesa
        - `tipo`: Tipo de mesa (NATIVA/EXTRANJERA)

        **🔧 Origen de los datos:**
        - Base procesada desde archivos ZIP: `padron_2025.zip` y `padron_extranjeros_2025.zip`
        - Agrupación por combinación única de `cod_circ` + `nro_mesa`
        """
        )

else:
    st.error("❌ No se pudieron cargar los datos")
    st.info(
        "💡 Verifica que el archivo 'base_mesas_electores.csv' exista en: utils/data/"
    )
    st.info(
        "💡 Asegúrate de haber ejecutado el procesamiento de las bases ZIP de padrones"
    )
