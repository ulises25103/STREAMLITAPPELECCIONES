import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="📊 Mesas Electorales", page_icon="🗳️", layout="wide")

st.title("📊 MESAS ELECTORALES - PADRON 2025")
st.markdown("---")


@st.cache_data
def cargar_datos():
    """Carga los datos del archivo CSV reducido"""
    # Método más robusto para encontrar el directorio raíz del proyecto
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Buscar hacia arriba hasta encontrar el directorio raíz del proyecto
    project_root = None
    for _ in range(10):  # Máximo 10 niveles hacia arriba
        if os.path.exists(
            os.path.join(current_dir, "utils", "data", "mesas_electores_reducido.csv")
        ):
            project_root = current_dir
            break
        parent = os.path.dirname(current_dir)
        if parent == current_dir:  # Llegamos a la raíz del sistema
            break
        current_dir = parent

    if project_root:
        ruta_csv = os.path.join(
            project_root, "utils", "data", "mesas_electores_reducido.csv"
        )
    else:
        # Fallback: usar ruta relativa desde donde esté corriendo el script
        ruta_csv = os.path.join("utils", "data", "mesas_electores_reducido.csv")

    try:
        df = pd.read_csv(ruta_csv)
        return df
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'mesas_electores_reducido.csv'")
        st.info(f"💡 Ruta buscada: {ruta_csv}")
        st.info("💡 El archivo debería estar en: utils/data/")

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
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🏛️ Municipios", f"{df['nombre_distrito'].nunique():,}")

    with col2:
        st.metric("📋 Mesas Totales", f"{len(df):,}")

    with col3:
        st.metric("👥 Electores Totales", f"{df['electores'].sum():,}")

    with col4:
        st.metric("📈 Promedio por Mesa", ".1f")

    st.markdown("---")

    # Filtros
    st.subheader("🔍 Filtros")

    col1, col2 = st.columns(2)

    with col1:
        municipios = ["Todos"] + sorted(df["nombre_distrito"].unique().tolist())
        municipio_seleccionado = st.selectbox(
            "🏛️ Filtrar por Municipio:",
            municipios,
            help="Selecciona un municipio para filtrar la tabla",
        )

    with col2:
        if municipio_seleccionado != "Todos":
            df_filtrado = df[df["nombre_distrito"] == municipio_seleccionado].copy()
        else:
            df_filtrado = df.copy()

        # Mostrar estadísticas del filtro
        st.metric("Mesas en selección", f"{len(df_filtrado):,}")
        st.metric("Electores en selección", f"{df_filtrado['electores'].sum():,}")

    st.markdown("---")

    # Tabla principal
    st.subheader("📋 TABLA DE MESAS ELECTORALES")

    # Configurar la tabla para mostrar mejor
    st.dataframe(
        df_filtrado,
        column_config={
            "nombre_distrito": st.column_config.TextColumn("Municipio", width="medium"),
            "cod_circ": st.column_config.TextColumn("Sección", width="small"),
            "establecimiento": st.column_config.TextColumn("Escuela", width="large"),
            "nro_mesa": st.column_config.NumberColumn("Mesa", width="small"),
            "electores": st.column_config.NumberColumn("Electores", width="small"),
        },
        use_container_width=True,
        hide_index=True,
    )

    # Información adicional
    with st.expander("ℹ️ Información del Dataset"):
        st.markdown(
            f"""
        **📊 Estadísticas del Dataset:**
        - **Total de mesas:** {len(df):,}
        - **Municipios únicos:** {df['nombre_distrito'].nunique()}
        - **Secciones únicas:** {df['cod_circ'].nunique()}
        - **Escuelas únicas:** {df['establecimiento'].nunique()}
        - **Total de electores:** {df['electores'].sum():,}

        **📋 Columnas disponibles:**
        - `nombre_distrito`: Municipio
        - `cod_circ`: Sección electoral
        - `establecimiento`: Nombre de la escuela
        - `nro_mesa`: Número de mesa
        - `electores`: Cantidad de electores en la mesa
        """
        )

else:
    st.error("❌ No se pudieron cargar los datos")
    st.info("💡 Verifica que el archivo CSV reducido exista en la ubicación correcta")
