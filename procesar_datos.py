import pandas as pd
import zipfile
import os
from pathlib import Path
from utils.constantes import SECCION_MUNICIPIOS

# Cambiar al directorio del proyecto
os.chdir(Path(__file__).parent)


def procesar_base_elecciones():
    """Procesa el archivo Base_Elecciones.zip para extraer municipios por sección"""

    zip_path = "utils/data/Base_Elecciones.zip"

    # Ver qué archivos hay en el zip
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        archivos = zip_ref.namelist()
        print("Archivos en el ZIP:")
        for archivo in archivos:
            print(f"  {archivo}")

        # Buscar archivos CSV
        archivos_csv = [f for f in archivos if f.endswith(".csv")]

        if not archivos_csv:
            print("No se encontraron archivos CSV en el ZIP")
            return {}

        # Procesar el primer archivo CSV encontrado
        archivo_csv = archivos_csv[0]
        print(f"\nProcesando: {archivo_csv}")

        try:
            with zip_ref.open(archivo_csv) as f:
                # Leer todo el archivo
                df = pd.read_csv(f, encoding="utf-8")
                print(f"Columnas encontradas: {list(df.columns)}")
                print(f"Total de filas: {len(df)}")

                # Buscar columnas relacionadas con sección y municipio
                cols_seccion = [col for col in df.columns if "seccion" in col.lower()]
                cols_municipio = [
                    col
                    for col in df.columns
                    if "municipio" in col.lower() or "distrito" in col.lower()
                ]

                print(f"Columnas de sección encontradas: {cols_seccion}")
                print(f"Columnas de municipio encontradas: {cols_municipio}")

                # Usar la columna Seccion si existe, sino IdCircuito
                if "Seccion" in df.columns:
                    col_seccion = "Seccion"
                elif cols_seccion:
                    col_seccion = cols_seccion[0]
                else:
                    print("No se encontró columna de sección")
                    return {}

                if cols_municipio:
                    col_municipio = cols_municipio[0]
                else:
                    print("No se encontró columna de municipio")
                    return {}

                print(f"Usando columna sección: {col_seccion}")
                print(f"Usando columna municipio: {col_municipio}")

                # Crear el diccionario sección -> lista de municipios
                seccion_municipios = {}

                # Agrupar por sección y obtener municipios únicos
                for seccion, group in df.groupby(col_seccion):
                    municipios = group[col_municipio].unique().tolist()
                    municipios = [str(m).strip() for m in municipios if pd.notna(m)]
                    if municipios:
                        seccion_municipios[str(seccion).strip()] = sorted(municipios)

                print(f"\nTotal de secciones procesadas: {len(seccion_municipios)}")

                # Mostrar algunas secciones de ejemplo
                print("\nEjemplos:")
                for i, (seccion, municipios) in enumerate(
                    list(seccion_municipios.items())[:5]
                ):
                    print(f"Sección {seccion}: {municipios[:3]}...")

                return seccion_municipios

        except Exception as e:
            print(f"Error procesando el archivo: {e}")
            return {}


def guardar_constante(seccion_municipios):
    """Guarda el diccionario como una constante en el archivo utils/constantes.py"""

    # Leer el archivo actual
    constantes_path = "utils/constantes.py"
    try:
        with open(constantes_path, "r", encoding="utf-8") as f:
            contenido_actual = f.read()
    except FileNotFoundError:
        contenido_actual = ""

    # Crear la nueva constante
    import pprint

    seccion_municipios_str = pprint.pformat(seccion_municipios, width=120, indent=4)

    nueva_constante = f"\n# Diccionario que asigna a cada sección sus municipios\nSECCION_MUNICIPIOS = {seccion_municipios_str}\n"

    # Agregar la nueva constante al final del archivo
    contenido_nuevo = contenido_actual + nueva_constante

    # Guardar el archivo
    with open(constantes_path, "w", encoding="utf-8") as f:
        f.write(contenido_nuevo)

    print(f"Constante SECCION_MUNICIPIOS agregada a {constantes_path}")


