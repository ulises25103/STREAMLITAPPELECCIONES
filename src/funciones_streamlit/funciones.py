from __future__ import annotations
from pathlib import Path
import sys
import os
import streamlit as st
import pandas as pd
import unicodedata
from functools import lru_cache
import hashlib

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Cache global para dataframes procesados
_CACHE_DATAFRAMES = {}
_CACHE_VOTOS_PROCESADOS = {}

# Importar desde la ruta correcta

from utils.constantes import DATA_PATH, BASE
from utils.constantes import MUNICIPIOS_AMBA


def _generar_cache_key(*args, **kwargs):
    """Genera una clave única para el cache basada en los argumentos."""
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    return hashlib.md5("|".join(key_parts).encode()).hexdigest()


@lru_cache(maxsize=32)
def obtener_dataframe_procesado(cargo=None, cargo2=None):
    """
    Función optimizada que carga y procesa el dataframe una sola vez,
    reutilizando el resultado para múltiples llamadas.
    """
    cache_key = _generar_cache_key(cargo, cargo2)

    if cache_key in _CACHE_DATAFRAMES:
        return _CACHE_DATAFRAMES[cache_key].copy()

    try:
        # Cargar dataframe base
        df = crear_dataframe(BASE, ",", cargo, cargo2)

        if df is None:
            return None

        # Procesamiento adicional optimizado
        df_procesado = _procesar_dataframe_para_analisis(df)

        # Guardar en cache
        _CACHE_DATAFRAMES[cache_key] = df_procesado

        return df_procesado.copy()

    except Exception as e:
        print(f"Error en obtener_dataframe_procesado: {e}")
        return None


def _procesar_dataframe_para_analisis(df):
    """
    Función interna que hace todo el procesamiento pesado una sola vez.
    """
    df = df.copy()

    # Asegurar tipos de datos optimizados
    if "votos" in df.columns:
        df["votos"] = pd.to_numeric(
            df["votos"], errors="coerce", downcast="integer"
        ).fillna(0)

    # Crear índices optimizados para búsquedas frecuentes
    df["tipoVoto_lower"] = df["tipoVoto"].str.lower()
    df["seccion_lower"] = df["Seccion"].str.lower()
    df["partido_lower"] = df["Agrupacion"].str.lower()

    # Pre-calcular datos agregados que se usan frecuentemente
    df_procesado = {
        "dataframe": df,
        "votos_por_partido": None,
        "votos_por_seccion": None,
        "votos_por_municipio": None,
        "votos_validos_por_seccion": None,
        "votos_validos_por_municipio": None,
    }

    return df_procesado


def limpiar_cache():
    """Limpia el cache cuando sea necesario."""
    global _CACHE_DATAFRAMES, _CACHE_VOTOS_PROCESADOS
    _CACHE_DATAFRAMES.clear()
    _CACHE_VOTOS_PROCESADOS.clear()
    obtener_dataframe_procesado.cache_clear()
    secciones_ganadas.cache_clear()
    municipios_ganados.cache_clear()
    votos_por_seccion.cache_clear()
    analizar_rangos_votos.cache_clear()
    obtener_secciones_ordenadas.cache_clear()


def limpiar_nombres_secciones(datos_dict):
    """
    Limpia los nombres de secciones en un diccionario, removiendo 'Sección'

    Args:
        datos_dict: Diccionario con secciones como claves

    Returns:
        dict: Diccionario con nombres de secciones limpios
    """
    if not datos_dict:
        return {}

    def limpiar_nombre_seccion(seccion):
        """Limpia el nombre de la sección removiendo 'Sección'."""
        seccion_limpia = seccion.replace("Sección", "").strip()
        seccion_limpia = seccion_limpia.replace("SECCIÓN", "").strip()
        return seccion_limpia

    # Crear nuevo diccionario con nombres limpios
    resultado_limpio = {}
    for seccion_completa, datos in datos_dict.items():
        seccion_limpia = limpiar_nombre_seccion(seccion_completa)
        resultado_limpio[seccion_limpia] = datos

    return resultado_limpio


def estadisticas_cache():
    """Devuelve estadísticas del uso del cache."""
    stats = {
        "dataframes_cacheados": len(_CACHE_DATAFRAMES),
        "cache_dataframe_maxsize": 32,
        "cache_secciones_maxsize": 16,
        "cache_municipios_maxsize": 16,
        "cache_votos_seccion_maxsize": 32,
        "cache_rangos_maxsize": 16,
        "cache_secciones_ordenadas_maxsize": 16,
    }
    return stats


