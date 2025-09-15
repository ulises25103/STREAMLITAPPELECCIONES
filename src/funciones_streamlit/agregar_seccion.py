import pandas as pd
import os
import sys

# Agregar la ruta del proyecto para poder importar constantes
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from utils.constantes import SECCION_MUNICIPIOS


def crear_mapeo_municipio_seccion():
    """Crea un diccionario que mapea cada municipio a su sección correspondiente"""

    mapeo_municipio_seccion = {}

    for seccion, municipios in SECCION_MUNICIPIOS.items():
        for municipio in municipios:
            mapeo_municipio_seccion[municipio] = seccion

    print(
        f"🔗 Mapeo creado: {len(mapeo_municipio_seccion)} municipios mapeados a {len(SECCION_MUNICIPIOS)} secciones"
    )
    return mapeo_municipio_seccion


def agregar_columna_seccion():
    """Agrega columna 'seccion' al CSV normalizado usando el mapeo de SECCION_MUNICIPIOS"""

    ruta_csv = os.path.join("utils", "data", "base_mesas_electores_normalizado.csv")

    print("🔍 Leyendo archivo CSV normalizado...")
    df = pd.read_csv(ruta_csv)

    print(f"📊 Archivo actual: {len(df):,} filas")
    print(f"📋 Columnas actuales: {list(df.columns)}")
    print()

    # Crear mapeo municipio -> sección
    mapeo_seccion = crear_mapeo_municipio_seccion()

    # Agregar columna de sección
    print("🏛️ Agregando columna 'seccion'...")
    df["seccion"] = df["nombre_circuito"].map(mapeo_seccion)

    # Verificar si hay municipios sin mapeo
    municipios_sin_mapeo = df[df["seccion"].isnull()]["nombre_circuito"].unique()

    if len(municipios_sin_mapeo) > 0:
        print(f"⚠️ Municipios sin mapeo encontrado: {sorted(municipios_sin_mapeo)}")
        print(
            "Esto puede indicar que falta algún municipio en la constante SECCION_MUNICIPIOS"
        )
    else:
        print("✅ Todos los municipios tienen mapeo correcto")

    print(f"\n📊 Estadísticas:")
    print(f"  Municipios únicos: {df['nombre_circuito'].nunique():,}")
    print(f"  Secciones únicas: {df['seccion'].nunique():,}")

    # Mostrar distribución por sección
    print("\n📈 Distribución por sección:")
    distribucion_seccion = df.groupby("seccion").size().sort_values(ascending=False)
    for seccion, count in distribucion_seccion.items():
        print(f"  {seccion}: {count:,} mesas")

    # Reorganizar columnas: poner seccion después de nombre_circuito
    columnas_ordenadas = [
        "cod_circ",
        "distrito",
        "nombre_circuito",
        "seccion",
        "establecimiento",
        "nro_mesa",
        "cantidad_electores",
        "tipo",
    ]

    df_final = df[columnas_ordenadas]

    print("\n📋 Columnas finales:")
    print(f"  {list(df_final.columns)}")

    # Crear nuevo archivo con la columna seccion
    ruta_con_seccion = os.path.join(
        "utils", "data", "base_mesas_electores_normalizado.csv"
    )
    print(
        f"\n💾 Actualizando archivo normalizado con columna 'seccion': {ruta_con_seccion}"
    )

    df_final.to_csv(ruta_con_seccion, index=False)
    print("✅ Archivo normalizado actualizado exitosamente")

    # Estadísticas finales
    print(f"\n📊 Resumen final:")
    print(f"  Total de mesas: {len(df_final):,}")
    print(f"  Circuitos únicos: {df_final['cod_circ'].nunique():,}")
    print(f"  Distritos únicos: {df_final['distrito'].nunique():,}")
    print(f"  Municipios únicos: {df_final['nombre_circuito'].nunique():,}")
    print(f"  Secciones únicas: {df_final['seccion'].nunique():,}")
    print(f"  Establecimientos únicos: {df_final['establecimiento'].nunique():,}")
    print(f"  Total electores: {df_final['cantidad_electores'].sum():,}")

    return df_final


def verificar_municipios_sin_seccion():
    """Verifica qué municipios del CSV no están en SECCION_MUNICIPIOS"""

    ruta_csv = os.path.join("utils", "data", "base_mesas_electores_normalizado.csv")
    df = pd.read_csv(ruta_csv)

    # Crear conjunto de municipios en SECCION_MUNICIPIOS
    municipios_en_constante = set()
    for municipios in SECCION_MUNICIPIOS.values():
        municipios_en_constante.update(municipios)

    # Municipios en CSV
    municipios_en_csv = set(df["nombre_circuito"].unique())

    # Comparar
    faltantes_en_constante = municipios_en_csv - municipios_en_constante
    faltantes_en_csv = municipios_en_constante - municipios_en_csv

    print("🔍 Verificación completa de mapeo:")
    print(f"  Municipios en CSV: {len(municipios_en_csv)}")
    print(
        f"  Municipios en constante SECCION_MUNICIPIOS: {len(municipios_en_constante)}"
    )

    if faltantes_en_constante:
        print(
            f"  ❌ Municipios en CSV pero no en constante: {sorted(faltantes_en_constante)}"
        )

    if faltantes_en_csv:
        print(
            f"  ℹ️ Municipios en constante pero no en CSV: {len(faltantes_en_csv)} municipios"
        )

    if not faltantes_en_constante:
        print("  ✅ Mapeo completo: Todos los municipios del CSV están en la constante")

    return len(faltantes_en_constante) == 0


if __name__ == "__main__":
    print("🏛️ AGREGANDO SECCIONES A LOS MUNICIPIOS")
    print("=" * 50)

    # Verificar mapeo primero
    mapeo_completo = verificar_municipios_sin_seccion()
    print()

    if mapeo_completo:
        # Proceder con la agregación
        df_resultado = agregar_columna_seccion()
    else:
        print(
            "❌ Error: Hay municipios sin mapeo. Revisa la constante SECCION_MUNICIPIOS."
        )
        df_resultado = None

    print("\n" + "=" * 50)
    print("✅ Proceso completado")
