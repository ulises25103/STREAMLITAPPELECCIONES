import pandas as pd
import os
from pathlib import Path


def procesar_mesas_electores():
    """Procesa mesas_electores_reducido.csv para agregar columna seccion"""

    # Cambiar al directorio del proyecto
    os.chdir(Path(__file__).parent)

    # Importar el diccionario de secciones
    from utils.constantes import SECCION_MUNICIPIOS

    # Crear un diccionario inverso: municipio -> sección
    municipio_a_seccion = {}
    for seccion, municipios in SECCION_MUNICIPIOS.items():
        for municipio in municipios:
            municipio_a_seccion[municipio.upper()] = seccion

    print(f"Creado mapeo municipio->sección con {len(municipio_a_seccion)} municipios")

    # Leer el archivo CSV
    mesas_path = "utils/data/mesas_electores_reducido.csv"
    df = pd.read_csv(mesas_path, encoding="utf-8")

    print(f"Archivo cargado: {len(df)} filas")
    print(f"Columnas actuales: {list(df.columns)}")

    # Función para determinar sección basada en nombre_distrito
    def obtener_seccion_por_municipio(nombre_distrito):
        if pd.isna(nombre_distrito):
            return "Sección Desconocida"

        municipio_normalizado = str(nombre_distrito).strip().upper()
        return municipio_a_seccion.get(municipio_normalizado, "Sección Desconocida")

    # Crear la nueva columna 'seccion' temporal con otro nombre
    df["seccion_temp"] = df["nombre_distrito"].apply(obtener_seccion_por_municipio)

    # Eliminar la columna 'cod_circ' y colocar 'seccion_temp' en su lugar
    columnas = list(df.columns)
    idx_cod_circ = columnas.index("cod_circ")

    # Crear DataFrame sin 'cod_circ'
    df = df.drop("cod_circ", axis=1)

    # Renombrar 'seccion_temp' a 'seccion'
    df = df.rename(columns={"seccion_temp": "seccion"})

    # Reordenar para colocar 'seccion' en la posición original de 'cod_circ'
    columnas_actuales = list(df.columns)
    seccion_idx = columnas_actuales.index("seccion")

    # Mover 'seccion' a la posición correcta
    if seccion_idx != idx_cod_circ:
        columnas_reordenadas = columnas_actuales.copy()
        columnas_reordenadas.pop(seccion_idx)
        columnas_reordenadas.insert(idx_cod_circ, "seccion")
        df = df[columnas_reordenadas]

    print(f"Columnas después del reordenamiento: {list(df.columns)}")
    print()
    print("Distribución de secciones asignadas:")
    distribucion = df["seccion"].value_counts()
    for seccion, count in distribucion.items():
        print(f"  {seccion}: {count} mesas")

    # Agregar columna de municipios usando el diccionario SECCION_MUNICIPIOS
    def obtener_municipios_por_seccion(seccion):
        return SECCION_MUNICIPIOS.get(seccion, [])

    df["municipios"] = df["seccion"].apply(obtener_municipios_por_seccion)

    # Guardar el archivo modificado
    output_path = "utils/data/mesas_electores_con_seccion.csv"
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"\nArchivo guardado como: {output_path}")
    print(f"Total de filas procesadas: {len(df)}")

    # Estadísticas finales
    secciones_con_datos = df[df["seccion"] != "Sección Desconocida"]
    print(
        f"Mesas con sección asignada: {len(secciones_con_datos)} ({len(secciones_con_datos)/len(df)*100:.1f}%)"
    )


if __name__ == "__main__":
    procesar_mesas_electores()