def ordenar_secciones(secciones, limpiar_nombres=True):
    """
    Ordena las secciones por número ordinal (Primera, Segunda, Tercera, etc.)
    Opcionalmente limpia los nombres removiendo "Sección"

    Args:
        secciones: Lista de nombres de secciones
        limpiar_nombres: Si True, remueve "Sección" de los nombres

    Returns:
        list: Lista ordenada de secciones (con nombres limpios si se especifica)
    """
    # Mapeo de números ordinales a valores numéricos
    ordinales = {
        "PRIMERA": 1,
        "SEGUNDA": 2,
        "TERCERA": 3,
        "CUARTA": 4,
        "QUINTA": 5,
        "SEXTA": 6,
        "SÉPTIMA": 7,
        "SÉPTIMA": 7,  # variante sin acento
        "OCTAVA": 8,
        "NOVENA": 9,
        "DÉCIMA": 10,
        "DÉCIMA": 10,  # variante sin acento
    }

    def limpiar_nombre_seccion(seccion):
        """Limpia el nombre de la sección removiendo 'Sección'."""
        seccion_limpia = seccion.replace("Sección", "").strip()
        seccion_limpia = seccion_limpia.replace("SECCIÓN", "").strip()
        return seccion_limpia

    def extraer_numero(seccion):
        """Extrae el número ordinal de una sección."""
        # Usar el nombre limpio para la comparación
        nombre_para_comparar = seccion.upper()
        if limpiar_nombres:
            nombre_para_comparar = limpiar_nombre_seccion(seccion).upper()

        for ordinal, numero in ordinales.items():
            if ordinal in nombre_para_comparar:
                return numero
        return 999  # Si no encuentra ordinal, va al final

    # Ordenar por número extraído
    secciones_ordenadas = sorted(secciones, key=extraer_numero)

    # Limpiar nombres si se solicita
    if limpiar_nombres:
        secciones_ordenadas = [
            limpiar_nombre_seccion(seccion) for seccion in secciones_ordenadas
        ]

    return secciones_ordenadas


@lru_cache(maxsize=16)
def obtener_secciones_ordenadas(
    cargo="DIPUTADOS PROVINCIALES", cargo2="SENADORES PROVINCIALES"
):
    """
    Obtiene la lista de secciones disponibles, ordenadas numéricamente.

    Returns:
        list: Lista ordenada de secciones
    """
    try:
        # Obtener dataframe procesado
        df_procesado = obtener_dataframe_procesado(cargo, cargo2)

        if df_procesado is None:
            return []

        df = df_procesado["dataframe"]

        # Obtener secciones únicas y ordenarlas
        secciones = df["Seccion"].unique()
        return ordenar_secciones(list(secciones))

    except Exception as e:
        print(f"Error obteniendo secciones ordenadas: {e}")
        return []


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))


def crear_dataframe(archivo_csv, separador=",", cargo=None, cargo2=None):
    try:
        archivo_csv = str(archivo_csv)  # por si viene como Path
        ext = Path(archivo_csv).suffix.lower()

        # Detectar si es .zip o .csv
        if ext == ".zip":
            df = pd.read_csv(
                archivo_csv,
                encoding="utf-8",
                sep=separador,
                compression="zip",
                low_memory=False,
            )
        else:
            df = pd.read_csv(
                archivo_csv, encoding="utf-8", sep=separador, low_memory=False
            )

        if df.empty:
            print("El archivo está vacío")
            st.warning("⚠️ ERROR INESPERADO")
            return None

        # Reemplazar nulos en la columna "votos" por 0 (si existe)
        if "votos" in df.columns:
            df["votos"] = df["votos"].fillna(0)

        # Filtrar por cargo si corresponde
        if cargo is not None and "Cargo" in df.columns:
            cargos_filtrar = [str(cargo).strip().lower(), str(cargo2).strip().lower()]
            df = df[
                df["Cargo"].astype(str).str.strip().str.lower().isin(cargos_filtrar)
            ]
        elif cargo is not None:
            st.warning(
                "⚠️ La columna 'Cargo' no existe en el archivo, no se aplicó el filtro."
            )

        # Normalizar nombres de secciones
        if "Seccion" in df.columns:
            df["Seccion"] = df["Seccion"].replace("Sección Capital", "Sección Octava")

        return df

    except FileNotFoundError:
        print(f"Error: el archivo '{archivo_csv}' no fue encontrado")
        st.warning("⚠️ ERROR INESPERADO")
    except pd.errors.ParserError:
        print("Error al leer el archivo CSV")
        st.warning("⚠️ ERROR INESPERADO")
    except Exception as e:
        print(f"Ocurrió una excepción inesperada: {e} ({type(e).__name__})")
        st.warning("⚠️ ERROR INESPERADO")

    return None