def procesar_mesas_electores(seccion_municipios):
    """Agrega la información de municipios al archivo mesas_electores_reducido.csv"""

    mesas_path = "utils/data/mesas_electores_reducido.csv"

    try:
        # Leer el archivo CSV
        df = pd.read_csv(mesas_path, encoding="utf-8")
        print(f"Archivo mesas_electores_reducido.csv cargado. Filas: {len(df)}")
        print(f"Columnas: {list(df.columns)}")

        # Verificar si ya existe la columna 'seccion'
        if "seccion" not in df.columns:
            print(
                "ADVERTENCIA: No se encontró columna 'seccion' en mesas_electores_reducido.csv"
            )
            print("Columnas disponibles:", list(df.columns))
            return

        # Crear columna de municipios basada en la sección
        def obtener_municipios(seccion):
            if pd.isna(seccion):
                return []
            seccion_str = str(seccion).strip()
            return seccion_municipios.get(seccion_str, [])

        df["municipios"] = df["seccion"].apply(obtener_municipios)

        # Guardar el archivo modificado
        output_path = "utils/data/mesas_electores_con_municipios.csv"
        df.to_csv(output_path, index=False, encoding="utf-8")
        print(f"Archivo guardado como: {output_path}")

        # Mostrar estadísticas
        municipios_agregados = df["municipios"].apply(len).sum()
        secciones_con_municipios = df[df["municipios"].apply(len) > 0].shape[0]
        print(f"Secciones con municipios asignados: {secciones_con_municipios}")
        print(f"Total de asignaciones municipio-sección: {municipios_agregados}")

    except Exception as e:
        print(f"Error procesando mesas_electores_reducido.csv: {e}")


def agregar_seccion_electoral_csv():
    """
    Agrega una columna de sección electoral al archivo mesas_electores_reducido.csv
    usando el mapeo de la constante SECCION_MUNICIPIOS
    """
    # Crear diccionario invertido: municipio -> sección
    municipio_a_seccion = {}
    for seccion, municipios in SECCION_MUNICIPIOS.items():
        for municipio in municipios:
            municipio_a_seccion[municipio.upper()] = seccion

    # Ruta del archivo
    archivo_csv = "utils/data/mesas_electores_reducido.csv"

    try:
        # Leer el archivo CSV
        print(f"Leyendo archivo: {archivo_csv}")
        df = pd.read_csv(archivo_csv, encoding="utf-8")

        print(f"Archivo leído con {len(df)} filas y {len(df.columns)} columnas")
        print(f"Columnas actuales: {list(df.columns)}")

        # Agregar columna de sección electoral
        def obtener_seccion(municipio):
            municipio_upper = str(municipio).upper()
            return municipio_a_seccion.get(municipio_upper, "NO ENCONTRADO")

        df["seccion_electoral"] = df["nombre_distrito"].apply(obtener_seccion)

        # Reordenar columnas para que seccion_electoral quede después de nombre_distrito
        columnas = ["nombre_distrito", "seccion_electoral"] + [
            col
            for col in df.columns
            if col not in ["nombre_distrito", "seccion_electoral"]
        ]
        df = df[columnas]

        # Guardar el archivo actualizado
        df.to_csv(archivo_csv, index=False, encoding="utf-8")
        print(f"Archivo actualizado guardado en: {archivo_csv}")
        print(f"Nueva estructura de columnas: {list(df.columns)}")

        # Verificar algunos mapeos
        print("\nEjemplos de mapeo:")
        ejemplos = (
            df[["nombre_distrito", "seccion_electoral"]].drop_duplicates().head(10)
        )
        for _, row in ejemplos.iterrows():
            print(f"  {row['nombre_distrito']} -> {row['seccion_electoral']}")

        # Verificar si hay municipios sin mapeo
        sin_mapeo = df[df["seccion_electoral"] == "NO ENCONTRADO"]
        if len(sin_mapeo) > 0:
            municipios_sin_mapeo = sin_mapeo["nombre_distrito"].unique()
            print(f"\nMunicipios sin mapeo encontrado ({len(municipios_sin_mapeo)}):")
            for municipio in municipios_sin_mapeo[:10]:  # Mostrar solo los primeros 10
                print(f"  {municipio}")
            if len(municipios_sin_mapeo) > 10:
                print(f"  ... y {len(municipios_sin_mapeo) - 10} más")

    except Exception as e:
        print(f"Error al procesar el archivo: {str(e)}")


if __name__ == "__main__":
    print("Agregando columna de sección electoral al archivo CSV...")
    agregar_seccion_electoral_csv()
