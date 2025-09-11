import pandas as pd
import os
from pathlib import Path


def crear_mapeo_seccion_municipio():
    """
    Crea un diccionario que mapea cada municipio a su sección electoral.
    """
    # Importar las constantes
    import sys

    sys.path.append(str(Path(__file__).parent))
    from utils.constantes import SECCION_MUNICIPIOS

    # Crear diccionario inverso: municipio -> sección
    municipio_a_seccion = {}

    for seccion, municipios in SECCION_MUNICIPIOS.items():
        for municipio in municipios:
            municipio_a_seccion[municipio] = seccion

    return municipio_a_seccion


def mapear_secciones_extranjeros():
    """
    Mapea las mesas de extranjeros con sus secciones electorales correctas.
    """

    # Cambiar al directorio del proyecto
    os.chdir(Path(__file__).parent)

    print("🗺️ Mapeando secciones electorales de extranjeros...")

    # Crear mapeo municipio -> sección
    mapeo = crear_mapeo_seccion_municipio()
    print(f"📊 Creado mapeo para {len(mapeo)} municipios")

    # Rutas de archivos
    ruta_actual = "utils/data/mesas_con_extranjeros.csv"
    ruta_nueva = "utils/data/mesas_con_extranjeros_secciones.csv"

    # Cargar datos
    print("📖 Cargando datos consolidados...")
    df = pd.read_csv(ruta_actual)
    print(f"✅ Datos cargados: {len(df):,} filas")

    # Separar mesas locales y extranjeras
    df_locales = df[df["seccion_electoral"] != "EXTRANJEROS"]
    df_extranjeros = df[df["seccion_electoral"] == "EXTRANJEROS"]

    print(f"🏠 Mesas locales: {len(df_locales):,}")
    print(f"🌍 Mesas de extranjeros: {len(df_extranjeros):,}")

    # Mapear secciones para extranjeros
    print("\n🔄 Mapeando secciones para extranjeros...")

    # Función para obtener sección de un municipio
    def obtener_seccion(municipio):
        return mapeo.get(
            municipio, "EXTRANJEROS"
        )  # Fallback a EXTRANJEROS si no se encuentra

    # Aplicar mapeo
    df_extranjeros = df_extranjeros.copy()
    df_extranjeros["seccion_electoral"] = df_extranjeros["nombre_distrito"].apply(
        obtener_seccion
    )

    # Verificar resultados del mapeo
    print("\n📊 Resultados del mapeo:")
    secciones_mapeadas = df_extranjeros["seccion_electoral"].value_counts()
    for seccion, cantidad in secciones_mapeadas.items():
        print(f"   - {seccion}: {cantidad} mesas")

    # Verificar si algún municipio no se pudo mapear
    no_mapeados = df_extranjeros[df_extranjeros["seccion_electoral"] == "EXTRANJEROS"]
    if len(no_mapeados) > 0:
        municipios_no_mapeados = no_mapeados["nombre_distrito"].unique()
        print(f"\n⚠️ Municipios no mapeados ({len(municipios_no_mapeados)}):")
        for municipio in municipios_no_mapeados:
            print(f"   - {municipio}")

    # Combinar dataframes
    print("\n🔗 Combinando datos...")
    df_actualizado = pd.concat([df_locales, df_extranjeros], ignore_index=True)

    # Ordenar por municipio y mesa
    df_actualizado = df_actualizado.sort_values(["nombre_distrito", "nro_mesa"])

    # Verificar estadísticas finales
    print("\n📊 Estadísticas finales:")
    print(f"   - Total de mesas: {len(df_actualizado):,}")

    # Distribución por sección
    secciones_total = df_actualizado["seccion_electoral"].value_counts()
    print("\n🏛️ Distribución por sección:")
    for seccion, cantidad in secciones_total.items():
        print(f"   - {seccion}: {cantidad:,} mesas")

    # Guardar archivo actualizado
    print(f"\n💾 Guardando archivo actualizado: {ruta_nueva}")
    df_actualizado.to_csv(ruta_nueva, index=False, encoding="utf-8")
    print("✅ Archivo guardado exitosamente!")

    # Mostrar algunas filas de ejemplo
    print("\n📋 Ejemplos de mesas de extranjeros con secciones correctas:")
    ejemplos = df_extranjeros.head(3)
    for _, row in ejemplos.iterrows():
        print(
            f"   - {row['nombre_distrito']} -> {row['seccion_electoral']} (Mesa {row['nro_mesa']})"
        )

    return df_actualizado


if __name__ == "__main__":
    resultado = mapear_secciones_extranjeros()
    if resultado is not None:
        print("\n🎉 ¡Mapeo completado exitosamente!")
    else:
        print("\n❌ El mapeo falló.")