def guardar_csv(
    df: pd.DataFrame,
    ruta_salida: Path,
    sep: str = ",",
    encoding: str = "utf-8",
    index: bool = False,
):
    """
    Guarda un DataFrame en un archivo CSV.

    Parámetros:
    - df: DataFrame que se desea guardar.
    - ruta_salida: ruta completa del archivo de salida (puede ser Path o str).
    - sep: separador de columnas (por defecto ',').
    - encoding: codificación del archivo (por defecto 'utf-8').
    - index: si se debe guardar el índice del DataFrame.

    Maneja excepciones comunes y da feedback en consola y Streamlit.
    """

    try:
        # Convertir a Path si es string
        ruta_salida = Path(ruta_salida)

        # Crear carpeta si no existe
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)

        # Guardar CSV
        df.to_csv(ruta_salida, sep=sep, encoding=encoding, index=index)
        print(f"✅ Archivo guardado: {ruta_salida}")
        st.success(f"✅ Archivo guardado con éxito: {ruta_salida.name}")

    except PermissionError:
        print(f"❌ Permiso denegado para guardar en: {ruta_salida}")
        st.warning("⚠️ No tenés permisos para guardar en esa ubicación.")
    except FileNotFoundError:
        print(f"❌ Ruta inválida: {ruta_salida}")
        st.warning("⚠️ La ruta especificada no existe.")
    except Exception as e:
        print(f"❌ Error inesperado al guardar: {e} ({type(e).__name__})")
        st.warning("⚠️ Error inesperado al guardar el archivo.")


def contar_votos_por_tipo_eleccion(df: pd.DataFrame):
    """
    Cuenta los votos por tipo de elección, separando votos válidos (Positivo + En Blanco)
    de votos Nulo, según la columna 'Tipo_Voto'.
    """
    try:
        # Asegurar tipo numérico en votos
        df["votos"] = pd.to_numeric(df["votos"], errors="coerce").fillna(0).astype(int)
        # Filtrar por tipo de voto
        df_validos = df[df["tipoVoto"].isin(["positivo", "blancos"])].copy()
        df_nulos = df[
            df["tipoVoto"].isin(["nulo", "recurridos", "comando", "impugnados"])
        ].copy()

        # Agrupar y sumar votos por tipo de elección
        votos_validos = df_validos.groupby("Cargo")["votos"].sum().reset_index()
        votos_validos.rename(columns={"votos": "votos_validos"}, inplace=True)

        votos_nulos = df_nulos.groupby("Cargo")["votos"].sum().reset_index()
        votos_nulos.rename(columns={"votos": "votos_nulos"}, inplace=True)

        # Unir ambos resultados (outer join para no perder elecciones sin nulos o sin válidos)
        resumen = pd.merge(votos_validos, votos_nulos, on="Cargo", how="outer").fillna(
            0
        )
        resumen[["votos_validos", "votos_nulos"]] = resumen[
            ["votos_validos", "votos_nulos"]
        ].astype(int)

    except KeyError as e:
        print(f"Error: Faltan columnas necesarias en el DataFrame {e}.")
    except Exception as e:
        print(f"Error al contar los votos por tipo de elección: {e}")
    return resumen


def contar_total_electores(df: pd.DataFrame) -> int:
    """
    Cuenta la cantidad total de electores a partir de un CSV con separador ';'.
    Asume que 'Electores' usa punto como separador de miles.
    """
    try:

        # Limpiar columna 'Electores': eliminar puntos, convertir a int
        df["Electores"] = (
            df["Electores"]
            .astype(str)
            .str.replace(".", "", regex=False)  # quita puntos separadores de miles
            .str.replace(",", "", regex=False)  # por si hay comas también
        )
        df["Electores"] = (
            pd.to_numeric(df["Electores"], errors="coerce").fillna(0).astype(int)
        )

        # Sumar total
        total_electores = df["Electores"].sum()

        return total_electores

    except Exception as e:
        print(f"Error al procesar el archivo de electores: {e}")
        return None


def sumar_votos(df: pd.DataFrame, tipo: str) -> int:
    """
    Lee el CSV con los votos por tipo de elección y suma los votos válidos + nulos
    de Diputados y Senadores Provinciales.
    """
    try:
        # Asegurar que las columnas sean numéricas
        df[tipo] = pd.to_numeric(df[tipo], errors="coerce").fillna(0)
        # Sumar total
        total = int(df[tipo].sum())

        return total

    except Exception as e:
        print(f"Error al sumar votos validos: {e}")
        return None


def crear_diccionario_votos_por_partido(
    df: pd.DataFrame, columna_partido: str = "Agrupacion", columna_votos: str = "votos"
) -> dict:
    """
    Crea un diccionario con el total de votos por partido.

    Parámetros:
    - df: DataFrame con los datos.
    - columna_partido: nombre de la columna con los partidos políticos.
    - columna_votos: nombre de la columna con los votos.

    Retorna:
    - Un diccionario: {partido: total_votos}
    """
    try:
        # Asegurar que la columna de votos sea numérica
        df[columna_votos] = (
            pd.to_numeric(df[columna_votos], errors="coerce").fillna(0).astype(int)
        )

        # Agrupar por partido y sumar los votos
        resumen = df.groupby(columna_partido)[columna_votos].sum()

        # Convertir a diccionario
        diccionario = resumen.to_dict()

        return diccionario

    except Exception as e:
        print(f"Error al crear el diccionario de votos por partido: {e}")
        return {}


def calcular_porcentaje_partidos(diccionario_votos: dict) -> pd.Series:
    """
    Recibe un diccionario {partido: total_votos} y devuelve una Serie con
    el % de participación de cada partido, ordenado descendente.
    """
    serie = pd.Series(diccionario_votos)
    total = serie.sum()

    if total == 0:
        return pd.Series(dtype=float)

    serie_pct = (serie / total * 100).sort_values(ascending=False).round(1)
    return serie_pct


def mostrar_diccionario_como_tabla(
    diccionario: dict,
    titulo: str = "📋 Total de votos por partido",
    tipo: str = "Partido",
):
    df = pd.Series(diccionario).sort_values(ascending=False).reset_index()
    df.columns = [tipo, "Votos"]

    # Formatear los valores de la columna Votos con separador de miles
    df["Votos"] = df["Votos"].apply(lambda x: f"{x:,}".replace(",", "."))

    st.subheader(titulo)
    st.table(df)


def votos_partido_y_validos_por_seccion(
    df: pd.DataFrame,
    partido_objetivo: str,
    col_partido: str = "Agrupacion",
    col_votos: str = "votos",
    col_seccion: str = "Seccion",
    col_tipo_voto: str = "tipoVoto",
) -> dict:
    """
    Devuelve un diccionario con los votos del partido y los votos válidos por sección electoral.
    No calcula el porcentaje, solo agrupa y retorna los valores.
    """
    try:
        # Verificar que las columnas existan
        required_cols = [col_votos, col_seccion, col_tipo_voto, col_partido]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"Columnas faltantes en el DataFrame: {missing_cols}")
            return {}

        # Asegurar tipo numérico
        df[col_votos] = (
            pd.to_numeric(df[col_votos], errors="coerce").fillna(0).astype(int)
        )

        # Filtrar votos positivos (válidos) - usar comparación directa con minúsculas
        df_validos = df[df[col_tipo_voto] == "positivo"]

        # Total válidos por sección
        votos_validos = df_validos.groupby(col_seccion)[col_votos].sum()

        # Votos del partido por sección - normalizar para comparación robusta
        df_partido = df_validos[
            df_validos[col_partido].str.strip().str.upper()
            == partido_objetivo.strip().upper()
        ]
        votos_partido = df_partido.groupby(col_seccion)[col_votos].sum()

        # Unir ambos en un diccionario por sección
        secciones = sorted(set(votos_validos.index).union(votos_partido.index))

        resultado = {
            seccion: {
                "votos_partido": int(votos_partido.get(seccion, 0)),
                "votos_validos": int(votos_validos.get(seccion, 0)),
            }
            for seccion in secciones
        }

        return resultado

    except Exception as e:
        print(f"Error al agrupar votos por sección: {e}")
        print(f"Tipo de error: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return {}


def calcular_porcentaje_partido_por_seccion(datos: dict) -> dict:
    """
    Recibe un diccionario con votos_partido y votos_validos por sección,
    y devuelve el porcentaje del partido en cada sección.
    """
    resultado = {}

    for seccion, valores in datos.items():
        votos_p = valores["votos_partido"]
        votos_v = valores["votos_validos"]
        if votos_v > 0:
            porcentaje = round((votos_p / votos_v) * 100, 1)
        else:
            porcentaje = 0.0
        resultado[seccion] = porcentaje

    return resultado


def guardar_archivo_subido(archivo, nombre_destino: str, carpeta: str = "data") -> str:
    """
    Guarda un archivo subido vía st.file_uploader en el disco.

    Parámetros:
    - archivo: archivo cargado (tipo BytesIO) desde Streamlit
    - nombre_destino: nombre con el que se va a guardar
    - carpeta: carpeta donde guardar (por defecto 'data')

    Retorna:
    - Ruta completa del archivo guardado (str)
    """
    try:
        # Crear la carpeta si no existe
        Path(carpeta).mkdir(parents=True, exist_ok=True)

        # Ruta completa
        ruta_final = Path(carpeta) / nombre_destino

        if archivo is None:
            raise ValueError("El archivo subido es None (no se seleccionó nada)")
        # Guardar archivo
        with open(ruta_final, "wb") as f:
            f.write(archivo.getbuffer())

        return str(ruta_final)

    except Exception as e:
        print(f"Error al guardar archivo: {e}")
        return ""


def _norm_txt_safe(x: str) -> str:
    if x is None:
        return ""
    s = str(x)
    # normalización robusta sin depender de paquetes externos
    import re, unicodedata

    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.casefold()
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    s = re.sub(r"\s+", " ", s)
    return s


def detectar_mesas_atipicas_por_partido(
    df: pd.DataFrame,
    partido: str,
    umbral_min: float = -5.0,  # mínimo permitido
    umbral_max: float = 5.0,  # máximo permitido
    incluir_blancos_en_denominador: bool = False,
    col_distrito="Distrito",
    col_escuela="Establecimiento",
    col_mesa="Mesa",
    col_partido="Agrupacion",
    col_tipo="tipoVoto",
    col_votos="votos",
) -> pd.DataFrame:
    """
    Detecta mesas cuya participación para 'partido' se desvía del promedio de su escuela
    en más de 'umbral_pp' puntos porcentuales.

    Denominador:
      - Si incluir_blancos_en_denominador=False: usa solo positivos.
      - Si True: usa válidos = positivos + blancos.

    Devuelve columnas:
      Distrito | Establecimiento | Mesa | votos_partido_mesa | denom_mesa | pct_mesa |
      votos_partido_escuela | denom_escuela | pct_escuela | desvio_pp
    """
    df = df.copy()

    # Normalizar
    df[col_votos] = pd.to_numeric(df[col_votos], errors="coerce").fillna(0)
    tipo_norm = df[col_tipo].astype(str).apply(_norm_txt_safe)
    part_norm = df[col_partido].astype(str).apply(_norm_txt_safe)
    target_partido = _norm_txt_safe(partido)
    # Conjuntos de tipos
    es_positivo = tipo_norm.isin({"positivo", "positivos", "valido", "validos"})
    es_blanco = tipo_norm.isin({"blanco", "blancos", "en blanco"})
    # --- Numeradores: votos del partido ---
    df_partido = df[part_norm == target_partido].copy()
    # (Solo líneas de positivos del partido; las filas de blancos no pertenecen a un partido)
    df_partido = df_partido[es_positivo.reindex(df_partido.index, fill_value=False)]
    if df_partido.empty:
        # Mostrar partidos detectados (normalizados) para ver por qué no matchea
        partidos_detectados = (
            df[col_partido].astype(str).map(_norm_txt_safe).value_counts().head(20)
        )
        st.warning(
            f"El partido '{partido}' no aparece tras normalizar. "
            f"Algunos partidos encontrados: {list(partidos_detectados.index[:5])}"
        )
        return pd.DataFrame(
            columns=[
                col_distrito,
                col_escuela,
                col_mesa,
                "votos_partido_mesa",
                "denom_mesa",
                "pct_mesa",
                "votos_partido_escuela",
                "denom_escuela",
                "pct_escuela",
                "desvio_pp",
            ]
        )
    votos_partido_mesa = (
        df_partido.groupby([col_distrito, col_escuela, col_mesa])[col_votos]
        .sum()
        .reset_index(name="votos_partido_mesa")
    )

    votos_partido_escuela = (
        df_partido.groupby([col_distrito, col_escuela])[col_votos]
        .sum()
        .reset_index(name="votos_partido_escuela")
    )

    # --- Denominadores: totales por mesa/escuela ---
    if incluir_blancos_en_denominador:
        mask_denom = es_positivo | es_blanco
    else:
        mask_denom = es_positivo

    df_denom = df[mask_denom].copy()

    denom_mesa = (
        df_denom.groupby([col_distrito, col_escuela, col_mesa])[col_votos]
        .sum()
        .reset_index(name="denom_mesa")
    )

    denom_escuela = (
        df_denom.groupby([col_distrito, col_escuela])[col_votos]
        .sum()
        .reset_index(name="denom_escuela")
    )

    # --- Joines ---
    base = denom_mesa.merge(
        votos_partido_mesa, on=[col_distrito, col_escuela, col_mesa], how="left"
    )
    base = base.merge(denom_escuela, on=[col_distrito, col_escuela], how="left")
    base = base.merge(votos_partido_escuela, on=[col_distrito, col_escuela], how="left")

    # Manejo de NaN (p.ej., si el partido no tiene votos en alguna escuela/mesa)
    for c in ["votos_partido_mesa", "votos_partido_escuela"]:
        base[c] = base[c].fillna(0)

    # % mesa y % escuela (en %)
    base["pct_mesa"] = (base["votos_partido_mesa"] / base["denom_mesa"]).replace(
        [pd.NA, float("inf")], 0
    ) * 100
    base["pct_escuela"] = (
        base["votos_partido_escuela"] / base["denom_escuela"]
    ).replace([pd.NA, float("inf")], 0) * 100

    # Desvío en puntos porcentuales
    base["desvio_pp"] = base["pct_mesa"] - base["pct_escuela"]
    # Filtrar por umbral (absoluto)
    # Filtrar por rango (entre mínimo y máximo)
    outliers = base[
        (base["desvio_pp"] >= umbral_min) & (base["desvio_pp"] <= umbral_max)
    ].copy()

    # Redondeo para visualización
    outliers["pct_mesa"] = outliers["pct_mesa"].round(1)
    outliers["pct_escuela"] = outliers["pct_escuela"].round(1)
    outliers["desvio_pp"] = outliers["desvio_pp"].round(1)

    # Orden agradable
    outliers = outliers.sort_values([col_distrito, col_escuela, col_mesa])

    # Reordenar columnas
    cols = [
        col_distrito,
        col_escuela,
        col_mesa,
        "votos_partido_mesa",
        "denom_mesa",
        "pct_mesa",
        "votos_partido_escuela",
        "denom_escuela",
        "pct_escuela",
        "desvio_pp",
    ]
    return outliers[cols]


@lru_cache(maxsize=16)
def municipios_ganados(
    partidos_str,  # Cambiar a string para que sea hashable para lru_cache
    municipios_amba_str=None,  # String para municipios AMBA
    cargo="DIPUTADOS PROVINCIALES",
    cargo2="SENADORES PROVINCIALES",
):
    """
    Calcula cuántos municipios ganó cada partido de una lista.
    Optimizada para usar cache y procesamiento compartido.
    """
    try:
        # Convertir strings de vuelta a objetos
        partidos = eval(partidos_str) if isinstance(partidos_str, str) else partidos_str
        municipios_amba = eval(municipios_amba_str) if municipios_amba_str else None

        # Obtener dataframe procesado del cache
        df_procesado = obtener_dataframe_procesado(cargo, cargo2)

        if df_procesado is None:
            return (
                pd.Series(dtype=int),
                pd.Series(dtype=int),
                pd.DataFrame(),
                pd.DataFrame(),
            )

        df = df_procesado["dataframe"]

        # Función de normalización
        def normalizar_texto(texto):
            if pd.isna(texto):
                return ""
            return str(texto).strip().upper()

        # Crear mapeo de partidos normalizados
        partidos_normalizados = {normalizar_texto(p): p for p in partidos}

        # Usar índices optimizados
        df_validos = df[df["tipoVoto_lower"] == "positivo"]

        if df_validos.empty:
            return (
                pd.Series(dtype=int),
                pd.Series(dtype=int),
                pd.DataFrame(),
                pd.DataFrame(),
            )

        # Limpiar valores NaN
        df_validos = df_validos.dropna(subset=["Agrupacion"])

        # Normalizar partidos
        df_validos = df_validos.copy()
        df_validos["partido_normalizado"] = df_validos["Agrupacion"].apply(
            normalizar_texto
        )

        # Filtrar partidos de interés
        partidos_norm_keys = list(partidos_normalizados.keys())
        df_filtrado = df_validos[
            df_validos["partido_normalizado"].isin(partidos_norm_keys)
        ]

        if df_filtrado.empty:
            return (
                pd.Series(dtype=int),
                pd.Series(dtype=int),
                pd.DataFrame(),
                pd.DataFrame(),
            )

        # Agrupar eficientemente
        resumen = (
            df_filtrado.groupby(["Distrito", "Agrupacion"])["votos"].sum().reset_index()
        )

        if resumen.empty:
            return (
                pd.Series(dtype=int),
                pd.Series(dtype=int),
                pd.DataFrame(),
                pd.DataFrame(),
            )

        # Encontrar ganadores
        ganadores_total = resumen.loc[resumen.groupby("Distrito")["votos"].idxmax()]
        conteo_total = ganadores_total["Agrupacion"].value_counts()

        # Crear resultado completo
        conteo_completo_total = pd.Series(0, index=partidos, dtype=int)
        for partido_original, cantidad in conteo_total.items():
            partido_norm = normalizar_texto(partido_original)
            if partido_norm in partidos_normalizados:
                nombre_original = partidos_normalizados[partido_norm]
                conteo_completo_total[nombre_original] = cantidad

        # Procesar AMBA si se proporciona
        if municipios_amba:
            municipios_amba_norm = [normalizar_texto(m) for m in municipios_amba]

            ganadores_total_copy = ganadores_total.copy()
            ganadores_total_copy["municipio_normalizado"] = ganadores_total_copy[
                "Distrito"
            ].apply(normalizar_texto)
            ganadores_amba = ganadores_total_copy[
                ganadores_total_copy["municipio_normalizado"].isin(municipios_amba_norm)
            ]

            conteo_amba = ganadores_amba["Agrupacion"].value_counts()
            conteo_completo_amba = pd.Series(0, index=partidos, dtype=int)
            for partido_original, cantidad in conteo_amba.items():
                partido_norm = normalizar_texto(partido_original)
                if partido_norm in partidos_normalizados:
                    nombre_original = partidos_normalizados[partido_norm]
                    conteo_completo_amba[nombre_original] = cantidad
        else:
            conteo_completo_amba = pd.Series(0, index=partidos, dtype=int)
            ganadores_amba = pd.DataFrame()

        return (
            conteo_completo_total,
            conteo_completo_amba,
            ganadores_total,
            ganadores_amba,
        )

    except Exception as e:
        print(f"ERROR en municipios_ganados: {e}")
        return (
            pd.Series(dtype=int),
            pd.Series(dtype=int),
            pd.DataFrame(),
            pd.DataFrame(),
        )


@lru_cache(maxsize=16)
def analizar_rangos_votos(
    partidos_str, cargo="DIPUTADOS PROVINCIALES", cargo2="SENADORES PROVINCIALES"
):
    """
    Analiza los porcentajes de votos por municipio para partidos específicos
    y los clasifica en rangos predefinidos.
    Optimizada para usar cache y procesamiento compartido.
    """
    try:
        # Convertir string de partidos a lista
        partidos_interes = (
            eval(partidos_str) if isinstance(partidos_str, str) else partidos_str
        )

        # Obtener dataframe procesado del cache
        df_procesado = obtener_dataframe_procesado(cargo, cargo2)

        if df_procesado is None:
            return {}

        df = df_procesado["dataframe"]

        # Función de normalización
        def normalizar_texto(texto):
            if pd.isna(texto):
                return ""
            return str(texto).strip().upper()

        # Usar índices optimizados
        df_validos = df[df["tipoVoto_lower"] == "positivo"]

        if df_validos.empty:
            return {}

        # Limpiar valores NaN
        df_validos = df_validos.dropna(subset=["Agrupacion"])

        # Calcular votos válidos totales por municipio
        votos_validos_por_municipio = (
            df_validos.groupby("Distrito")["votos"]
            .sum()
            .reset_index()
            .rename(columns={"votos": "votos_validos_total"})
        )

        # Calcular votos por partido y municipio
        votos_partido_por_municipio = (
            df_validos.groupby(["Distrito", "Agrupacion"])["votos"].sum().reset_index()
        )

        # Unir eficientemente
        df_completo = pd.merge(
            votos_partido_por_municipio,
            votos_validos_por_municipio,
            on="Distrito",
            how="left",
        )

        # Calcular porcentajes
        df_completo["porcentaje"] = (
            df_completo["votos"] / df_completo["votos_validos_total"]
        ) * 100

        # Inicializar resultados
        resultados = {}

        for partido_interes in partidos_interes:
            # Normalizar nombre del partido
            partido_norm = normalizar_texto(partido_interes)

            # Filtrar datos del partido específico
            df_partido = df_completo[
                df_completo["Agrupacion"].apply(normalizar_texto) == partido_norm
            ].copy()

            if df_partido.empty:
                resultados[partido_interes] = {
                    "< 20%": 0,
                    "20-30%": 0,
                    "30-40%": 0,
                    "40-50%": 0,
                    "> 50%": 0,
                }
                continue

            # Clasificar por rangos
            rangos = {
                "< 20%": len(df_partido[df_partido["porcentaje"] < 20]),
                "20-30%": len(
                    df_partido[
                        (df_partido["porcentaje"] >= 20)
                        & (df_partido["porcentaje"] < 30)
                    ]
                ),
                "30-40%": len(
                    df_partido[
                        (df_partido["porcentaje"] >= 30)
                        & (df_partido["porcentaje"] < 40)
                    ]
                ),
                "40-50%": len(
                    df_partido[
                        (df_partido["porcentaje"] >= 40)
                        & (df_partido["porcentaje"] < 50)
                    ]
                ),
                "> 50%": len(df_partido[df_partido["porcentaje"] >= 50]),
            }

            resultados[partido_interes] = rangos

        return resultados

    except Exception as e:
        print(f"ERROR en analizar_rangos_votos: {e}")
        return {}


@lru_cache(maxsize=32)
def votos_por_seccion(
    seccion, cargo="DIPUTADOS PROVINCIALES", cargo2="SENADORES PROVINCIALES"
):
    """
    Calcula los votos por partido para una sección específica.
    Optimizada para usar cache y procesamiento compartido.
    """
    try:
        # Obtener dataframe procesado del cache
        df_procesado = obtener_dataframe_procesado(cargo, cargo2)

        if df_procesado is None:
            return {}

        df = df_procesado["dataframe"]

        # Función de normalización
        def normalizar_texto(texto):
            if pd.isna(texto):
                return ""
            return str(texto).strip().upper()

        # Si el nombre de sección no contiene "Sección", agregarlo para búsqueda
        if "sección" not in seccion.lower():
            seccion_completa = f"Sección {seccion}"
        else:
            seccion_completa = seccion

        # Normalizar nombre de sección para comparación
        seccion_norm = normalizar_texto(seccion_completa)

        # Filtrar por sección específica usando índices optimizados
        df_seccion = df[
            (df["tipoVoto_lower"] == "positivo")
            & (df["Seccion"].apply(normalizar_texto) == seccion_norm)
        ]

        if df_seccion.empty:
            print(f"ADVERTENCIA: No se encontraron datos para la sección {seccion}")
            return {}

        # Limpiar valores NaN
        df_seccion = df_seccion.dropna(subset=["Agrupacion"])

        # Calcular votos por partido
        votos_por_partido = (
            df_seccion.groupby("Agrupacion")["votos"].sum().sort_values(ascending=False)
        )

        # Calcular votos en blanco (desde el dataframe original)
        df_blancos = df[
            (df["Seccion"].apply(normalizar_texto) == seccion_norm)
            & (df["tipoVoto_lower"] == "blancos")
        ]

        votos_blancos = df_blancos["votos"].sum() if not df_blancos.empty else 0

        # Agregar votos en blanco al resultado
        if votos_blancos > 0:
            # Crear nueva serie incluyendo votos en blanco
            votos_con_blancos = votos_por_partido.copy()
            votos_con_blancos["VOTOS EN BLANCO"] = votos_blancos
            votos_con_blancos = votos_con_blancos.sort_values(ascending=False)

            # Calcular total incluyendo votos en blanco
            total_votos = votos_con_blancos.sum()

            # Calcular porcentajes
            porcentajes = (votos_con_blancos / total_votos * 100).round(1)

            resultado = {
                "votos": votos_con_blancos.to_dict(),
                "porcentajes": porcentajes.to_dict(),
                "total_votos": total_votos,
                "partidos": list(votos_con_blancos.index),
                "votos_blancos": votos_blancos,
            }
        else:
            # Si no hay votos en blanco, usar el cálculo original
            total_votos = votos_por_partido.sum()
            porcentajes = (votos_por_partido / total_votos * 100).round(1)

            resultado = {
                "votos": votos_por_partido.to_dict(),
                "porcentajes": porcentajes.to_dict(),
                "total_votos": total_votos,
                "partidos": list(votos_por_partido.index),
                "votos_blancos": 0,
            }

        return resultado

    except Exception as e:
        print(f"ERROR en votos_por_seccion: {e}")
        return {}


@lru_cache(maxsize=16)
def secciones_ganadas(
    partidos_str,  # Cambiar a string para que sea hashable para lru_cache
    cargo="DIPUTADOS PROVINCIALES",
    cargo2="SENADORES PROVINCIALES",
):
    """
    Calcula cuántas secciones ganó cada partido de una lista.
    Optimizada para usar cache y procesamiento compartido.
    """
    try:
        # Convertir string de partidos de vuelta a lista
        partidos = eval(partidos_str) if isinstance(partidos_str, str) else partidos_str

        # Obtener dataframe procesado del cache
        df_procesado = obtener_dataframe_procesado(cargo, cargo2)

        if df_procesado is None:
            return pd.Series(dtype=int), pd.DataFrame()

        df = df_procesado["dataframe"]

        # Función de normalización
        def normalizar_texto(texto):
            if pd.isna(texto):
                return ""
            return str(texto).strip().upper()

        # Crear mapeo de partidos normalizados
        partidos_normalizados = {normalizar_texto(p): p for p in partidos}

        # Usar índices optimizados para filtrado rápido
        df_validos = df[df["tipoVoto_lower"] == "positivo"]

        if df_validos.empty:
            return pd.Series(dtype=int), pd.DataFrame()

        # Limpiar valores NaN
        df_validos = df_validos.dropna(subset=["Agrupacion"])

        # Normalizar partidos para comparación
        df_validos = df_validos.copy()
        df_validos["partido_normalizado"] = df_validos["Agrupacion"].apply(
            normalizar_texto
        )

        # Filtrar partidos de interés
        partidos_norm_keys = list(partidos_normalizados.keys())
        df_filtrado = df_validos[
            df_validos["partido_normalizado"].isin(partidos_norm_keys)
        ]

        if df_filtrado.empty:
            return pd.Series(dtype=int), pd.DataFrame()

        # Agrupar eficientemente
        resumen = (
            df_filtrado.groupby(["Seccion", "Agrupacion"])["votos"].sum().reset_index()
        )

        if resumen.empty:
            return pd.Series(dtype=int), pd.DataFrame()

        # Encontrar ganadores
        ganadores = resumen.loc[resumen.groupby("Seccion")["votos"].idxmax()]
        conteo = ganadores["Agrupacion"].value_counts()

        # Crear resultado completo
        conteo_completo = pd.Series(0, index=partidos, dtype=int)
        for partido_original, cantidad in conteo.items():
            partido_norm = normalizar_texto(partido_original)
            if partido_norm in partidos_normalizados:
                nombre_original = partidos_normalizados[partido_norm]
                conteo_completo[nombre_original] = cantidad

        return conteo_completo, ganadores

    except Exception as e:
        print(f"ERROR en secciones_ganadas: {e}")
        return pd.Series(dtype=int), pd.DataFrame()
